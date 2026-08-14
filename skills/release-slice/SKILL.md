---
name: release-slice
description: >
  The "ship a slice" ritual for open-sourcing pieces of a private system: take a component →
  sanitize → leak-scan (hard gate) → publish to GitHub → changelog/roadmap/tag on cadence →
  content wave. Trigger on "/release-slice <piece>", "ship the next slice", "release pain #N".
  Publishing without the leak-scan gate is forbidden.
license: MIT
---

RELEASE-SLICE - конвейер «кусок системы → публичный репо → волна» (движение «бесплатная школа»)

КОНТЕКСТ (канон = vault `decision-open-second-brain-free-education-go-2026-07-02`):
- Отдаём БЕСПЛАТНО скелет/уроки, НИКОГДА содержимое/данные. MIT. Учим, не продаём.
- Роадмап болей = `%WORKDIR%\public-repos\claude-bible\ROADMAP.md` (публичное обещание: релизы пн+чт).
- GitHub-пуши автономны (Антон 03.07 «ПОСТИ все сам - ДОВЕРЯЮ»); Telegram/FB/каналы сохраняют свои гейты.
- Семья репо: каждый новый репо декларирует родство (ссылка на claude-bible = карта семьи) + FOR-ROBOTS.md.

ШАГИ (по порядку, ни один не пропускать):

1. АНТИ-ДУБЛЬ + RECALL: проверь, не делает/сделала ли эту порцию параллельная сессия (grep staging `public-repos\`, `priority.json`, свежие ретро, шина). Флот активен: чужая работа = присоединись, не дублируй.

2. ИНВЕНТАРИЗАЦИЯ КУСКА: что входит (скрипты из `_imports`/`~/.claude/scripts`, реглументы-паттерны, грабли из памяти). Оцени «сколько личного внутри» - это определяет глубину чистки. Читай реализацию, не пересказывай по памяти.

3. STAGING: собери репо в `%WORKDIR%\public-repos\<имя>\` (НЕ в волте). Минимум: README (боль → механики → quickstart 5 мин → Versioning → Who made this + WA CTA +1 341 222 9178 + star-ask «нужны первые 10») · docs/ (спека) · reference/ или templates/ (санитизированный код/шаблоны) · FOR-ROBOTS.md (альфа по ранжиру + как применить) · LICENSE (MIT, Anton Dzyatkovsky) · CHANGELOG.md · devlog/.

4. САНИТИЗАЦИЯ (класс, не точечно): реальные chat_id → плейсхолдеры; hostname'ы → роли (hub, laptop-1); ключи только из env; никаких абсолютных путей E:\/C:\; имена команды/лидов → убрать; «шрамы» (истории багов) оставлять - это ценность, но обезличенно.

5. ⛔ HARD GATE - LEAK-SCAN: `python $IMPORTS_ROOT/leak_scan.py <staging-dir>` → exit 0 (CLEAN) обязателен; INFO по авторизованному CTA - норма; FAIL = чинить, не обходить. Сканер нормализует пробелы/тире - ad-hoc grep ЗАПРЕЩЁН как замена. + ручной просмотр глазами.

5b. ⛔ СМЫСЛОВОЙ ГЕЙТ (anton 04.07): публикуем ПАТТЕРНЫ, не живые внутренности - без топологии машин, каналов/механики одобрений, живых поверхностей контроля; публикация ОТСТАЁТ от продакшена (наружу идёт обкатанное/заменённое, не сегодняшний живой контур). Security-формулировки только доказуемые («слои контролей / blast radius / что остаётся человеку»; ⛔ «делаем агентов безопасными», «secure by design», обещания результата). Канон: волт `reglament-security-yazyk-i-granitsy-publikatsiy` + память security-claims-language.

6. ПИСЬМО-ГИГИЕНА: длинные тире (em/en dash) в текстах запрещены, только короткий дефис (сигнал Антона 19.06); никаких выдуманных цифр/длительностей (P14); прогони /taste-check при сомнении.

7. GIT: коммит-identity публично-безопасная (`Anton Dzyatkovsky <Palo-Alto-AI-Research-Lab@users.noreply.github.com>`), `git init -b main` → `gh repo create Palo-Alto-AI-Research-Lab/<имя> --public --source . --push` → тег `v0.1.0` → `git push origin main --tags`. Обнови в claude-bible: ROADMAP (боль → ✅ shipped as [линк]) + CHANGELOG (новая версия, что вошло) → пуш. Верификация: `gh repo view` PUBLIC + `gh api .../tags`.

8. КОНТЕНТ-ВОЛНА: запусти /wow с углом порции (тот сам: эпизод → гейт-чат 00-06 → после ➕ тизеры в ClawRus/ClawEng, paste-ready FB в 00-05, лог в 00-07). Лонгрид EN кладётся в репо (docs/), лонгрид RU - Нина.

9. СЛЕД: строка в ленту 00-07 (что → куда → ссылка), отметка в решении-каноне (чекбокс порции), реиндекс волта если писал заметки (`brain_embed_update.py`, для канона --force).

КАДЕНС: релизы с тегом - понедельник и четверг; мелкие коммиты - каждый день по готовности. Обещание публичное, его держим.

ГРАНИЦЫ: деньги/обязательства/секреты = стоп + Антон. Волт-записи = сперва `vault_backup.py`. Порция режется по ценности (АК-47), не ради нарезки. Очередь болей и «что не открываем никогда» (коннекторы-логика, governance-протоколы приватной части, persona-кодекс) - в решении-каноне.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
