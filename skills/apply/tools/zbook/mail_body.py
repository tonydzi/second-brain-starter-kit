# -*- coding: utf-8 -*-
"""python mail_body.py <regex> — тела сегодняшних писем по компании (первые 700 симв. текста)."""
import imaplib, os, re, sys, email
sys.stdout.reconfigure(encoding="utf-8")
pat = re.compile(sys.argv[1], re.I)
pw = None
for line in open(os.environ.get("GMAIL_A_SECRET", os.path.join(os.environ.get("CLAUDE_SECRETS", r"[путь владельца] May26\secrets"), "gmail-a-apppassword.env")), encoding="utf-8"):
    if line.startswith("GMAIL_A_APP_PASSWORD="):
        pw = line.split("=", 1)[1].strip()
M = imaplib.IMAP4_SSL("imap.gmail.com")
M.login("dzyatkovskiy.a@gmail.com", pw)
M.select("INBOX", readonly=True)
typ, data = M.search(None, '(SINCE "03-Sep-2026")')
for mid in data[0].split():
    typ, md = M.fetch(mid, "(RFC822)")
    msg = email.message_from_bytes(md[0][1])
    frm = str(msg.get("From", ""))
    if not pat.search(frm):
        continue
    body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "ignore")
            break
    if not body:
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "ignore")
                body = re.sub(r"<[^>]+>", " ", html)
                break
    body = re.sub(r"\s+", " ", body).strip()
    print("=====", frm[:50], "|", str(msg.get("Date", ""))[:31])
    print(body[:700])
    print()
M.logout()
