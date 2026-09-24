---
title: "Регламент — Любая LLM = равноправный безопасный актор над Vault (вендор-независимость двойника)"
aliases: ["Любая LLM ведёт Vault", "Any-LLM vault actor", "Вендор-независимость двойника"]
date_established: 2026-06-29
type: reglament
stage: distilled
status: active
origin: anton
authored_by: claude-code
audience: both
theme: operations-governance
tags: [reglament, bible, multi-llm, multivendor, vendor-independence, governance]
concept: "[[concept-digital-immortality]]"
supersedes: "правило «только Claude Code пишет в Vault» (частично — см. §1)"
---

# Регламент — Любая LLM = равноправный безопасный актор над Vault

> Конституционное правило. Установил Антон (origin: anton, «++» 2026-06-29). Меняется только Антоном.

## Зачем
Знания и правила двойника не должны быть заперты в одном вендоре. Если Anthropic/Claude упрётся в лимит или вырубится — **любая LLM (Codex, Grok, Antigravity, будущие) должна сесть за Vault и вести его как Claude, ничего не сломав.** Это страховка главной цели — цифрового двойника `[[concept-digital-immortality]]`.

## Правила
1. **Отмена монополии Claude на запись.** Прежнее «только Claude Code пишет в Vault» отменяется. Любая одобренная LLM = равноправный актор над Vault И кодом. (Изоляция Cowork в `_cowork-inbox` как safety-net сохраняется — это про Cowork-песочницу, не про запрет другим LLM.)
2. **Безопасность не зависит от Claude.** Предохранители — МЕХАНИЧЕСКИЕ, работают у ЛЮБОГО коммитера без живого Claude: git pre-commit hooks + standalone-скрипты (бэкап-перед-записью, валидация frontmatter/провенанса, orphan-check, проверка ссылок, запрет правок конституции). Правило «Claude посмотрит» ЗАПРЕЩЕНО как единственный барьер.
3. **Единое поведение.** ВСЕ LLM подчиняются одному поведенческому канону идентично. Behavioral canon = одинаков; harness-механика (имена скиллов/MCP/пути) у каждого вендора неизбежно своя — это не нарушение «идентичности».
4. **Коллаборация только через общие артефакты** (Vault + git + файл-шина), НЕ единый диспетчер подписок (тот отклонён — [[decision-hermes-multivendor-arbitrage-rejected]]). Каждый вендор — свой харнесс, своя подписка.
5. **Гетеро-верификация.** Финальную проверку кода/правок делает LLM ДРУГОГО вендора (гетеро-пара ловит больше дефектов); implementer не объявляет «done» сам.
6. **Человеческий гейт (Вожак) сохраняется.** Merge в main, смена правил, Tier-2 — через человека. Смена ЭТОГО регламента — только Антон.

## Механика (двухслойный канон)
`SHARED-CANON/CORE.md` (жёсткие инварианты, ≤1 стр, все грузят целиком) + `SHARED-CANON/rules/*.md` (полный канон по темам, по надобности). `CLAUDE.md`→`@import CORE.md`; `AGENTS.md`=тот же CORE (Codex/Grok/Antigravity читают нативно). Держать CORE маленьким (кап 32 КБ у Codex, «lost in the middle»).

## Связано
[[decision-multi-llm-vendor-independence]] · [[reglament-semejnoe-upravlenie-vozhak-ogranichennyy-i-rasporyaditeli]] (Вожак+распорядители — тот же governance-слой) · [[decision-hermes-multivendor-arbitrage-rejected]] · [[reglament-multi-machine-claude-i-peredacha-mezhdu-mashinami]].
