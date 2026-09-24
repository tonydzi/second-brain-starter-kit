---
title: Fleet Machine Optimization Playbook
type: protocol
status: active
date_established: 2026-07-07
origin: anton
machine: [машина флота]
operator: Anton
tags: [fleet, performance, optimization, multi-machine]
---

# Оптимизация машины — общий плейбук флота

Директива Антона (07.07.2026): каждая машина флота прогоняет само-оптимизацию, чтобы меньше тормозила. Делать КАК HP17. Отчёт + ACK в чат 03.

## Что сделали на [машина флота] (эталон)
- Убили **28 дублей telegram-mcp** (накопились от незакрытого Claude Desktop) → **+5.6 ГБ**.
- Нашли **31-часовой Claude Desktop** = 324 процесса / 18.5 ГБ → рестарт приложения возвращает память.
- Убрали **5 из автозагрузки**: Roblox, Discord, OneDrive, Adobe Sync, Edge авто-запуск (бэкап .reg).
- Нашли **два антивируса разом** (Defender + Kaspersky) = двойное сканирование диска → оставляем ОДИН.
- Выключили фоновых диск-жоров: **SysMain, DiagTrack, DoSvc**; **ExpressVPN** → ручной (не нужен, есть Tailscale).

## Чек-лист (адаптируй под свою ОС)
1. **Дубли/зомби MCP** — накопились ли копии telegram-mcp / любого MCP от незакрытых сессий? Оставить 1 на живую сессию, лишние убить (они переподключатся).
2. **Старые сессии/приложения** — Claude Desktop открыт сутками копит процессы. Перезапустить / закрыть завершённые чаты.
3. **Автозагрузка** — убрать несущественное (игры, мессенджеры, лишние облачные синки, неиспользуемый VPN). Оставить: Syncthing, Tailscale, Claude, нужный диск-синк.
4. **Двойной антивирус** — НЕ держать два real-time AV. Выбрать один.
5. **Фоновые диск-жоры** — выключить Superfetch/телеметрию/P2P-раздачу апдейтов; исключить тяжёлые рабочие папки из индексации ОС где зря.
6. **Тяжёлый фон → на ХАБ** (правило desktop-max-laptop-min): реиндекс, эмбеддинги, архивы, ночные watcher → хаб, не пиры.
7. **Отчёт**: RAM до/после · топ-потребители · что отключил · что требует ОК оператора.

## Per-OS
- **Windows** (хаб [машина флота], [коллега] MYOWNPC): Task Manager → Автозагрузка; services.msc; скан дублей python/node MCP.
- **Mac** ([машина флота], [коллега]): System Settings → General → Login Items; Activity Monitor (RAM/CPU); дубли node/python MCP; обычно нет двойного AV.
- **VPS-Маяк** (Linux headless): runaway python/node, дубли MCP, systemd-службы, память; это якорь — эссеншелы не трогать.

Связано: desktop-max-laptop-min [internal], machine-bus-telegram-rail [internal], one-system-propagate [internal].
