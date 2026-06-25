"""File share folder operations via WinRM."""

from __future__ import annotations

import winrm
import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)


def _get_session() -> winrm.Session:
    settings = get_settings()
    return winrm.Session(
        f"http://{settings.file_share_server}:5985/wsman",
        auth=(settings.ldap_bind_dn.split(",")[0].replace("CN=", ""), settings.ldap_bind_password),
        transport="ntlm",
    )


def create_department_folder(department_name: str, ad_group_name: str | None = None) -> bool:
    settings = get_settings()
    group = ad_group_name or department_name
    share_local_path = "X:\\"

    script = f"""
$deptPath = Join-Path "{share_local_path}" "{department_name}"
if (-not (Test-Path $deptPath)) {{
    New-Item -ItemType Directory -Path $deptPath -Force | Out-Null
}}

$acl = Get-Acl $deptPath
$acl.SetAccessRuleProtection($true, $false)

$adminRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "BLUILU\\Domain Admins", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.AddAccessRule($adminRule)

$groupRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "BLUILU\\{group}", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.AddAccessRule($groupRule)

Set-Acl $deptPath $acl
Write-Output "OK"
"""

    try:
        session = _get_session()
        result = session.run_ps(script)
        if result.status_code == 0:
            logger.info("department_folder_created", department=department_name, group=group)
            return True
        else:
            logger.warning(
                "department_folder_creation_failed",
                department=department_name,
                error=result.std_err.decode("utf-8", errors="replace"),
            )
            return False
    except Exception as exc:
        logger.warning("department_folder_creation_error", department=department_name, error=str(exc))
        return False


def check_folder_exists(folder_name: str) -> bool:
    share_local_path = "X:\\"
    script = f'Test-Path (Join-Path "{share_local_path}" "{folder_name}")'

    try:
        session = _get_session()
        result = session.run_ps(script)
        output = result.std_out.decode("utf-8", errors="replace").strip()
        return output == "True"
    except Exception as exc:
        logger.warning("folder_check_error", folder=folder_name, error=str(exc))
        return False
