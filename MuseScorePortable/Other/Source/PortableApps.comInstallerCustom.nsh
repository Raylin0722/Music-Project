!insertmacro GetParent

Var bolCustomV3Upgrade

!macro CustomCodePreInstall
	${If} ${FileExists} "$INSTDIR\App\AppInfo\appinfo.ini"
		ReadINIStr $0 "$INSTDIR\App\AppInfo\appinfo.ini" "Version" "PackageVersion"
		${VersionCompare} $0 "4.0.1.0" $R0
		${If} $R0 == 2
		${AndIf} ${FileExists} "$INSTDIR\Data\MuseScore3\*.*"
			StrCpy $bolCustomV3Upgrade true
			${GetParent} $INSTDIR $1
			${If} ${FileExists} "$1\MuseScorePortableLegacy3\*.*"
				;Upgrade 3 files to 4
				Rename "$INSTDIR\Data\MuseScore3" "$INSTDIR\Data\MuseScoreDocs"
				CreateDirectory "$INSTDIR\Data\CloudScores"
				CreateDirectory "$INSTDIR\Data\MuseScore"
				CreateDirectory "$INSTDIR\Data\MuseScoreLocal"
				CreateDirectory "$INSTDIR\Data\VST3"
			${Else}
				CreateDirectory "$1\MuseScorePortableLegacy3"
				CopyFiles /SILENT "$INSTDIR\*.*" "$1\MuseScorePortableLegacy3"
				WriteINIStr "$1\MuseScorePortableLegacy3\App\AppInfo\appinfo.ini" "Details" "Name" "MuseScore Portable (Legacy 3)"
				WriteINIStr "$1\MuseScorePortableLegacy3\App\AppInfo\appinfo.ini" "Details" "AppID" "MuseScorePortableLegacy3"
				
				;Upgrade 3 files to 4
				Rename "$INSTDIR\Data\MuseScore3" "$INSTDIR\Data\MuseScoreDocs"
				CreateDirectory "$INSTDIR\Data\CloudScores"
				CreateDirectory "$INSTDIR\Data\MuseScore"
				CreateDirectory "$INSTDIR\Data\MuseScoreLocal"
				CreateDirectory "$INSTDIR\Data\VST3"
				CopyFiles /SILENT "$INSTDIR\App\DefaultData\MuseScore\*.*" "$INSTDIR\Data\MuseScore"
				CopyFiles /SILENT "$INSTDIR\App\DefaultData\settings\*.*" "$INSTDIR\Data\settings"
			${EndIf}
		${Else}
			${If} $R0 == 0
				${GetParent} $INSTDIR $1
				${If} ${FileExists} "$1\MuseScorePortableLegacy3\*.*"
					${IfNot} ${FileExists} "$INSTDIR\Data\MuseScoreDocs\*.*"
						CreateDirectory "$INSTDIR\Data"
						CopyFiles /SILENT "$INSTDIR\App\DefaultData\*.*" "$INSTDIR\Data"
					${EndIf}
					;Copy 3 files into 4 and reset settings for proper paths
					Rename "$INSTDIR\Data\MuseScore\MuseScore4.ini" "$INSTDIR\Data\MuseScore\MuseScore4-Broken.ini"
					StrCpy $bolCustomV3Upgrade true
					CopyFiles /SILENT "$1\MuseScorePortableLegacy3\Data\MuseScore3\*.*" "$INSTDIR\Data\MuseScoreDocs"
				${EndIf}
			${EndIf}
		${EndIf}
	${EndIf}
!macroend

!macro CustomCodePostInstall
	${If} $bolCustomV3Upgrade == true
		CopyFiles /SILENT "$INSTDIR\App\DefaultData\MuseScore\*.*" "$INSTDIR\Data\MuseScore"
	${EndIf}
!macroend
