#Requires AutoHotkey v2.0
#SingleInstance Force

; In v2, command-line arguments are stored in the global A_Args array
; Check if at least two arguments (X and Y coordinates) were passed
if (A_Args.Length >= 2) {
    x := A_Args[1]
    y := A_Args[2]

    ; Move mouse instantly (Speed = 0) and click
    MouseMove(x, y, 0)
    Click()

    SoundBeep(750, 200)
}

; Terminate script execution after handling input
ExitApp()