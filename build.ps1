# Пересборка ProxyPulse: .exe + установщик. Запуск: .\build.ps1
#
# Собираем ВНЕ папки проекта: проект лежит в OneDrive, и тот залочивает
# файлы прямо во время записи — сборка падает с "файл занят другим процессом".
# Заодно 60 МБ артефактов не уезжают в облако при каждой пересборке.

$ErrorActionPreference = "Stop"
$out  = "C:\Users\Bog_1\ProxyPulse-build"
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"

Write-Host "[1/2] PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean --log-level WARN `
    --distpath "$out\dist" --workpath "$out\build" ProxyPulse.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "[2/2] Inno Setup..." -ForegroundColor Cyan
if (-not (Test-Path $iscc)) { throw "Inno Setup not found: $iscc" }
& $iscc "ProxyPulse.iss" | Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }

$setup = "$out\ProxyPulse-4.0-setup.exe"
Write-Host "`nDone: $setup ($([math]::Round((Get-Item $setup).Length/1MB,1)) MB)" -ForegroundColor Green
