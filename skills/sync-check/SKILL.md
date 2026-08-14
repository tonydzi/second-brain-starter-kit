---
name: sync-check
description: >
  READ-ONLY green/red report on THIS machine's file synchronization with the whole fleet — one
  command instead of polling the sync REST API by hand. Shows: peers connected, per-share state
  + files still needed (need=0 = in sync) + folder errors, and how many sync-conflict files
  accumulated (the silent sign two machines are fighting over a file). Trigger on "/sync-check",
  "is sync alive", "sync status". 0 tokens, changes nothing.
license: MIT
---

# /sync-check — здоров ли синк между моими машинами

Одна команда отвечает на вопрос «доехало ли / синкаемся ли мы сейчас» по ВСЕМ Syncthing-папкам этой машины, без ручного дёрганья REST. READ-ONLY, 0 токенов, портативно (ключ API берётся из локального конфига → работает на любой машине клана).

**Движок:** `$IMPORTS_ROOT/sync_check/sync_check.ps1` (git-бэкап в `_imports`, синкается через claude-imports). Теперь включает **детект дрейфа Device ID** (live `myID` vs `machines.json` → RED при расхождении — поймал бы инцидент 25.06).

**Уборка sync-conflict файлов** (когда отчёт показал «WARN sync-conflict files: N»): `python $IMPORTS_ROOT/sync_check/resolve_conflicts.py` (dry-run) → для каждого конфликта сравнивает с живым: `--quarantine` БЕЗОПАСНО переносит конфликты живого дерева в `_sync-conflict-archive\<дата>\` (move, не delete → восстановимо; orphans без живого двойника НЕ трогает), `--apply` удаляет только доказанные подмножества. Исключает уже-архивные/`.stversions`. Канон: [[reglament-chp-poterya-sinka-mezhdu-mashinami]] §6.

## Запуск
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$IMPORTS_ROOT/sync_check\sync_check.ps1"
```

## Как читать вывод
- **PEERS** — сколько пиров подключено. `0 connected` = синк МЁРТВ (машина спала / Syncthing застрял) → запустить сторож `syncthing_watchdog.ps1` (см. реглумент миграции, on-wake задача `SyncthingWatchdogOnWake`).
- **по каждой папке** `OK / WARN / RED`:
  - `OK` + `NEED=0` = папка в синке, всё доехало.
  - `WARN` + `NEED>0` = ещё качается (норм, если ненадолго; зависло — смотреть пиров).
  - `RED` = `state=error` или есть ошибки папки → разобраться (права/диск/конфликт).
- **sync-conflict файлы** — отдельный WARN (не валит в RED). Их рост = две машины правят один файл (например `settings.json`) → нужно решить «свежее бьёт старое» (Антон) и почистить `*.sync-conflict-*`.
- **EXIT 0** = всё зелёное; **EXIT 2** = есть RED.

## Когда звать
- Антон спрашивает «доехало ли на хаб / Mac», «синк жив?».
- ПЕРЕД тем как полагаться на свежий файл с другой машины («не найдено» ≠ «нет файла» — может ещё ехать; память deterministic-script-gotchas).
- ПОСЛЕ инцидента синка (как nested-folder D2 24-25.06) — подтвердить, что мост восстановлен.
- На КАЖДОЙ машине свой прогон (отчёт локальный); чтобы сверить весь клан — спросить каждую машину через `/inbox`/шину.

## Границы
- Read-only: ничего не чинит и не двигает. Лечение застрявшего синка = сторож (отдельно).
- Видит только то, что знает локальный Syncthing-демон; если демон не запущен — так и скажет (RED).
