#Requires AutoHotkey v2.0
#SingleInstance Force

DllCall "AllocConsole"
WinHide "ahk_id " DllCall("GetConsoleWindow", "Ptr")

CoordMode("ToolTip", "Screen")
CoordMode("Mouse", "Screen")

stdin := FileOpen("*", "r", "UTF-8")

last_cast_time := 0

Loop {
    if stdin.AtEOF {
        Sleep 1
        continue
    }
    
    line := stdin.ReadLine()
    line := Trim(line)
    
    if (line != "") {
        params := StrSplit(line, ",")
        if (params.Length >= 2) {
            action := params[1]
            payload := params[2]

            if (action == "PAUSED") {
                Click "Up"
                
            } else if (action == "CAST") {
                current_time := A_TickCount
                if (current_time - last_cast_time >= 500) {
                    MouseMove 1000, 200, 5
                    Click "Down"
                    Sleep 30
                    Click "Up"
                    last_cast_time := current_time
                }
                
            } else if (action == "RIGHT_PULSE") {
                ; High-frequency right pulse
                Click "Down"
                
            } else if (action == "LEFT_WAIT") {
                ; Rapid release for immediate left drift
                Click "Up"
            }

            hud_text := "ACTION: " . action . "`n" . payload
            ToolTip(hud_text, 800, 800)
        }
    }
}

q::ExitApp