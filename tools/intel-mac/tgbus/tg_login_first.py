#!/usr/bin/env python3
"""Первая Telegram-сессия этой машины (обычно label mcp): телефон + код + пароль 2FA.
Всё, что вводит человек, идёт через окна macOS (secret_dialog.ask -> secret_prompt.sh): оператор может не видеть
вкладок терминала, пароль вводится скрыто. Формат api_id, api_hash и телефона проверяется ДО импорта Telethon и
до любого обращения к сети: три неудачные попытки = отказ, а не бесконечный переспрос.
Секреты: api_id/api_hash в api.env рядом (права 600); строка сессии только в <label>.session.env (600).
На экран ничего секретного не печатается. Пароль 2FA нигде не сохраняется.
Запускать интерпретатором venv сервера: <папка узла>/mcp/telegram-mcp/.venv/bin/python tg_login_first.py --label mcp
Вторая сессия (rail) делается tg_login_rail.py: её QR-токен подтверждает эта, первая.
"""
import argparse, os, stat, sys
from pathlib import Path
from secret_dialog import ask

D = Path(os.path.expanduser("~/Library/Application Support/claude-tgbus"))
ap = argparse.ArgumentParser(); ap.add_argument("--label", default="mcp", choices=["mcp", "rail"]); a = ap.parse_args()

def load_env(p):
    env = {}
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1); env[k.strip()] = v.strip()
    return env

def write_secret(p, text):
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)   # новый файл рождается 600, без окна между write и chmod
    os.fchmod(fd, 0o600)                                              # mode у os.open действует только при создании: существующий файл чиним тут же
    with os.fdopen(fd, "w") as f: f.write(text)

D.mkdir(parents=True, exist_ok=True); os.chmod(D, stat.S_IRWXU)
out = D / f"{a.label}.session.env"
if out.exists():
    print(f"{out.name} уже есть: повторный вход не делаю (убери файл, если нужен перелогин)."); sys.exit(0)

api = load_env(D / "api.env")
if not api.get("TELEGRAM_API_ID") or not api.get("TELEGRAM_API_HASH"):
    i = ask("api_id", r"[0-9]{5,10}", "api_id со страницы https://my.telegram.org (число из 5-10 цифр)", hidden=False)
    if int(i) >= 2**31: print("api_id вне диапазона: вход остановлен до обращения к сети."); sys.exit(4)
    h = ask("api_hash", r"[0-9a-f]{32}", "api_hash оттуда же (ровно 32 символа a-f/0-9). Ввод скрыт.")
    api = {"TELEGRAM_API_ID": i, "TELEGRAM_API_HASH": h}
    write_secret(D / "api.env", f"TELEGRAM_API_ID={i}\nTELEGRAM_API_HASH={h}\n"); print("api.env записан (600)")
phone = ask("telegram_phone", r"\+[0-9]{7,15}", "Номер телефона Telegram в международном формате (плюс и код страны)", hidden=False)

def ask_code(): return ask("telegram_code", r"[0-9]{4,8}", "Код подтверждения, который Telegram прислал в приложение или SMS", hidden=False)
def ask_password(): return ask("telegram_2fa", r".+", "Облачный пароль Telegram (двухэтапная проверка). Ввод скрыт, нигде не сохраняется.")

# Telethon импортируется только после того, как формат проверен: до этой строки сети не было
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

with TelegramClient(StringSession(), int(api["TELEGRAM_API_ID"]), api["TELEGRAM_API_HASH"],
                    device_model="Mac (Intel) claude-tgbus", system_version="macOS", app_version=f"1.0 {a.label}") as c:
    c.start(phone=phone, password=ask_password, code_callback=ask_code)
    me = c.get_me()
    if not me: print("вход не состоялся"); sys.exit(1)
    write_secret(out, f"TELEGRAM_SESSION_STRING={c.session.save()}\n")
    print(f"rail OK: сессия [{a.label}] записана (600), аккаунт подтверждён. Строка и идентификаторы на экран не выводятся.")
