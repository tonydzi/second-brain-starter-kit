---
name: peer-export
description: >-
  Rebuild the scrubbed "PaloAlto AI Research Lab Knowledge" export of Anton's PRIVATE vault for
  external advisors/peers — classify every file (SHARE/SCRUB/NEVER/JUDGE/MANUAL) → build the core →
  scrub secrets → mask email/phone → fix links → verify the copy is clean. Idempotent re-run for the
  next advisor cohort, so a refresh is one command instead of re-dictating five 300–500-word role
  briefs. Trigger on "/peer-export", "обнови экспорт для внешних", "пересобери PaloAlto AI Research
  Lab Knowledge", "scrubbed export волта", "подключаем внешнего advisor — собери пакет", "share our
  system with X". DISTINCT from obsidian-ingest (ingests INTO the private vault — opposite direction)
  and dedup (finds duplicates). ⛔ PUBLISH (git init / GitHub / invites) is Tier-2 → Anton's explicit
  "+". ⚠️ CONSUMER-FIRST: build the export only once a real NAMED advisor has said yes (Connect rule:
  no consumer = built-into-the-void). macOS follower.
---

# /peer-export — scrubbed-пакет волта для внешних advisors

> 🧒 **When reporting to Anton:** end with a child-simple «Простыми словами» recap.

Пересобирает чистую (allowlist + скраб секретов) копию приватного волта в отдельном корне для внешних. Кодирует один раз то, что раньше диктовалось заново 5 брифами: политику allowlist, словарь красных флагов, порядок сборки, гейт «счётчик=счётчик». Детерминированные скрипты + Sonnet-судьи только на спорном остатке.

## ⚠️ Сперва потребитель, потом сборка (Connect + AK-47)
Прежде чем запускать: **есть ли реальный named advisor, сказавший «да»?** Нет → не собирать полный пакет (это ровно «строим для потребителя, которого нет»). Есть → собрать под то, что нужно именно ему. Первый прогон S1–S5 (2026-07-07) дал 3479 файлов **без единого потребителя** — не повторять вслепую.

## Пути (реальные, на этом Маке)
- **Корень экспорта:** `/Users/<имя>/Obsidian/PaloAlto-AI-Research-Lab-Knowledge/` (вне синка приватного волта)
- **Приватный источник:** `~/Obsidian/Anton-Knowledge` (read-only при сборке)
- **Классификатор:** `~/CLAUDE-Mac-2019/audit-peer-export/peer_classify.py` → `classification.json` (+ `batches/judge-NN.json` для судей)
- **Скраб/сборка:** `~/CLAUDE-Mac-2019/peer-export-tools/`
- **Техстатус/счётчики:** `PaloAlto-AI-Research-Lab-Knowledge/EXPORT-STATUS.md`

## Запуск (идемпотентная пересборка — порядок ЖЁСТКИЙ)
```bash
cd ~/CLAUDE-Mac-2019/audit-peer-export
python3 peer_classify.py            # 1) вердикт каждому файлу → classification.json
#    JUDGE-остаток → Sonnet-судьи (claude -p --model sonnet), см. JUDGE-INSTRUCTIONS.md, кэш вердиктов
cd ~/CLAUDE-Mac-2019/peer-export-tools
python3 build_export.py             # 2) ядро (allowlist as-is)
python3 full_tail.py                # 3) 🟡 SHARE+SCRUB хвост по classification
python3 mask_email_phone.py         # 4) маскировать email/телефоны
python3 link_pass.py                # 5) починить вики-ссылки внутри экспорта
python3 scrub_scan.py               # 6) ⛔ ГЕЙТ: скан секретов — ДОЛЖЕН быть чист
```
DoD: `scrub_scan.py` = 0 находок **И** счётчики папок в `EXPORT-STATUS.md` совпадают до/после. Только тогда «собрано».

## ⛔ Публикация = Tier-2 (не автоматизируется этим скиллом)
`git init` → приватный GitHub → инвайты advisors — **только по явному «+» Антона** (наружу + необратимо). Скилл собирает и проверяет; кнопку «наружу» жмёт Антон. Флип-статус живёт в [[peer-export-lab-knowledge]].

## Скраб — что ловит гейт
Секрет-паттерны: `sk-`, `ghp_`, `xoxb`, `AKIA`, `-----BEGIN … PRIVATE KEY-----`, содержимое `secrets\`. Плюс folder-policy NEVER (CRM, личные темы, внешние источники) и маска email/phone. Ложно-отрицательный det-SHARE НЕ копируется вслепую — спорное идёт судьям/в MANUAL-доску.

## Грабли
- ⚠️ `det`-SHARE ≠ можно вслепую копировать (был ложно-отрицательный) → JUDGE/MANUAL остаток обязателен.
- ⚠️ «claimed-done без доказательства» уже случалось (аппендикс заявлял докопированный хвост, а на диске меньше) → всегда сверять счётчик на диске, а не верить логу.
- Судьи — на Sonnet (грунт, бесплатный бак), `ANTHROPIC_API_KEY` снят.

## Канон
Память [[peer-export-lab-knowledge]] · [[connect-rule-pipeline-ownership]] (named consumer) · [[credential-store]] (секреты вне экспорта) · правила [[always-archive-artifacts-to-vault]]. Связано [[hub-not-bottleneck-peers-self-serve]].
