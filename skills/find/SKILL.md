---
name: find
description: >
  Find a person, lead, contact or company by name in ANY spelling — deterministic name search
  that catches transliteration (Viktor/Victor across alphabets), wrong-keyboard-layout typing,
  and typos. Trigger on "/find <name>", "find <name>", "show everyone named <X>". This is
  SPELLING/exact-name search (0 tokens, NOT RAG) — the complement to semantic vault search.
license: MIT
---

# /find — умный поиск имени/компании по написанию

> 🧒 **When reporting to Anton:** end with a child-simple "Простыми словами" recap.

Детерминированный, 0 токенов — **НЕ RAG**. Эмбеддинги не понимают каракули (`dbrnjh`, опечатки, раскладку); это ловит отдельный код по фонетическим отпечаткам + нечёткому сравнению. Для поиска по СМЫСЛУ — это `/ask`, не сюда.

## Когда сюда
«найди Виктора» · «все Викторы» · «найди компанию Мерлион» · «кто такой <имя>» · `dbrnjh`/опечатки/транслит — любое имя ЧЕЛОВЕКА, лида, контакта или КОМПАНИИ в любом написании.

## Запуск (ВСЕГДА `PYTHONUTF8=1` — иначе cp1252 краш на виндовой консоли)
`PYTHONUTF8=1 python "$IMPORTS_ROOT/namesearch/find_name.py" <имя> [--html] [--all]`
- по умолчанию: лиды + люди + компании + Apple-контакты (заметки волта скрыты)
- `--all` — добавить заголовки заметок всего волта
- `--html` — визуальный дашборд в `_Dashboards\Name-Search-*.html` (Антон работает глазами — предлагай его для длинных списков)

Имя в кириллице даёт чистый запрос (виктор → ровно `viktor`); раскладочный/опечаточный запрос — расширяется автоматически.

## Смежное
- `expand_query.py <слово> [--grep] [--line]` — развернуть слово во все написания для grep по волту или для скармливания в `/ask` (RAG-хук).
- Индекс `names.db` пересобирается недельной задачей (и вручную `name_index.py --vault`). Если после большого импорта чего-то не хватает — упомяни, что нужна пересборка; сам не запускай без спроса.

## Ответ
- Дай список/таблицу (display · тип · файл-ссылка); для длинного — `--html` дашборд.
- Компания всплывает первой по запросу фирмы + связанные люди.
- Если 0 хитов — скажи прямо, предложи проверить написание или пересобрать индекс; не угадывай.
- Коротко; закончи 🧒-рекапом.

## Не путать
- `/ask` = по смыслу (RAG, эмбеддинги). `/find` = по написанию (детерминированный отпечаток). Канон-память [[smart-name-search]].

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
