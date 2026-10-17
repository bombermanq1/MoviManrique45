<#
.SYNOPSIS
    Valida, exporta e inicia la demostración web local de MoviManrique45.

.DESCRIPTION
    No descarga datos, no modifica fuentes RAW ni necesita PostgreSQL. Antes de
    servir el sitio, ejecuta el exportador que comprueba los 8.332 eventos y los
    604 IDs congelados del indicador principal.
#>
[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Puerto = 8501,
    [switch]$SoloExportar
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$raiz = Split-Path -Parent $PSScriptRoot
$python = Join-Path $raiz ".venv\Scripts\python.exe"
$web = Join-Path $raiz "web"

if (-not (Test-Path -LiteralPath $python)) {
    throw "No se encontró el entorno virtual en $python. Cree .venv e instale requirements.txt."
}

Push-Location $raiz
try {
    Write-Host "Verificando los insumos locales del MVP..." -ForegroundColor Cyan
    & $python .\scripts\verificar_insumos_demo.py
    if ($LASTEXITCODE -ne 0) {
        throw "La verificación de insumos falló. No se generó ni sirvió una vista parcial."
    }

    Write-Host "Validando y exportando la vista web derivada..." -ForegroundColor Cyan
    & $python -m src.dashboard.exportar_web
    if ($LASTEXITCODE -ne 0) {
        throw "La exportación del dashboard terminó con código $LASTEXITCODE."
    }

    if ($SoloExportar) {
        Write-Host "Exportación validada. No se inició el servidor por -SoloExportar." -ForegroundColor Green
        return
    }

    Write-Host "Demostración disponible en http://127.0.0.1:$Puerto/" -ForegroundColor Green
    Write-Host "Presione Ctrl+C para detener el servidor." -ForegroundColor Yellow
    # La demostración contiene ubicaciones históricas: se limita explícitamente
    # a loopback y no se publica en interfaces de red locales.
    & $python -m http.server $Puerto --bind 127.0.0.1 --directory $web
    if ($LASTEXITCODE -ne 0) {
        throw "El servidor local terminó con código $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
