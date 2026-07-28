; ===== فایل نصب‌ساز نهایی برای اپلیکیشن TradingAppBS =====

[Setup]
AppName=Trading App B&S
AppVersion=1.0
DefaultDirName={autopf}\TradingAppBS
DefaultGroupName=Trading App B&S
OutputDir=Output
OutputBaseFilename=TradingAppSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
WizardStyle=modern
SetupIconFile=arad_icon.ico
DisableDirPage=no

[Files]
; فایل اجرایی اصلی
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion

; فایل آیکون برای اپ و میانبر
Source: "arad_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; پوشه استاتیک‌ها
Source: "static\*"; DestDir: "{app}\static"; Flags: recursesubdirs createallsubdirs

; پوشه قالب‌های HTML
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs createallsubdirs

; دیتاهای اولیه منتقل به مسیر APPDATA/TradingAppBS
Source: "TradingAppData\*"; DestDir: "{userappdata}\TradingAppBS"; Flags: recursesubdirs createallsubdirs

; پوشه یادداشت‌ها (notes)
Source: "TradingAppData\notes\*"; DestDir: "{userappdata}\TradingAppBS\notes"; Flags: recursesubdirs createallsubdirs

; پوشه تصاویر آموزش
Source: "static\learn_images\*"; DestDir: "{app}\static\learn_images"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Trading App B&S"; Filename: "{app}\app.exe"; IconFilename: "{app}\arad_icon.ico"
Name: "{commondesktop}\Trading App B&S"; Filename: "{app}\app.exe"; IconFilename: "{app}\arad_icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "ایجاد میانبر در دسکتاپ"; GroupDescription: "آیکون‌های اضافی:"

[Run]
Filename: "{app}\app.exe"; Description: "اجرای اپ بعد از نصب"; Flags: nowait postinstall skipifsilent
