#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract contacts from all AddressBook abcddb sources -> CSV + JSON + name map."""
import os, re, glob, json, csv, sqlite3

SRC = glob.glob(os.path.expanduser(
    "~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb"))
OUT = "/tmp/contacts_export/out"
os.makedirs(OUT, exist_ok=True)

def digits(s):
    return re.sub(r"\D", "", s or "")

def phone_key(s):
    d = digits(s)
    return d[-10:] if len(d) >= 10 else d  # last10 for intl matching; short codes kept

people = {}   # signature -> record

def norm(s): return (s or "").strip()

for db in SRC:
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
    except Exception:
        continue
    try:
        rows = con.execute("""
            SELECT Z_PK, ZFIRSTNAME, ZLASTNAME, ZMIDDLENAME, ZNICKNAME, ZORGANIZATION
            FROM ZABCDRECORD""").fetchall()
    except Exception:
        con.close(); continue
    for zpk, first, last, mid, nick, org in rows:
        first, last, mid, nick, org = map(norm, (first, last, mid, nick, org))
        try:
            phones = [r[0] for r in con.execute(
                "SELECT ZFULLNUMBER FROM ZABCDPHONENUMBER WHERE ZOWNER=?", (zpk,)) if r[0]]
            emails = [r[0] for r in con.execute(
                "SELECT ZADDRESS FROM ZABCDEMAILADDRESS WHERE ZOWNER=?", (zpk,)) if r[0]]
        except Exception:
            phones, emails = [], []
        if not (first or last or org or nick or phones or emails):
            continue
        namesig = " ".join(x for x in (first, last, org) if x).lower()
        if namesig:
            sig = "N:" + namesig
        elif emails:
            sig = "E:" + emails[0].lower()
        elif phones:
            sig = "P:" + phone_key(phones[0])
        else:
            continue
        rec = people.setdefault(sig, {"first": first, "last": last, "middle": mid,
                                      "nickname": nick, "org": org,
                                      "phones": set(), "emails": set()})
        # prefer the most complete name fields
        for k, v in (("first", first), ("last", last), ("middle", mid),
                     ("nickname", nick), ("org", org)):
            if v and not rec[k]:
                rec[k] = v
        rec["phones"].update(p.strip() for p in phones)
        rec["emails"].update(e.strip() for e in emails)
    con.close()

# finalize
records = []
name_phone = {}
name_email = {}
for rec in people.values():
    phones = sorted(rec["phones"])
    emails = sorted(rec["emails"])
    disp = " ".join(x for x in (rec["first"], rec["last"]) if x) or rec["nickname"] or rec["org"] or (phones[0] if phones else (emails[0] if emails else ""))
    records.append({
        "display_name": disp, "first": rec["first"], "last": rec["last"],
        "middle": rec["middle"], "nickname": rec["nickname"], "org": rec["org"],
        "phones": phones, "emails": emails,
    })
    for p in phones:
        k = phone_key(p)
        if k and (k not in name_phone or len(disp) > len(name_phone.get(k, ""))):
            name_phone[k] = disp
    for e in emails:
        name_email[e.lower()] = disp

records.sort(key=lambda r: (r["display_name"] or "").lower())

with open(os.path.join(OUT, "contacts.json"), "w", encoding="utf-8") as f:
    json.dump({"count": len(records), "contacts": records}, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "contacts.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Display Name", "First", "Last", "Middle", "Nickname", "Organization", "Phones", "Emails"])
    for r in records:
        w.writerow([r["display_name"], r["first"], r["last"], r["middle"], r["nickname"],
                    r["org"], "; ".join(r["phones"]), "; ".join(r["emails"])])

with open(os.path.join(OUT, "name_map.json"), "w", encoding="utf-8") as f:
    json.dump({"phones": name_phone, "emails": name_email}, f, ensure_ascii=False)

print("sources:", len(SRC))
print("unique contacts:", len(records))
print("with phone:", sum(1 for r in records if r["phones"]))
print("with email:", sum(1 for r in records if r["emails"]))
print("phone->name map:", len(name_phone), "| email->name map:", len(name_email))
