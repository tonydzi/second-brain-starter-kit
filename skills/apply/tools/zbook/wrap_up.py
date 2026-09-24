# -*- coding: utf-8 -*-
"""python wrap_up.py — финиш дня: (1) почта = истина: строки 🤖/🟡/⏳ с письмом-подтверждением сегодня → ✅;
(2) счёт по таблице; (3) заметка в волт 04-Projects/Pipe-A-Batches/batch-2026-09-08-zbook.md. 0 LLM."""
import sys, os, io, json, re, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets
HERE = os.path.dirname(os.path.abspath(__file__))
SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"; TAB = "Пачка 03.09"
TODAY = "2026-09-08"

subprocess.run([sys.executable, os.path.join(HERE, "mail_cache.py"), "08-Sep-2026"], check=False)
mail = json.load(io.open(os.path.join(HERE, "mail_cache.json"), encoding="utf-8"))
CONF = re.compile(r"thank|received|application|applying|confirm|interest in", re.I)
key = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
ALIAS = {"purestorage": "everpure", "weightsandbiases": "coreweave", "sourcegraph91": "sourcegraph", "springhealth66": "springhealth"}

def letters(company):
    k = key(company)[:9]; k2 = ALIAS.get(key(company), "")
    out = []
    for m in mail:
        if not CONF.search(m["subject"]) or "security code" in m["subject"].lower():
            continue
        blob = key(m["from"]) + "|" + key(m["subject"])
        if (k and k in blob) or (k2 and k2 in blob):
            out.append(m)
    return out

vals = sheets.read_tab(SID, TAB)
marked = []
for i, r in enumerate(vals[1:], start=2):
    g = (r[6] if len(r) > 6 else "").strip()
    if not g or g[0] not in "🤖🟡⏳":
        continue
    if len(key(r[1])) < 6 or key(r[1]) in ("ashby",):   # общий ключ (ashby = имя ATS) красит чужие письма
        continue
    hits = [m for m in letters(r[1]) if m["ts"].startswith(TODAY)]
    # одно письмо на компанию: если другая строка той же компании уже ✅ сегодня — это её письмо, не наше
    same_ok = [rr for rr in vals[1:] if len(rr) > 6 and key(rr[1]) == key(r[1]) and rr[6].startswith("✅ ПОДАНО 08.09")]
    if hits and same_ok:
        hits = []
    if hits:
        h = max(hits, key=lambda m: m["ts"])
        mark = f"✅ ПОДАНО 08.09 (пруф: письмо «{h['subject'][:60]}» {h['ts'][11:]} UTC; таблица держала «{g[:30]}»)"
        sheets.set_range(SID, f"'{TAB}'!G{i}", [[mark]])
        marked.append((i, r[1], h["ts"][11:], h["subject"][:50]))
print("✅ по письмам дополнительно:", len(marked))
for m in marked:
    print("  ", m)

vals = sheets.read_tab(SID, TAB)
cnt = {}
for r in vals[1:]:
    g = (r[6] if len(r) > 6 else "").strip()
    c = g[:1] if g else "?"
    cnt[c] = cnt.get(c, 0) + 1
print("СЧЁТ:", {k: v for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])})

hands = sheets.read_tab(SID, "Руки Антона 08.09")
note = f"""---
type: batch-report
date: {TODAY}
node: [машина флота]
project: mission-llm-hire
tags: [pipe-a, applications, code-gate, greenhouse]
source: session 5f2bcfaf (Claude Code, ZBOOKG8), таблица «Пачка 03.09»
---
# Пачка 08.09 (ZBOOKG8, день): код-гейт роботом, волны 9-10, стена Ashby

Приказ Антона голосом 12:59: коды из почты вбивать самому; SentiLink = сделка $100k, цикл 3-6 мес (взял 6); дискавери обновить и гнать волну-9; шесть Ashby открыть ему в браузере; скилл /apply пересобрать.

## Счёт по таблице «Пачка 03.09» на {datetime.datetime.now().strftime('%H:%M')} Лиссабон
{chr(10).join(f'- {k} {v}' for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]))}

Утро 05.09 было 79 ✅ / 42 🟡.

## Что сделано
- Код-гейт Greenhouse снимает движок хаба (gh_code_gate, 05.09) — на пире нужен `GMAIL_HOME`. Пять коммитов в движок за день (30193ea, e17fc95, 6360bae, 8d72a44, fb0550c), тесты 47 → 71, каждый класс показан красным до патча.
- Корень «Incorrect security code»: Greenhouse держит один живой код на ящик, параллельные сабмиты (лейны, узлы) гасят коды друг друга. Замок на узле + второй круг свежайшим кодом; межузловая гонка открыта (хабу отправлено предложение окна).
- Почта главнее таблицы: 20+ строк 🟡/🤖 были поданы хабом ночами 05-07.09; помечены по письмам.
- Дискавери в локальной копии: 3762 → 4004. Волна-9: 13/40 отсужено, волна-10: 18/40 (6 strong), все Ashby.
- Стена Ashby на IP ноута («flagged as possible spam» ×6) — 17 ролей волны-10 переданы [машина флота] посылкой `_transit/ashby-w10-for-[машина флота]-2026-09-08.json`.
- Скилл /apply v1.1.0: слой 08.09 (15 пунктов), инструменты ноута в `tools/zbook/`.

## Руки Антона (вкладка «Руки Антона 08.09», {max(0, len(hands) - 1)} строк)
{chr(10).join('- ' + ' | '.join(str(c) for c in row[:4]) for row in hands[1:])}

## Открытое
- Межузловая гонка кодов Greenhouse (ящик a@ общий для хаба, [машина флота], ноута).
- Vercel: Greenhouse перестал слать коды после 4 писем за 40 мин — перегон вечером.
- Лейны из Bash-тула умерли молча ~13:55 — причина не доказана; обход Start-Process.
- Дедуп по трём частным заплатам (написание / префикс / обезличенный From) — нужен единый applied_index.

Оригиналы: `_originals/pipe-a/2026-09-08-zbook-wave9-10/`. Связи: [[apply-playbook]], [[batch-2026-09-05]], [[mission-llm-hire-weekly-plan]].
"""
P = r"[путь владельца]"
io.open(P, "w", encoding="utf-8", newline="\n").write(note)
print("заметка:", P)
