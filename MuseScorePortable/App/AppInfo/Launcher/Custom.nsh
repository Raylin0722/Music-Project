${SegmentFile}

${Segment.OnInit}
	${registry::Read} "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentBuild" $0 $1

	${If} $0 < 10000 ;earlier than Windows 10
		StrCpy $AppName "MuseScore"
		${If} ${IsWin2000}
			StrCpy $1 2000
		${ElseIf} ${IsWinXP}
			StrCpy $1 XP
		${ElseIf} ${IsWin2003}
			StrCpy $1 2003
		${ElseIf} ${IsWinVista}
			StrCpy $1 Vista
		${ElseIf} ${IsWin2008}
			StrCpy $1 2008
		${ElseIf} ${IsWin7}
			StrCpy $1 7
		${ElseIf} ${IsWin2008R2}
			StrCpy $1 "2008 R2"
		${ElseIf} ${IsWin8}
			StrCpy $1 8
		${ElseIf} ${IsWin2012}
			StrCpy $1 2012
		${Else}
			StrCpy $1 "Pre-Win10"
		${EndIf}	
		StrCpy $0 "10"
		MessageBox MB_OK "$(LauncherIncompatibleMinOS)"
		Abort
	${EndIf}
!macroend
