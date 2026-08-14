---
name: fb-post
description: >
  Publish a VETTED post to a personal Facebook wall through the owner's real logged-in Chrome
  (live-tab automation = low-ban-risk path), rate-limit-guarded and draft-first. Trigger on
  "/fb-post", "publish to facebook", "post this to my wall". The text comes from the content-
  factory drafts in the owner's authorial voice; the skill handles the mechanics: paste, verify
  what's actually in the composer, confirm after reload.
license: MIT
---

# /fb-post — опубликовать пост на стену Антона (безопасно, draft-first)

**Зачем.** Контент-фабрика и FB-дневник уже ПИШУТ посты голосом Антона, но черновик до сих пор оседает в Saved/волте. Не хватало только «кнопки публикации». Этот скилл закрывает её — и делает это самым безопасным способом (действуем в живой залогиненной вкладке Chrome, а не headless-ботом), с жёстким счётчиком объёма.

**Главные правила (из Deep-Research #32):**
- Публикация = **OUTBOUND + PUBLIC = Tier-2** → финальный текст показываю Антону и жду явного `+` (или он сам жмёт «Опубликовать»). Никогда не публикую молча.
- **Голос Антона = Opus.** Текст беру из готового черновика (`content-factory`, `facebook-diary`, `episode`) или пишу на Opus. Не выдумываю новый голос, не даю Sonnet писать авторское.
- **Объём низкий:** `fb_guard` режет на ≤8 постов/день. Не дублировать один и тот же текст (спам-флаг).

---

## 0. Предохранитель ПЕРЕД браузером (обязательно)
```bash
python "$USERPROFILE/.claude/scripts/fb_guard.py" check post
```
- `OK post (...)` → можно продолжать.
- `BLOCKED post: ...` (exit 3) → СТОП. Скажи Антону, что дневной лимит постов исчерпан, предложи запланировать на завтра. Не обходи.

## 1. Текст (голос Антона, Opus)
1. Если Антон дал готовый черновик — бери его. Если просит «оформи из X» — собери на Opus в его голосе (см. `fb-diary-voice`: вплетённо, с самоиронией, ~4000 знаков для дневникового; короче для анонса).
2. Покажи Антону **финальный текст** и спроси `+`. Это Tier-2 gate — без явного «да» дальше не идём.

## 2. Браузер (Claude-in-Chrome, живая вкладка)
> Браузерная работа — строго ЛОКАЛЬНО на этой машине (Антон за хабом). Не тащить окно Claude вперёд.
> ⛔ IP-гейт (anton 16.07): постинг/комментинг FB — ТОЛЬКО с хаба `HUB-1` (постоянный IP). Ты на другой машине? НЕ постить отсюда — задачу текстом на хаб (шина/03). Канон: `reglament-ip-sensitive-deystviya-tolko-s-haba`.

1. Проверь, что Chrome-MCP подключён: `mcp__Claude_in_Chrome__list_connected_browsers`. Если нет — попроси Антона открыть Chrome с расширением (не падай в Playwright).
2. Открой/выбери вкладку `facebook.com` (он уже залогинен — НЕ трогаем логин/пароль). Если не залогинен — это блок, скажи Антону.
3. Найди композер: `mcp__Claude_in_Chrome__find` запросом «What's on your mind / Что у вас нового — create post box». Кликни, чтобы открыть окно создания поста.
4. Введи текст в поле композера (`form_input` по ref из `find`). **НЕ нажимай «Опубликовать»** сам, пока не выполнен Tier-2 gate из §1.
5. После явного `+` Антона — нажми кнопку «Опубликовать»/«Post» (или попроси Антона нажать, если он рядом и хочет сам). ⚠️ Диалог двухшаговый: compose → «Next» → Post settings → «Post». Сделай скриншот результата (`computer` screenshot), чтобы Антон ВИДЕЛ, что пост ушёл.
6. **Футер 1-м комментарием** (правило §7.7, тело поста без ссылок): открой опубликованный пост → поле «Comment» → блоки B+C+E из `_imports\content-factory\_STYLE-footer.md` (только живые ссылки). ⚠️ Enter отправляет коммент — переносы строк только Shift+Enter.
7. **Селф-лайк** (правило Антона 05.07: «первый лайк всегда тяжело ставить»): поставь Like на свой пост сразу после футер-коммента. Штатный шаг, отдельно не спрашивать.
8. Грабли композера: первый клик может попасть в Stories (лента сдвигается при ленивой подгрузке) — после навигации подожди ~2с, скриншот, потом клик по свежим координатам.

## 3. Зафиксируй в счётчике (ПОСЛЕ успешной публикации)
```bash
python "$USERPROFILE/.claude/scripts/fb_guard.py" record post
```

## 4. Доложи
Одной строкой: что опубликовано + ссылка/скрин + «сегодня постов N/8».

---

## Стоп-краны (account safety)
- Любое предупреждение FB (checkpoint, «вы делаете это слишком часто», запрос подтверждения личности) → **немедленно СТОП**, доложи Антону, НЕ ретрай-спам (ретраи и есть путь в бан).
- Не публиковать идентичный текст повторно.
- Не трогать логин/пароль/2FA — если не залогинен, это блок для Антона.

## Связанное
- `/fb-reply` — ответы на комментарии (Фаза 1, тот же guard).
- Движок-счётчик: `~/.claude/scripts/fb_guard.py` (общий на post/reply/dm).
- Тексты: `content-factory`, `facebook-diary`, `episode`, голос — `fb-diary-voice`.
- Канон: Decision Memo 2026-06-28 (набор FB-скиллов), `chrome-autonomy-self-drive`, `browser-work-on-peers-not-hub`.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
