---
name: outbound-gate
description: "Gate for any outbound message before it leaves: pull request or issue comment, DM, invite, post, email. Use before sending to check facts, tone, platform rules, registry status and AI-slop, and to block text that fails."
version: 1.3.0
license: MIT
---

OUTBOUND_GATE — исходящее только на живую просьбу (anton 26.07, строгий регламент)

ЦЕЛЬ: каждое исходящее (PR, коммент, DM, инвайт, пост-заявка, письмо) целится в ЧЬЮ-ТО живую потребность, а не в пустоту. Замер 26.07: 8 PR → человеческий отклик ровно у одного, единственного issue-matched. Возврат = чужая живая просьба, не наш объём.

ПОРЯДОК (шаги строго по очереди; провал шага = стоп, не шипим):

0. ПРЕРЫВАНИЕ-ЧЕК (всегда первым). Есть ли живой ответ человека на наше ПРОШЛОЕ исходящее (мейнтейнер на PR, ответ в DM, коммент)?
   - GitHub: `gh pr list`/`gh api` по нашим открытым PR (реестр в памяти/MEMORY.md) + вахта pr_watch.
   - Есть ответ → это прерывание №1: сначала отвечаем same-day, потом всё остальное (вкл. новый PR и ретро). Отклик экосистемы = сама суть миссии.
   - Просьба о КРЕДИТЕ = удовлетворить немедленно и щедро: co-author в authors/registry + референс на исходный issue, коммит с проверяемым диффом.
   - После нашего ответа тишина ~3 дня → ОДИН вежливый пинг («готово, скажи если поправить — same-day»), не чаще.

1. АНКЕР-ЧЕК: чью живую просьбу закрывает ЭТО исходящее? Обязателен линк-анкер:
   - PR → open issue / proposal / discussion мейнтейнера (радар: дашборд LLM-Cookbook-Radar + `gh search issues`);
   - DM/инвайт → его вопрос/боль/пост, на который отвечаем;
   - пост/заявка → явный запрос площадки/человека.
   Анкера НЕТ → НЕ шипим. «Ещё один рецепт/DM в пустоту» = антипаттерн. Либо ищем анкер (issue-matching), либо идея → alpha-backlog. Тихое прошлое исходящее не добивать объёмом — менять таргетинг.

1-бис. PRIOR-ART-ЧЕК В САМОМ РЕПО (anton 24.09, урок serena#2048 «already fixed via #2096»): перед PR/issue — ДВЕ команды по теме касания: `gh pr list -R <repo> --search "<ключевые слова>" --state all --limit 10` + `gh search issues --repo <repo> "<слова>" --limit 10`; плюс беглый взгляд на свежие коммиты затронутого файла (`gh api repos/<repo>/commits?path=<file>&per_page=5`). Нашёлся открытый/свежезакрытый двойник → НЕ шипим свой, идём в ЕГО тред (ревью/коммент по §4.7). Класс: outbound-pr-duplicates-existing-work.
1-тер. ⭐ ПРАВО ВХОДА — ПРОВЕРЯЕТСЯ ВМЕСТЕ С ЗАНЯТОСТЬЮ, ОБА ДО СТРОЙКИ (08.10.2026). Дверь может быть никем не занята и при этом НЕ ПРИНИМАТЬ PR: репо требует assignment до PR и авто-закрывает остальное. Замер 05.10, оплаченный целым прогоном: `pydantic/pydantic-ai#8582` пришла FREE (и это правда), вклад построен целиком, PR #9835 авто-закрыт ботом через минуту — а в `CONTRIBUTING.md` это стояло словами, то есть ловилось бесплатно ДО стройки. Единственный судья — `python3 ~/.claude/scripts/door_claimcheck.py` (JSONL с `repo`/`issue` на stdin): вердикт `GATED` = НЕ строим. ⛔ Копий этой логики здесь НЕ делаем — спрашиваем прибор. ⚠️ И ещё раз перед `gh pr create`: между отсевом и Send issue могут назначить другому.


1-тер. ПУТЬ-ВЕРИФИКАЦИИ-ЧЕК для веера (anton 24.09, урок Nango 10 PR): волна >2 однотипных PR → ДО отправки первого назвать, ЧЕМ каждый будет верифицирован (ключ/окружение/тест) и есть ли этот ресурс У НАС — сверка по реестру `~/.claude/registry/verification_park.json` (status=have обязателен; absent там значит «не нашли в названном охвате», не «нет в мире» — нашёл ключ → допиши реестр). Ресурса нет → PR не рождается (или рождается ровно один пилот). Класс: fanout-before-verification-path-known, родня human-step-needs-forcing-function.

1-кватер. ОДИН РЕПО — ОДИН НАШ ОТКРЫТЫЙ PR (30.09.2026, оплачено `QwenLM/Qwen-Agent#927`).
   Два наших PR в одном репо конкурируют за внимание ОДНОГО мейнтейнера и вместе читаются как
   веер, даже если каждый по делу. #927 и #928 мы открыли в один день и #927 закрыли САМИ через
   сутки — работа впустую, потому что правила не было.
   ```bash
   python3 ~/.claude/scripts/gh_pr_discipline.py one-pr <owner/repo>   # exit 1 = не открываем
   ```
   exit 1 → новый PR НЕ рождается. Вместо него по порядку предпочтения: довести существующий до
   мержа (ответить, снять stale, ребейзнуть) · влить новую работу коммитом в него же, если тема та
   же · закрыть мёртвый своими руками ПЕРЕД новым · уйти в другой репо через `/issue-match`.
   exit 4 = забор упал: это **не** «чисто», вердикт не выдаём и не шипим (§5.4 индикатор = claim).
   Класс: `two-our-prs-compete-in-one-repo`, родня `cold-pr-into-silent-queue`.
   ⭐ **ШАБЛОННОСТЬ (anton 01.10.2026, оплачено NangoHQ/nango)**: гейт ВСЕГДА зовётся с заголовком нового PR:
   ```bash
   python3 ~/.claude/scripts/gh_pr_discipline.py one-pr <owner/repo> --title "<заголовок нового PR>"
   ```
   Заголовок отличается от прошлых наших в этом репо ТОЛЬКО именем сущности (вендор/провайдер/язык/модель)
   и ни один из них не MERGED → exit 1 + вопрос «а первый по шаблону уже приняли?». N таких PR = ОДИН веер,
   а не N вкладов. Разрешено: один первый → вердикт человека → остальные, лучше одним PR на несколько
   сущностей, если их CONTRIBUTING это допускает. Замер: 9 PR «add support for <вендор>», 8 закрыты, а
   закрывающий коммент #7539 показал их процедуру на новый API — дверь была, но мы уже отстрелялись.
   Б (выше) считает ЧИСЛО открытых, это — ШАБЛОННОСТЬ; `1-тер` — путь проверки. Три разных вопроса, не дубль.
   Класс: `template-pr-fanout-one-repo`. Тест: `_test_gh_pr_discipline.py` D1–D7 (красный до фикса 01.10).

1-квинт. ПОЧИНКА-НЕ-ФИЧА + ПОДПИСЬ ПО РАЗМЕРУ РЕПО (anton 06.10.2026, голосовая; ревью codex 07.10 вложен).
   Замер 118 наших PR: крупные репо (≥10k★) починка/доки 55% мержа, НЕПРОШЕНЫЕ фичи 6% (0 инженерных
   фич-мержей). Фичи мержатся только привязанные к существующему issue мейнтейнера (telegram-mcp#227,
   Abstractify#69) или в приглашённых форматах (cookbook/examples — единственный крупный фича-мерж оттуда).
   Перед PR в ЧУЖОЙ репо — две кнопки (0 LLM, звёзды и issue забираются через `gh`):
   ```bash
   python3 ~/.claude/scripts/gh_pr_discipline.py feature-gate <owner/repo> --title "<заголовок>" [--issue N] [--invited]
   python3 ~/.claude/scripts/gh_pr_discipline.py sign-check  <owner/repo>
   ```
   feature-gate: 🟢 починка = быстрая дорожка (issue заранее не нужен) · 🟢 фича+issue в мелком · 🟡 фича+issue
   в крупном (только если issue ЯВНО зовёт PR, иначе discussions) · 🟡 приглашённый формат · 🔴 exit 1 =
   НЕПРОШЕНАЯ фича (сперва discussions / заведи issue / неси в наш репо). Своё issue фичу НЕ отмывает.
   sign-check: крупный/корпоративный репо → подпись = сам автор-профиль, БЕЗ промо-ссылок на внешнюю работу
   (технически необходимые — reproducer/upstream issue/спека/запрошенный прототип — можно; правила репо/DCO/CLA
   выше); <1000★ и не корпоративный → ссылка `github.com/tonydzi` допустима. Классы: `unsolicited-feature-to-big-repo`,
   `big-repo-signature-name-only`. Тест: `_test_gh_pr_discipline.py` E1–E9 (красный до фикса 06.10). Метрика
   отбора: `gh_pr_discipline.py metric` (мержи в ≥10k★/мес + доля по типам — виден скат обратно в фичи).

2. ДОЛГ-ЧЕК (люди): `$OBSIDIAN_VAULT/_outreach/outreach_log.py check` + RECALL по адресату (CRM-карточка, история). Висящий НАШ долг перед человеком (неотвеченный его вопрос) → сперва закрыть долг, потом просить. [[outreach-relationship-debt-gate]]

3. КРЕДИТ ВПЕРЁД: автору анкера — кредит сразу в самом артефакте (упоминание issue + @автор в описании/интро), не ждать просьбы.

3-бис. ТЕКСТ-ГЕЙТ /ai-slop (anton 14.08): любой ИИ-написанный текст этого исходящего перед отправкой — финальный проход `/ai-slop` (ban-лист, ритм, канцелярит). Исключения ровно три: (а) текст с плашкой Майкрофта §3.3 — родной AI-голос честен; (б) машиночитаемое (GitHub/техдока/dev-log/journey-machine); (в) текст, написанный Антоном руками. Канон: `reglament-posty-ot-lica-antona-tolko-cherez-ai-slop`.

3-тер. ФАКТ-ГЕЙТ: у КАЖДОГО числа, даты и чужого состояния в тексте назван ИСТОЧНИК (06.10.2026, оплачено письмом в группу «ALTO furniture return»).
   `/ai-slop` выше судит СТИЛЬ. Этот шаг судит ФАКТУРУ -- то, за что краснеет адресат.
   ```bash
   python ~/.claude/scripts/outbound_fact_lint.py --text "<текст исходящего>"
   # exit 2 -> на каждую находку: --src "<кусок>=<кто/что сказал, когда>"
   python ~/.claude/scripts/outbound_fact_lint.py --text "<текст>" --src "12 октября=мастер, WhatsApp 06.10"
   ```
   exit 2 = текст НЕ уходит. Два законных хода, третьего нет:
   (1) **спроси источник** (исполнителя, анкету, страницу, календарь) и назови его в `--src`;
   (2) **убери факт из письма**: «сообщу дату, как только получу» -- это не слабее, это честно.
   ⛔ Отговорка источником не является: «помню», «кажется», «из головы», `iirc` отбиваются кодом.
   ⚠️ Прибор судит ФОРМУ, а не правду: он не знает, сколько фактов пропустил, и не проверяет,
   что названный источник сказал верно -- это вердикт автора (§5.5 слепая зона печатается всегда).
   Замер шума 06.10 по 1940 нашим живым исходящим (`dm_messages.db`, с 01.08): находки у 29.2%, то есть
   дверь просит источник примерно у каждого третьего письма, а не у каждого ([[gate-must-not-cry-wolf-on-our-own-cta]]).
   Семья: `cifra-v-ishodyashchem-ne-u-istochnika` (5 случаев с 03.09.2026; `prior_art.py class` печатает эту дверь).
   Почему дверь, а не памятка: правило «число требует источник» уже лежало в прозе дважды
   (`/borrowed-audience` §Цифры в теле PR, `/cv-outreach` §date_verified) -- оба раза ВНУТРИ одной
   рельсы, и обе новые поверхности (анкета 02.10, мессенджер 06.10) реализовали дефект заново.
   Тест: `scripts/_test_outbound_fact_lint.py` (41 проверка, красное доказано ВОСЕМЬЮ сломами через `red_proof.py`).
   ⚠️ Предел двери, названный вслух: она живёт в ЭТОМ скилле, значит покрывает исходящее, идущее через скилл.
   Бытовое письмо в мессенджер её минует -- на этот путь с 06.10 поставлена ТЕНЬ `hooks/outbound_fact_shadow.py`
   (PreToolUse, exit 0 всегда, только замер); 🌾 урожай 2026-10-13 решает, ставить ли туда блокирующий гейт.

4. SHIP по прежним гейтам (скилл ничего не ослабляет): GitHub PR — шипим сами сразу [[ship-github-no-plus-wait]]; публичные каналы/посты — публикуем САМИ (гейт Наташи снят 06.08.2026; у неё остался стоп-кран `paused` на поток, спрашивается через `pub_registry.can_post`); leak-scan перед любым публичным пушем; Tier-2 (деньги/юр/секреты) — Антон.

5. ВАХТА ПОСЛЕ SHIP: журнал (outreach_log / MEMORY-строка PR) + вахта ответов (pr_watch / робот-тик). Отправка обязана флипать статус журнала [[outreach-queued-status-swallows-replies]].
   ⛔ 5-бис. TELEGRAM-ЛИЧКА: вахта = СТРОКА В РЕЕСТРЕ СТОРОЖА, и ставится она В ТОМ ЖЕ ЗАХОДЕ, что отправка.
   `python ~/.claude/scripts/lead_thread_watch.py register <chat_id> --who "<Имя @handle>" --account <аккаунт> --context "<...>"` (идемпотентно).
   Нет строки -> ответ человека не видит ни `lead_thread_watch`, ни рутина `lead-thread-reply`: их «долгов 0» меряет СПИСОК, а не переписку.
   Замер 06.10.2026: волна 10 личек @ClawRus 04.10, ОТВЕТИЛИ 8, не подхвачен НИ ОДИН 44-50 ч -- ни одного chat_id в реестре не было. Тело шага -> `/telegram-lead-outreach` §4-бис.

ОТЧЁТ Антону (ELI5): что шипнули → чей анкер закрыли (линк) → кому кредит → какая вахта стоит. Провал гейта → честно: «анкера нет, в бэклог».

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
