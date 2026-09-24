#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export iMessage/SMS history from a chat.db copy -> per-conversation Markdown + JSON.
Decodes the `attributedBody` typedstream blob (97% of messages store text there),
labels senders with real names from the Contacts name map."""
import os, re, json, sqlite3, datetime

DB = "/tmp/msg/chat.db"
OUT = "/tmp/msg/out"
NAME_MAP = "/tmp/contacts_export/out/name_map.json"
CONV_DIR = os.path.join(OUT, "conversations")
os.makedirs(CONV_DIR, exist_ok=True)

APPLE_EPOCH = [id]  # 2001-01-01 in unix seconds

try:
    nm = json.load(open(NAME_MAP, encoding="utf-8"))
    NAME_PHONE, NAME_EMAIL = nm["phones"], nm["emails"]
except Exception:
    NAME_PHONE, NAME_EMAIL = {}, {}

def phone_key(s):
    d = re.sub(r"\D", "", s or "")
    return d[-10:] if len(d) >= 10 else d

def name_for(handle_id):
    if not handle_id:
        return None
    if "@" in handle_id:
        return NAME_EMAIL.get(handle_id.lower())
    return NAME_PHONE.get(phone_key(handle_id))

def label(handle_id):
    n = name_for(handle_id)
    return f"{n} ({handle_id})" if n else (handle_id or "Unknown")

def decode_ab(blob):
    """Extract text from an attributedBody typedstream blob."""
    if not blob:
        return None
    b = bytes(blob)
    i = b.find(b"NSString")
    if i < 0:
        return None
    k = b.find(b"\x2b", i + 8, i + 24)  # '+' marker precedes the inline string length
    if k < 0:
        return None
    q = k + 1
    if q >= len(b):
        return None
    m = b[q]
    if m == 0x81:
        length = int.from_bytes(b[q+1:q+3], "little"); s = q + 3
    elif m == 0x82:
        length = int.from_bytes(b[q+1:q+5], "little"); s = q + 5
    else:
        length = m; s = q + 1
    if length <= 0 or length > len(b):
        return None
    return b[s:s+length].decode("utf-8", "replace")

def ts(date_ns):
    if not date_ns:
        return ""
    try:
        return datetime.datetime.fromtimestamp(date_ns/1e9 + APPLE_EPOCH).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

# handles
handle = {r["ROWID"]: r["id"] for r in con.execute("SELECT ROWID, id FROM handle")}
# chats
chats = {}
for r in con.execute("SELECT ROWID, chat_identifier, display_name, style, service_name FROM chat"):
    chats[r["ROWID"]] = dict(id=r["chat_identifier"], name=r["display_name"] or "",
                             style=r["style"], service=r["service_name"] or "")
# participants per chat
parts = {}
for r in con.execute("SELECT chat_id, handle_id FROM chat_handle_join"):
    parts.setdefault(r["chat_id"], []).append(handle.get(r["handle_id"], ""))
# message -> chat (first chat if several)
msg_chat = {}
for r in con.execute("SELECT chat_id, message_id FROM chat_message_join ORDER BY message_id"):
    msg_chat.setdefault(r["message_id"], r["chat_id"])
# attachments per message
att = {}
for r in con.execute("""SELECT maj.message_id, a.filename, a.mime_type, a.transfer_name, a.total_bytes
                        FROM message_attachment_join maj JOIN attachment a ON a.ROWID=maj.attachment_id"""):
    att.setdefault(r["message_id"], []).append(dict(
        filename=r["filename"], mime=r["mime_type"] or "",
        name=r["transfer_name"] or (os.path.basename(r["filename"]) if r["filename"] else ""),
        bytes=r["total_bytes"] or 0))

# iterate messages
conv_msgs = {}   # chat_id -> list of msg dicts
all_json = []
n_text_col = n_decoded = n_empty = 0
for r in con.execute("""SELECT ROWID, date, is_from_me, handle_id, text, attributedBody,
                        cache_has_attachments, associated_message_type
                        FROM message ORDER BY date"""):
    mid = r["ROWID"]
    cid = msg_chat.get(mid)
    body = r["text"]
    if body and body.strip():
        n_text_col += 1
    else:
        body = decode_ab(r["attributedBody"])
        if body:
            n_decoded += 1
    attachments = att.get(mid, [])
    if (not body or not body.strip()) and not attachments:
        n_empty += 1
        if r["associated_message_type"]:   # pure tapback/reaction metadata
            continue
    sender = "Me" if r["is_from_me"] else label(handle.get(r["handle_id"], ""))
    rec = dict(id=mid, chat_id=cid, date=ts(r["date"]), is_from_me=bool(r["is_from_me"]),
               sender=sender, text=(body or ""), attachments=attachments)
    conv_msgs.setdefault(cid, []).append(rec)
    all_json.append(rec)

con.close()

# write JSON (complete)
with open(os.path.join(OUT, "messages.json"), "w", encoding="utf-8") as f:
    json.dump({"exported_messages": len(all_json), "conversations": len(conv_msgs),
               "source": "Apple Messages (iMessage/SMS) chat.db", "notes": all_json}, f,
              ensure_ascii=False, indent=2)

# conversation title + filename
def conv_title(cid):
    c = chats.get(cid, {})
    if c.get("name"):
        return c["name"]
    ps = [p for p in parts.get(cid, []) if p]
    if len(ps) == 1:
        return label(ps[0])
    if ps:
        names = [name_for(p) or p for p in ps]
        return ", ".join(names[:4]) + (" …" if len(ps) > 4 else "")
    return c.get("id") or f"chat-{cid}"

def slug(t, cid):
    t = re.sub(r'[\\/:*?"<>|\x00-\x1f]', " ", t)
    t = re.sub(r"\s+", " ", t).strip(" .")
    return (t[:70].strip() or f"chat-{cid}")

used = {}
index = []
for cid, msgs in conv_msgs.items():
    title = conv_title(cid)
    base = slug(title, cid)
    key = base.lower()
    if key in used:
        used[key] += 1; base = f"{base} ({used[key]})"
    else:
        used[key] = 0
    c = chats.get(cid, {})
    fm = ["---", f'conversation: "{title.replace(chr(34), "")}"',
          f'chat_identifier: "{c.get("id","")}"',
          f'type: {"group" if c.get("style")==43 else "direct"}',
          f'service: {c.get("service","")}', f"messages: {len(msgs)}",
          f"first: {msgs[0]['date']}", f"last: {msgs[-1]['date']}",
          'source: "Apple Messages (iMessage/SMS)"', "---", "", f"# {title}", ""]
    lines = []
    last_day = None
    for m in msgs:
        day = m["date"][:10]
        if day != last_day:
            lines.append(f"\n### {day}\n"); last_day = day
        who = "**Me**" if m["is_from_me"] else f"**{m['sender']}**"
        tm = m["date"][11:16]
        txt = m["text"].strip()
        lines.append(f"- `{tm}` {who}: {txt}" if txt else f"- `{tm}` {who}:")
        for a in m["attachments"]:
            lines.append(f"    - 📎 {a['name']} ({a['mime']}, {a['bytes']} bytes)")
    with open(os.path.join(CONV_DIR, base + ".md"), "w", encoding="utf-8") as f:
        f.write("\n".join(fm + lines) + "\n")
    index.append((len(msgs), msgs[-1]["date"], title, base))

# index sorted by recency
index.sort(key=lambda x: x[1], reverse=True)
with open(os.path.join(OUT, "_INDEX.md"), "w", encoding="utf-8") as f:
    f.write(f"# iMessage — {len(conv_msgs)} conversations, {len(all_json)} messages\n\n")
    f.write("Sorted by most recent activity.\n\n")
    for n, last, title, base in index:
        f.write(f"- [{title}](conversations/{base.replace(' ','%20')}.md) — {n} msgs, last {last[:10]}\n")

print(f"messages exported: {len(all_json)} (text-col {n_text_col}, decoded {n_decoded}, empty {n_empty})")
print(f"conversations: {len(conv_msgs)} md files")
