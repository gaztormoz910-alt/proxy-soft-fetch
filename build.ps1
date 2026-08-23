# Локальная пересборка ProxyPulse: .exe + установщик. Запуск: .\build.ps1
#
# Собираем ВНЕ папки проекта: проект лежит в OneDrive, и тот залочивает файлы
# прямо во время записи — сборка падает с "файл занят другим процессом".
# Заодно 60 МБ артефактов не уезжают в облако при каждой пересборке.
#
# То же самое, но на серверах GitHub, делает .github/workflows/release.yml —
# он запускается по тегу и сам публикует релиз.

param([string]$Version = "4.0")

$ErrorActionPreference = "Stop"
$out  = "C:\Users\Bog_1\ProxyPulse-build"
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"

Write-Host "[1/3] version_info.txt ($Version)..." -ForegroundColor Cyan
python tools/make_version_info.py $Version
if ($LASTEXITCODE -ne 0) { throw "make_version_info failed" }

Write-Host "[2/3] PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean --log-level WARN `
    --distpath "$out\dist" --workpath "$out\build" ProxyPulse.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "[3/3] Inno Setup..." -ForegroundColor Cyan
if (-not (Test-Path $iscc)) { throw "Inno Setup not found: $iscc" }
& $iscc "/DAppVersion=$Version" "/DSrcDir=$out\dist\ProxyPulse" "/DOutDir=$out" ProxyPulse.iss |
    Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }

$setup = "$out\ProxyPulse-setup.exe"
Write-Host "`nDone: $setup ($([math]::Round((Get-Item $setup).Length/1MB,1)) MB)" -ForegroundColor Green
