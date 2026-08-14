---
name: content-mine
description: >
  Manual run of the CONTENT MINER — read through recent Claude Code sessions and capture
  content-worthy moments as DRAFTS into the publishing funnel (draft-first, nothing goes out).
  Trigger on "/content-mine", "mine sessions for content", "what in our sessions deserves a
  post". Thin wrapper over the miner engine: 0-token detector → taste judge → capture into the
  drafts queue.
license: MIT
---

CONTENT_MINE — sessions → funnel drafts (draft-first, вкус за мной)

ЦЕЛЬ: намайнить из наших сессий Claude Code контентно-достойные МОМЕНТЫ и сложить их ЧЕРНОВИКАМИ в воронку контент-фабрики. Публикация — только «+» Антона через /episode. Ничего наружу.

Антон делегировал вкус «что достойно контента» мне (2026-07-08). Не переспрашиваю, что добавить — решаю сам.

ПУТИ:
- Движок: `$IMPORTS_ROOT/content-factory\content_miner.py` (семья alpha-extraction / intention_mine; читает живой пул `vault_sessions`).
- Воронка (интейк): `content-factory\triage\posts.jsonl` (+ `posts.md`), `source_kind: session`. Пишет через `voice_triage.py append` (дедуп/upsert).
- Дайджест: `content-factory\miner\candidates\cand-latest.md`. Леджер: `miner\captured.jsonl`.

ШАГИ:
1. СКАН (детерминированно, 0 токенов). По умолчанию свежее: `python content_miner.py mine --days 7`. Долг/весь архив: `mine --all --operator Anton --cap 150`. Флаги: `--day YYYY-MM-DD`, `--operator all`, `--cap N`. Запомни `OVER_THRESHOLD` и `OUT`.
2. Пусто (SESSIONS=0 / OVER_THRESHOLD=0) → скажи «свежих достойных моментов нет» и стоп.
3. ЧИТАЙ дайджест `cand-latest.md` (или `OUT`). Каждый ### = сессия `src | дата | машина | оператор [PRIV] {score · tags}` + заголовок + сниппеты ([U]=Антон, [A]=Claude). Смотри верхние (HOT→WARM); при большом объёме — фан-аут Sonnet-судей по слайсам (см. `miner\slices\`), они возвращают JSON-вердикты, ты дедупишь и захватываешь.
4. СУДИ ВКУСОМ: оставь по-настоящему достойные РАЗНЫЕ истории (собрал/зашипил · война с багом/root-cause · human+AI/мультимашинный/консенсус приём · острый инсайт · «вау»). Отбрось рутину, тонкое, форки-дубли (похожий заголовок → одна история), чисто приватное. Позиционирование: не-кодер+AI = козырь, цель — оффер от LLM-компании + аудитория билдеров.
5. ЗАХВАТИ достойные: `python content_miner.py capture --src <cc:xxxxxxxx> --title "<хук>" --note "<суть>" --tier teaser|medium|longread|dev-log --angle "<угол>" --visibility public|personal|private`. Тир: teaser=хук; medium=дневник FB; longread=нарратив; dev-log=сухой технический. [PRIV]/неочищаемое → `--visibility personal`. Движок блокирует секрет-токены и дедупит по src.
6. МОСТ В КАНОН (закон «событие → сначала бит → потом пост», [[show-canon-single-source]]): для 1–2 самых сильных public-моментов создай черновик БИТА в `04-Projects\show-canon\beats-inbox\` по шаблону `beats\_TEMPLATE-beat.md` (+`authored_by: content-miner`); в `beats\` напрямую НЕ писать — переносит писатель канона. Прошлые (pre-canon, до 08.07) события — backfill-бит только при реальной сборке эпизода из них.
7. ОТЧЁТ Антону (ELI5): сколько сессий просканил → сколько черновиков в воронку (с тирами) → сколько бит-кандидатов в инбокс канона; что дальше = /episode по «+», очередь наружу = `registry\pub_registry.py` (queue → next → posted, лимиты в limits.json). Показать `python content_miner.py captured --limit N`.

ГРАНИЦЫ (AK-47):
- Draft-first ЖЕЛЕЗНО: только черновики; авто-паблиша нет; наружу ничего.
- Секреты/приватное/CRM/лиды не в контент (гейт движка + [[credential-store]]).
- Не строй параллельный монолит — переиспользуй content_miner + voice_triage + /episode.
- Грунт (детект/классификация) = Sonnet; авторский текст поста = Opus (это делает уже /episode, не тут).
- Ручной аналог ночного `content-miner-nightly`; долг по архиву закрыт разово 2026-07-09 (`miner\debt-log.md`).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
