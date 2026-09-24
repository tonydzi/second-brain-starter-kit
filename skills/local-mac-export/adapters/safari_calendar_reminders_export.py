#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export Safari (bookmarks/reading list/history), Calendar (.ics + JSON), Reminders (MD+JSON)."""
import os, re, json, sqlite3, plistlib, datetime

APPLE = [id]
GD = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-dzyatkovskiy.a@gmail.com/My Drive/!_Claude_[машина флота]")

def ts(core):
    if core is None: return ""
    try: return datetime.datetime.fromtimestamp(core + APPLE).strftime("%Y-%m-%d %H:%M:%S")
    except Exception: return ""

# ---------------- SAFARI ----------------
SOUT = os.path.join(GD, "Safari Export 2026-06-11"); os.makedirs(SOUT, exist_ok=True)
with open(os.path.expanduser("~/Library/Safari/Bookmarks.plist"), "rb") as f:
    bm = plistlib.load(f)

bookmarks, reading = [], []
def walk(node, path):
    t = node.get("WebBookmarkType")
    if t == "WebBookmarkTypeList":
        title = node.get("Title", "")
        for ch in node.get("Children", []):
            walk(ch, path + ([title] if title and title != "BookmarksBar" else [title] if title else []))
    elif t == "WebBookmarkTypeLeaf":
        url = node.get("URLString", "")
        title = (node.get("URIDictionary") or {}).get("title", "") or url
        entry = {"title": title, "url": url, "folder": "/".join(p for p in path if p)}
        if "com.apple.ReadingList" in path:
            rl = node.get("ReadingList", {})
            entry["date_added"] = str(rl.get("DateAdded", ""))
            entry["preview"] = (rl.get("PreviewText", "") or "")[:300]
            reading.append(entry)
        else:
            bookmarks.append(entry)
walk(bm, [])

hist = []
try:
    con = sqlite3.connect("file:" + os.path.expanduser("~/Library/Safari/History.db") + "?mode=ro", uri=True)
    for url, vc, vt, title in con.execute("""
        SELECT i.url, i.visit_count, MAX(v.visit_time), (SELECT title FROM history_visits vv WHERE vv.history_item=i.id AND vv.title IS NOT NULL ORDER BY vv.visit_time DESC LIMIT 1)
        FROM history_items i LEFT JOIN history_visits v ON v.history_item=i.id GROUP BY i.id ORDER BY MAX(v.visit_time) DESC"""):
        hist.append({"url": url, "title": title or "", "visits": vc, "last_visit": ts(vt)})
    con.close()
except Exception as e:
    print("history error:", e)

json.dump({"bookmarks": bookmarks, "reading_list": reading, "history": hist},
          open(os.path.join(SOUT, "safari_export.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def md_links(items, hdr):
    out = [f"# {hdr} — {len(items)}", ""]
    for b in items:
        t = (b["title"] or b["url"]).replace("[", "(").replace("]", ")")[:150]
        extra = f" — `{b['folder']}`" if b.get("folder") else ""
        extra += f" — {b['last_visit'][:10]}" if b.get("last_visit") else ""
        out.append(f"- [{t}]({b['url']}){extra}")
    return "\n".join(out) + "\n"
open(os.path.join(SOUT, "Bookmarks.md"), "w", encoding="utf-8").write(md_links(bookmarks, "Закладки Safari"))
open(os.path.join(SOUT, "Reading List.md"), "w", encoding="utf-8").write(md_links(reading, "Reading List"))
open(os.path.join(SOUT, "History.md"), "w", encoding="utf-8").write(md_links(hist, "История Safari"))
print(f"SAFARI: bookmarks {len(bookmarks)}, reading list {len(reading)}, history {len(hist)}")

# ---------------- CALENDAR ----------------
COUT = os.path.join(GD, "Calendar Export 2026-06-11"); os.makedirs(COUT, exist_ok=True)
ICS = os.path.join(COUT, "ics"); os.makedirs(ICS, exist_ok=True)
con = sqlite3.connect("file:/tmp/cal/Calendar.sqlitedb?mode=ro", uri=True)
cals = {r[0]: (r[1] or f"calendar-{r[0]}") for r in con.execute("SELECT ROWID, title FROM Calendar")}
events = []
for r in con.execute("""SELECT summary, description, start_date, end_date, all_day, calendar_id,
                        url, UUID, entity_type, due_date, completion_date, creation_date
                        FROM CalendarItem WHERE summary IS NOT NULL"""):
    events.append({"summary": r[0], "description": (r[1] or "")[:2000], "start": ts(r[2]),
                   "end": ts(r[3]), "all_day": bool(r[4]), "calendar": cals.get(r[5], str(r[5])),
                   "url": r[6] or "", "uid": r[7] or "", "entity_type": r[8],
                   "due": ts(r[9]), "completed": ts(r[10]), "created": ts(r[11])})
con.close()
events.sort(key=lambda e: e["start"] or e["due"] or "")
json.dump({"count": len(events), "calendars": sorted(set(cals.values())), "events": events},
          open(os.path.join(COUT, "calendar_export.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def esc(s): return (s or "").replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
def icsdt(s, allday):
    if not s: return None
    d = s.replace("-", "").replace(":", "").replace(" ", "T")
    return d[:8] if allday else d
by_cal = {}
for e in events:
    if not e["start"]: continue
    by_cal.setdefault(e["calendar"], []).append(e)
for cal, evs in by_cal.items():
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MacExport//Claude//EN",
             f"X-WR-CALNAME:{esc(cal)}"]
    for e in evs:
        lines += ["BEGIN:VEVENT", f"UID:{e['uid'] or id(e)}", f"SUMMARY:{esc(e['summary'])}"]
        s = icsdt(e["start"], e["all_day"]); en = icsdt(e["end"], e["all_day"])
        if e["all_day"]:
            lines.append(f"DTSTART;VALUE=DATE:{s}")
            if en: lines.append(f"DTEND;VALUE=DATE:{en}")
        else:
            lines.append(f"DTSTART:{s}")
            if en: lines.append(f"DTEND:{en}")
        if e["description"]: lines.append(f"DESCRIPTION:{esc(e['description'])}")
        if e["url"]: lines.append(f"URL:{esc(e['url'])}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    safe = re.sub(r'[\\/:*?"<>|]', "_", cal)[:60]
    open(os.path.join(ICS, safe + ".ics"), "w", encoding="utf-8").write("\r\n".join(lines) + "\r\n")
print(f"CALENDAR: {len(events)} events, {len(by_cal)} ics files")

# ---------------- REMINDERS ----------------
ROUT = os.path.join(GD, "Reminders Export 2026-06-11"); os.makedirs(ROUT, exist_ok=True)
con = sqlite3.connect("file:/tmp/rem/reminders.sqlite?mode=ro", uri=True)
try:
    lists = {r[0]: r[1] for r in con.execute("SELECT Z_PK, ZNAME FROM ZREMCDBASELIST")}
except Exception:
    lists = {}
rems = []
for r in con.execute("""SELECT ZTITLE, ZNOTES, ZCOMPLETED, ZCOMPLETIONDATE, ZCREATIONDATE, ZDUEDATE, ZFLAGGED, ZLIST
                        FROM ZREMCDREMINDER"""):
    rems.append({"title": r[0] or "", "notes": r[1] or "", "completed": bool(r[2]),
                 "completed_at": ts(r[3]), "created": ts(r[4]), "due": ts(r[5]),
                 "flagged": bool(r[6]), "list": lists.get(r[7], str(r[7]))})
con.close()
rems.sort(key=lambda x: (x["completed"], x["due"] or "9999"))
json.dump({"count": len(rems), "reminders": rems},
          open(os.path.join(ROUT, "reminders_export.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
md = ["# Напоминания (Apple Reminders)", f"\nВсего: {len(rems)}\n"]
cur = None
for r in rems:
    if r["list"] != cur:
        cur = r["list"]; md.append(f"\n## {cur}\n")
    box = "x" if r["completed"] else " "
    extra = f" 📅 {r['due'][:16]}" if r["due"] else ""
    extra += " 🚩" if r["flagged"] else ""
    md.append(f"- [{box}] {r['title']}{extra}")
    if r["notes"]: md.append(f"    - {r['notes'][:300]}")
open(os.path.join(ROUT, "Reminders.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print(f"REMINDERS: {len(rems)} items")
