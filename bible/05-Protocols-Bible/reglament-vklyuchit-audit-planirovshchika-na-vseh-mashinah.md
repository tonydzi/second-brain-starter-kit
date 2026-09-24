---
title: "Включить аудит Планировщика задач на ВСЕХ машинах (CCTV для scheduled-tasks)"
aliases:
  - "TaskScheduler audit log on every machine"
  - "камера видеонаблюдения за задачами"
  - "кто включает/выключает scheduled-task"
date_established: 2026-06-27
type: reglament
stage: distilled
audience: both
origin: anton
tags: [reglament, infra, audit, scheduled-tasks, forensics, multi-machine, onboarding]
---

# Включить аудит Планировщика задач на ВСЕХ машинах

> **Правило Антона (origin: anton, 2026-06-27, дословно):** «надо включить ВСЕГДА и ВЕЗДЕ на всех ПИРАХ!» — про журнал аудита Планировщика задач Windows («камеру видеонаблюдения»), который записывает, КТО и ЧТО делает с запланированными задачами.

## Зачем (корень)
Когда кто-то (другая параллельная Claude-сессия, скрипт, человек) **создаёт / включает / выключает / меняет** scheduled-task — по умолчанию Windows этого **не записывает** (журнал `Microsoft-Windows-TaskScheduler/Operational` выключен). Без него «кто разбудил задачу?» определить ретроспективно нельзя — слепое пятно. Это и поймало нас 2026-06-27: хаб-авторизованно-выключенный дубль-генератор (`Claude Dashboard Refresh Hourly` = `session_archive.py`) кто-то пере-включал, а доказать кто — нечем, потому что «камера» была выключена. Корень — не задача, а **отсутствие аудита** инфра-слоя.

## Правило
- **На КАЖДОЙ машине клана** (хаб + ноут + ПК коллег + Маки + любой новый узел) журнал аудита Планировщика **должен быть ВКЛЮЧЁН**. Это **обязательный шаг онбординга** новой машины (рядом с git-бэкапом конфига и Syncthing-watchdog).
- Журнал = `Microsoft-Windows-TaskScheduler/Operational`. События: **106** (задача зарегистрирована), **140** (обновлена), **141** (удалена), **142** (выключена) — каждое с **SID пользователя + точным временем**.
- Связка для полной улики: журнал даёт «когда и под каким аккаунтом», а `dupgen_guardian.py` (снимок живых claude/node-сессий в момент флипа) даёт «какая именно сессия» → вместе = виновник пойман.

## Как (AK-47, один файл, само-поднимается)
- Скрипт: `[путь владельца]` (само-elevate через UAC) → зовёт воркер `enable_task_audit.ps1` → `wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true /ms:[id]`. Идемпотентно (повторный запуск безвреден). Результат пишется в `_audit_enable_result.txt` (`enabled: true` = готово).
- **Нужен админ (UAC) один раз на машину** — это единственный шаг, где нужен живой оператор/Антон (нажать «Да»). Предупредить заранее, что выскочит окно UAC (затемнит экран), и где нажать.
- Откат (если когда-то понадобится): `wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:false`.
- Проверка статуса: `wevtutil gl Microsoft-Windows-TaskScheduler/Operational` → строка `enabled: true`.
- Чтение «кто трогал задачи»: `wevtutil qe Microsoft-Windows-TaskScheduler/Operational /c:20 /rd:true /f:text` (или Event Viewer → Applications and Services Logs → Microsoft → Windows → TaskScheduler → Operational).

## Статус раскатки
- **laptop-HP17** (`[машина флота]`) — ✅ ВКЛЮЧЕНО 2026-06-27 21:09 (admin=True, exit 0).
- хаб `[машина флота]`, `[машина флота]`, `[машина флота]` — запрос на включение разослан по шине (DUAL-SEND); каждый оператор прогоняет `enable_task_audit.cmd` локально (нужен их UAC).

## Границы
- Включение журнала = read-only диагностика, **ничего не ломает** и не трогает данные; единственная «цена» — разовый UAC.
- Не путать с включением полного Security-аудита (Object Access) — здесь именно лёгкий Operational-журнал Планировщика, его достаточно.

Связано: [[reglament-multi-machine-claude-i-peredacha-mezhdu-mashinami]] (онбординг машин), config-safety-backup-and-migration-check [internal], session-machine-tagging [internal] (кто/где), `dupgen_guardian.py` (снимок сессии-виновника). Bound by `operating-agreement`.
