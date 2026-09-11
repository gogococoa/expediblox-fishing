#Requires AutoHotkey v2.0
#SingleInstance Force

; Unbuffer stdout/stdin streams
DllCall("AllocConsole")
WinHide("ahk_id " DllCall("GetConsoleWindow", "Ptr"))

CoordMode("Mouse", "Screen")
SendMode("Input")
SetDefaultMouseSpeed(0)

stdin := FileOpen("*", "r", "UTF-8")

Loop {
    if stdin.AtEOF {
        Sleep(10)
        continue
    }
    
    line := stdin.ReadLine()
    line := Trim(line)
    
    if (line != "") {
        coords := StrSplit(line, ",")
        if (coords.Length >= 2) {
            x := Integer(coords[1])
            y := Integer(coords[2])
            
            ToolTip("AHK GOT COMMAND: X=" x " Y=" y, x + 20, y + 20)
            SetTimer(() => ToolTip(), -1500)
            
            DllCall("SetCursorPos", "Int", x, "Int", y)
            Click("left")
            SoundBeep(900, 100)
        }
    }
}