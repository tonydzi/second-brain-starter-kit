---
title: "Проактивно предлагай DR, когда документация/прогресс опережает обучение LLM"
type: reglament
stage: distilled
source: claude-code-rules-intake
origin: anton
authored_by: hybrid
posted_by: "Claude (Fable 5)"
date_established: 2026-07-06
theme: ai-operations
applies_to: "Claude Code и любой LLM-актор Антона; человеко-ассистенты — как принцип «смотри живой источник, не память»"
audience: both
status: active
tags: [регламент, deep-research, DR, документация, эпистемика, alpha-protocol]
concept: "[[protocol-alpha-protocol-recall-plus-deep-research]]"
priority: must
confidence: 0.9
---

**Правило (WHEN → DO):** Всегда ПРОАКТИВНО предлагаю Deep Research (DR) по любой теме, где документация или прогресс продукта уходят вперёд быстрее, чем обучается LLM. Не жду триггера `R+DR` и не отвечаю по памяти — предлагаю сам строкой «сделать DR?» (или сразу выдаю промпт, если тема стратегическая).

**Зачем.** У любой LLM есть дата отсечки обучения. Инструменты, на которых мы живём (Claude Code, VS Code, Tailscale, Hetzner, OpenAI, модели Anthropic), меняются еженедельно — новые команды, флаги, фичи, цены, депрекейшены. Память модели про них устаревает молча. Корень (2026-07-06): я ДВАЖДЫ за вечер уверенно сказал «такой фичи нет» (Claude Code `/rename`, SSH в Claude Desktop) — обе существовали, Антон нашёл сам. Пробел вскрылся → сделали DR26-07-06-HUB-01 по SSH-доступу к Маяку, и он дал рабочее решение (VS Code Tunnels), которого я «не знал».

**Триггеры «здесь нужен DR» (WHEN):**
- Вопрос про возможности/фичи/лимиты/цены живого инструмента, особенно быстро-движущегося (Claude Code, VS Code, облака, LLM-провайдеры).
- Я ловлю себя на отрицательном утверждении «X не умеет / такого нет / это невозможно» про живой продукт → сначала DR/живой источник, потом вывод. Зеркало: negative-claims-need-live-verification [internal].
- Стратегическая новизна (продукт/архитектура/GTM) → полный Alpha Protocol L2, как и раньше.
- Тема, где «правильный способ» мог поменяться с моей отсечки (best practices, безопасность, интеграции).

**Как (DO):** одна строка-предложение «💡 тут стоит DR — прогресс по <теме> уходит быстрее моего обучения; выдать промпт?»; на «+» — Alpha Protocol (RECALL → GAP → номерной DR-промпт наружу → Synthesis). Тривиальное и стабильное (не движется) — без DR, не спамить (ak47-simplicity [internal]).

**Границы.** DR наружу выдаю промптом (Антон гоняет во внешнем инструменте), сам не ресёрчу, кроме лёгкого web-паса для заточки промпта. Каждый DR — номер + реестр [[reglament-numeratsiya-dr-i-reestr]]. Не подменяет недельный автоскан документации — тот ловит новое системно ([[reglament-nedelnyy-mayning-alfy-iz-dokumentacii]]); это правило — про реактивный момент «здесь я могу говорить из устаревшей памяти».

Связано: [[protocol-alpha-protocol-recall-plus-deep-research]], [[protocol-epistemic-neutrality-fringe-research]], verify-existing-before-proposing [internal].
