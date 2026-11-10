param(
    [string]$Config = 'configs/generic.json'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    $pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw 'Primero crear el entorno: py -3.12 -m venv .venv; luego instalar: .\.venv\Scripts\python.exe -m pip install -e .'
    }
    & $pythonPath -m rx_torax.prepare --config $Config
    if ($LASTEXITCODE -ne 0) { throw "La preparación falló (código $LASTEXITCODE). Revisar el mensaje anterior." }
} finally {
    Pop-Location
}
