# -*- coding: utf-8 -*-
"""Пересобрать applied_set.json по ФАКТУ: прошлый набор + компании из таблицы «Пачка 03.09»
+ отправители писем-подтверждений за сегодня (почта = ground truth подач)."""
import json, os, re, sys, imaplib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets

HERE = os.path.dirname(os.path.abspath(__file__))
SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"

applied = set(json.load(open(os.path.join(HERE, "applied_set.json"), encoding="utf-8")))
before = len(applied)

# 1) все компании из сегодняшней таблицы (любой статус — трогали, значит не берём заново)
for row in sheets.read_tab(SID, "Пачка 03.09")[1:]:
    if len(row) > 1 and row[1].strip():
        applied.add(row[1].strip())
after_sheet = len(applied)

# 2) отправители писем-подтверждений за сегодня
pw = None
for line in open(os.environ.get("GMAIL_A_SECRET", os.path.join(os.environ.get("CLAUDE_SECRETS", r"[путь владельца] May26\secrets"), "gmail-a-apppassword.env")), encoding="utf-8"):
    if line.startswith("GMAIL_A_APP_PASSWORD="):
        pw = line.split("=", 1)[1].strip()
M = imaplib.IMAP4_SSL("imap.gmail.com")
M.login("dzyatkovskiy.a@gmail.com", pw)
M.select("INBOX", readonly=True)
typ, data = M.search(None, '(SINCE "03-Sep-2026")')
CONF = re.compile(r"thank(s| you) for (applying|your application)|application (received|was submitted|has been)|"
                  r"received your application|thanks for your application|thanks for applying", re.I)
GENERIC = re.compile(r"greenhouse-mail|no-?reply@|donotreply@|jobs@|careers@|talent@|recruiting@", re.I)
SUBJ_CO = re.compile(r"(?:applying (?:to|at|for)|application (?:to|with|at)|interest in)\s+(?:the\s+)?"
                     r"([A-Za-z0-9][\w&.\' -]{1,40}?)(?=\s*(?:[!.,|:(]|\s(?:has|was|-|–|\||for|\(|team)|$))", re.I)
STRIP = re.compile(r"\s+(hiring team|recruiting team|talent team|team|recruitment team|hiring)$", re.I)
mail_cos = set()
for mid in data[0].split():
    typ, md = M.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
    hdr = md[0][1].decode("utf-8", "ignore")
    m = re.search(r"Subject:\s*(.+?)(?:\r?\nFrom:|\r?\n\r?\n|$)", hdr, re.S)
    f = re.search(r"From:\s*(.+?)(?:\r?\nSubject:|\r?\n\r?\n|$)", hdr, re.S)
    subj = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    frm = re.sub(r"\s+", " ", f.group(1)).strip() if f else ""
    if not CONF.search(subj):
        continue
    name = re.sub(r"<.*?>", "", frm).replace('"', "").strip()
    for _ in range(2):
        name = STRIP.sub("", name).strip()
    # 08.09: обезличенный отправитель (greenhouse-mail.io, jobs@, donotreply@) — компания живёт в ТЕМЕ
    if not name or GENERIC.search(frm) or "@" in name:
        mc = SUBJ_CO.search(subj)
        if mc:
            name = mc.group(1).strip(" !.,-")
    if name and len(name) > 1:
        mail_cos.add(name)
M.logout()
applied |= mail_cos

json.dump(sorted(applied), open(os.path.join(HERE, "applied_set.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"applied_set: {before} -> {len(applied)} (+{after_sheet-before} из таблицы, +{len(applied)-after_sheet} новых из почты)")
print("из почты:", ", ".join(sorted(mail_cos)))
