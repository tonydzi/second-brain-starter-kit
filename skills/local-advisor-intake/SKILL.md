---
name: advisor-intake
description: Ящик советов внешних advisor'ов — собрать PR/issues из приватного репо PaloAlto-AI-Research-Lab-Knowledge, показать что предложили / что взяли / что отклонили, довести каждый совет до вердикта (мерж/отклон/эпизод). Потребитель для рекомендаций advisors, чтобы они не тонули («музей → инструмент»). Триггеры "/advisor-intake", "ящик советов", "что предложили advisors", "разбери рекомендации", "advisor feedback", "что там от peers". Тонкая обёртка над ~/.claude/scripts/advisor_intake.py (0 LLM пул через gh). Канон: память peer-export-lab-knowledge, connect-rule-pipeline-ownership.
---

## ⚖️ ШАГ 0 — СНАЧАЛА БИБЛИЯ (обязательно, origin: anton 2026-07-26)

Перед ЛЮБЫМ действием этого скилла подними выстраданные правила Библии по лидам:

```bash
python3 ~/.claude/scripts/bible_leads.py            # карта (0 токенов)
python3 ~/.claude/scripts/bible_leads.py --grep <тема>   # срез
```

Идёт РАНЬШЕ `outreach_log.py check` и раньше RECALL по человеку. Нет правила в Библии →
это находка, после работы занести через `/intake`, а не импровизировать молча.
Канон: `reglament-lyubaya-rabota-s-lidami-snachala-bibliya` · `_Bible-Outreach-MOC` · CLAUDE.md §9.5

# /advisor-intake — ящик советов advisor'ов

Замыкание Connect-цепочки peer-export: репо отдали → advisors смотрят → **их советы приходят как PR/issues → сюда → до вердикта**. Без этого шага советы тонут.

## Что делает
1. `python3 ~/.claude/scripts/advisor_intake.py` — тянет issues+PR из `tonydzi/PaloAlto-AI-Research-Lab-Knowledge` (gh, 0 LLM), рендерит `_Dashboards/Advisor-Intake.html`: 🆕new / triaged / merged / rejected.
2. `--triage` — печатает необработанные (🆕) для разбора в сессии.

## Триаж-цикл + ОТВЕТ (по каждому 🆕) — правило Антона 20.07: работаем с ответами ВСЕГДА
**SLA: содержательный ответ advisor'у ≤48ч. Планка качества ответа = Fable 5** (пока лимиты свободны; fallback Opus). Рутины Fable не гоняют — отвечает живая сессия по пингу SLA-сторожа.
1. Прочитать PR/issue ЦЕЛИКОМ (`gh issue view N --repo <repo>` / `gh pr view`).
2. RECALL перед вердиктом: что у нас УЖЕ есть по теме (память + grep волта + публичные PR) — частая находка «мы это уже сделали, advisor не видит» → ответ с пруфом, бесплатный ход.
3. Вердикт: **accepted** (берём → adopt-конвейер) · **merged/shipped** (сделано) · **rejected** (с причиной, уважительно) · **defer** (обдумать — но ответ всё равно ≤48ч).
4. **ОТВЕТ в issue/PR** от аккаунта лаборатории (`gh issue comment N --body-file …`): вердикт + что уже сделано с пруфами + что берём + честные next steps БЕЗ жёстких дат-обещаний (обязательства = hard-stop). Ответы = тип C исходящего (по делу) — шлю сам, журналирую постфактум.
5. Записать в ledger append-only `_outreach/advisor_intake_ledger.jsonl`:
   `{"kind":"issue","number":N,"verdict":"accepted","by":"…","note":"… ; ответ issuecomment-…","ts":"…"}`
6. Дашборд перечитает ledger и переставит статус; SLA-ALERT гаснет сам (сторож видит наш коммент).
7. **Мерж кода — Tier-2**: применение чужого PR к репо = решение Антона (показать дифф → «+»). Я готовлю, он мержит.
8. Взятый совет → кандидат в контент-эпизод (правило «всё = контент»): «advisor предложил X, мы взяли, вот до→после».

## SLA-сторож (0 LLM, в рутине)
`advisor_intake.py` сам печатает `ALERT ⏰ advisor без ответа Nд: …` для 🆕 старше 48ч без нашего коммента; обёртка `advisor_intake.command` постит алерты в 03. «Отвечено» = наш коммент в GH (детерминированно), не запись в ledger.

## Границы
- Пул read-only. Мерж/закрытие PR наружу = Tier-2, триггер Антона.
- Не путать с `/comments` (комменты под нашими постами) и `/pipeline` (наши лиды).

## Рутина
Еженедельно авто-обновляет дашборд (launchd `ai.paloalto.advisor-intake`). Ручной прогон — этим скиллом.
