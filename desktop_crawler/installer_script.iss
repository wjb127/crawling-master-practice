; Inno Setup 인스톨러 스크립트
; 크롤링 마스터 v1.0.0

#define MyAppName "크롤링 마스터"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "크몽 프리랜서"
#define MyAppURL "https://github.com/wjb127/crawling-master-practice"
#define MyAppExeName "CrawlingMaster.exe"

[Setup]
; 앱 정보
AppId={{E8F4B3C2-9A7D-4F2E-B5C8-1D3A6E9F8B2C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 기본 설치 경로
DefaultDirName={autopf}\CrawlingMaster
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; 출력 설정
OutputDir=installer
OutputBaseFilename=CrawlingMaster_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes

; Windows 버전 요구사항
MinVersion=6.1
ArchitecturesInstallIn64BitMode=x64

; 설치 UI 설정
WizardStyle=modern
WizardImageFile=wizard_image.bmp
WizardSmallImageFile=wizard_small.bmp

; 언어 설정
ShowLanguageDialog=no
LanguageDetectionMethod=locale

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 메인 실행 파일
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 추가 파일들
Source: "README_USER.md"; DestDir: "{app}"; DestName: "사용설명서.txt"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; 폴더 구조 생성을 위한 더미 파일
Source: "dummy.txt"; DestDir: "{app}\results"; Flags: ignoreversion
Source: "dummy.txt"; DestDir: "{app}\logs"; Flags: ignoreversion

[Dirs]
; 사용자 데이터 폴더 생성
Name: "{app}\results"
Name: "{app}\logs"
Name: "{app}\temp"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\사용 설명서"; Filename: "{app}\사용설명서.txt"
Name: "{group}\결과 폴더 열기"; Filename: "{app}\results"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 설치 완료 후 실행
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\사용설명서.txt"; Description: "사용 설명서 보기"; Flags: postinstall shellexec skipifsilent unchecked

[UninstallDelete]
; 언인스톨 시 생성된 데이터 삭제 (선택적)
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"
; results 폴더는 사용자 데이터이므로 보존

[Code]
// 설치 전 확인
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // .NET Framework 확인 (필요한 경우)
  // Python 런타임이 포함되어 있으므로 별도 체크 불필요
  
  // 이전 버전 확인
  if RegKeyExists(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{E8F4B3C2-9A7D-4F2E-B5C8-1D3A6E9F8B2C}_is1') then
  begin
    if MsgBox('이전 버전이 설치되어 있습니다. 제거하고 계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // 이전 버전 제거
      Exec(ExpandConstant('{uninstallexe}'), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      Result := False;
    end;
  end;
end;

// 설치 완료 메시지
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 바탕화면 바로가기에 관리자 권한 설정 (필요한 경우)
    // 크롤링 앱은 일반적으로 관리자 권한 불필요
  end;
end;

// 언인스톨 확인
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox('크롤링 마스터를 제거하시겠습니까?' + #13#10 + 
                   '(저장된 결과 파일은 보존됩니다)', 
                   mbConfirmation, MB_YESNO) = IDYES;
end;

[Messages]
; 한국어 커스텀 메시지
korean.BeveledLabel=크롤링 마스터 v1.0.0
korean.WelcomeLabel1=[name] 설치를 시작합니다
korean.WelcomeLabel2=이 프로그램은 웹사이트를 크롤링하여 CSV/Excel 파일로 저장하는 도구입니다.%n%n계속하려면 다음을 클릭하세요.
korean.FinishedLabel=설치가 완료되었습니다.%n%n바탕화면에서 크롤링 마스터를 실행할 수 있습니다.

[CustomMessages]
korean.LaunchProgram=%1 실행하기
korean.CreateDesktopIcon=바탕화면에 바로가기 만들기
korean.CreateQuickLaunchIcon=빠른 실행에 아이콘 만들기