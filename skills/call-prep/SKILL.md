---
name: call-prep
description: "Бриф перед звонком: сперва БРОНЬ (Calendly → Google Calendar → Gmail-проекция Calendly в ящике bb), идентификация по email/телефону/TG из формы, и только потом волт/CRM/Telegram. Триггеры: /call-prep, подготовь к звонку, кто такой … звонок, у меня звонок с, brief me for the call. Тёзки не угадываем."
version: 1.0.0
---

# /call-prep — подготовь меня к звонку

> 🧒 Доклад Антону кончается блоком «Простыми словами» ([[eli5-always]]).

**Боль (14.09.2026):** «у меня звонок с каким-то Барри, кто он». Сессия пошла в волт+Telegram,
нашла 12 Барри и подготовила НЕ того. Верный лежал в ящике bb одним письмом Calendly
«New Event: [человек] [человек] - 20:30 Mon, 14 Sep 2026 - 1-on-1 with Tony» с email, телефоном,
TG-хендлом из формы и Meet-ссылкой. Антон: «первым делом календарь, потом почта; у нас есть ещё Calendly».

**Закон скилла:** имя без брони = НЕ идентификация. Сначала бронь → ключи (email · телефон · TG-хендл
из формы) → только по КЛЮЧУ ищем человека в волте/CRM/Telegram. Совпадение по имени не считается.

Пути: `VAULT=${OBSIDIAN_VAULT:-$HOME/Obsidian/Anton-Knowledge}`, `IMP=${IMPORTS_ROOT:-$HOME/Obsidian/_imports}`.

## Шаг 1. Двери брони — строго по порядку, первая живая даёт истину

### 1а. Calendly-коннектор (истина броней, аккаунт paloaltolab) — нужен Claude
`meetings-list_events` (окно сегодня−завтра) → `list_event_invitees` по event_uri → ответы формы (TG-хендл).
Проверка наличия: ToolSearch «calendly» / «meetings».
- **[машина флота] ([машина флота]), замер 14.09.2026:** ToolSearch «calendly meetings list_events invitees» и «+meetings» →
  коннектора НЕТ. Живёт на хабе. Нет коннектора → не стоп, иди дальше.

### 1б. Снимок Calendly для call_reminders
`python3 $IMP/crm-engine/call_reminders.py --calendly $IMP/crm-engine/reports/calendly-bookings.json`
(брифинг окна 24ч/1ч, время в поясе Антона и гостя; паспорт `~/.claude/scripts/docs/call-reminders.md`).
Снимок пишет тот, у кого есть Calendly MCP (рутина inbound-triage-daily, шаг 6а, на хабе).
Ключ связи бронь↔CRM = TG-хендл, который лид сам написал в форме.
- **[машина флота], замер 14.09.2026:** `--help` отвечает, но файла `reports/calendly-bookings.json` на узле НЕТ →
  дверь пустая. Проверь возраст файла (`pulled_at`), если он есть; старше суток = подсказка, не истина.

### 1в. Google Calendar [рабочий аккаунт]
`python3 $IMP/call-bot/gcal_events.py`
- **[машина флота], замер 14.09.2026:** `NOT AUTHORIZED: no calendar token for 'bb' — run: python gcal_auth.py bb`.
  Не авторизовано на [машина флота]. Сам не авторизую (нужен человек в браузере) — строка в «НЕ проверено».
  В живой сессии с коннектором Google Calendar (нужен Claude) — `list_events` по [рабочий аккаунт]@gmail.com, Europe/Lisbon.

### 1г. Gmail-проекция Calendly (ЖИВАЯ на [машина флота]) — рабочая лошадь
Брони Calendly приходят письмами в ящик **bb**. Bash с `dangerouslyDisableSandbox: true`:
```bash
cd ~/CLAUDE-Mac-2019/gmail
python3 gmail_check.py search "from:notifications@calendly.com <Имя> newer_than:30d" --label bb 2>/dev/null
python3 gmail_check.py search "from:notifications@calendly.com newer_than:7d" --label bb --max 10 2>/dev/null   # без имени
python3 gmail_check.py search "from:notifications@calendly.com [человек] <Имя> newer_than:30d" --label bb 2>/dev/null  # отмены
python3 gmail_check.py read bb <msgid> 2>/dev/null | python3 -c 'import sys,re,html;t=sys.stdin.read();t=re.sub(r"(?is)<(style|head|title)[^>]*>.*?</\1>"," ",t);t=re.sub(r"<br[^>]*>|</p>","\n",t);t=html.unescape(re.sub(r"<[^>]+>"," ",t));print("\n".join(l.strip() for l in t.splitlines() if l.strip()))'
```
Из текста берём: Invitee · Invitee Email · Text Reminder Number · Event Date/Time (UTC) · Location (Meet) ·
Invitee Time Zone · Description · Questions (роль + TG handle).
- Грабли: без `--label bb` поиск идёт по всем ящикам и один падает `invalid_scope` трейсбэком ПОСЛЕ вывода — не блокер,
  но с `--label bb` чисто. В zsh не пиши `===СЛОВО` в echo (=cmd-расширение).
- **[машина флота], замер 14.09.2026 (живой):** `search "calendly [человек] newer_than:30d"` → bb: 2 письма
  «New Event: [человек] [человек] - 20:30 Mon, 14 Sep» и «… 20:30 Tue, 15 Sep» (оба от 10.09, соседние дни = ДУБЛЬ-БРОНЬ);
  `read` + экстрактор дал Email, телефон, UTC-время, Meet-ссылку, пояс Eastern, TG-хендл. Отмен 0.
  Без имени за 7д: 5 писем (2 брони + recap/action item).

## Шаг 2. Правила брони
- **Тёзки** → не угадывать. Несколько кандидатов и нет брони → показать Антону список с ключами, не бриф.
- **Дубль-брони** (один гость на соседние дни / два слота) → флаг Антону первой строкой: какой настоящий, второй отменить?
- **Время** всегда тремя поясами: UTC · Лиссабон (Europe/Lisbon) · пояс гостя из формы.
- Письма «[человек]» / «Rescheduled» новее брони → бронь недействительна.

## Шаг 3. Только ПОСЛЕ ключей — кто это
Искать по email / телефону / TG-хендлу, не по имени:
```bash
grep -rli "<хендл>\|<email>\|<телефон без +>" "$VAULT/07-People" "$VAULT/04-Projects/crypto/Platinum-CRM/leads" 2>/dev/null
```
- Несколько карточек на одного человека (напр. `person-<имя>.md` + `person-<хендл>.md`) → склеить в брифе, флаг «дубль карточек».
- Telegram MCP (нужен Claude): `search_contacts <хендл>` и `get_history` по ВСЕМ 4 аккаунтам
  (`list_accounts`: [рабочий аккаунт] · tonydzi · [рабочий аккаунт] · [рабочий аккаунт]). Совпадение телефона в контакте с номером из формы = ✅ идентификация.
  Свежая переписка → «чего он хочет»; где он нам ОТВЕЧАЛ → с какого аккаунта писать ([[outbound-to-lead-all-channels]]).
- **[машина флота], замер 14.09.2026 (живой):** grep по хендлу → `person-[человек]-[человек].md` + `person-bpm002.md` (дубль) +
  CRM `leads/2023/[человек]-[человек].md` + `leads/2025/bpm002.md`; `search_contacts Bpm002` на [рабочий аккаунт] → контакт с тем же
  телефоном, что в форме Calendly = идентичность доказана.

## Шаг 4. Бриф (формат)
1. **Когда / ссылка / контакты** — время UTC · Лиссабон · гость; Meet; email; телефон; TG; флаги (дубль-бронь, отмена).
2. **Кто это** — роль, компания, откуда знаем, сколько звонков было (из карточек, со ссылками).
3. **Чего он хочет** — по свежей переписке и полю Description/Questions формы.
4. **Что мы уже для него делали** — прошлые звонки, ФА, интро, обещания (`/promises`, CRM).
5. **Как вести звонок** — 3 вопроса · что взять с него (CTA-чек-лист) · наш ask · следующий шаг до конца звонка.
6. **Риски** — тёзки, дубль-карточки, «beware of fakes», стухший контекст, деньги/юр.
7. **Проверено / НЕ проверено** — каждая дверь строкой: прошла / пусто / не авторизована (почему).

После звонка → `/fa` (фоллоуап голосом Антона). Лида нет в CRM или карточка без источника → дописать по [[crm-lead-full-provenance]].

## Safety
Read-only: ничего не шлёт, не бронирует, не отменяет. Отмена дубль-брони = решение Антона (исходящее гостю).
Личные данные гостя — только в бриф Антону, не в волт-заметки общего доступа и не наружу.

## Потребитель
- **Антон в живой сессии** — «у меня звонок с X, кто это».
- **Рутина inbound-triage-daily, шаг 6** (хаб) — бриф на брони окна 24ч после снимка Calendly.
- **/agenda** — у встречи в календаре без контекста → указатель на /call-prep.
- **/local-to-call** — после брони пре-колл-бриф делает /call-prep.
- **/fa** — после звонка берёт бриф как контекст.

Годится любому агенту: шаги 1б/1в/1г/3-grep = наши скрипты; шаги 1а, 3-Telegram, Calendar-коннектор — нужен Claude.
