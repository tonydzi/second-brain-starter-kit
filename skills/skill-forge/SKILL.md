---
name: skill-forge
description: "Пир-локальная кузница скиллов: создать local-<skill> на своём узле и подготовить промоушен в общий набор через гейт. Используй, когда придумал новый скилл на follower-машине."
consumer: "Писатель общего набора скиллов и полка Codex Desktop"
permissions: [filesystem]
risk_level: shell-local
processes_untrusted_data: false
disable-model-invocation: false
origin: [машина флота]
related: decision-2026-07-14-fleet-skill-autonomy-local-namespace
version: 1.1.0
---

# skill-forge — кузница скиллов пира (Ось А + гейт промоушена)

Реализация одобренного дизайна [[decision-2026-07-14-fleet-skill-autonomy-local-namespace]]:
пир создаёт СВОИ скиллы локально (никого не «отравляет», радиус поражения чужих = 0),
а на общий набор флота попадает только через гейт. Пока `local-*` — живёт только здесь
(`.stignore local-*`, не синкается, не откатывается receiveonly, но грузится loader'ом).

Привратник: `skill_guard.py` в этой же папке (0-LLM, stdlib). Рельсы из DR26-07-14-MACANTON-01.

---

## Режим A — `new` (создать local-скилл)

1. **Имя** — `local-<slug>`, только `[a-z0-9-]`. Проверить:
   `python ~/.claude/skills/skill-forge/skill_guard.py --check-name local-<slug>`
2. **Скаффолд**: создать `~/.claude/skills/local-<slug>/SKILL.md` с frontmatter:
   - `name`, `description` (когда вызывать), `permissions: [...]` (filesystem/shell/network — что реально нужно),
     `risk_level` (inert / shell-local / shell-networked / secret-touching / always-loaded-core / irreversible — таксономия ChatGPT-DR),
     `processes_untrusted_data: true|false`, `disable-model-invocation: true` для side-effect/ручных.
   - ⚠️ **shell OFF по умолчанию**: не проси `shell` без реальной нужды; скилл с shell → обязательный review при промоушене.
3. **Гейт-скан** сразу: `python ~/.claude/skills/skill-forge/skill_guard.py`
   (рельс 1 collision + рельс 3 sync-conflict — узнаешь сразу, не шадоуишь ли общий скилл).
4. **`/tt`** новый скилл (прогнать вживую → сломать → доказать) ДО любого промоушена.

## Режим B — `promote` (local → общий набор флота)

Гейт (одобрен Антоном): **`/tt` + leak-scan + collision-check + risk-classify + 1 мнение пира → маршрут писателю.**
Follower НЕ пишет общий набор сам (он receiveonly) — готовит бандл и отдаёт единственному писателю.

1. **Гейт детерминированно** (всё, что можно проверить машиной, здесь и сейчас):
   ```
   python ~/.claude/skills/skill-forge/skill_guard.py --leak local-<slug>
   ```
   → collision (рельс 1) + sync-conflict (рельс 3) + name (Step 2) + leak (рельс 6). Exit 1 = стоп.
   Тяжёлый leak-scan при наличии — `gitleaks`/`trufflehog` поверх (движок `/release-slice`).
2. **`/tt` пройден?** — без ✅ не промоутим.
3. **Risk-класс** → если `secret-touching` / `always-loaded-core` / `irreversible` / trigger Tier-2 →
   **гейт Антона** (QQQ в 02), иначе — 1 мнение пира достаточно.
4. **1 мнение пира** — `bus_send.py <peer> "SKILL-REVIEW: local-<slug> …"` ([[peer-opinion-before-fleet-rollout]]).
5. **Маршрут писателю**: скопировать бандл в `[шина]/_transit/canon-proposals/` + пинг писателю
   (сейчас = хаб; после Step 3 миграции = Маячок). Писатель снимает `local-`, коммитит, синкает всем
   ([[skills-rollout-all-machines-default]]). ⛔ Сам `local-` не снимаю на follower — это работа писателя.
6. **Дверь Codex после записи в общий источник.** На узле, где существует
   `~/.claude/scripts/codex_skills_bridge.py`, писатель обязан сразу выполнить:
   `python ~/.claude/scripts/codex_skills_bridge.py sync`, затем
   `python ~/.claude/scripts/codex_skills_bridge.py status`. Любой ненулевой код = промоушен
   не завершён. Скрипта на этом узле нет → отправить применение на хаб; не создавать копию руками.

---

## Границы (что НЕ делает этот скилл)
- **Step 3 (перенос писателя hub→Маячок)** — fleet-консенсус, НЕ отсюда.
- **Step 5 (кодификация в Библию/CLAUDE.md)** — канонический писатель (хаб), ПОСЛЕ сборки механизма.
- **OS-read-only на shared/** (вызов B из DR) — инфра узла, отдельно от этого скилла.

🧒 Простыми словами: это верстак, чтобы придумать свой инструмент прямо у себя, проверить, что
он не ломает чужие и не прячет секрет, а потом отдать «главному [человек]», который раздаёт всем.
