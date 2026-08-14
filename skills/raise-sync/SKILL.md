---
name: raise-sync
description: >
  ACTIVE recovery when machines can't see each other over the file-sync network — the "raise the
  sync" runbook as one command. Establishes ground truth at the hub (live sync API, NOT memory
  or one peer's claim), publishes the hub's verified device ID over the messaging rail, and
  guides each disconnected peer to re-pair. Trigger on "/raise-sync", "sync is down", "machines
  can't see each other".
license: MIT
---

# /raise-sync — поднять синк, когда машины не видят друг друга

Активный runbook на ЧП «потеря синка» (полный канон + почему = Библия [[reglament-chp-poterya-sinka-mezhdu-mashinami]]). Принцип: **истину устанавливаем по ЖИВОМУ API хаба, а не по памяти и не по словам одного пира** (пир может держать устаревшую запись — так ноут однажды уверенно звал «верни 2KPYBY4», что сломало бы Нина).

Аккаунт/группа шины и ключ — из `~/.claude/tg_bus.json` (Telegram) и env `STGUIAPIKEY` (Syncthing API). Хаб LAN = `10.0.0.10:22000`.

## Шаг 0 — Детект (где болит)
```bash
APIKEY=$(powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('STGUIAPIKEY','User')" | tr -d '\r')
curl -s -H "X-API-Key: $APIKEY" "http://127.0.0.1:8384/rest/system/connections" | python -c "import sys,json;d=json.load(sys.stdin);[print(k[:7], v.get('connected'), v.get('address')) for k,v in d.get('connections',{}).items()]"
```
(Или быстрый красный/зелёный — скилл `/sync-check`.) Кто `connected:false` = отвалился.

## Шаг 1 — Истина НА ХАБЕ (факты, не память)
```bash
# myID хаба (должен совпасть с machines.json HUB-1 = EEAETB6...)
curl -s -H "X-API-Key: $APIKEY" "http://127.0.0.1:8384/rest/system/status" | python -c "import sys,json;print('myID=',json.load(sys.stdin)['myID'])"
# демон серверит РЕАЛЬНЫЙ волт? (пути на %VAULT_ROOT%\..., данные есть)
curl -s -H "X-API-Key: $APIKEY" "http://127.0.0.1:8384/rest/config/folders" | python -c "import sys,json;[print(f['id'],'->',f['path']) for f in json.load(sys.stdin)]"
```
- Если `myID` НЕ совпадает с реестром / папки пустые → демон поднят на ЧУЖОМ home: **чини home (тот, где родной cert.pem + папки), НЕ пере-паривай пиров на временный ID.**
- Если `myID` совпадает и папки реальные → личность легитимна, проблема на стороне пиров (устаревшая запись хаба).

## Шаг 2 — Сверка с реестром (детект дрейфа)
Сравни live `myID` с `_machine-bus/machines.json` (поле `deviceID` хаба). Расходится без явной миграции = подозрение; совпадает = публикуем как канон.

## Шаг 3 — Опубликуй VERIFIED Device ID хаба в шину (out-of-band пруф)
Через Telegram-MCP (`chat_id`/`account` из `tg_bus.json`):
```
🤖 [<хаб> -> ALL] hub <имя> = <EEAETB6-полный-ID>, addr tcp://10.0.0.10:22000. VERIFIED живым API (серверит весь волт). Пиры: впишите этот ID, удалите устаревший, рестарт демона, рапорт connected.
```
Это снимает Tier-2-гейт пира («вписать чужой ID = отдать волт») — пир получил доказательство со стороны самого хаба.

## Шаг 4 — Веди пиров (они чинят у себя; я не могу реконфигурить чужой Syncthing)
Каждому disconnected: впиши хаб = verified ID, верный адрес, **удали устаревший ID** (частая грабля — фантомный старый → «Hello → forcibly closed / unknown device»), рестарт демона штатным сторожем → рапорт `🤖 [пир -> хаб] connected` или что мешает.

## Шаг 5 — Проверь
Повтори Шаг 0: все `connected:true`, бэклог качается (`needFiles` падает). Доложи Антону состав.

## Анти-грабли (выучено кровью 2026-06)
- НЕ верь ОДНОМУ пиру в диагнозе идентичности — источник истины = живой API хаба.
- НЕ откатывай хаб на старый ID, если другой пир уже работает на новом (сломаешь работающего).
- Сторож с «зависанием» → сперва проверь слой видимости (логи/ключ/403), а не ядро.

## Связанное
- `/sync-check` — read-only статус (детект). Этот скилл — РЕКАВЕРИ.
- Dead-man-switch `sync_monitor.py` (задача «Claude Sync Monitor») пингует Антона при отвале пира → часто `/raise-sync` стартует ПО его пингу.
- Канон: [[reglament-chp-poterya-sinka-mezhdu-mashinami]], [[machine-bus-telegram-rail]], [[syncthing-v21-gotchas]].

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
