---
name: x-post
description: >
  Publish a VETTED post/tweet to an X (Twitter) account through the owner's real logged-in
  Chrome (live-tab, low-ban-risk path), rate-guarded and draft-first. Trigger on "/x-post",
  "tweet this", "post to X". Counts length the way X does (every link = 23 chars) and refuses
  over-limit texts instead of silently truncating.
license: MIT
---

# /x-post — пост в X с аккаунта Антона (Chrome, draft-first)

**Зачем.** EN-тизеры (/episode) до сих пор оседали черновиками — не было постера в X. Тот же безопасный паттерн, что /fb-post: живая залогиненная вкладка, никакого headless.

## 0. Предохранитель (обязательно)
```bash
python "$USERPROFILE/.claude/scripts/_shared/social_guard.py" check x --text "<финальный текст>"
```
`BLOCKED` (exit 3) → СТОП, доложи (лимит 6/день или дубль). Не обходи.

## 1. Текст (голос Антона, Opus)
Бери готовый черновик (episode teaser EN / intention-lane) или пиши на Opus. Один твит ≤280 символов — посчитай ДО браузера; длиннее → тред (каждый твит ≤280, нить через reply) или предложи Антону сократить.

## 2. Tier-2 gate (draft-first)
Покажи финальный текст (+ разбивку треда, если тред) → жди явного `+`. Без «+» ничего не публикуется.

## 3. Браузер (Claude-in-Chrome, живая вкладка)
> Браузерная работа — локально на этой машине; окно вперёд не тащить.
> ⛔ IP-гейт (anton 16.07): постинг в X/соцсети с бан-риском — ТОЛЬКО с хаба `HUB-1` (постоянный IP). На другой машине НЕ постить — задачу текстом на хаб. Канон: `reglament-ip-sensitive-deystviya-tolko-s-haba`.
1. `list_connected_browsers` → нет расширения → блок, скажи Антону (не падать в Playwright).
2. Вкладка `x.com`. **Сверь залогиненный handle** (аватар/меню профиля) = **@Tony_Stef_** из реестра. Другой аккаунт → СТОП, спроси. Не залогинен → блок (логин/2FA не трогаем в X — checkpoint-риск).
3. Композер: `find` «post composer / What's happening». Введи текст (`form_input`). **Кнопку Post не жми** до выполненного гейта §2.
4. После `+` — Post. Тред: после первого твита кнопка «+» в композере / reply на свой твит.
5. Скриншот опубликованного + URL твита (клик по timestamp → адресная строка) = доказательство.

## 4. Зафиксируй (ПОСЛЕ успешной публикации)
```bash
python "$USERPROFILE/.claude/scripts/_shared/social_guard.py" record x --text "<текст>"
```
Доклад: ссылка + скрин + «сегодня x N/6».

## Стоп-краны
- Любой checkpoint/captcha/«unusual activity» X → немедленно СТОП, доложи, ноль ретраев.
- Не публиковать идентичный текст повторно; не постить чужими аккаунтами.
- Ссылки в тексте — только живые и наши (link-safety).

## Связанное
`/fb-post` (образец паттерна) · `/tg-post` · `/episode` (тиры: teaser EN → X) · гейт `scripts\_shared\social_guard.py` · реестр `00-System\Channels-Registry.md`.
