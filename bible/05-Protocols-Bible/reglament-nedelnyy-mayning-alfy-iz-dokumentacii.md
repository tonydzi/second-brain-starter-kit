---
title: "Раз в неделю майнить альфу из ВСЕЙ документации наших инструментов"
type: reglament
stage: distilled
source: claude-code-rules-intake
origin: anton
authored_by: hybrid
posted_by: "Claude (Fable 5)"
date_established: 2026-07-06
theme: ai-operations
applies_to: "Хаб-сессия / сервис doc-alpha-weekly; результат — Антону"
audience: both
status: active
tags: [регламент, документация, альфа, автоскан, рутина, changelog]
concept: "[[concept-bible-platinum]]"
priority: must
confidence: 0.9
---

**Правило (WHEN → DO):** Раз в неделю прочёсывать ВСЮ документацию/чейнджлоги инструментов, на которых мы работаем, находить новое и намайнивать «альфу» — конкретные фичи/изменения, применимые к НАМ. Это системная пара к реактивному [[reglament-proaktivno-predlagay-dr-kogda-doki-operezhayut-obuchenie]]: то ловит момент, это ловит регулярно.

**Зачем.** Прогресс продуктов опережает обучение LLM (корень — тот же двойной ложный «фичи нет» 2026-07-06). Без систематического скана мы узнаём о нужных фичах случайно и поздно. Антон дословно: «один раз в неделю проверять ВСЮ ДОКУМЕНТАЦИЮ и находить фишки и майнить АЛЬФУ из документации применительно к нам — нужен сервис сделать».

**Сервис (построен 2026-07-06):** `[путь владельца]`.
- `doc_sources.json` — курируемый список источников {name, url, why-us, fetch}. Расширяется по мере роста стека.
- `doc_alpha_watch.py` — детерминированная часть (0 токенов): `raw`-источники (плоский changelog, напр. Claude Code CHANGELOG) диффит построчно и выдаёт НОВЫЕ строки; `hash`/динамические HTML-страницы помечает «еженедельно перечитать» (в них нонсы → хеш флапает, честно не притворяемся, что детектим). Использует certifi (свежий trust-store, проверку НЕ отключаем).
- Задача `doc-alpha-weekly` (scheduled, Вс 05:42 Лиссабон) — суждение: гоняет скрипт, WebFetch'ит review-источники, RECALL нашего стека, майнит альфу (что·почему-нам·действие·уверенность), пишет дайджест `05-Resources\Doc-Alpha\doc-alpha-<дата>.md`, реиндексит, пингует Антона в чат 03 (Tier-2 → плюс 02 POLICE). Чистая неделя тоже репортится (молчание = инцидент).

**Стек на сегодня (что сканируем):** Claude Code (CLI+Desktop+Remote Control+tmux-ферма Маяка), VS Code (Tunnels на Маяк), Tailscale, Hetzner Cloud, OpenAI embeddings (RAG), Anthropic API/модели. Новый инструмент в обиходе → добавить источник в `doc_sources.json`.

**Границы / AK-47.** Детерминизм (фетч+диф) — код, 0 токенов; LLM только судит релевантность (грунт на Sonnet). Не плодить дубль-скрипты на каждый источник — один движок + список URL (generalize-after-third-repeat [internal]). Упавший источник = дефект (чинить URL/скрипт), не «ничего нового». Дом рутины — машинный слой (scheduled-task), Библия хранит правило.

Связано: [[reglament-proaktivno-predlagay-dr-kogda-doki-operezhayut-obuchenie]], negative-claims-need-live-verification [internal], evaluate-recurring-into-routine [internal], creator-watcher [internal] (тот же паттерн «watch → gate → волт», но для AI-креаторов).
