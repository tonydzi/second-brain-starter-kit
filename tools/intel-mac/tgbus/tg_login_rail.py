#!/usr/bin/env python3
"""Вторая своя сессия этой машины: Telethon-рельса (rail).
QR-токен подтверждает mcp-сессия (донор). Демон на время акцепта выгружается, чтобы на одном
auth key не было двух клиентов, и сразу поднимается обратно. 2FA вводит владелец в окне macOS
(secret_dialog.ask -> secret_prompt.sh, скрытый ввод); пароль не печатается и не сохраняется.
Строка сессии: только в rail.session.env (600).
Путь к plist демона приходит из окружения TGBUS_DAEMON_PLIST (его задаёт onboard-intel-mac.sh): метка агента
у каждого флота своя, в коде её нет.
Коды: 0 = сессия записана · 1 = вход не состоялся · 2 = пароль не введён · 3 = пароль неверен трижды · 5 = неверный вызов."""
import asyncio, os, subprocess, sys, time
from pathlib import Path
from secret_dialog import ask

D = Path(os.path.expanduser("~/Library/Application Support/claude-tgbus"))
OUT = D / "rail.session.env"
PLIST = os.environ.get("TGBUS_DAEMON_PLIST", "")

def env(p): return dict(l.rstrip("\n").split("=", 1) for l in open(p) if "=" in l and not l.startswith("#"))
def write_secret(p, text):
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)   # новый файл рождается 600, без окна между write и chmod
    os.fchmod(fd, 0o600)                                              # mode у os.open действует только при создании: существующий файл чиним тут же
    with os.fdopen(fd, "w") as f: f.write(text)
def daemon(action):
    subprocess.run(["launchctl", action, PLIST], capture_output=True); time.sleep(3)   # без -w: не переключаем disabled-флаг агента

async def main():
    if OUT.exists(): print("rail.session.env уже есть: повторный вход не делаю."); return 0
    if not PLIST or not os.path.isfile(PLIST): print("TGBUS_DAEMON_PLIST не задан или файла нет: не знаю, какой демон выгружать на время акцепта"); return 5
    from telethon import TelegramClient, errors, functions
    from telethon.sessions import StringSession
    api = env(D / "api.env"); donor_env = env(D / "mcp.session.env")
    api_id, api_hash = int(api["TELEGRAM_API_ID"]), api["TELEGRAM_API_HASH"]
    new = TelegramClient(StringSession(), api_id, api_hash, device_model="Mac (Intel) claude-tgbus", system_version="macOS", app_version="1.0 rail")
    await new.connect(); qr = await new.qr_login()
    need_pw = False
    daemon("unload"); print("демон выгружен на время акцепта")
    try:
        donor = TelegramClient(StringSession(donor_env["TELEGRAM_SESSION_STRING"]), api_id, api_hash)
        await donor.connect()
        for _ in range(3):
            try:
                await donor(functions.auth.AcceptLoginTokenRequest(token=qr.token)); print("QR-токен подтверждён донором")
                await qr.wait(timeout=30); break
            except errors.SessionPasswordNeededError: need_pw = True; break
            except (asyncio.TimeoutError, errors.AuthTokenExpiredError): await qr.recreate()
        await donor.disconnect()
    finally:
        daemon("load"); print("демон поднят обратно")
    if need_pw:
        note = ""
        for attempt in range(3):
            try:
                pw = ask("telegram_2fa", r".+", note + "Облачный пароль Telegram (двухэтапная проверка) того же аккаунта, чья mcp-сессия уже есть на этой машине. Нужен один раз, для второй сессии (рельса).", tries=1)
            except SystemExit:
                print("пароль не введён"); await new.disconnect(); return 2
            try: await new.sign_in(password=pw); break
            except errors.PasswordHashInvalidError: note = "Неверный пароль, попробуй ещё раз. "; print("неверный пароль, попытка", attempt + 1)
            finally: pw = None
        else: await new.disconnect(); return 3
    me = await new.get_me()
    if not me: print("вход не состоялся"); await new.disconnect(); return 1
    write_secret(OUT, f"TELEGRAM_SESSION_STRING={new.session.save()}\n")
    print("rail OK: сессия [rail] записана (600), аккаунт подтверждён. Строка и идентификаторы на экран не выводятся.")
    await new.disconnect(); return 0

sys.exit(asyncio.run(main()))
