---
title: "Подъём синка (Syncthing/связь между машинами) — ВСЕГДА автономно, сам, проактивно"
type: reglament
stage: distilled
origin: anton
authored_by: hybrid
ai_author: claude-opus
owner: anton
creator: anton
date_established: 2026-06-27
theme: operations
applies_to: "ассистенты + AI-агенты (все, кто действует для Антона)"
status: active
audience: both
tags: [регламент, библия, автономность, syncthing, синк, self-heal, anton-original]
concept: "[[concept-bible-platinum]]"
aliases: ["Поднимай синк сам", "Raise sync autonomously", "Синк автономно"]
---

**Правило (Антон, 2026-06-27, дословно):** *«ВСЕГДА ПОДНИМАЙ СИНК — МАКСИМАЛЬНО АВТОНОМНО БЕЗ ЮЗЕРА / МЕНЯ САМ ПРОАКТИВНО!!!»* (origin: anton).

Касается ВСЕХ акторов (живые ассистенты + AI). Когда вижу, что синк между машинами лёг (Syncthing-линк down, пир не виделся, `[шина]` молчит) — поднимаю САМ, не спрашивая «поднять ли?», и не жду, что Антон это сделает.

**Норма.**
1. **Заметил лежащий синк → СРАЗУ поднимаю** (spot-broken-always-offer-fix [internal] — но здесь сразу ДЕЙСТВУЮ, а не «предлагаю»). Не оставляю синк лежать «до подтверждения».
2. **Диагностика по корню, не симптому** (fix-root-cause-not-symptoms [internal], verify-existing-before-proposing [internal]): живой API хаба = источник истины (`/rest/system/status` myID, `/system/connections`, `/stats/device` lastSeen), НЕ один пир и НЕ config-файлы. Канон инцидента/runbook = [[reglament-chp-poterya-sinka-mezhdu-mashinami]]; скилл `/raise-sync`.
3. **Хаб-сторона — выжимаю на 100% сам:** демон жив и discoverable, watchdog дёрнут, `sync_monitor` отстреливает авто-nudge упавшему пиру в TG-группу, `machine_bus` авто-failover в TG. Эти 3 слоя self-heal = «синк чинится сам» (machine-bus-telegram-rail [internal], память sync-self-heal-layers [internal]).
4. **Истинный блок = ТОЛЬКО peer-local:** удалённо процесс на чужой машине не стартануть. Если демон пира мёртв / у пира VPN глушит P2P — поднимаю что могу с хаба (nudge + координация по шине), а недостающее peer-local действие отправляю на ту машину её роботом/оператором. Антона зову лишь когда нужен ЕГО физический ввод (его пароль/VPN на ЕГО машине) — одной фразой что мешает.
5. **Каждая машина держит свой Syncthing-watchdog** (5-мин OS-задача: демон упал→подними, API завис→рестарт, circuit-breaker против пилы) — обязательный шаг онбординга (config-safety-backup-and-migration-check [internal], [[reglament-migratsiya-mashin-playbook]]).

Машинный подъём для AI-агента — `CLAUDE.md` («ALWAYS: поднимай синк автономно») + память raise-sync-autonomous [internal]. Связано с minimize-user-time-autonomy [internal], [[reglament-chp-poterya-sinka-mezhdu-mashinami]], machine-bus-telegram-rail [internal], one-system-propagate [internal]. Bound by `operating-agreement`.
