!define PRODUCT_NAME "{{ installer.package_name }}"
!define PRODUCT_VERSION "{{ installer.package_version }}"
!define INSTALLER_NAME "{{ installer.installer_name }}"
{% if installer.icon is not none %}
  !define PRODUCT_ICON "{{ installer.icon }}"
{% endif %}

; Marker file to tell the uninstaller that it's a user installation
!define USER_INSTALL_MARKER _user_install_marker

SetCompressor "{{ installer.compressor }}"

!if "${NSIS_PACKEDVERSION}" >= 0x03000000
  Unicode true
  ManifestDPIAware true
!endif

RequestExecutionLevel user
!include FileFunc.nsh
!include LogicLib.nsh

; Modern UI installer stuff
!include "MUI2.nsh"
!define MUI_ABORTWARNING
{% if installer.icon is not none %}
  !define MUI_ICON "{{ installer.icon }}"
  !define MUI_UNICON "{{ installer.icon }}"
{% endif %}

; UI pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

; Logging
!define /IfNDef LVM_GETITEMCOUNT 0x1004
!define /IfNDef LVM_GETITEMTEXTA 0x102D
!define /IfNDef LVM_GETITEMTEXTW 0x1073
!if "${NSIS_CHAR_SIZE}" > 1
!define /IfNDef LVM_GETITEMTEXT ${LVM_GETITEMTEXTW}
!else
!define /IfNDef LVM_GETITEMTEXT ${LVM_GETITEMTEXTA}
!endif

Name "${PRODUCT_NAME}"
OutFile "${INSTALLER_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

Var FORCE
Var ENV
Var PYTHON
Var PYTHONW

Section "!${PRODUCT_NAME}" sec_app
  SetRegView 64
  ;Check byteness
  SectionIn RO
  StrCpy $ENV "{{ installer.env_name }}"
  StrCpy $PYTHON "$INSTDIR\$ENV\python.exe"
  StrCpy $PYTHONW "$INSTDIR\$ENV\pythonw.exe"

  {% if installer.clean_instdir %}
    Push "$INSTDIR"
    Call isEmptyDir
    Pop $0
    StrCmp $0 0 0 +2
      ${If} $FORCE == "yes"
        RMDir /r "$INSTDIR\*.*"
        Goto noabort
      ${EndIf}
      MessageBox MB_YESNO `"$INSTDIR" is not empty, delete its content and continue installing?` IDYES true IDNO false
      true:
        RMDir /r "$INSTDIR\*.*"
        Goto noabort
      false:
        Abort
      noabort:
  {% endif %}

  ; Install directories
  SetOutPath "$INSTDIR\$ENV"
        File /r "{{ installer.env_name }}\*.*" ; I can't use $ENV here

  {% for dir in installer.include_dirs %}
    SetOutPath "$INSTDIR\{{ dir }}"
        File /r "{{ dir }}\*.*"
  {% endfor %}
  SetOutPath "$INSTDIR"

  ; Install files
  {% for fn in installer.include_files %}
    SetOutPath "$INSTDIR"
        File "{{ fn }}"
  {% endfor %}

  nsExec::ExecToLog '$PYTHON "$INSTDIR\$ENV\Scripts\conda-unpack-script.py"'
  ; Run Scripts
  {% for script in installer.postinstall_python_scripts %}
    nsExec::ExecToLog '"$PYTHON" {{ script }}'
  {% endfor %}
  Pop $0
  ${IfNot} $0 == 0
      MessageBox MB_ICONSTOP "There was an error installing ${PRODUCT_NAME}"
      StrCpy $0 "$INSTDIR\install_log.txt"
      Push $0
      Call DumpLog
      Abort
  ${EndIf}

  ; Setup shortcuts
  {% for shortcut in installer.shortcuts %}
    CreateShortCut "{{ shortcut.shortcut_name }}" "{{ shortcut.target_file }}" "{{ shortcut.parameters }}" \
      "{{ shortcut.icon_file }}" "{{ shortcut.icon_index_number }}"
  {% endfor %}

  WriteUninstaller $INSTDIR\uninstall.exe

  {% if installer.register_uninstaller %}
  ; Add ourselves to Add/remove programs
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "InstallLocation" "$INSTDIR"
    {% if installer.icon is not none %}
      WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                        "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
    {% endif %}
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "NoRepair" 1
  {% endif %}

  StrCpy $0 "$INSTDIR\install_log.txt"
  Push $0
  Call DumpLog

SectionEnd

Section "Uninstall"
  SetRegView 64
  StrCpy $ENV "{{ installer.env_name }}"
  StrCpy $PYTHON "$INSTDIR\$ENV\python.exe"
  StrCpy $PYTHONW "$INSTDIR\$ENV\pythonw.exe"

  ; Run Scripts
  {% for script in installer.preuninstall_python_scripts %}
    nsExec::ExecToLog '"$PYTHON" {{ script }}'
  {% endfor %}

  {% for shortcut in installer.shortcuts %}
    Delete "{{ shortcut.shortcut_name }}"
  {% endfor %}

  {% if installer.icon is not none %}
    Delete "$INSTDIR\${PRODUCT_ICON}"
  {% endif %}

  ; Uninstall directories
  RMDir /r "$INSTDIR\$ENV\*.*"

  {% for dir in installer.include_dirs %}
    RMDir /r "$INSTDIR\{{ dir }}\*.*"
  {% endfor %}

  {% for fn in installer.include_files %}
    Delete "$INSTDIR\{{ fn }}"
  {% endfor %}

  Delete "$INSTDIR\install_log.txt"

  {% if installer.register_uninstaller %}
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
  {% endif %}

  Delete "$INSTDIR\uninstall.exe"

  RMDir $INSTDIR
SectionEnd


; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:${PRODUCT_NAME}"

FunctionEnd

Function .onInit
  ; Change default to HOME folder
  InitPluginsDir
  ${If} $INSTDIR == ""
    StrCpy $INSTDIR "{{ installer.default_install_dir }}"
  ${EndIf}
  ; Check if the force flag was set
  ${GetOptions} $CMDLINE "/FORCE" $R9
  ${IfNot} ${Errors}
    StrCpy $FORCE "yes"
  ${Else}
    StrCpy $FORCE "no"
  ${EndIf}
  DetailPrint $FORCE
FunctionEnd

{% if installer.clean_instdir %}
  Function isEmptyDir
    ; Check if a directory is empty, from https://nsis.sourceforge.io/Check_if_dir_is_empty
    # Stack ->                    # Stack: <directory>
    Exch $0                       # Stack: $0
    Push $1                       # Stack: $1, $0
    FindFirst $0 $1 "$0\*.*"
    strcmp $1 "." 0 _notempty
      FindNext $0 $1
      strcmp $1 ".." 0 _notempty
        ClearErrors
        FindNext $0 $1
        IfErrors 0 _notempty
          FindClose $0
          Pop $1                  # Stack: $0
          StrCpy $0 1
          Exch $0                 # Stack: 1 (true)
          goto _end
       _notempty:
         FindClose $0
         ClearErrors
         Pop $1                   # Stack: $0
         StrCpy $0 0
         Exch $0                  # Stack: 0 (false)
    _end:
  FunctionEnd
{% endif %}

Function DumpLog
  ; Logging function from https://nsis.sourceforge.io/Dump_log_to_file
  Exch $5
  Push $0
  Push $1
  Push $2
  Push $3
  Push $4
  Push $6
  FindWindow $0 "#32770" "" $HWNDPARENT
  GetDlgItem $0 $0 1016
  StrCmp $0 0 exit
  FileOpen $5 $5 "w"
  StrCmp $5 "" exit
    SendMessage $0 ${LVM_GETITEMCOUNT} 0 0 $6
    System::Call '*(&t${NSIS_MAX_STRLEN})p.r3'
    StrCpy $2 0
    System::Call "*(i, i, i, i, i, p, i, i, i) i  (0, 0, 0, 0, 0, r3, ${NSIS_MAX_STRLEN}) .r1"
    loop: StrCmp $2 $6 done
      System::Call "User32::SendMessage(i, i, i, i) i ($0, ${LVM_GETITEMTEXT}, $2, r1)"
      System::Call "*$3(&t${NSIS_MAX_STRLEN} .r4)"
      !ifdef DumpLog_As_UTF16LE
      FileWriteUTF16LE ${DumpLog_As_UTF16LE} $5 "$4$\r$\n"
      !else
      FileWrite $5 "$4$\r$\n" ; Unicode will be translated to ANSI!
      !endif
      IntOp $2 $2 + 1
      Goto loop
    done:
      FileClose $5
      System::Free $1
      System::Free $3
  exit:
    Pop $6
    Pop $4
    Pop $3
    Pop $2
    Pop $1
    Pop $0
    Pop $5
FunctionEnd