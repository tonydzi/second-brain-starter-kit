---
name: mac-export
description: >-
  Pull a NATIVE macOS data source (Contacts, Apple Notes, Reminders, Calendar) off THIS Mac into
  Anton's Obsidian vault as MD + JSON, plus a handoff README so the next Claude Code session knows
  what landed there. One skill, per-source adapters, idempotent refresh. Trigger on "/mac-export
  <источник>", "выкачай контакты/заметки/напоминания/календарь с мака", "выкачай всё с мака в
  обсидиан", "export contacts/notes/reminders/calendar from Mac", "что ещё можно достать с мака что
  недоступно с ПК", "pull <native mac source> into the vault". This is a native .app SQLite/AppleScript
  puller — DISTINCT from obsidian-ingest (archives an already-existing artifact/URL) and from
  gmail/telegram-reimport/whatsapp-sync (connector pulls of other sources). macOS-only (runs on the
  Mac that owns the data). Each source = a brick in the digital twin ([[main-goals]] цель №1).
---

# /mac-export &lt;источник&gt; — тащим родные данные Мака в волт

> 🧒 **When reporting to Anton:** end with a child-simple «Простыми словами» recap.

Один паттерн для всех: родная база .app (SQLite / AppleScript) → `MD + JSON` в известный путь волта → короткий `README_FOR_CLAUDE.md` для следующей сессии. Меняется только адаптер под источник. Детерминированно, 0 токенов LLM (чистое извлечение). Работает на той машине, что владеет данными (этот Мак) — с ПК эти источники недоступны, в этом весь смысл.

## Когда сюда
«выкачай контакты/заметки/напоминания/календарь с мака» · «что ещё можно достать с мака, чего нет на ПК» · любой родной источник macOS в волт. НЕ сюда: уже готовый файл/URL/артефакт → `/obsidian-ingest`; Gmail/Telegram/WhatsApp → их коннекторы.

## Источники и адаптеры

| Источник | Родная база (копировать в tmp перед чтением!) | Выход в волте | Движок | Статус |
|---|---|---|---|---|
| **contacts** | `~/Library/Application Support/AddressBook/**/AddressBook-v22.abcddb` (+`-wal`,`-shm`); контакты = `ZABCDRECORD where Z_ENT=22` | ⚠️ КАНОН с 2026-08-20 = волт `07-People/Contacts/` (8 542, CRM-обогащены) + `_imports/apple-contacts/` (json/vcf/db, конвейер хаба); GDrive-копия `[машина флота]usa-Apr26/Contacts/` = legacy (GDrive-app выключен). Обновление карточек = merge (`merge_cards.py`), НЕ перезапись — иначе стираются crm-поля | `.../Contacts/_tools/extract_contacts.py` | ✅ ПРОВЕРЕН (12 495 контактов, 2026-06-11) [[contacts-export]] |
| **notes** | `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite` | `!_Claude_[машина флота]/Apple Notes Export &lt;дата&gt;/` (`notes_export.json`+`Notes/`+`attachments/`+`_INDEX.md`) | экспортёр рядом с выходом (см. `README_FOR_CLAUDE.md`) | ✅ ПРОВЕРЕН (649 заметок, 2026-06-11) |
| **reminders** | `~/Library/Group Containers/group.com.apple.reminders/Container_v1/Stores/Data-*.sqlite` (ZREMCDREMINDER; списки ZREMCDBASELIST) | `!_Claude_[машина флота]/Reminders Export <дата>/` (`Reminders.md` чекбоксы + JSON) | `adapters/safari_calendar_reminders_export.py` | ✅ ПРОВЕРЕН (57 шт, 2026-08-20) |
| **calendar** | `~/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb` (⚠️ НЕ `~/Library/Calendars/**.ics` — там бэкапы 2018-2022!) | `!_Claude_[машина флота]/Calendar Export <дата>/` (`ics/` по календарю + JSON) | `adapters/safari_calendar_reminders_export.py` | ✅ ПРОВЕРЕН (27 476 событий, 15 .ics, 2026-08-20) |
| **imessage** | `~/Library/Messages/chat.db` (+wal/shm; нужен Full Disk Access у Claude.app) | `!_Claude_[машина флота]/iMessage Export <дата>/` (MD по диалогу + `messages.json` + `attachments/`) | `adapters/imessage_export.py` (декодер attributedBody: `NSString`→`0x2b`→varint→UTF-8; имена из name_map контактов) | ✅ ПРОВЕРЕН (39 052 сообщ / 3 376 диалогов / 1 645 вложений, 2026-08-20) |
| **safari** | `~/Library/Safari/Bookmarks.plist` + `History.db` + `CloudTabs.db` (FDA) | `!_Claude_[машина флота]/Safari Export <дата>/` (Bookmarks/ReadingList/History .md + JSON) | `adapters/safari_calendar_reminders_export.py` | ✅ ПРОВЕРЕН (3 301 закладка / 196 RL / 851 история, 2026-08-20) |

> ⚠️ **Контакты — два адаптера, числа разные:** `_tools/extract_contacts.py` (Z_ENT=22, один источник, 12 495) vs `adapters/contacts_extract_allsources.py` (все 13 баз-источников + дедуп, 15 423, + name_map телефон/почта→имя для iMessage). Расхождение ОБЪЯСНЕНО (сессия contacts-dedupe 2026-08-20): 12 495 = фильтр «есть имя» (16 887 сырых → 14 502 named → дедуп), 15 423 = все записи включая безымянные email-only с другим дедупом. Оба числа честные, фильтры разные.

## Запуск
```bash
# 1) КОПИЯ базы в tmp (иначе читаешь устаревший снимок — WAL не влит)
cp "<db>" "<db>-wal" "<db>-shm" /tmp/mac-export/ 2>/dev/null
# 2) прогнать адаптер источника (contacts проверен):
python3 "/Users/<имя>/Library/CloudStorage/GoogleDrive-dzyatkovskiy.a@gmail.com/My Drive/!_Obsidian/[машина флота]usa-Apr26/Contacts/_tools/extract_contacts.py"
# 3) для нового источника — склонировать структуру extract_contacts.py под его SQLite-схему
```
После прогона: положить/обновить `README_FOR_CLAUDE.md` (что за источник, сколько записей, схема frontmatter) → это и есть хэндофф следующей сессии. Идемпотентно: перезапуск перетирает выход (для contacts — чистит `People/`).

## Грабли
- ⚠️ **AppleScript блокируется privacy (ошибка -1741)** для Contacts/Notes/Reminders → читать SQLite напрямую, не через AppleScript.
- ⚠️ **Читать копию, не живую БД:** SQLite Apple держит хвост в `-wal`; без копирования `.sqlite`+`-wal`+`-shm` в tmp получишь устаревшие данные.
- Фильтр контактов = «есть имя» (сырьё ~16 887 → 12 495 с именем); дубли по email/phone/name.
- Новый источник → сперва глянуть его схему (`sqlite3 <db> .tables`), потом лепить адаптер по образцу `extract_contacts.py`.

## Канон
Память [[contacts-export]] · правило [[always-archive-artifacts-to-vault]] (всё в волт + реиндекс + перелинковка) · цель [[main-goals]] (каждый источник — кирпич двойника). После нового экспорта — реиндекс RAG (`brain_embed_update.py`) как у других импортов.
