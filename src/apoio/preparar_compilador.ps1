$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $projectRoot
New-Item -ItemType Directory -Path '.tools' -Force | Out-Null
$archivePath = Join-Path $projectRoot '.tools/w64devkit-x64-2.11.0.7z.exe'
if (-not (Test-Path -LiteralPath $archivePath)) {
    Invoke-WebRequest -Uri 'https://github.com/skeeto/w64devkit/releases/download/v2.11.0/w64devkit-x64-2.11.0.7z.exe' -OutFile $archivePath
}
$expectedHash = '54c2bb9962e8a30c8270e34c5efc3d5fee579f53087fa7d435b95fbba2af7b2b'
if ((Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
    throw 'SHA-256 do compilador difere do arquivo inspecionado.'
}
# Read the archive with libarchive/tar; do not execute the downloaded SFX stub.
$members = tar -tf $archivePath
if ($LASTEXITCODE -ne 0) { throw 'Falha ao listar o arquivo do compilador.' }
foreach ($member in $members) {
    if (-not $member.StartsWith('w64devkit/') -or $member -match '(^|[/\\])\.\.([/\\]|$)') {
        throw "Caminho inesperado no pacote: $member"
    }
}
tar -xf $archivePath -C (Join-Path $projectRoot '.tools')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao extrair o compilador.' }
& (Join-Path $projectRoot '.tools/w64devkit/bin/gcc.exe') --version
