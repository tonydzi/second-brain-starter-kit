#!/usr/bin/env python3
"""Ждать в комнате новые сообщения по теме от НЕ-моего отправителя (через MCP-демон).
  tgwait.py <min_id> [секунд=540]   -> печатает найденные сообщения целиком, exit 0; exit 3 = таймаут.
Пустой результат демон отдаёт текстом, не JSON, это не ошибка."""
import asyncio, json, os, sys, time
# комната, тег темы и моё отображаемое имя: из окружения, в коде их нет; проверка ДО тяжёлых импортов, чтобы падать с текстом, а не трейсбеком
ROOM = int(os.environ.get("TGBUS_ROOM", "0") or 0); TAG = os.environ.get("TGWAIT_TAG", ""); ME = os.environ.get("TGWAIT_ME", "")
if not ROOM: sys.exit("TGBUS_ROOM не задан")
if not TAG or not ME: sys.exit("TGWAIT_TAG и TGWAIT_ME обязательны: пустой тег совпал бы с любым текстом, пустое имя не отсечёт мои же сообщения")
if len(sys.argv) < 2 or not sys.argv[1].isdigit(): sys.exit("использование: tgwait.py <min_id> [секунд=540]")
MIN = int(sys.argv[1]); LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 540
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def fetch():
    async with streamablehttp_client("http://127.0.0.1:8765/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("get_new_messages_since", {"chat_id": ROOM, "min_id": MIN, "limit": 30})
            out = "\n".join(getattr(c, "text", "") for c in res.content)
    if res.isError: raise RuntimeError(out[:200])
    try: return json.loads(out).get("results", [])
    except json.JSONDecodeError: return []          # "No new messages since id N."

async def main():
    t0, errs = time.time(), 0
    while time.time() - t0 < LIMIT:
        try:
            hits = [m for m in await fetch() if m["sender"] != ME and TAG in m["text"]]
            if hits:
                for m in sorted(hits, key=lambda m: m["id"]):
                    print(f"===== id={m['id']} {m['date']} sender={m['sender']}\n{m['text']}\n", flush=True)
                print(f"[ответ получен через {int(time.time()-t0)} с; ошибок опроса: {errs}]", flush=True); return 0
        except Exception as e:
            errs += 1; print("poll error:", type(e).__name__, str(e)[:160], flush=True)
        await asyncio.sleep(20)
    print(f"[за {LIMIT} с сообщений по теме от других нет; ошибок опроса: {errs}]", flush=True); return 3

sys.exit(asyncio.run(main()))
