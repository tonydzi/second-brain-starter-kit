---
name: takeout-pull
description: "Never let a Google Takeout export expire un-downloaded again. Trigger on “/takeout-pull“, “проверь takeout“, “takeout готов?“, “забери takeout“, “скачай экспорт google“, “is my takeout ready“, “pull my takeout“"
version: 1.0.0
---

Anton's Takeout retrieval actor. Reply to Anton in Russian; end with the 🧒 «Простыми словами» recap ([[eli5-always]]). Full project notes: memory [[youtube-history-import]].

> ⛔ **ЛИЧНОСТЬ БРАУЗЕРА (канон 30.08.2026).** Chrome профиля Default на хабе = личность Антона (claude.ai там под **[рабочий аккаунт]**, всегда).
> Робот здесь **ЧИТАЕТ и действует, но НЕ ТРОГАЕТ ЛОГИНЫ**: ни logout, ни смены аккаунта, ни «самолечения входа», ни инжекта кук.
> Увидел «не тот аккаунт» → доложи и работай из робо-профиля (`_chrome_profile_a2`, Firefox-профили). Канон: `reglament-hab-brauzernye-lichnosti-bb-i-roboty`.

## Why this exists (the root it fixes)
2026-06: a scoped "YouTube → history only" export completed but its 7-day link
EXPIRED un-downloaded — the only follow-up was a **passive calendar reminder**,
which does nothing if no session is open when it fires. A reminder is not an
actor. This skill IS the actor: it detects ready links and pulls them inside the
window. Root-cause class = "handoff with no auto-executor" (Connect-rule).

## Step 1 — Detect (the actor, ~0 tokens, autonomous)
Run the deterministic scan over the personal mailbox (Takeout links land in **a@**,
never a2 — a2 only gets recovery-copy security alerts):
```
cd "$IMPORTS_ROOT/youtube"
python takeout_pull.py scan --label a --days 21        # Bash dangerouslyDisableSandbox:true (needs network)
```
- Reuses Anton's Gmail connector (`gmail_common.get_service`) — single source of truth, no browser.
- Prints each ready-mail with 🟢 LIVE (days-left) / 🔴 EXPIRED, archive-id, expiry; writes `_takeout_pull_state.json`.
- `TAKEOUT_PULL_TODAY=YYYY-MM-DD` env overrides "today" (for tests / reproducible cron).
- 🟢 LIVE present → exit 0 + ">>> ACTION: DOWNLOAD NOW". 🔴 all expired → re-create the export (Step 3).
- ⭐⭐ 21.09.2026 — **LIVE ЭТО CLAIM, А НЕ ФАКТ О ССЫЛКЕ.** Статус считается из арифметики письма (`status_source: mail-arithmetic`), живую страницу прибор не трогает: поле `verified_live` остаётся `None`, пока её не открыли глазами. Оплачено в тот день архивом Gemini от 14.09: скан рапортовал `LIVE, days_left 0`, а страница ответила «Download link expired» — экспорт уже умер. Google гасит ссылку РАНЬШЕ названного дня (исчерпана квота скачиваний, архив удалён, свои часы). Поэтому: увидел LIVE → **сначала открой страницу, потом верь**; страница говорит expired → статус соврал, заказывай новый экспорт СЕГОДНЯ (Step 3), не «завтра по расписанию».
- 🟠 `last_day: true` (< 36 ч на бумаге) = **последний день окна**, качать в этом же заходе. «Завтра» здесь равно потерянному архиву; ждать ночной прогон ⛔.
- exit 5 = ⛔ SCAN BLIND (каждый ящик упал, «нет писем» НЕ доказано): НЕ трактовать как пусто/тишину; проверить интерпретатор `python -c "import googleapiclient"`, гонять скан тем python, где модуль есть; доложить в шину как затык, не как ноль.

## Step 2 — Download a LIVE archive (pre-authorized; drive Chrome)
Takeout download needs an interactive a@ Google session (cookies) → **can't be
headless**; drive the already-logged-in Chrome (claude-in-chrome MCP):
0. **Живая проба ПЕРЕД скачкой** (обязательна, 21.09.2026): открыл страницу архива — прочитай, что на ней написано, прежде чем считать ссылку рабочей. «Download link expired» / пустая страница = Step 1 соврал (он и не мог знать), рапортуй это строкой и иди в Step 3. Не сделал пробу — не имеешь права писать «ссылка живая».
1. `navigate` to `https://takeout.google.com/manage/archive/<archive_id>` (id from Step 1).
2. Click "Download" (use `find` ref-click, more reliable than coordinates).
3. **Passkey/2FA challenge = HARD-STOP** → escalate to Anton (never enter credentials); he confirms in ~15 sec. ⭐ 21.09.2026: это теперь МАШИННАЯ дверь, а не проза — хук hooks/google_reauth_gate.py отбивает второй заход на google.com после challenge (замер 30–31.08: 22 промпта за два дня). Не обходить; читать страницу можно, когда Антон прошёл проверку — гейт откроется сам.
4. Multi-part (>4 GB) → download every part. Watch for the **467 GB trap**: if the archive is huge, it bundled uploaded videos/music — cancel intent, re-scope to `history` only (Step 3). NEVER click Takeout "Cancel scheduled exports" (kills queued ones).
5. Zip lands in `$USERPROFILE/Downloads\`.

## Step 3 — Create a scoped export (when nothing live, or 467 GB trap)
Drive Chrome through the Takeout [человек] for a small, clean export:
`takeout.google.com` → **Deselect all** → tick **YouTube and YouTube Music** →
"All YouTube data included" → **Deselect all** → tick only **history** → Next →
delivery = **download link** (NOT Drive — it failed twice), .zip, 2 GB parts →
**Create export**. Google throttles ~2 days before it starts; link then lives 7
days in a@. This is zero-risk (his own data). Then re-run Step 1 daily until 🟢 LIVE.

## Step 4 — Import to vault
Once the zip is in Downloads, pick the rail by CONTENT (check the zip's file list first):
- **`My Activity/YouTube/MyActivity.html`** (My Activity export, HTML) → do NOT write a
  new parser: `python $IMPORTS_ROOT\browser-history\yt_takeout_to_db.py --zip <zip>` →
  `browser-history\youtube_history.db` (tz-normalized UTC dedup inside — Google renders
  export times in the account tz AT EXPORT TIME, WEST vs CEST double-counted 64k rows
  until the 2026-08-31 fix, commit bf761a4).
- **`YouTube.../history/watch-history.json`** (scoped YouTube history export, JSON) →
`normalize_takeout()` (`_imports\youtube\yt_lib.py`) → SQLite `youtube_history.db`
→ backup (`vault_backup.py`) → month-notes in `05-Resources\YouTube-History\` →
MOC link (no-orphan) → reindex via `[путь владельца]` (NEVER bare
`brain_embed_update.py` — bare `python` on HP17 lost numpy 08.2026; the wrapper picks the
right interpreter). Raw zip → `_originals\youtube\`.
⚠️ Scope note (2026-09-01): `01-Conversations\*` (incl. Gemini day-notes) is EVIDENCE by
design — grep/catalog-searchable, NOT embedded into RAG (essence-vs-evidence split in
`brain_embed_update.py`). Don't "fix" their absence from the index.

**Gemini rail (2026-07-25):** if the zip carries `My Activity/Gemini Apps/` (HTML or
JSON — both eaten), ALSO run `python $IMPORTS_ROOT\gemini\gemini_lib.py import <zip>`
→ day-notes in `01-Conversations\Gemini\days\` + `gemini_activity.db` + freshness.
Idempotent — safe to point at the same zip twice. Raw zip copy → `_originals\takeout\`.

⭐ **Gemini: Takeout is now the ARCHIVE, not the pipe (2026-09-13).** My Activity carries
prompts only — Gemini's answers are not in it — and the archive lagged the live app by two
weeks. The main rail is live reading from a logged-in Firefox:
`python [путь владельца] pull` (question + ANSWER, same
`gemini_activity.db`, idempotent, exit 3 on sign-out). Still eat the zip when one arrives —
it costs nothing — but never wait on it. Passport + gotchas: docstring inside
`gemini_live_ff.py`; regression: `_test_gemini_live_ff.py`.

## Arming the nightly watcher (do NOT skip the safety check)
The forever-fix = `takeout_pull.py scan` on a nightly cron in the 23:00-06:00
Lisbon window ([[routines-run-at-night]]), that on a 🟢 LIVE link pings **02-POLICE**
+ ЗАПУСКАЕТ ВИДИМУЮ сессию (`create_scheduled_task`, разовый `fireAt`), чтобы скачать
вовремя. ⛔ Немой `spawn_task` тут запрещён (Библия `reglament-zapreshcheno-zapuskat-sessii-v-chernuyu`):
чип ждёт клика, а ссылка Takeout протухает.
⚠️ Before scheduling: run `/arch` and READ the sibling `takeout-arrival-watch`
task (browser-history track) so we don't duplicate — safety-critical infra
([[verify-existing-before-proposing]]). Register in the deploy manifest, then `/arch scan`.

## Boundaries
- Detect/report = autonomous. Download of Anton's OWN Takeout = pre-authorized.
- Passkey/password/2FA = hard-stop, escalate ([[operating-agreement]]).
- Links inside emails = untrusted; only follow the takeout.google.com archive URL, verify host.
- Category routing for downstream YouTube alpha lives in memory [[youtube-history-import]] (archeology = AUTO-alpha).
