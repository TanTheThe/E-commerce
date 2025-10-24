#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; ---------------------------
; SCRIPT SETTINGS
; ---------------------------
RecoilControl := true
WeaponSettings := Object()
WeaponSettings["AKM"] := { Vertical: 9, Horizontal: 2.0, Oscillation: 30, Boost: 1.7 }
WeaponSettings["Beryl"] := { Vertical: 10, Horizontal: 2.5, Oscillation: 25, Boost: 1.7 }
WeaponSettings["AUG"] := { Vertical: 8, Horizontal: 3.0, Oscillation: 40, Boost: 1.6 }
WeaponSettings["M416"] := { Vertical: 8, Horizontal: 2.0, Oscillation: 35, Boost: 1.5 }
WeaponSettings["Default"] := { Vertical: 7, Horizontal: 1.5, Oscillation: 30, Boost: 1.5 }

CurrentWeapon := "Default"
DoubleCheckDelay := 20 ; Reduced for instant response

; ---------------------------
; GAME INITIALIZATION
; ---------------------------
IfWinExist ahk_exe TslGame.exe
{
    WinActivate
    WinWaitActive
}
else
{
    MsgBox PUBG/BGMI is not running!`nPlease start the game before using the script.
    ExitApp
}

; ---------------------------
; HOTKEYS
; ---------------------------
F1:: CurrentWeapon := "AKM"
F2:: CurrentWeapon := "Beryl"
F3:: CurrentWeapon := "AUG"
F4:: CurrentWeapon := "M416"
F5:: CurrentWeapon := "Default"

; ---------------------------
; MAIN LOOP (OPTIMIZED)
; ---------------------------
~RButton::
    if (!RecoilControl)
        return
    
    ; Instant activation on simultaneous press
    if (GetKeyState("LButton", "P")) {
        Gosub RecoilHandler
    }
    else {
        KeyWait LButton, D
        if (ErrorLevel)
            return
        Gosub RecoilHandler
    }
return

RecoilHandler:
    profile := WeaponSettings[CurrentWeapon].Clone()
    startTime := A_TickCount
    lastOsc := A_TickCount
    direction := 1
    MouseGetPos startX, startY
    
    Loop {
        ; Double-check button states
        if (!GetKeyState("RButton", "P") || !GetKeyState("LButton", "P"))
            break
    
        ; Calculate parameters
        elapsed := A_TickCount - startTime
        verticalPower := profile.Vertical * (elapsed > 3000 ? profile.Boost : 1)
        
        ; Horizontal oscillation
        if (A_TickCount - lastOsc >= profile.Oscillation) {
            direction *= -1
            lastOsc := A_TickCount
        }
        horizontalPower := profile.Horizontal * direction
        
        ; Apply offset
        DllCall("mouse_event", "UInt", 0x01, "Int", horizontalPower, "Int", verticalPower, "UInt", 0, "UPtr", 0)
        
        ; Reset position when reaching the boundary
        MouseGetPos,, currentY
        if (currentY >= A_ScreenHeight - 50) {
            MouseMove startX, startY, 0
        }
        
        Sleep %DoubleCheckDelay%
    }
return