---
name: fix-windows-keyboard
description: >-
  Diagnose and reversibly fix a Windows keyboard where Shift, Caps Lock, Alt+Shift or the
  layout switch stopped working: stuck modifiers, Sticky/Filter Keys, ctfmon, layout toggle
  registry value, input hooks (AutoHotkey, remote-desktop tools) and OEM keyboard filter
  drivers such as HP Easy Clean. Use when keys or layout switching stop responding.
  Triggers: "shift does not work", "layout does not switch", "caps lock stuck".
license: MIT
---

# fix-windows-keyboard: Shift / Caps Lock / Alt+Shift stopped working

The tool is `kbd_fix.py` next to this file. Run it as
`python -X utf8 kbd_fix.py <command>`. Commands: `status`, `fix`, `watch`.

## Decision flow

1. `status`: prints a check or cross per class. Exit code 2 means at least one cross.
2. Class H (OEM filter driver process alive) found: run `fix` to stop it, then ask the owner before uninstalling.
3. Any other cross: run `fix`.
4. All checks pass: run `watch --seconds 120` while the user presses keys in Notepad.
5. Every key arrived: the hardware is fine, look for a window that intercepts input (full-screen remote desktop, per-app layout).
6. Only some keys arrived: hardware or driver; test an external USB keyboard and `osk.exe`.
7. Nothing arrived: focus was elsewhere, repeat with Notepad in front.

## Step 1. Diagnosis classes

- A: a stuck modifier key.
- B: Sticky Keys or Filter Keys enabled.
- C: `ctfmon` or the voice-typing window (TextInputHost) holds the foreground.
- D: layout switch hotkey, `HKCU\Keyboard Layout\Toggle`; normal values are 1 / 1 / 3 (Alt+Shift).
- E: `Scancode Map` in HKLM.
- F: input interceptors (AutoHotkey, remote-desktop tools in control mode, PowerToys, vendor utilities).
- G: keyboard devices in PnP.
- H: a vendor background app with a keyboard filter driver. Example: HP Easy Clean (`HPKbfDriver.sys`) sits as an upper filter on the keyboard class and, while the app runs, drops modifiers: letters arrive, Shift/Alt/Caps do not, Alt+Shift does not switch layout. Stopping the process restores them. It is reversible: start the app again from the Start menu. Removing it for good (`Remove-AppxPackage`) is the owner's decision; editing `UpperFilters` needs admin, a reboot and risks losing the keyboard, so do not.

## Step 2. Fix (reversible, no UAC)

`fix` releases all 8 modifiers via SendInput, disables Sticky and Filter Keys (hotkeys untouched), restores the layout Toggle value with a backup under `~/.claude/kbd_fix/`, and tries to restart ctfmon. Flags: `--caps-off` turns Caps Lock off, `--no-ctfmon` skips ctfmon.

ctfmon runs elevated: without admin it cannot be killed or started (WinError 740). The script then leaves it alone and prints the command for an elevated window. Editing `Scancode Map` needs UAC and a reboot; leave it to the owner.

## Step 3. Hardware or software: record keypresses

`watch --seconds 120` logs modifiers and counts ordinary keys as one number (no text, no order), then gives a verdict. Letters at 20 or more with zero modifiers means the modifiers die below Windows. Ask the user to press in Notepad, 2 or 3 times each: left Shift, right Shift, Caps Lock, left Alt, Alt+Shift.

Two layers can fail at once: a deaf ctfmon (the process lives but Alt+Shift and Win+Space do not switch layout even with synthetic keys; check `GetKeyboardLayout` before and after a synthetic chord; fix by killing ctfmon and restarting the `MsCtfMonitor` task from an elevated prompt) and an OEM filter driver that survives uninstalling the app (a restart of the device may fail; only a reboot clears it). Test synthetic input in Notepad first (separates Windows from hardware), then physical presses.

## Step 4. Report

One line: failure class, what was done, evidence (`status` output after), what is left for the owner.

## macOS

No automation. `kbd_fix.py` prints a cheat sheet: Sticky and Slow Keys in `com.apple.universalaccess`, key remaps via `hidutil property --get UserKeyMapping`, Karabiner as the first suspect.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
