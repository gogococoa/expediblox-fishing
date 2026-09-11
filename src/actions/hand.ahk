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
        Sleep 10
        continue
    }
    
    line := stdin.ReadLine()
    line := Trim(line)
    
    if (line != "") {
        params := StrSplit(line, ",")
        if (params.Length >= 2) {
            action := params[1]    ; "CAST", "RIGHT_PULSE", "LEFT_WAIT", "PAUSED"
            payload := params[2]   ; HUD payload

            if (action == "PAUSED") {
                MouseMove 800, 300, 5
                Sleep 4000
            }
            else {
                ; --- Control Logic Execution ---
                if (action == "CAST") {
                    current_time := A_TickCount
                    ; Spam cast click every 0.5 seconds (500ms)
                    if (current_time - last_cast_time >= 500) {
                        MouseMove 1000, 200, 5
                        hud_text := "ACTION: " . action . "`n" . payload
                        Click "Down"
                        Sleep 50
                        Click "Up"
                        last_cast_time := current_time
                    }
                    
                } else if (action == "RIGHT_PULSE") {
                    ; Rules 1 & 2: Click and hold for 0.2 seconds (200ms)
                    Click "Down"
                    Sleep 5
                    
                } else if (action == "LEFT_WAIT") {
                    ; Rules 3 & 4: Do nothing and wait 0.1 seconds (100ms)
                    Click "Up"
                    Sleep 5
                    
                }
            }

            ; --- Live Diagnostic Overlay ---
            hud_text := "ACTION: " . action . "`n" . payload
            ToolTip(hud_text, 800, 800)
        }
    }
}

q::ExitApp