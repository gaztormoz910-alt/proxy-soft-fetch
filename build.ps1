# Локальная пересборка ProxyPulse: .exe + установщик. Запуск: .\build.ps1
#
# Собираем ВНЕ папки проекта: он лежит в облачной синхронизируемой папке, а она
# залочивает файлы прямо во время записи — сборка падает с "файл занят".
# Заодно 60 МБ артефактов не уезжают в облако при каждой пересборке.
#
# То же самое, но на серверах GitHub, делает .github/workflows/release.yml —
# он запускается по тегу и сам публикует релиз.

param([string]$Version = "")

$ErrorActionPreference = "Stop"
# Каталог сборки в профиле пользователя, но вычисляется, а не вписан: иначе
# логин ОС уехал бы в отслеживаемый файл (см. tools/verify_scrub.py).
$out  = Join-Path $HOME "ProxyPulse-build"
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
}

if (-not $Version) { $Version = (Get-Content VERSION -Raw).Trim() }

Write-Host "[1/5] version $Version..." -ForegroundColor Cyan
py -3.13 tools/set_version.py $Version
if ($LASTEXITCODE -ne 0) { throw "set_version failed" }

Write-Host "[2/5] PyInstaller..." -ForegroundColor Cyan
py -3.13 -m PyInstaller --noconfirm --clean --log-level WARN `
    --distpath "$out\dist" --workpath "$out\build" ProxyPulse.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "[3/5] Обезличить PE-метаданные .exe..." -ForegroundColor Cyan
py -3.13 tools/scrub_pe.py --clean "$out\dist\ProxyPulse\ProxyPulse.exe"
py -3.13 tools/scrub_pe.py --verify "$out\dist\ProxyPulse\ProxyPulse.exe"
if ($LASTEXITCODE -ne 0) { throw "scrub_pe .exe failed" }

Write-Host "[4/5] Inno Setup..." -ForegroundColor Cyan
if (-not (Test-Path $iscc)) { throw "Inno Setup not found: $iscc" }
& $iscc "/DAppVersion=$Version" "/DSrcDir=$out\dist\ProxyPulse" "/DOutDir=$out" ProxyPulse.iss |
    Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }

$setup = "$out\ProxyPulse-setup.exe"
Write-Host "[5/5] Обезличить PE-метаданные установщика..." -ForegroundColor Cyan
py -3.13 tools/scrub_pe.py --clean $setup
py -3.13 tools/scrub_pe.py --verify $setup
if ($LASTEXITCODE -ne 0) { throw "scrub_pe setup failed" }

Write-Host "`nDone: $setup ($([math]::Round((Get-Item $setup).Length/1MB,1)) MB)" -ForegroundColor Green
