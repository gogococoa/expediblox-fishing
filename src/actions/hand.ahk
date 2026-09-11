#Requires AutoHotkey v2.0
#SingleInstance Force

DllCall("AllocConsole")
WinHide("ahk_id " DllCall("GetConsoleWindow", "Ptr"))

; Force ToolTip coordinates to follow absolute screen pixels
CoordMode("ToolTip", "Screen")
CoordMode("Mouse", "Screen")

stdin := FileOpen("*", "r", "UTF-8")

is_holding := false

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
            action := params[1]    ; "CAST", "HOLD", "RELEASE", "PAUSED"
            payload := params[2]   ; "[BOT: ACTIVE] [FISHING] FishX:..."
            
            ; 1. Display Game State (Line 1)
            state_text := "STATE: UNKNOWN"
            if InStr(payload, "[IDLE]") {
                state_text := "STATE: [ IDLE ] - Ready to Cast"
            } else if InStr(payload, "[FISHING]") {
                state_text := "STATE: [ FISHING ] - Minigame Active"
            }

            ; 2. Display Catch Containment Status (Line 2)
            fish_status := (is_inside_str == "INSIDE") ? ">>> IN TARGET <<<" : "--- OUT OF TARGET ---"

            ; Combine into a clean structured HUD overlay at top-left screen (100, 100)
            hud_text := state_text . "`n" . fish_status . "`n" . payload
            ToolTip(hud_text, 100, 100)
        }
    }
}