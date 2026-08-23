; Установщик ProxyPulse. Компиляция: ISCC.exe ProxyPulse.iss
;
; Ставим в профиль пользователя, а НЕ в Program Files, и это осознанно:
; программа пишет рядом с собой базу GeoLite2-Country.mmdb (качает при первом
; запуске) и папки с результатами. В Program Files без прав администратора
; запись запрещена, и обновление базы молча ломалось бы. Побочный плюс —
; установка не требует UAC, обычному человеку достаточно двойного клика.

#define AppName "ProxyPulse"
#define AppExe  "ProxyPulse.exe"

; Версию и пути можно переопределить снаружи: ISCC /DAppVersion=4.1 /DSrcDir=...
; Так собирает CI (версия берётся из тега) и локальный build.ps1 (папка вне
; OneDrive). Без переопределения работают значения по умолчанию.
#ifndef AppVersion
  #define AppVersion "4.0"
#endif
#ifndef SrcDir
  #define SrcDir "dist\ProxyPulse"
#endif
#ifndef OutDir
  #define OutDir "installer"
#endif

[Setup]
AppId={{8F3A1C42-5D7E-4B93-A1F6-2C9E7D4B8A15}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName} {#AppVersion}
OutputDir={#OutDir}
; Имя БЕЗ версии — сознательно. От него зависит постоянная ссылка
; .../releases/latest/download/ProxyPulse-setup.exe: появись в имени версия,
; ссылка ломалась бы у всех при каждом релизе. Версия видна в заголовке
; релиза, в теге и в свойствах самого .exe.
OutputBaseFilename=ProxyPulse-setup
SetupIconFile=assets\ProxyPulse.ico
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
DisableDirPage=auto

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#SrcDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Скачанная база и результаты прогонов создаются уже после установки,
; поэтому установщик о них не знает и сам бы их не удалил.
Type: files;      Name: "{app}\GeoLite2-Country.mmdb"
Type: filesandordirs; Name: "{app}\results_live"
Type: filesandordirs; Name: "{app}\results_elite"
