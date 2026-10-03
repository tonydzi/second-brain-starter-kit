#!/usr/bin/env python3
"""Telethon-рельса этой машины (сессия rail, независимая от MCP-демона). 0 LLM.
  tgbus.py me
  tgbus.py read  <chat_id> [--limit 30] [--grep TEXT] [--since-id N]
  tgbus.py send  <chat_id> "текст"          -> печатает id, перечитывает отправленное из истории
  tgbus.py check                              -> exit 0 если сессия жива и комната видна (печатает только «rail OK: комната видна», без названия и id)
"""
import argparse, asyncio, json, os, re, sys
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession

D = Path(os.path.expanduser("~/Library/Application Support/claude-tgbus"))
ROOM = int(os.environ.get("TGBUS_ROOM", "0") or 0)   # id комнаты флота: из окружения, в коде его нет

def env(p):
    return dict(l.rstrip("\n").split("=", 1) for l in open(p) if "=" in l and not l.startswith("#"))

def client():
    api = env(D / "api.env"); ses = env(D / "rail.session.env")
    return TelegramClient(StringSession(ses["TELEGRAM_SESSION_STRING"]), int(api["TELEGRAM_API_ID"]), api["TELEGRAM_API_HASH"])

async def who(m):
    s = await m.get_sender()
    return getattr(s, "username", None) or getattr(s, "first_name", None) or getattr(s, "title", None) or str(m.sender_id)

async def main(a):
    async with client() as c:
        if a.cmd == "me":
            me = await c.get_me(); print("rail OK" if me else "rail DEAD"); return 0 if me else 1   # без @username/id: квитанции и verify их не печатают
        if a.cmd == "check":
            if not ROOM: print("TGBUS_ROOM не задан: проверить видимость комнаты нельзя (используй `me`)"); return 2
            me = await c.get_me(); ent = await c.get_entity(ROOM)   # не нашлась = исключение и ненулевой выход
            print("rail OK: комната видна" if me and ent else "rail DEAD"); return 0 if me and ent else 1   # без названия комнаты: оно уходит в квитанции и отчёты
        ent = await c.get_entity(a.chat_id)
        if a.cmd == "read":
            out = []
            async for m in c.iter_messages(ent, limit=a.limit, min_id=a.since_id or 0):
                if not m.message: continue
                if a.grep and a.grep not in m.message: continue
                out.append({"id": m.id, "date": m.date.strftime("%Y-%m-%d %H:%M"), "from": await who(m), "text": m.message})
            for r in reversed(out):
                print(f"--- id={r['id']} {r['date']} from={r['from']}\n{r['text']}\n")
            print(f"[{len(out)} сообщений]"); return 0
        if a.cmd == "send":
            sent = await c.send_message(ent, a.text)
            back = (await c.get_messages(ent, ids=[sent.id]))[0]
            ok = back is not None and back.message == a.text
            print(json.dumps({"sent_id": sent.id, "date": sent.date.strftime("%Y-%m-%d %H:%M"), "reread_ok": ok}, ensure_ascii=False))
            return 0 if ok else 1

p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
sp.add_parser("me"); sp.add_parser("check")
r = sp.add_parser("read"); r.add_argument("chat_id", type=int); r.add_argument("--limit", type=int, default=30); r.add_argument("--grep"); r.add_argument("--since-id", type=int)
s = sp.add_parser("send"); s.add_argument("chat_id", type=int); s.add_argument("text")
sys.exit(asyncio.run(main(p.parse_args())))
