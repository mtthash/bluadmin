"""GPO policy management endpoints."""

from __future__ import annotations

import asyncio
import os
import uuid as uuid_mod

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_permissions
from app.config import get_settings

import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PolicyStatus(BaseModel):
    policy: str
    status: str
    detail: str | None = None


def _get_winrm_session():
    import winrm
    settings = get_settings()
    return winrm.Session(
        f"http://{settings.file_share_server}:5985/wsman",
        auth=(
            settings.ldap_bind_dn.split(",")[0].replace("CN=", ""),
            settings.ldap_bind_password,
        ),
        transport="ntlm",
    )


def _configure_wallpaper_gpo(download_url: str, dest_file: str) -> str:
    settings = get_settings()
    server = settings.file_share_server

    unc_path = f"\\\\{server}\\Departamentos\\{dest_file}"

    session = _get_winrm_session()

    script = f"""
$sharePath = (Get-SmbShare -Name 'Departamentos').Path
$dest = Join-Path $sharePath '{dest_file}'

# Baixar imagem da API do BluAdmin
try {{
    Invoke-WebRequest -Uri '{download_url}' -OutFile $dest -UseBasicParsing -TimeoutSec 30
}} catch {{
    Write-Error "Falha ao baixar imagem: $($_.Exception.Message)"
    exit 1
}}

Import-Module GroupPolicy

$gpoName = 'BluAdmin - Wallpaper'
$gpo = Get-GPO -Name $gpoName -ErrorAction SilentlyContinue
if (-not $gpo) {{
    $gpo = New-GPO -Name $gpoName -Comment 'Wallpaper corporativo gerenciado pelo BluAdmin'
    New-GPLink -Name $gpoName -Target 'DC=bluilu,DC=local' -LinkEnabled Yes | Out-Null
}}

Set-GPRegistryValue -Name $gpoName -Key 'HKCU\\Control Panel\\Desktop' -ValueName 'Wallpaper' -Type String -Value '{unc_path}' | Out-Null
Set-GPRegistryValue -Name $gpoName -Key 'HKCU\\Control Panel\\Desktop' -ValueName 'WallpaperStyle' -Type String -Value '10' | Out-Null
Set-GPRegistryValue -Name $gpoName -Key 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -ValueName 'Wallpaper' -Type String -Value '{unc_path}' | Out-Null
Set-GPRegistryValue -Name $gpoName -Key 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -ValueName 'WallpaperStyle' -Type String -Value '10' | Out-Null

Write-Output "OK"
"""

    result = session.run_ps(script)
    output = result.std_out.decode("utf-8", errors="replace").strip()

    if result.status_code != 0 or "OK" not in output:
        error = result.std_err.decode("utf-8", errors="replace")
        raise Exception(error or "Falha ao configurar GPO de wallpaper")

    return unc_path


@router.get("/uploads/{filename}")
async def serve_upload(filename: str) -> FileResponse:
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")
    return FileResponse(path)


@router.post(
    "/wallpaper",
    response_model=PolicyStatus,
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def set_wallpaper(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> PolicyStatus:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="O arquivo deve ser uma imagem")

    contents = await image.read()
    max_size = 10 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(status_code=422, detail="Imagem deve ter no maximo 10MB")

    filename = image.filename or "wallpaper.jpg"
    extension = filename[filename.rfind("."):] if "." in filename else ".jpg"
    dest_file = f"wallpaper{extension}"

    temp_name = f"{uuid_mod.uuid4().hex}{extension}"
    temp_path = os.path.join(UPLOAD_DIR, temp_name)
    with open(temp_path, "wb") as f:
        f.write(contents)

    settings = get_settings()
    download_url = f"http://192.168.1.2:8000/api/v1/policies/uploads/{temp_name}"

    try:
        unc_path = await asyncio.to_thread(_configure_wallpaper_gpo, download_url, dest_file)
        logger.info("wallpaper_gpo_applied", path=unc_path)
        return PolicyStatus(
            policy="wallpaper",
            status="success",
            detail=f"Wallpaper aplicado: {unc_path}. Sera atualizado no proximo logon.",
        )
    except Exception as exc:
        logger.error("wallpaper_gpo_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Erro ao aplicar wallpaper: {str(exc)}")
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


@router.get(
    "/",
    response_model=list[PolicyStatus],
    dependencies=[Depends(require_permissions(["user:manage"]))],
)
async def list_policies() -> list[PolicyStatus]:
    policies = []
    try:
        session = _get_winrm_session()
        script = """
Import-Module GroupPolicy
$gpo = Get-GPO -Name 'BluAdmin - Wallpaper' -ErrorAction SilentlyContinue
if ($gpo) {
    $reg = Get-GPRegistryValue -Name 'BluAdmin - Wallpaper' -Key 'HKCU\\Control Panel\\Desktop' -ValueName 'Wallpaper' -ErrorAction SilentlyContinue
    if ($reg) { Write-Output "wallpaper:active:$($reg.Value)" }
    else { Write-Output "wallpaper:active:configurado" }
} else {
    Write-Output "wallpaper:inactive:nao configurado"
}
"""
        result = session.run_ps(script)
        output = result.std_out.decode("utf-8", errors="replace").strip()
        for line in output.split("\n"):
            parts = line.strip().split(":", 2)
            if len(parts) == 3:
                policies.append(PolicyStatus(policy=parts[0], status=parts[1], detail=parts[2]))
    except Exception as exc:
        policies.append(PolicyStatus(policy="wallpaper", status="unknown", detail=f"Nao foi possivel verificar: {str(exc)}"))
    return policies
