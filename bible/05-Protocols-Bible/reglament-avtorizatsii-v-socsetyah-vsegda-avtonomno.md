---
title: "Авторизации/логины в Telegram и соцсетях/мессенджерах — ВСЕГДА автономно, сам, проактивно"
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
supersedes_partial: "reglament-maksimalnaya-avtonomnost-ekonom-vremya-antona §3 (для домена соц/мессенджер-логинов, где креды+2FA уже в store)"
tags: [регламент, библия, автономность, авторизация, логины, telegram, anton-original]
concept: "[[concept-bible-platinum]]"
aliases: ["Логины в TG автономно", "Авторизации в соцсетях сам", "Social/messenger auth autonomous"]
---

**Правило (Антон, 2026-06-27, дословно):** *«ВСЕГДА ДЕЛАЙ ВСЕ АВТОРИЗАЦИИ В ТГ и ДРУГИЕ СОЦ СЕТИ / МЕССЕНДЖЕРЫ — МАКСИМАЛЬНО АВТОНОМНО БЕЗ ЮЗЕРА / МЕНЯ САМ ПРОАКТИВНО!!!»* (origin: anton). Подтверждено на месте: «да логинь хаб ДА!!!».

Касается ВСЕХ акторов (живые ассистенты + AI). Возникло из FIX B (своя @[рабочий аккаунт]-сессия на каждой машине, чтобы убить `AuthKeyDuplicated`): я переспросил «логинить ли хаб?» — Антон ответил, что переспрашивать на логине НЕ надо, делать сам.

**Норма.**
1. **Логин/авторизацию/повторный вход/выдачу сессии в Telegram и любых соцсетях/мессенджерах — выполняю САМ, до конца, проактивно.** Не выдаю Антону инструкцию «введи код / залогинься» и не жду его «да» на сам факт входа.
2. **OTP/код — забираю сам** (из чата 777000 через свою сессию/MCP, telegram-otp-self-fetch [internal]); **2FA-пароль — беру из store** (`secrets\telegram_2fa.env` и т.п., credential-store [internal] — «используй, не только храни»). Я — менеджер паролей Антона, вставляю креды сам.
3. **Это СУЖАЕТ прежний барьер** «зову Антона на вводе пароля/2FA» ([[reglament-maksimalnaya-avtonomnost-ekonom-vremya-antona]] §3): для аккаунтов, где креды + 2FA УЖЕ в store, вход = автономно, БЕЗ эскалации. Зову Антона ТОЛЬКО если секрета реально нет в store (тогда одной фразой: какого секрета не хватает).
4. **Хард-стопы остаются** (это про РИСК, не про логин): после входа — деньги / необратимое / исходящее наружу третьим лицам / выдача секрета наружу = Tier-2 по `operating-agreement`, пауза/спрос. Сам ВХОД — не Tier-2, когда есть мандат и креды. Логин не ломает чужие сессии (Telegram разрешает много сессий на аккаунт).
5. **Link-safety** (chrome-autonomy-self-drive [internal]): не ввожу креды на незнакомом/фишинговом адресе.
6. **Свой путь к OTP мёртв → зови пира** (Антон 2026-07-04): любой пир коллаборации с живой сессией аккаунта читает код и передаёт по шине — Tier-1, Антона не звать. Механика и формат → [[reglament-piry-pomogayut-drug-drugu-s-loginami-otp-relay]].

Машинный подъём для AI-агента — `CLAUDE.md` («ALWAYS: авторизации в соцсетях автономно») + память social-auth-autonomous [internal]. Связано с minimize-user-time-autonomy [internal], credential-store [internal], telegram-account-identities [internal], telegram-otp-self-fetch [internal], machine-bus-telegram-rail [internal]. Bound by `operating-agreement`.
