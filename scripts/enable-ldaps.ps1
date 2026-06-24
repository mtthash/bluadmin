$dnsName = [System.Net.Dns]::GetHostByName($env:COMPUTERNAME).HostName
$domain = (Get-ADDomain).DNSRoot

Write-Host "Configurando LDAPS para: $dnsName ($domain)"

$cert = New-SelfSignedCertificate -DnsName $dnsName, $domain, "localhost", "192.168.1.250" -CertStoreLocation "Cert:\LocalMachine\My" -KeyAlgorithm RSA -KeyLength 2048 -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(10) -Provider "Microsoft RSA SChannel Cryptographic Provider" -KeySpec KeyExchange

Write-Host "Certificado criado: $($cert.Thumbprint)"

$rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
$rootStore.Open("ReadWrite")
$rootStore.Add($cert)
$rootStore.Close()

Write-Host "Certificado adicionado ao Trusted Root"

Write-Host "Reiniciando NTDS..."
Restart-Service NTDS -Force

Start-Sleep -Seconds 5

$test = Test-NetConnection -ComputerName localhost -Port 636
if ($test.TcpTestSucceeded) {
    Write-Host "LDAPS HABILITADO - Porta 636 respondendo"
} else {
    Write-Host "Porta 636 ainda nao responde. Aguarde e teste: Test-NetConnection -ComputerName localhost -Port 636"
}

$rule = Get-NetFirewallRule -DisplayName "LDAPS" -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName "LDAPS" -Direction Inbound -Protocol TCP -LocalPort 636 -Action Allow
    Write-Host "Regra de firewall criada para porta 636"
}

Write-Host "Pronto! Altere o .env para LDAP_PORT=636 e LDAP_USE_SSL=true"
