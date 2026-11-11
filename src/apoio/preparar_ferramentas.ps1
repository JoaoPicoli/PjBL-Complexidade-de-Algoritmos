$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $projectRoot
New-Item -ItemType Directory -Path '.tools/python' -Force | Out-Null
python -m pip install --disable-pip-version-check --no-cache-dir --target .tools/python 'sympy==1.14.0' 'mpmath==1.3.0' 'numpy==2.1.2' 'matplotlib==3.11.1' 'pypdf==7.0.0'
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências Python locais.' }
$downloads = @(
    @{
        Url = 'https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-pc-windows-msvc.zip'
        File = '.tools/tectonic.zip'
        Hash = 'f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f'
    },
    @{
        Url = 'https://github.com/jgm/pandoc/releases/download/3.13/pandoc-3.13-windows-x86_64.zip'
        File = '.tools/pandoc.zip'
        Hash = '23e1f2e978a3df80db8bf65c9c59534f41a23140480cfb4f783a882ab7dc6a4e'
    }
)
foreach ($download in $downloads) {
    if (-not (Test-Path -LiteralPath $download.File)) {
        Invoke-WebRequest -Uri $download.Url -OutFile $download.File
    }
    $actualHash = (Get-FileHash -LiteralPath $download.File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $download.Hash) { throw "Hash incorreto: $($download.File)" }
    Expand-Archive -LiteralPath $download.File -DestinationPath '.tools' -Force
}
Write-Output 'Ferramentas locais preparadas. Poppler e as fontes Windows são pré-requisitos externos.'
