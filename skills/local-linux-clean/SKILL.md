---
name: local-linux-clean
description: >
  Чистка нагрузки на МАЯКЕ ([машина флота], Linux VPS, headless) и любом linux-узле: зомби,
  залипшие headless-LLM вызовы (gemini -p / claude -p / codex exec), orphan-MCP, CPU-обжоры.
  Триггеры: "/linux-clean", "почисти маяк", "маяк тормозит", "зомби процессы на маяке",
  "убей зависший процесс", "kill zombies linux", "linux cleanup", "high load маяк".
  Обёртка над ~/.claude/scripts/proc_patrol.py (orphan-MCP/zombie/stale-claude/CPU-hog,
  общий кросс-платформенный движок, cron */30) + ~/.claude/scripts/headless_llm_watchdog.py
  (headless-LLM >30мин, Linux-локальный сторож, cron */10, родился из TASK #06289e27
  [машина флота] 31.07 — [машина флота] нашёл gemini -p, живший 5ч48м и державший 1.4GB).
  ⚠️ На Маяке НЕТ живого человека за терминалом — оба движка работают ПОЛНОСТЬЮ автономно
  по крону, этот скилл нужен только для ручного разбора/дебага, не как «зайди и почисти».
---

# local-linux-clean — чистка зомби и залипших LLM-вызовов на Маяке (headless)

Два независимых движка, оба уже на кроне, оба самодостаточны (§5.5: сторож не живёт в том,
что сторожит — но здесь сторожа два РАЗНЫХ файла, каждый может умереть без другого):

1. `proc_patrol.py` (кросс-платформенный, шарится на весь флот через Syncthing, НЕ трогать
   его kill-логику без координации — правка бьёт Windows/Mac тоже) — orphan-MCP,
   stale-claude >24ч, zombie-репорт, CPU-обжоры/ЗАЛИП. Cron `*/30 * * * *`.
2. `headless_llm_watchdog.py` (Linux-локальный, НЕ шарится, можно удалить не трогая
   proc_patrol) — headless-LLM CLI-вызовы (`gemini -p`, `claude -p`, `codex exec`,
   `codex -p`) старше 30 минут (2× флотский стандарт MAXSEC=900,
   [[inbox-robot-hang-guard]]). Cron `*/10 * * * *`.

## Шаг 1 — ЗАМЕР (обоими движками, ничего не убивать вслепую)

```bash
python3 ~/.claude/scripts/proc_patrol.py --dry-run
python3 ~/.claude/scripts/headless_llm_watchdog.py --dry-run
ps -Ao state | grep -c '^Z'                    # зомби прямо сейчас
cat /proc/meminfo | grep -i swap                # ИСТИНА про своп
uptime                                          # load average
```

## Шаг 2 — headless-LLM: почему 30 минут, а не 15 (MAXSEC)

Флотский стандарт `MAXSEC=900` (15 мин) — это порог, после которого ХОЗЯИН вызова
(живая claude-сессия) должен сам заметить и разобраться. `headless_llm_watchdog.py` берёт
**2× этот порог (30 мин)**, потому что на Маяке никто не смотрит на `ps` глазами — цель не
«поймать первое подозрение», а «не убить настоящий долгий DR-fanout». Дельта-замер CPU
(как в mac-clean Шаг 1) здесь НЕ нужен: headless-LLM вызов, ждущий сетевой ответ, может
жечь 0% CPU и всё равно быть мёртвым — критерий тут ВОЗРАСТ, не горение.

⚠️ Паттерны матчатся по подстроке командной строки (`gemini -p`, `claude -p`, `codex exec`,
`codex -p`) — **живая двусторонняя `claude`-сессия (без `-p`) никогда не матчится**, поэтому
сторож физически не может убить сессию, которая ждёт результата вызова (только сам вызов).

## Шаг 3 — зомби и orphan-MCP на Linux (проще Мака — нет launchd)

```bash
ps -Ao pid,ppid,etime,state,ucomm | awk '$4 ~ /^Z/'   # кто завис, чей родитель
ps -o ppid= -p <PID_родителя_зомби>                    # родитель родителя (systemd = pid 1)
```

- Родитель зомби `ppid=1` → уже усыновлён `systemd` (аналог launchd), он сам пожнёт — не
  трогать.
- Родитель — `cron`/`sh` (обычный класс на Маяке, видно в логе `_proc_patrol_[машина флота].log`)
  → безвредно, `cron` сам подчищает при следующем тике; патруль только докладывает.
- orphan-MCP (телеграм/whatsapp mcp-сервер без живого родителя) → `proc_patrol.py` убивает
  сам, ничего руками делать не нужно.

## Шаг 4 — ВЕРИФИКАЦИЯ

```bash
python3 ~/.claude/scripts/proc_patrol.py --verify              # schedule+state свежие
python3 ~/.claude/scripts/headless_llm_watchdog.py --verify    # schedule+state свежие
tail -20 ~/.claude/scripts/_proc_patrol_[машина флота].log
tail -20 ~/.claude/scripts/_headless_llm_watchdog_[машина флота].log
```

Оба сторожа алярмят в шину (`bus_send.py ALL`) только когда есть находка (`dirty`/`kill_list`
непустой) — тишина = чисто, по канону §5.5. `headless_llm_watchdog` дополнительно сверяет
PID-ы с прошлым тиком и не долбит шину повторно за тот же самый висяк, пока он ещё дожимается.

## Связанное
- Движки: `~/.claude/scripts/proc_patrol.py` (общий, флот), `~/.claude/scripts/headless_llm_watchdog.py` (локальный, Маяк)
- Тесты: `_test_proc_patrol.py`, `_test_headless_llm_watchdog.py` (fake-снапшоты, без реальных kill)
- Память: [[inbox-robot-hang-guard]] (MAXSEC=900 источник), [[proc-patrol-robot]], [[watchdog-must-verify-the-item]] (§5.5)
- Мак-близнец: `local-mac-clean` (тот же класс проблем, launchd вместо cron, зомби-развилка сложнее из-за ActivityWatch)
- Win-близнец: `local-win-clean` — НЕ построен, задача на хабе (Task Scheduler / taskkill)
