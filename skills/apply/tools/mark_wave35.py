#!/usr/bin/env python3
"""Отметка исходов волны 35 ([машина флота], Ashby, 08.09.2026) в реестре Трубы А.

Истина исходов — журнал воркфлоу `journal.jsonl` прогона wf_9e8153d3-bd7, не память агента.
MAP статусов: applied→applied · closed→closed · blocked-question→blocked-question ·
blocked-captcha→blocked-captcha · error→blocked-error.
Побочно пишет `w35_applied_urls.json` (список УСПЕШНЫХ подач) — постоянный дом журнала,
из которого `restore_applied.py` считает подачи; scratchpad стирается, tools/ переживает.

Вход: journal.jsonl прогона. Выход: записи в Sheets через mark_row.mark + w35_applied_urls.json.
Кто дёргает: сессия волны 35, один раз. Рельса: детерминированный python, 0 LLM.
Updated: 2026-09-08.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import mark_row

DATE = "2026-09-08"
MAP = {"applied": "applied", "closed": "closed", "blocked-question": "blocked-question",
       "blocked-captcha": "blocked-captcha", "error": "blocked-error"}
JOURNAL = ("/Users/<имя>/.claude/projects/-Users-anton-Library-CloudStorage-GoogleDrive-"
           "dzyatkovskiy-a-gmail-com-My-Drive---Claude-[машина флота]/190a8859-0456-4cf5-b341-da29febfa4bb/"
           "subagents/workflows/wf_9e8153d3-bd7/journal.jsonl")


def main():
    results = []
    for line in open(JOURNAL, encoding="utf-8"):
        rec = json.loads(line)
        if rec.get("type") == "result":
            results.extend(rec["result"].get("results", []))
    if not results:
        print("⛔ журнал не дал ни одного исхода — отмечать нечего")
        return 2

    applied, counts = [], {}
    for r in results:
        status = MAP.get(r["outcome"], "blocked-error")
        counts[status] = counts.get(status, 0) + 1
        mark_row.mark(r["url"], status, DATE)
        print(f"  {r['company']:14} {r['outcome']:18} → {status}")
        if status == "applied":
            applied.append(r["url"])

    out = os.path.join(HERE, "w35_applied_urls.json")
    json.dump(applied, open(out, "w"), indent=1)
    print(f"\nитог: {counts}")
    print(f"журнал подач: {out} ({len(applied)} url)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
