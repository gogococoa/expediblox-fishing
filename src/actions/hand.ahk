#Requires AutoHotkey v2.0
#SingleInstance Force

DllCall("AllocConsole")
WinHide("ahk_id " DllCall("GetConsoleWindow", "Ptr"))

; Force ToolTip coordinates to follow absolute screen pixels
CoordMode("ToolTip", "Screen")
CoordMode("Mouse", "Screen")

stdin := FileOpen("*", "r", "UTF-8")

Loop {
    if stdin.AtEOF {
        Sleep(10)
        continue
    }
    
    line := stdin.ReadLine()
    line := Trim(line)
    
    if (line != "") {
        params := StrSplit(line, ",")
        if (params.Length >= 2) {
            state := params[1]     ; "INSIDE" or "OUTSIDE"
            metrics := params[2]   ; "FX:120|BS:100|BE:300"
            
            ; Live Diagnostic HUD Overlay at (100, 100)
            if (state == "INSIDE") {
                ToolTip("=== FISH CAPTURED [ INSIDE ] ===`nMetrics: " metrics, 100, 100)
            } else {
                ToolTip("--- FISH ESCAPED [ OUTSIDE ] ---`nMetrics: " metrics, 100, 100)
            }
        }
    }
}