---
name: release-slice
description: >-
  Open-source one slice of a private system: take a component, sanitize it, run a leak-scan as a
  hard gate, publish to GitHub, then changelog, roadmap and tag on cadence, then the content
  wave. Publishing without passing the leak-scan is forbidden. Triggers: "/release-slice
  <piece>", "ship the next slice".
license: MIT
version: 1.1.0
---

RELEASE-SLICE - конвейер «кусок системы → публичный репо → волна» (движение «бесплатная школа»)

КОНТЕКСТ (канон = vault `decision-open-second-brain-free-education-go-2026-07-02`):
- Отдаём БЕСПЛАТНО скелет/уроки, НИКОГДА содержимое/данные. MIT. Учим, не продаём.
- ⭐ STAGING-КОРЕНЬ ПЕР-МАШИННЫЙ (портируемость, 04.08): `$PUBLIC_REPOS`, а если пусто — Windows-узлы `E:\!CLAUDE-PaloAltoPC-June26\public-repos\`, Mac/Linux `~/public-repos/`. ⛔ Хардкод `E:\` в шагах ниже больше не писать: из-за него скилл 4 недели не запускался ни с одного узла Антона кроме хаба (замер 04.08 — выпуск `verdict-contract` пришлось вести конвейером вручную).
- Роадмап болей = `<STAGING>/claude-bible/ROADMAP.md` (публичное обещание: релизы пн+чт).
- GitHub-пуши автономны (Антон 03.07 «ПОСТИ все сам - ДОВЕРЯЮ»); Telegram/FB/каналы сохраняют свои гейты.
- Семья репо: каждый новый репо декларирует родство (ссылка на claude-bible = карта семьи) + FOR-ROBOTS.md.

ШАГИ (по порядку, ни один не пропускать):

1. АНТИ-ДУБЛЬ + RECALL: проверь, не делает/сделала ли эту порцию параллельная сессия (grep staging `public-repos\`, `priority.json`, свежие ретро, шина). Флот активен: чужая работа = присоединись, не дублируй.

2. ИНВЕНТАРИЗАЦИЯ КУСКА: что входит (скрипты из `_imports`/`~/.claude/scripts`, реглументы-паттерны, грабли из памяти). Оцени «сколько личного внутри» - это определяет глубину чистки. Читай реализацию, не пересказывай по памяти.

2b. ⛔ ГЕЙТ DOGFOOD (CLAUDE.md §5.9, канон `reglament-snachala-na-svoih-potom-naruzhu-dogfooding`): кусок уходит НАРУЖУ только после боевого прогона ВНУТРИ. Назови имя внутреннего пользователя (живой человек, НЕ автор куска: Антон · Наташа · Руслана · оператор узла) + его настоящую задачу; он проходит quickstart своими руками; боли записываются письменно (пустой список тоже пишем: «болей нет» + имя + дата) в карточку `10-Tasks\`; P0-боли (не смог сделать задачу) закрыты или явно приняты с причиной; ретест делает тот же человек. Явный скип гейта разрешён, но тогда вердикт релиза максимум ⚠️, не ✅ — и причина пишется в devlog. Это НЕ дубль shadow-прогона (§5.7): тот ловит «сломано», этот — «работает, но пользоваться невозможно».

3-бис. ⭐ ПОДПИСЬ И КОНТАКТЫ В РЕПО (anton 10.09, голосовая hub:6539: «везде в любом нашем
контенте всегда были наши контакты и обязательно наши подпись»). README несёт **полный блок**
подписи, и в нём ОБЯЗАТЕЛЬНА ссылка на профиль `github.com/tonydzi` — WhatsApp-строки одной мало:
читатель, пришедший за скриптом, должен видеть, что рядом лежат ещё 60 репо. Единственный источник
текста — `$OBSIDIAN_VAULT/08-Templates/github-touch-signature.md` §Полный блок; карта поверхностей
= `$OBSIDIAN_VAULT/08-Templates/outbound-signature.md`. CITATION.cff и научные ссылки —
исключение (`Anton Dziatkovskii (Tony Dzi)` + ORCID, без CTA). Проверка перед пушем:
`grep -c "github.com/tonydzi" README.md` ≥ 1, иначе репо не публикуем.

3. STAGING: собери репо в `<STAGING>/<имя>/` (см. STAGING-КОРЕНЬ выше; НЕ в волте). Минимум: README (боль → механики → quickstart 5 мин → Versioning → Who made this + WA CTA +1 341 222 9178 + star-ask «нужны первые 10») · docs/ (спека) · reference/ или templates/ (санитизированный код/шаблоны) · FOR-ROBOTS.md (альфа по ранжиру + как применить) · LICENSE (MIT, Anton Dzyatkovsky) · CHANGELOG.md · devlog/.

3b. ⛔ КОМПЛЕКТ РОЖДЕНИЯ (формат-файлы кладутся ЗДЕСЬ, не ночным сторожем):

    ```
    python ~/.claude/scripts/repo_birth_kit.py --init <STAGING>/<имя> --name <имя> --abstract "одно предложение о репо"
    ```

    Кладёт `CITATION.cff` (целиком детерминирован) и СКЕЛЕТ `FOR-ROBOTS.md` — альфу в скелете пишешь ты, машина её не выдумывает. Замер 09.09.2026: 7 из 7 последних публичных репозиториев родились БЕЗ формат-файлов и получили их коммитом ночного сторожа в 22:48–23:56 UTC; доля рождений с форматом была 0%. Проза в этом шаге просила FOR-ROBOTS.md и не спотыкала — спотыкает только exit-код шага 7a.

3c. ⛔⛔ ДОРОГА К РЕПО — ГЕЙТ РОЖДЕНИЯ (anton 01.10.2026, замер 07.10: 55 публичных
не-форков, у 36 ноль звёзд, ни один наш примитив не ставился командой — все восемь имён на
PyPI отдавали 404). Правило «владей примитивом, не будь донором кода» мы исполнили как
«выпусти 55 примитивов» — тот же дефект веера, что убил 8 из 9 PR в NangoHQ/nango, только
направленный на свою организацию. **Один примитив с дорогой бьёт пятьдесят пять без дороги.**

Публичный репо рождается, только если названы ТРИ вещи:
  1. **команда установки** — ровно то, что набирает посторонний (`pip install X`, `npx Y`,
     `docker run Z`). ⛔ `git clone` ответом НЕ СЧИТАЕТСЯ: клонировать ради пробы никто не
     будет, и именно этот ask сделал 36 репо невидимыми.
  2. **место, где человек наткнётся, НЕ ЗНАЯ НАС** — реестр, awesome-лист, живой чужой тред.
     ⛔ Наши каналы (@ClawRus, @ClawEng, palo-alto.ai) не считаются: это аудитория, которая
     у нас уже есть, а не дорога снаружи.
  3. **метрика на 30 дней** — ⛔ НЕ ЗВЁЗДЫ (их ставят из вежливости). Загрузки, форки,
     входящие issue от посторонних.

Нет ответа на все три → **репо остаётся приватным**. Дверь (fail-closed, exit 1 блокирует шаг):

```
python3 ~/.claude/scripts/road_to_it.py declare <имя> --install "..." --discovery "..." --metric "..." --judge-after <дата>
python3 ~/.claude/scripts/road_to_it.py check <имя>     # обязателен перед пушем в public
```

Репо не продукт (профиль, зеркало, архив) → `road_to_it.py exempt <имя> --reason "..."`; без
причины отбивается. Состояние по флоту + ЧЕСТНОЕ ПОКРЫТИЕ со слепой зоной:
`road_to_it.py audit`. Тест двери: `python3 ~/.claude/scripts/_test_road_to_it.py` (14 тестов,
краснеют на мутации `validate`). Класс дефекта: `published-without-a-road-to-it`.

4. САНИТИЗАЦИЯ (класс, не точечно): реальные chat_id → плейсхолдеры; hostname'ы → роли (hub, laptop-1); ключи только из env; никаких абсолютных путей E:\/C:\; имена команды/лидов → убрать; «шрамы» (истории багов) оставлять - это ценность, но обезличенно.

5. ⛔ HARD GATE - LEAK-SCAN: `python $IMPORTS_ROOT/leak_scan.py <staging-dir>` → exit 0 (CLEAN) обязателен; INFO по авторизованному CTA - норма; FAIL = чинить, не обходить. Сканер нормализует пробелы/тире - ad-hoc grep ЗАПРЕЩЁН как замена. + ручной просмотр глазами.

5b. ⛔ СМЫСЛОВОЙ ГЕЙТ (anton 04.07): публикуем ПАТТЕРНЫ, не живые внутренности - без топологии машин, каналов/механики одобрений, живых поверхностей контроля; публикация ОТСТАЁТ от продакшена (наружу идёт обкатанное/заменённое, не сегодняшний живой контур). Security-формулировки только доказуемые («слои контролей / blast radius / что остаётся человеку»; ⛔ «делаем агентов безопасными», «secure by design», обещания результата). Канон: волт `reglament-security-yazyk-i-granitsy-publikatsiy` + память security-claims-language.

6. ПИСЬМО-ГИГИЕНА: длинные тире (em/en dash) в текстах запрещены, только короткий дефис (сигнал Антона 19.06); никаких выдуманных цифр/длительностей (P14); прогони /taste-check при сомнении.

7a. ⛔ HARD GATE — КОМПЛЕКТ ПЕРЕД ПУШЕМ (после `git init` + `git add -A` + первого коммита, ДО `gh repo create`):

    ```
    python ~/.claude/scripts/repo_birth_kit.py --check <STAGING>/<имя>
    ```

    exit 0 обязателен. exit 1 = не пускать наружу, читать претензии поимённо: «НЕТ» (файла нет) · «не заполнен (остались TODO)» (скелет не дописан) · **«не в git»** (файл лежит на диске, но `gh repo create --source . --push` отправляет ТОЛЬКО закоммиченное — этот разрыв молчит и назван панелью вторых глаз 09.09). Гейт держит тот же список файлов, что и ночной `publish_format_gate.py`: расхождение двух списков само по себе баг.

7. GIT: коммит-identity публично-безопасная (`Anton Dziatkovskii <194927794+tonydzi@users.noreply.github.com>` — ⚠️ 13.08.2026: было `Palo-Alto-AI-Research-Lab@users.noreply.github.com`, аккаунт переименован в tonydzi, старого пользователя больше НЕТ; значение сверено с живым `git config --global user.email`), `git init -b main` → `gh repo create tonydzi/<имя> --public --source . --push` → тег `v0.1.0` → `git push origin main --tags`. Обнови в claude-bible: ROADMAP (боль → ✅ shipped as [линк]) + CHANGELOG (новая версия, что вошло) → пуш. Верификация: `gh repo view` PUBLIC + `gh api .../tags`.

7b. ⭐ ВИДЖЕТ «ПРОЧИТАТЬ С ИИ» ПРИ РОЖДЕНИИ (anton 19.09.2026, голосом: «кнопки на моем гитхабе, под каждой статьей»). Сразу после того, как репо создан и запушен:

    ```
    python ~/.claude/scripts/read_with_ai.py --repo tonydzi/<имя> --apply <STAGING>/<имя>/README.md
    ```

    Кладёт под README блок: фолд «скопировать промпт» (копи-кнопку рисует сам GitHub на fenced-блоке) + три диплинка Codex/ChatGPT/Claude, открывающие репо уже загруженным в агента, + подпись `github.com/tonydzi`. Идемпотентно (маркеры), коммить вместе с остальным. Дверь целиком = скилл `/read-with-ai`; волна по всем репо = `read_with_ai_rollout.py`. Пропуск шага = вердикт релиза максимум ⚠️ с названной причиной.

8. КОНТЕНТ-ВОЛНА: запусти /wow с углом порции (тот сам: эпизод → гейт-чат 00-06 → после ➕ тизеры в ClawRus/ClawEng, paste-ready FB в 00-05, лог в 00-07). Лонгрид EN кладётся в репо (docs/), лонгрид RU - Наташе.

9. СЛЕД: строка в ленту 00-07 (что → куда → ссылка), отметка в решении-каноне (чекбокс порции), реиндекс волта если писал заметки (`brain_embed_update.py`, для канона --force).

КАДЕНС: релизы с тегом - понедельник и четверг; мелкие коммиты - каждый день по готовности. Обещание публичное, его держим.

ГРАНИЦЫ: деньги/обязательства/секреты = стоп + Антон. Волт-записи = сперва `vault_backup.py`. Порция режется по ценности (АК-47), не ради нарезки. Очередь болей и «что не открываем никогда» (коннекторы-логика, governance-протоколы приватной части, persona-кодекс) - в решении-каноне.

## ⭐ Чёрный юмор обязателен (anton 10.09.2026, голосом)

Любой текст, который этот скилл отправляет ЖИВОМУ человеку наружу, несёт чёрную самоиронию — ровный служебный тон = дефект, объяснять надо не шутку, а её отсутствие. Строку берёшь через `/mycroft-joke` (полка (д) банка + строки 56-62 под холодное касание), приёмка — `/taste-check` P36. ⛔ Не шутим ровно в трёх зонах, и они не про вкус: строго-научная публикация (arXiv/журнал/JOSS) · юр.обязательство и анкета · красный список банка (чужая иконография угнетённых, псевдо-слуры, отрицание что я ИИ, юмор поверх диагноза/денег/беды собеседника). Одна шутка на тред. Канон: CLAUDE.md §3.3 §Поправка 10.09 + [[dark-humor-default-everywhere-external]].

## ⭐ Полнота списка потребителей (anton 10.09.2026)

Первый найденный потребитель почти никогда не единственный — он просто лежал на поверхности. Поиск закончен не когда кто-то найден, а когда **две оси подряд дали ноль новых имён**; внутренний потребитель (узел флота, робот, наш же скилл с костылём) ищется ПЕРВЫМ. Девять осей перебора и обязательный вердикт с числом («осей N/9 · адресов M · насыщение да/нет») — `/consumer-hunt` §Шаг 1-бис. ⚠️ Исчерпывающим обязан быть ПОИСК, адресация идёт по правилам двери: найденный адрес не выбрасывается, а получает статус и дату (🟢 постучались · ⏸ глухая очередь по замеру · 🪦 непереносимо). Канон: `reglament-vypustil-funkcional-naydi-potrebiteley-i-pridi-k-nim` §Поправка 10.09 + [[consumers-are-a-set-not-the-first-one]].

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
