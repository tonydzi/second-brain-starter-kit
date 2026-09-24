# -*- coding: utf-8 -*-
"""python mail_for.py <regex> — письма за сегодня по компании (From+Subject+время)."""
import imaplib, os, re, sys, email.utils
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
from email.header import decode_header, make_header
n = 0
for mid in data[0].split():
    typ, md = M.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
    hdr = md[0][1].decode("utf-8", "ignore")
    if not pat.search(hdr):
        continue
    def grab(k):
        m = re.search(rf"{k}:\s*(.+?)(?:\r?\n[A-Z][a-z-]+:|\r?\n\r?\n|$)", hdr, re.S)
        if not m:
            return ""
        try:
            return str(make_header(decode_header(re.sub(r"\s+", " ", m.group(1)).strip())))
        except Exception:
            return re.sub(r"\s+", " ", m.group(1)).strip()
    d = grab("Date")
    try:
        d = email.utils.parsedate_to_datetime(d).strftime("%H:%M")
    except Exception:
        pass
    n += 1
    print(f"{d} | {grab('From')[:45]} | {grab('Subject')[:110]}")
print("--", n, "писем")
M.logout()
