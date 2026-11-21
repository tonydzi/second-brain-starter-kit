"""kbd_fix.py: не работают Shift / Caps Lock / Alt+Shift / Ctrl / Alt на ноуте.

Паспорт
  вход:   status | watch [--seconds N] | fix [--no-ctfmon] [--caps-off]
  выход:  текст в stdout + строка JSON в ~/.claude/kbd_fix/usage.jsonl
          (ts, node, actor, event, outcome); exit 0 = ок, 2 = найдена поломка
  кто зовёт: скилл /fix-windows-keyboard (the user голосом: «клавиша не работает», «шифт не работает»),
          любая сессия Claude/Codex на узле флота
  что ломается: без user32 (не Windows) печатает ветку macOS; GetAsyncKeyState
          видит только то, что дошло до Windows: тишина в watch = железо/драйвер
  рельса: локально, LLM не нужна (детерминированный ремонт)

Классы поломок, которые лечит fix (все обратимые, без UAC):
  A. залипший модификатор (Shift/Ctrl/Alt/Win держится «нажатым» после AnyDesk,
     computer-use hold_key, макро-кнопки мыши Razer) -> SendInput key-up на все 8
  B. включены Залипание / Фильтрация клавиш (5 раз Shift, долгий правый Shift)
     -> SystemParametersInfo выключает флаг ON, горячую клавишу не трогает
  C. завис ctfmon / TextInputHost (голосовой ввод Win+H держит фокус)
     -> перезапуск ctfmon, TextInputHost Windows поднимет сам
  D. сбито сочетание переключения раскладки (Alt+Shift) -> HKCU Toggle = 1/1/3
  H. запущен HP Easy Clean (StoreApp): его фильтр-драйвер HPKbfDriver.sys
     («HP Easy Clean Keyboard Filter Driver», верхний фильтр класса клавиатуры)
     режет Shift/Alt/Caps, буквы проходят; Alt+Shift не переключает раскладку
     -> Stop-Process HP.EasyClean.StoreApp (вернуть: запустить из Пуска).
     Улика 23.10.2026 laptop-A: после остановки Alt+Shift ожил (слова the user);
     автозапуска у него нет, поднимает DCOM по протоколу hpeasyclean-app2app
Только диагноз (правка требует UAC/перезагрузки или решения the user):
  E. Scancode Map в HKLM (переназначение клавиш) · F. процессы-перехватчики
     (AutoHotkey, AnyDesk --control, PowerToys, Razer Synapse) · G. устройство
     клавиатуры не OK в PnP
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

IS_WIN = sys.platform == "win32"
STATE_DIR = Path.home() / ".claude" / "kbd_fix"

MODS = {  # имя -> virtual-key
    "LShift": 0xA0, "RShift": 0xA1, "LCtrl": 0xA2, "RCtrl": 0xA3,
    "LAlt": 0xA4, "RAlt": 0xA5, "LWin": 0x5B, "RWin": 0x5C,
}
VK_CAPITAL = 0x14
EASYCLEAN_EXE = "HP.EasyClean.StoreApp.exe"  # имя на laptop-A; детект по подстроке easyclean


def stop_easyclean() -> str | None:
    """Класс H: гасит HP Easy Clean. Обратимо: приложение остаётся, запуск из Пуска.
    Успех = процесс реально пропал (перепроверка Get-Process), а не слово «stopped»."""
    out = _ps("$p = Get-Process | Where-Object { $_.ProcessName -match 'easyclean' }; "
              "if (-not $p) { 'none' } else { $p | ForEach-Object { try { Stop-Process -Id $_.Id -Force -ErrorAction Stop; "
              "'killed ' + $_.Id } catch { 'denied ' + $_.Id + ' ' + $_.Exception.Message } }; Start-Sleep -Milliseconds 500; "
              "$left = Get-Process | Where-Object { $_.ProcessName -match 'easyclean' }; "
              "if ($left) { 'STILL ' + (($left | ForEach-Object { $_.Id }) -join ',') } else { 'GONE' } }")
    out = out.strip()
    if not out or out.startswith("<ps error"):
        return "⚠️ HP Easy Clean: PowerShell не ответил, не остановлен (" + (out or "пусто") + ")"
    if out == "none":
        return None
    lines = out.splitlines()
    if lines and lines[-1] == "GONE":
        return "HP Easy Clean остановлен (" + "; ".join(lines[:-1]) + "); вернуть: запустить из Пуска"
    return "⚠️ HP Easy Clean НЕ остановлен (" + "; ".join(lines) + "): нужен админ-запуск Stop-Process"


HOOKERS = ("autohotkey", "anydesk", "powertoys", "razer", "synapse", "sharpkeys",
           "kanata", "keyboardmanager", "logioptions", "teamviewer")

# SystemParametersInfo
SPI_GETFILTERKEYS, SPI_SETFILTERKEYS = 0x0032, 0x0033
SPI_GETSTICKYKEYS, SPI_SETSTICKYKEYS = 0x003A, 0x003B
SPI_GETTOGGLEKEYS, SPI_SETTOGGLEKEYS = 0x0034, 0x0035
SPIF_UPDATE = 0x01 | 0x02
FKF_FILTERKEYSON = 0x1
SKF_STICKYKEYSON = 0x1


def _log(event: str, outcome: str, **extra) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "node": socket.gethostname(), "actor": os.environ.get("KBD_FIX_ACTOR", "claude"),
               "event": event, "outcome": outcome, **extra}
        with open(STATE_DIR / "usage.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------- Windows
if IS_WIN:
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)

    class STICKYKEYS(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwFlags", wintypes.DWORD)]

    class FILTERKEYS(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwFlags", wintypes.DWORD),
                    ("iWaitMSec", wintypes.DWORD), ("iDelayMSec", wintypes.DWORD),
                    ("iRepeatMSec", wintypes.DWORD), ("iBounceMSec", wintypes.DWORD)]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("_pad", ctypes.c_byte * 32)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]

    KEYEVENTF_KEYUP = 0x2
    user32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]
    user32.SystemParametersInfoW.restype = wintypes.BOOL
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.GetKeyState.restype = ctypes.c_short


def key_down(vk: int) -> bool:
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def caps_on() -> bool:
    return bool(user32.GetKeyState(VK_CAPITAL) & 0x1)


def _spi_get(get_code: int, struct):
    s = struct()
    s.cbSize = ctypes.sizeof(struct)
    if not user32.SystemParametersInfoW(get_code, s.cbSize, ctypes.byref(s), 0):
        s.dwFlags = 0xFFFFFFFF  # маркер «не могу судить», не путать с «выкл»
    return s


def _reg(path: str, name: str | None = None):
    import winreg
    hive, sub = path.split("\\", 1)
    root = {"HKCU": winreg.HKEY_CURRENT_USER, "HKLM": winreg.HKEY_LOCAL_MACHINE}[hive]
    try:
        with winreg.OpenKey(root, sub) as k:
            if name is None:
                out, i = {}, 0
                while True:
                    try:
                        n, v, _ = winreg.EnumValue(k, i)
                    except OSError:
                        return out
                    out[n] = v
                    i += 1
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return None


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True,
                              text=True, timeout=40, encoding="utf-8", errors="replace").stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"<ps error {e}>"


def diagnose() -> dict:
    sticky = _spi_get(SPI_GETSTICKYKEYS, STICKYKEYS)
    filt = _spi_get(SPI_GETFILTERKEYS, FILTERKEYS)
    toggle = _reg(r"HKCU\Keyboard Layout\Toggle") or {}
    scancode = _reg(r"HKLM\SYSTEM\CurrentControlSet\Control\Keyboard Layout", "Scancode Map")
    procs = _ps("Get-CimInstance Win32_Process | ForEach-Object { $_.Name + '|' + $_.CommandLine }")
    hookers = sorted({ln.strip()[:160] for ln in procs.splitlines()
                      if any(h in ln.lower().split("|")[0] for h in HOOKERS)})
    pnp = _ps("Get-PnpDevice -Class Keyboard -PresentOnly | ForEach-Object { $_.Status + '|' + $_.FriendlyName }")
    devices = [ln.strip() for ln in pnp.splitlines() if ln.strip()]
    fg = _ps("Add-Type -Namespace W -Name F -MemberDefinition '[DllImport(\"user32.dll\")] public static extern "
             "IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\")] public static extern int "
             "GetWindowThreadProcessId(IntPtr h, out int p);'; $p=0; [void][W.F]::GetWindowThreadProcessId("
             "[W.F]::GetForegroundWindow(),[ref]$p); (Get-Process -Id $p).ProcessName").strip()
    ctf = any(ln.lower().startswith("ctfmon.exe|") for ln in procs.splitlines())
    easyclean = any("easyclean" in ln.lower().split("|")[0] for ln in procs.splitlines())
    # класс I (23.10): фильтр Easy Clean живёт в цепочке клавиатуры и после удаления приложения
    filters = _reg(r"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e96b-e325-11ce-bfc1-08002be10318}", "UpperFilters") or []
    return {
        "kbf_filter": "HPKbfDriver" in filters,
        "held": [n for n, vk in MODS.items() if key_down(vk)],
        "caps_on": caps_on(),
        "sticky_on": None if sticky.dwFlags == 0xFFFFFFFF else bool(sticky.dwFlags & SKF_STICKYKEYSON),
        "filter_on": None if filt.dwFlags == 0xFFFFFFFF else bool(filt.dwFlags & FKF_FILTERKEYSON),
        "toggle": {k: str(v) for k, v in toggle.items()},
        "toggle_ok": str(toggle.get("Language Hotkey", toggle.get("Hotkey", "1"))) in ("1", "2"),
        "scancode_map": bool(scancode),
        "hookers": hookers,
        "devices": devices,
        "devices_ok": all(d.startswith("OK|") for d in devices) and bool(devices),
        "foreground": fg,
        "ctfmon": ctf,
        "easyclean": easyclean,
    }


def print_status(d: dict) -> int:
    bad = 0
    def line(ok: bool, text: str):
        nonlocal bad
        bad += 0 if ok else 1
        print(("✅ " if ok else "❌ ") + text)
    line(not d["held"], "залипших модификаторов нет" if not d["held"] else f"ЗАЛИП: {', '.join(d['held'])} (класс A, fix отпустит)")
    print(f"ℹ️ Caps Lock сейчас {'ВКЛ' if d['caps_on'] else 'выкл'}")
    for key, nm in (("sticky_on", "Залипание"), ("filter_on", "Фильтрация")):
        if d[key] is None:
            line(False, f"{nm}: не могу судить (SystemParametersInfo отказал)")
    if d["sticky_on"] is not None:
        line(d["sticky_on"] is not True, "Залипание клавиш выкл" if not d["sticky_on"] else "Залипание клавиш ВКЛ (класс B)")
    if d["filter_on"] is not None:
        line(d["filter_on"] is not True, "Фильтрация ввода выкл" if not d["filter_on"] else "Фильтрация ввода ВКЛ: короткие нажатия глотаются (класс B)")
    line(d["ctfmon"], "ctfmon жив" if d["ctfmon"] else "ctfmon НЕ запущен: Alt+Shift не переключит раскладку (класс C)")
    line(d["toggle_ok"], f"сочетание раскладки {d['toggle'] or 'по умолчанию'}" if d["toggle_ok"] else f"сочетание раскладки сбито: {d['toggle']} (класс D)")
    if str(d["toggle"].get("Language Hotkey")) == "2":
        print("ℹ️ раскладка переключается Ctrl+Shift, НЕ Alt+Shift (выбор в настройках; fix его не меняет)")
    line(not d["scancode_map"], "переназначений Scancode Map нет" if not d["scancode_map"] else "ЕСТЬ Scancode Map в HKLM: клавиши переназначены (класс E, правка = UAC + перезагрузка)")
    line(d["devices_ok"], "клавиатуры в PnP: " + "; ".join(d["devices"]))
    print("ℹ️ передний план: " + (d["foreground"] or "?") +
          ("  ← голосовой ввод / экранная клавиатура держит фокус (класс C)" if "textinputhost" in (d["foreground"] or "").lower() else ""))
    line(not d.get("easyclean"), "HP Easy Clean не запущен" if not d.get("easyclean")
         else "HP Easy Clean ЗАПУЩЕН: его драйвер HPKbfDriver режет Shift/Alt, Alt+Shift не переключит (класс H, fix остановит)")
    if d.get("kbf_filter"):
        print("ℹ️ фильтр HPKbfDriver (Easy Clean) в цепочке клавиатуры (класс I): после удаления/убийства Easy Clean "
              "может застрять и глотать Shift при зажатом Alt. Проверка: watch (строка «аккорды»). Лечение: перезагрузка; "
              "живой pnputil /restart-device встроенной PS/2 даёт 3010")
    for h in d["hookers"]:
        print("ℹ️ перехватчик ввода (класс F): " + h)
    return bad


def release_modifiers() -> list[str]:
    released = []
    for name, vk in MODS.items():
        was = key_down(vk)
        inp = INPUT(type=1)
        inp.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
        sent = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        if was:
            released.append(name if sent else f"{name}(SendInput отказал: UIPI/админ-окно)")
    return released


def press_caps() -> None:
    for flags in (0, KEYEVENTF_KEYUP):
        inp = INPUT(type=1)
        inp.u.ki = KEYBDINPUT(wVk=VK_CAPITAL, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def accessibility_off() -> list[str]:
    done = []
    for get, put, st, bit, nm in ((SPI_GETSTICKYKEYS, SPI_SETSTICKYKEYS, STICKYKEYS, SKF_STICKYKEYSON, "StickyKeys"),
                                  (SPI_GETFILTERKEYS, SPI_SETFILTERKEYS, FILTERKEYS, FKF_FILTERKEYSON, "FilterKeys")):
        s = _spi_get(get, st)
        if s.dwFlags == 0xFFFFFFFF:  # чтение отказало: не пишем мусор в настройки ОС
            done.append(f"⚠️ {nm}: не прочитан, не трогаю")
        elif s.dwFlags & bit:
            s.dwFlags &= ~bit
            ok = user32.SystemParametersInfoW(put, s.cbSize, ctypes.byref(s), SPIF_UPDATE)
            done.append(f"{nm} off" if ok else f"⚠️ {nm}: Windows отказала выключить")
    return done


def fix_toggle() -> str | None:
    import winreg
    cur = _reg(r"HKCU\Keyboard Layout\Toggle") or {}
    want = {"Hotkey": "1", "Language Hotkey": "1", "Layout Hotkey": "3"}
    # 1 = Alt+Shift, 2 = Ctrl+Shift (выбор человека, не трогаем), 3 = выключено -> чиним
    if str(cur.get("Language Hotkey", cur.get("Hotkey", "1"))) in ("1", "2"):
        return None
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / f"toggle-backup-{int(time.time())}.json").write_text(json.dumps({k: str(v) for k, v in cur.items()}), encoding="utf-8")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Keyboard Layout\Toggle") as k:
        for n, v in want.items():
            winreg.SetValueEx(k, n, 0, winreg.REG_SZ, v)
    user32.SystemParametersInfoW(0x005B, 0, None, SPIF_UPDATE)  # SPI_SETLANGTOGGLE: перечитать сейчас
    return f"Toggle {cur} -> {want} (бэкап в {STATE_DIR})"


def _ctfmon_pids() -> str:
    out = _ps("(Get-Process ctfmon -EA SilentlyContinue).Id -join ','").strip()
    return out if out.replace(",", "").isdigit() else ""


def restart_ctfmon(uac: bool = False) -> str:
    # ctfmon живёт с повышенными правами: без админа taskkill = Access denied, а прямой
    # запуск = WinError 740 (замер laptop-A 20.10). Поэтому: убили -> поднимаем через
    # explorer (ShellExecute, без UAC); не убили -> не трогаем, процесс цел.
    before = _ctfmon_pids()
    exe = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "ctfmon.exe"
    if not before:  # ctfmon мёртв: убивать нечего, сразу поднимаем
        subprocess.run(["explorer.exe", str(exe)], capture_output=True)
        time.sleep(2)
        return f"ctfmon был мёртв -> {'поднят ' + _ctfmon_pids() if _ctfmon_pids() else '⚠️ НЕ поднялся: Win+R → ctfmon'}"
    r = subprocess.run(["taskkill", "/IM", "ctfmon.exe", "/F"], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        if not uac:
            return f"ctfmon не перезапущен: нужны права админа (процесс {before or 'нет'} цел). Повтори `fix --uac`"
        # 23.10: живой ctfmon перестал обрабатывать Alt+Shift и Win+Space (даже синтетику);
        # перезапуск через UAC + системную задачу MsCtfMonitor вернул переключение. Окно UAC жмёт человек.
        inner = ('(taskkill /IM ctfmon.exe /F & timeout /t 1 >nul & schtasks /run /tn '
                 '"\\Microsoft\\Windows\\TextServicesFramework\\MsCtfMonitor")')
        _ps("Start-Process cmd.exe -ArgumentList '/c','" + inner + "' -Verb RunAs -WindowStyle Hidden -Wait")
        for _ in range(10):
            time.sleep(0.5)
            now = _ctfmon_pids()
            if now and now != before:
                return f"ctfmon перезапущен через UAC ({before} -> {now})"
        return f"⚠️ ctfmon через UAC не перезапущен (UAC отклонён или задача не стартовала), процесс {_ctfmon_pids() or 'НЕТ'}"
    time.sleep(0.7)
    subprocess.run(["explorer.exe", str(exe)], capture_output=True)
    for _ in range(10):
        time.sleep(0.5)
        if _ctfmon_pids():
            return f"ctfmon перезапущен ({before} -> {_ctfmon_pids()})"
    return "⚠️ ctfmon убит и НЕ поднялся: Win+R → ctfmon (или выйти из учётки и войти)"


def cmd_fix(args) -> int:
    before = diagnose()
    actions = []
    rel = release_modifiers()
    actions.append(f"отпущены модификаторы (были зажаты: {', '.join(rel) or 'ни одного'})")
    actions += accessibility_off()
    t = fix_toggle()
    if t:
        actions.append(t)
    if not args.no_ctfmon:
        actions.append(restart_ctfmon(uac=args.uac))
    ec = stop_easyclean()
    if ec:
        actions.append(ec)
    if args.caps_off and caps_on():
        press_caps()
        time.sleep(0.2)
        actions.append("Caps Lock выключен" if not caps_on() else "⚠️ Caps Lock НЕ выключился (SendInput заблокирован?)")
    print("ДЕЙСТВИЯ:")
    for a in actions:
        print("  · " + a)
    print("\nПОСЛЕ:")
    after = diagnose()
    bad = print_status(after)
    if any("⚠️" in a or "отказал" in a for a in actions):
        bad += 1
    _log("fix", "ok" if bad == 0 else "residual", before_held=before["held"], actions=actions)
    print("\nДальше: нажми Shift/Caps. Не помогло → `watch` покажет, доходит ли нажатие до Windows.")
    return 0 if bad == 0 else 2


def cmd_watch(args) -> int:
    keys = {**MODS, "Caps": VK_CAPITAL}
    prev = {k: key_down(vk) for k, vk in keys.items()}
    held0 = [k for k, v in prev.items() if v]
    if held0:
        print("⚠️ зажаты ДО начала записи: " + ", ".join(held0) + " (залипание, сперва fix)")
    seen = {k: (1 if prev[k] else 0) for k in keys}  # зажатая до старта = замечена
    # обычные клавиши (буквы, цифры, пробел, Enter): только ОБЩЕЕ число, без текста и порядка.
    # Отличает «никто не жал» от «буквы доходят, а модификаторы мертвы».
    plain = [0x0D, 0x20] + list(range(0x30, 0x3A)) + list(range(0x41, 0x5B))
    for vk in plain:
        user32.GetAsyncKeyState(vk)  # сброс младшего бита «нажата с прошлого опроса»
    plain_n = 0
    # аккорд Alt+Shift и переключение раскладки (класс I, 23.10): Alt и Shift порознь доходили,
    # а вместе Shift пропадал, Alt давал пачку сверхкоротких tap, раскладка не менялась
    chords = 0
    alt_taps_by_sec: dict[str, int] = {}
    user32.GetForegroundWindow.restype = ctypes.c_void_p
    user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    user32.GetKeyboardLayout.restype = ctypes.c_void_p

    def _layout():
        tid = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
        return (user32.GetKeyboardLayout(tid) or 0) & 0xFFFF
    lay, switches, in_chord = _layout(), 0, False
    args.seconds = max(5, args.seconds)
    end = time.time() + args.seconds
    print(f"ЖМИ по очереди: левый Shift, правый Shift, Caps Lock, левый Alt, Alt+Shift ({args.seconds} с). Пишу модификаторы; обычные клавиши только общим числом, без текста.")
    sys.stdout.flush()
    while time.time() < end:
        for k, vk in keys.items():
            raw = user32.GetAsyncKeyState(vk)
            d = bool(raw & 0x8000)
            if raw & 0x1 and not d and not prev[k]:  # нажали и отпустили между опросами
                seen[k] += 1
                print(f"{datetime.now():%H:%M:%S.%f}"[:-3] + f" {k} tap")
                if k in ("LAlt", "RAlt"):
                    sec = f"{datetime.now():%H:%M:%S}"
                    alt_taps_by_sec[sec] = alt_taps_by_sec.get(sec, 0) + 1
            if d != prev[k]:
                if d:
                    seen[k] += 1
                print(f"{datetime.now():%H:%M:%S.%f}"[:-3] + f" {k} {'DOWN' if d else 'up'}")
                sys.stdout.flush()
                prev[k] = d
        for vk in plain:
            if user32.GetAsyncKeyState(vk) & 0x1:
                plain_n += 1
        both = (prev["LAlt"] or prev["RAlt"]) and (prev["LShift"] or prev["RShift"])
        if both and not in_chord:
            chords += 1
            print(f"{datetime.now():%H:%M:%S.%f}"[:-3] + " АККОРД Alt+Shift")
        in_chord = both
        cur = _layout()
        if cur and cur != lay:  # 0 = переднего окна нет (смена фокуса), не переключение (замер 23.10 12:56)
            switches += 1
            print(f"{datetime.now():%H:%M:%S.%f}"[:-3] + f" РАСКЛАДКА {lay:#06x} -> {cur:#06x}")
            lay = cur
        time.sleep(0.01)
    bursts = {s: n for s, n in alt_taps_by_sec.items() if n >= 3}
    print(f"\nобычных клавиш (буквы/цифры/пробел) дошло: {plain_n}")
    print(f"аккорды Alt+Shift: {chords} · переключений раскладки: {switches} · пачки Alt-tap (≥3 за секунду): {len(bursts)}")
    print("ИТОГ нажатий: " + ", ".join(f"{k}={n}" for k, n in seen.items()))
    dead = [k for k in ("LShift", "RShift", "Caps", "LAlt") if seen[k] == 0]
    if not any(seen.values()) and plain_n >= 20:
        verdict = (f"буквы доходят ({plain_n}), а ни один модификатор нет → модификаторы мертвы ниже Windows: "
                   "шлейф/клавиатура. Проверь osk.exe и внешней клавиатурой")
    elif not any(seen.values()):
        verdict = ("ни одно нажатие не дошло: либо никто не жал, либо фокус у окна с перехватом "
                   "(AnyDesk полноэкранный, RDP), либо умерла вся клавиатура. Повтори, нажимая в Блокноте")
    elif dead:
        # «не замечена» ≠ «мертва»: прибор не знает, жали ли её (панель 20.10, 4 модели из 4)
        verdict = (f"не замечены: {', '.join(dead)}. Если их ЖАЛИ, а остальные дошли → это ниже Windows: "
                   f"клавиатура/шлейф/драйвер; проверь osk.exe и внешней клавиатурой. Не жали → не судимы")
    else:
        rest = [k for k in ("LCtrl", "RCtrl", "RAlt", "LWin") if seen[k] == 0]
        verdict = ("LShift, RShift, Caps, LAlt доходят до Windows → эти клавиши целы, поломка в приложении/раскладке: fix + проверь окно"
                   + (f". Не нажимались (не судимы): {', '.join(rest)}" if rest else ""))
    if bursts and chords == 0:
        verdict += (" · ⚠️ Alt приходил пачками сверхкоротких нажатий без Shift → фильтр-драйвер глотает Shift "
                    "при Alt (класс I, HPKbfDriver): перезагрузка")
    elif chords and not switches:
        verdict += " · аккорд Alt+Shift дошёл, а раскладка не сменилась → ctfmon / сочетание раскладки (классы C, D)"
    elif chords and switches:
        verdict += " · ✅ Alt+Shift доходит и переключает раскладку"
    print("ВЕРДИКТ: " + verdict)
    _log("watch", "dead:" + ",".join(dead) if dead else "all-arrive", seen=seen, plain=plain_n,
         chords=chords, switches=switches, alt_bursts=len(bursts))
    return 2 if dead else 0


# ---------------------------------------------------------------- macOS
MAC_HELP = """macOS ветка (ручная, проверено не на всех узлах):
  defaults read com.apple.universalaccess stickyKey        # 1 = Залипание включено
  defaults read com.apple.universalaccess slowKey          # 1 = Медленные клавиши
  hidutil property --get UserKeyMapping                    # не пусто = клавиши переназначены
  ioreg -l -w0 | grep -i -E 'HIDKeyboard|AppleEmbeddedKeyboard' | head
Лечение: Системные настройки → Универсальный доступ → Клавиатура (выкл Залипание/Медленные);
  hidutil property --set '{"UserKeyMapping":[]}' снимает переназначение до перезагрузки;
  Caps Lock не переключает раскладку? Клавиатура → Источники ввода → «Caps Lock переключает».
  Karabiner-Elements / BetterTouchTool в процессах = первый подозреваемый."""


def main() -> int:
    ap = argparse.ArgumentParser(description="Ремонт модификаторов клавиатуры (Shift/Caps/Alt+Shift)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    w = sub.add_parser("watch"); w.add_argument("--seconds", type=int, default=60)
    f = sub.add_parser("fix"); f.add_argument("--no-ctfmon", action="store_true"); f.add_argument("--caps-off", action="store_true"); f.add_argument("--uac", action="store_true")
    args = ap.parse_args()
    if not IS_WIN:
        print(f"{platform.system()}: автоматика только для Windows.\n" + MAC_HELP)
        _log(args.cmd, "non-windows")
        return 0
    if args.cmd == "status":
        bad = print_status(diagnose())
        _log("status", "ok" if bad == 0 else f"bad:{bad}")
        return 0 if bad == 0 else 2
    if args.cmd == "watch":
        return cmd_watch(args)
    return cmd_fix(args)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
