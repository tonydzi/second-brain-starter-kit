---
title: "MOC — Holy Bible (Platinum регламенты)"
aliases:
- MOC Holy Bible
- Библия MOC
- регламенты MOC
tags:
- MOC
- holy-bible
- governance
- sop
type: moc
language: ru
status: active
generated_by: tools/gen_moc_bible.py
summary: "Статическая навигация по своду регламентов: 287 файла в 05-Protocols-Bible, сгруппированы по theme. Без dataview — все ссылки разрешаются в этом репозитории."
---

# MOC — Holy Bible (Platinum регламенты)

> Сгенерировано `tools/gen_moc_bible.py` из фактического содержимого `05-Protocols-Bible/`. Не редактировать руками — правка переживёт только до следующей регенерации. Проверка на дрейф: `python3 tools/gen_moc_bible.py --check`.

**Корпус:** 287 правил в `05-Protocols-Bible/`. Это дистиллят — сырой Telegram-корпус (2005 нот) в экспорт не входит и здесь не адресуется.

## ⛔ Safety floor — `must` / `STOP` (61)

Правила, которые бьют свежесть: новое правило без явного `priority` их не отменяет (precedence-лестница, правило 0).

- [Alpha Protocol — перед стратегическим решением: Recall + Deep Research + Synthesis (не реализуем на одном recall)](../05-Protocols-Bible/protocol-alpha-protocol-recall-plus-deep-research.md) — research-protocol
- [Протокол «Привратник»: заявка на вступление = бан-фри доступ к людям](../05-Protocols-Bible/protocol-gatekeeper-join-request-funnel.md) — без темы
- [Anti-leak на ВЫХОДЕ, не на сборе — приватный корпус читаем целиком, барьер на исходящем](../05-Protocols-Bible/reglament-anti-leak-na-vyhode.md) — privacy · `STOP`
- [ЧП «компьютеры не видят друг друга»: аудит потери синка, КОРЕНЬ, профилактика и план действий](../05-Protocols-Bible/reglament-chp-poterya-sinka-mezhdu-mashinami.md) — machine-ops
- [Подпись контента - «придумано Майкрофтом и Тони, Palo Alto AI Research Lab» + CTA](../05-Protocols-Bible/reglament-content-attribution-mycroft-anton.md) — без темы
- [Кросс-машинная авторизация: одобрил на одной машине = действует на всех; не переспрашивать](../05-Protocols-Bible/reglament-cross-machine-authorization-ne-pereprashivat.md) — machine-ops
- [Дата и время — в НАЧАЛЕ и в КОНЦЕ каждого ответа Антону](../05-Protocols-Bible/reglament-data-vremya-v-nachale-i-konce-kazhdogo-otveta.md) — communication
- [Деньги / обязательства / сомнение / незнакомец → СТОП, эскалация Антону, не отвечай сам](../05-Protocols-Bible/reglament-dengi-obyazatelstva-somnenie-neznakomec-stop-eskalaciya.md) — warm-maintenance · `COMPOSE`
- [Дистанционное одобрение (QQQ) — пингуй Антона в чате, он подтверждает с телефона](../05-Protocols-Bible/reglament-distancionnoe-odobrenie-qqq.md) — multi-machine-comms
- [Дневной потолок ИНИЦИАЦИЙ на аккаунт ~15 (новый — 5–10); ответы знакомым не считаются](../05-Protocols-Bible/reglament-dnevnoj-potolok-iniciacij-na-akkaunt.md) — warm-maintenance · `COMPOSE`
- [Запустил долгий процесс — проверяй, что он ЖИВ, ~каждые 20 минут (liveness)](../05-Protocols-Bible/reglament-dolgiy-protsess-proveryat-zhiv-li-on-kazhdye-20-minut.md) — governance
- [Естественный джиттер + утренний разгон очереди: не пачкой в одну секунду и не всё ровно в 08:00](../05-Protocols-Bible/reglament-dzhitter-i-utrennij-razgon-ocheredi.md) — warm-maintenance · `NEW`
- [Элитные крипто-комьюнити → НИКАКОГО холодного DM, только value-first / тёплое интро](../05-Protocols-Bible/reglament-elitnye-kripto-komyuniti-zero-cold-dm-value-first.md) — outreach · `STOP`
- [Файл «не нашёлся» — сначала проверить, НЕ пересоздавать (может просто доезжать по синку или искался не там)](../05-Protocols-Bible/reglament-fayl-ne-nashelsya-snachala-proverit-ne-peresozdavat.md) — provenance-operations
- [Фоновая/крон-задача — ВСЕГДА с жёстким таймаутом и убийцей всего дерева процессов](../05-Protocols-Bible/reglament-fonovaya-zadacha-vsegda-s-taymautom-i-ubiytsey-dereva.md) — ai-operations
- [Голосовое — РЕДКО и только живым голосом Антона; синтетику/TTS НИКОГДА](../05-Protocols-Bible/reglament-golosovoe-redko-i-tolko-zhivym-golosom.md) — warm-maintenance · `COMPOSE`
- [Как пирам общаться в каждом канале — единый конверт + точка встречи на канал](../05-Protocols-Bible/reglament-kak-piram-obshchatsya-v-kazhdom-kanale.md) — multi-machine-comms
- [Как ПРАВИЛЬНО писать в MEMORY.md (always-loaded индекс памяти)](../05-Protocols-Bible/reglament-kak-pravilno-pisat-v-memory-md.md) — ai-operations
- [Открывай НОВОЙ правдивой деталью; нет детали — честный нейтральный заход, но НЕ выдумывай](../05-Protocols-Bible/reglament-kazhdyj-ping-novaya-pravdivaya-detal-ili-chestnyj-zahod.md) — warm-maintenance · `COMPOSE`
- [Перед правкой sensitive-файла или межмашинным консенсусом — проверь, не работает ли параллельная сессия над тем же, и сначала договорись (координация против гонок за общий файл)](../05-Protocols-Bible/reglament-koordinatsiya-sessiy-pered-pravkoy-sensitive-failov.md) — multi-machine-operations
- [НЕ подделывай опечатки и не имитируй «человеческое несовершенство» искусственно](../05-Protocols-Bible/reglament-ne-poddelyvaj-opechatki-i-nesovershenstvo.md) — warm-maintenance · `NEW`
- [Раз в неделю майнить альфу из ВСЕЙ документации наших инструментов](../05-Protocols-Bible/reglament-nedelnyy-mayning-alfy-iz-dokumentacii.md) — ai-operations
- [Пиши его неформальным регистром (строчные + его пунктуация), а не отшлифованным официозом](../05-Protocols-Bible/reglament-neformalnyj-registr-antona-ne-oficioz.md) — warm-maintenance · `COMPOSE`
- [Регламент — нервная система машин = всегда без LLM; тупой детектор первым, LLM только на мышление](../05-Protocols-Bible/reglament-nervnaya-sistema-mashin-bez-llm-tupoy-detektor-pervym.md) — без темы
- [Никогда один и тот же текст пачкой — у каждого имя + правдивая личная отсылка](../05-Protocols-Bible/reglament-nikogda-odinakovyj-tekst-pachkoj.md) — warm-maintenance · `COMPOSE`
- [Ночная автономность — пока Антон спит, работай максимально сам](../05-Protocols-Bible/reglament-nochnaya-avtonomnost-poka-anton-spit.md) — ai-operations
- [Новый контакт → сразу карточка в CRM (нулевая задержка)](../05-Protocols-Bible/reglament-novyy-kontakt-srazu-v-crm.md) — crm-outreach
- [Каждый Deep Research получает номер DRYY-MM-DD-NN + строку в реестре](../05-Protocols-Bible/reglament-numeratsiya-dr-i-reestr.md) — ai-operations
- [Весь сгенерированный контент получает номер NOTEYY-MM-DD-МАШИНА-NN + строку в реестре](../05-Protocols-Bible/reglament-numeratsiya-kontenta-note-i-reestr.md) — ai-operations
- [Осознанное согласие — объясни ЗАЧЕМ перед действием (особенно связывание машин); вожак тоже осознанно понимает ведомого и не творит ереси](../05-Protocols-Bible/reglament-osoznannoe-soglasie-obyasni-zachem-pered-svyazyvaniem-mashin.md) — communications-protocol
- [Сначала искренний интерес, потом вопрос (touch-base по [человек])](../05-Protocols-Bible/reglament-outreach-genuine-interest-first.md) — outreach
- [Пауза перед отправкой = время «прочитать + набрать», пропорционально длине, не мгновенно](../05-Protocols-Bible/reglament-pauza-pered-otpravkoj-chtenie-plus-nabor.md) — warm-maintenance · `NEW`
- [PeerFlood / FloodWait / спам-блок → немедленный СТОП на сутки + эскалация Антону, не обходить](../05-Protocols-Bible/reglament-peerflood-floodwait-stop-i-eskalaciya.md) — warm-maintenance · `COMPOSE`
- [Регламент — перед изменением системы сверься с картой (/arch)](../05-Protocols-Bible/reglament-pered-izmeneniem-sistemy-sverstis-s-kartoy-arch.md) — без темы
- [Перед ЛЮБОЙ активностью — сначала RECALL всего, что у нас есть по теме (весь волт + RAG)](../05-Protocols-Bible/reglament-pered-lyuboy-aktivnostyu-snachala-recall-vsego-volt-i-rag.md) — governance
- [Перед необратимым/важным — предупреди и жди; перед «готово» — перепроверь себя](../05-Protocols-Bible/reglament-pered-neobratimym-vazhnym-predupredi-i-zhdi-pered-gotovo-pereproveris.md) — communications-protocol
- [Переменная задержка по живости диалога: горячо → минуты, обычно → до часа-полутора, возобновление → часы; НИКОГДА не фиксированная](../05-Protocols-Bible/reglament-peremennaya-zaderzhka-po-zhivosti-dialoga.md) — warm-maintenance · `NEW`
- [Нужно подтверждение/действие Антона на экране — УБЕДИСЬ, что он реально это видит, и ДАЙ скриншот (не гоняй вслепую)](../05-Protocols-Bible/reglament-podtverzhdenie-na-ekrane-ubedis-chto-anton-vidit-day-skrin.md) — operations-ux
- [Каждую сессию Claude Code помечать АВТОРОМ = машина + человек (кто и на каком компьютере делал работу)](../05-Protocols-Bible/reglament-pomechat-mashinu-na-kazhdoy-sessii.md) — provenance-operations
- [Правило Connect — эстафета ответственности: владей задачей до результата, держи конвейер A→Z, подсвечивай обрыв](../05-Protocols-Bible/reglament-pravilo-connect-esafeta-otvetstvennosti.md) — ai-operations
- [Каперство — нагло, но легально; никогда фрод (для всех, кто действует ОТ ЛИЦА Антона наружу)](../05-Protocols-Bible/reglament-privateer-bold-but-legal-never-fraud.md) — без темы
- [Проактивно предлагай DR, когда документация/прогресс опережает обучение LLM](../05-Protocols-Bible/reglament-proaktivno-predlagay-dr-kogda-doki-operezhayut-obuchenie.md) — ai-operations
- [Браузерная работа (окна Chrome, бук звонков) — каждая машина делает СВОЮ строго САМА, локально; никакого кросс-машинного диспатча; хаб не отвлекаем](../05-Protocols-Bible/reglament-rabota-s-brauzerom-na-pirah-ne-na-habe.md) — machine-ops
- [Раскатка фиксов: распаковывай посылки/апдейты НЕМЕДЛЕННО + деплой-манифест](../05-Protocols-Bible/reglament-raskatka-fiksov-deploy-manifest.md) — machine-ops
- [Шина клана не зависит от Telegram-MCP + у КАЖДОЙ машины своя TG-сессия (лечим AuthKeyDuplicated)](../05-Protocols-Bible/reglament-shina-telegram-bez-mcp-i-svoya-sessiya-na-mashinu.md) — machine-ops
- [Синхронизация всех акторов — через Telegram-чат 03, первично и обязательно](../05-Protocols-Bible/reglament-sinhronizaciya-cherez-telegram-03.md) — machine-ops
- [Сначала прочитай последние 10 сообщений и ответь на ТО, что человек реально написал](../05-Protocols-Bible/reglament-snachala-prochitaj-poslednie-10-i-otvet-na-vhodyashchee.md) — warm-maintenance · `COMPOSE`
- [Всплыла старая тема / инцидент → СНАЧАЛА RECALL, потом копай; и истину бери из ЖИВОГО источника, не со стале-копии](../05-Protocols-Bible/reglament-snachala-recall-potom-kopay-i-istina-iz-zhivogo-istochnika.md) — ways-of-working
- [Реглумент: standing-мандат на исходящее + пакетное одобрение 1×/день](../05-Protocols-Bible/reglament-standing-mandat-ishodyashchee-paketnoe-odobrenie.md) — outreach-operations
- [Тексты Антона до 2023 включительно — человеческое золото (приоритет для голоса и обучения)](../05-Protocols-Bible/reglament-teksty-do-2023-chelovecheskoe-zoloto-prioritet-golosa.md) — data-provenance-voice
- [Регламент: Telegram-автоматизации — ВСЕГДА свой обычный аккаунт, НЕ боты](../05-Protocols-Bible/reglament-telegram-avtomatizatsii-svoy-akkaunt-ne-boty.md) — без темы
- [Транскрипты видео → youtube-transcript-api ПЕРВЫМ; Whisper (GPU) только для видео, одобренных Антоном ГОЛОСОМ; экономь ресурсы](../05-Protocols-Bible/reglament-transkripty-api-pervym-whisper-tolko-golosom-odobrennoe.md) — resource-economy
- [Триггер «03» / «теперь вы сами» — машины сами находят консенсус и сами исполняют, Антона не дёргают](../05-Protocols-Bible/reglament-trigger-03-avtonomnyy-konsensus-mashin.md) — multi-machine-comms
- [Варьируй зачин РАЗНЫМ СОДЕРЖАНИЕМ — никакой копипасты первой строки между контактами](../05-Protocols-Bible/reglament-varjiruj-zachin-net-kopipasty-mezhdu-kontaktami.md) — warm-maintenance · `COMPOSE`
- [Все артефакты ВСЕГДА сохраняем в волт — забрать, сохранить, реиндексировать, перелинковать](../05-Protocols-Bible/reglament-vse-artefakty-vsegda-v-volt-pereindeks-perelinkovka.md) — second-brain
- [Регламент — ВСЕ нотификации и крики CC в Telegram идут в ЧАТ 03 (bus-группа)](../05-Protocols-Bible/reglament-vse-notifikatsii-i-kriki-cc-v-chat-03.md) — без темы
- [Всегда хвали источник вдохновения - huge thanks, теги, отсылки; мы не воруем, мы реверс-инжинирим с поклоном](../05-Protocols-Bible/reglament-vsegda-hvali-istochnik-vdohnoveniya.md) — content · `COMPOSE`
- [Для тёплого поддержания сообщение БЕЗ вопроса/CTA допустимо (carve-out к «всегда нужен вопрос»)](../05-Protocols-Bible/reglament-warm-soobshchenie-bez-cta-dopustimo-carveout.md) — warm-maintenance · `COMPOSE`
- [Окно бодрствования: писать только 08:00–23:00 по локальному времени Антона, ночью молчать](../05-Protocols-Bible/reglament-warm-window-08-23-chasy-antona.md) — warm-maintenance · `NEW`
- [Профиль аккаунта живой и заполненный (фото/имя/био); изменения профиля — только после «да» Антона (Tier-2)](../05-Protocols-Bible/reglament-zhivoj-zapolnennyj-profil-pered-zapuskom.md) — warm-maintenance · `COMPOSE`
- [Журнал задач — сделанные и несделанные, с перелинковкой; несделанная попадает в реестр СРАЗУ](../05-Protocols-Bible/reglament-zhurnal-zadach-sdelannye-i-nesdelannye-s-perelinkovkoy.md) — ai-operations

## Правила по темам

| Тема | Правил |
|---|---:|
| communications-protocol | 128 |
| без темы | 63 |
| warm-maintenance | 20 |
| ai-operations | 16 |
| machine-ops | 7 |
| social-media | 5 |
| operations | 4 |
| operations-governance | 4 |
| multi-machine-comms | 3 |
| governance | 3 |
| communication | 2 |
| outreach | 2 |
| provenance-operations | 2 |
| content-factory | 2 |
| research-protocol | 1 |
| ai-native | 1 |
| process-quality | 1 |
| privacy | 1 |
| data-architecture | 1 |
| content-pipeline | 1 |
| multi-machine-operations | 1 |
| crm-outreach | 1 |
| communications | 1 |
| decision-hygiene | 1 |
| operations-ux | 1 |
| knowledge-search | 1 |
| machine-governance | 1 |
| data-quality-vault | 1 |
| positioning-security | 1 |
| operations-safety | 1 |
| ways-of-working | 1 |
| cost-control | 1 |
| outreach-operations | 1 |
| data-provenance-voice | 1 |
| resource-economy | 1 |
| data-processing | 1 |
| second-brain | 1 |
| content | 1 |
| calls-pipeline | 1 |
| memory-architecture | 1 |

### communications-protocol (128)

- [Автономный монитор звонков BB Platinum — бот сам следит за календарём, пингует команду и шлёт follow-up по approve](../05-Protocols-Bible/reglament-avtonomnyy-monitor-zvonkov-bb-platinum.md) · 2026-06-23
- [Букинг звонков через чат «Календарь» — ТОЛЬКО BB Platinum (Детковский A2 пока не трогаем)](../05-Protocols-Bible/reglament-buking-zvonkov-bb-platinum.md) · 2026-06-23
- [коллекнтивные звонки правило](../05-Protocols-Bible/reglament-card-kollekntivnye-zvonki-pravilo.md)
- [правила дозвона до антона](../05-Protocols-Bible/reglament-card-pravila-dozvona-do-antona.md)
- [правила использования chatgpt](../05-Protocols-Bible/reglament-card-pravila-ispolzovaniya-chatgpt.md)
- [правила обработки аудио и рабочей нагрузки](../05-Protocols-Bible/reglament-card-pravila-obrabotki-audio-i-rabochey-nagruzki.md)
- [правила отчётов в чате ассистентов](../05-Protocols-Bible/reglament-card-pravila-otchetov-v-chate-assistentov.md)
- [правила пользования чатом gpt](../05-Protocols-Bible/reglament-card-pravila-polzovaniya-chatom-gpt.md)
- [правила работы с gpt чатом антона](../05-Protocols-Bible/reglament-card-pravila-raboty-s-gpt-chatom-antona.md)
- [правило чатов с учителями и школами](../05-Protocols-Bible/reglament-card-pravilo-chatov-s-uchitelyami-i-shkolami.md)
- [правило делать промежуточный отчет](../05-Protocols-Bible/reglament-card-pravilo-delat-promezhutochnyy-otchet.md)
- [правило делегирования срочных дозвонов по важным вопросам работникам в португалии](../05-Protocols-Bible/reglament-card-pravilo-delegirovaniya-srochnyh-dozvonov-po-vazhnym-vop.md)
- [правило для отчетов в чат с антоном](../05-Protocols-Bible/reglament-card-pravilo-dlya-otchetov-v-chat-s-antonom.md)
- [правило дозвона антону](../05-Protocols-Bible/reglament-card-pravilo-dozvona-antonu.md)
- [правило дозвона антону по срочным задачам](../05-Protocols-Bible/reglament-card-pravilo-dozvona-antonu-po-srochnym-zadacham.md)
- [правило дозвона до антона](../05-Protocols-Bible/reglament-card-pravilo-dozvona-do-antona.md)
- [правило дозвона до антона по срочным задачам](../05-Protocols-Bible/reglament-card-pravilo-dozvona-do-antona-po-srochnym-zadacham.md)
- [правило дозвона в случае ранних записей антона](../05-Protocols-Bible/reglament-card-pravilo-dozvona-v-sluchae-rannih-zapisey-antona.md)
- [правило фиксации задач в отчёте](../05-Protocols-Bible/reglament-card-pravilo-fiksatsii-zadach-v-otchete.md)
- [правило использования gpt](../05-Protocols-Bible/reglament-card-pravilo-ispolzovaniya-gpt.md)
- [правило коллективных звонков](../05-Protocols-Bible/reglament-card-pravilo-kollektivnyh-zvonkov.md)
- [правило коммуникации с денисом по рабочим чатам](../05-Protocols-Bible/reglament-card-pravilo-kommunikatsii-s-denisom-po-rabochim-chatam.md)
- [правило контролировать отчеты риты по общественным работам](../05-Protocols-Bible/reglament-card-pravilo-kontrolirovat-otchety-rity-po-obschestvennym-ra.md)
- [правило начинать день с плана и заканчивать отчетом](../05-Protocols-Bible/reglament-card-pravilo-nachinat-den-s-plana-i-zakanchivat-otchetom.md)
- [правило о приоритете связи по задачам через звонок](../05-Protocols-Bible/reglament-card-pravilo-o-prioritete-svyazi-po-zadacham-cherez-[человек].md)
- [правило о рабочих звонках митах с антоном](../05-Protocols-Bible/reglament-card-pravilo-o-rabochih-zvonkah-mitah-s-antonom.md)
- [правило о суммарном учете времени в отчете](../05-Protocols-Bible/reglament-card-pravilo-o-summarnom-uchete-vremeni-v-otchete.md)
- [правило обогащения голосовых сообщений в чатах](../05-Protocols-Bible/reglament-card-pravilo-obogascheniya-golosovyh-soobscheniy-v-chatah.md)
- [правило оформления отчета на задачи](../05-Protocols-Bible/reglament-card-pravilo-oformleniya-otcheta-na-zadachi.md)
- [правило оформления отчета по задачам](../05-Protocols-Bible/reglament-card-pravilo-oformleniya-otcheta-po-zadacham.md)
- [правило отчета по задачам](../05-Protocols-Bible/reglament-card-pravilo-otcheta-po-zadacham.md)
- [правило перевода голосовых сообщений в чатах](../05-Protocols-Bible/reglament-card-pravilo-perevoda-golosovyh-soobscheniy-v-chatah.md)
- [правило переводов в чатах сообщений не на русском и не на англ языке](../05-Protocols-Bible/reglament-card-pravilo-perevodov-v-chatah-soobscheniy-ne-na-russkom-i.md)
- [правило по составлению ответов на вопросы с использованием chatgpt](../05-Protocols-Bible/reglament-card-pravilo-po-sostavleniyu-otvetov-na-voprosy-s-ispolzovan.md)
- [правило поэтапной отчётности в рабочих чатах](../05-Protocols-Bible/reglament-card-pravilo-poetapnoy-otchetnosti-v-rabochih-chatah.md)
- [правило пояснять комментировать выставленные в чат материалы](../05-Protocols-Bible/reglament-card-pravilo-poyasnyat-kommentirovat-vystavlennye-v-chat-mat.md)
- [правило пропущенных звонков](../05-Protocols-Bible/reglament-card-pravilo-propuschennyh-zvonkov.md)
- [правило проведения коллективных звонков](../05-Protocols-Bible/reglament-card-pravilo-provedeniya-kollektivnyh-zvonkov.md)
- [правило распределения тз по чатам](../05-Protocols-Bible/reglament-card-pravilo-raspredeleniya-tz-po-chatam.md)
- [правило тайминга задач в отчетах](../05-Protocols-Bible/reglament-card-pravilo-tayminga-zadach-v-otchetah.md)
- [правило указания задач в отчёте](../05-Protocols-Bible/reglament-card-pravilo-ukazaniya-zadach-v-otchete.md)
- [правило в первую очередь звонить](../05-Protocols-Bible/reglament-card-pravilo-v-pervuyu-ochered-zvonit.md)
- [правило закрепления информации в чатах для антона](../05-Protocols-Bible/reglament-card-pravilo-zakrepleniya-informatsii-v-chatah-dlya-antona.md)
- [правило запросов gpt](../05-Protocols-Bible/reglament-card-pravilo-zaprosov-gpt.md)
- [Даём информацию о планах и итогах за день только в конкретных показателях — в](../05-Protocols-Bible/reglament-daem-informatsiyu-o-planah-i-itogah-za-den-tolko-v-konk.md) · 2025-01-25
- [Если Антон даёт задачу, нужно немедленно приступить к выполнению или сразу](../05-Protocols-Bible/reglament-esli-anton-daet-zadachu-nuzhno-nemedlenno-pristupit-k-v.md) · 2025-10-22
- [Если Антон или Анна дали задачу — она требует дословного исполнения. Если](../05-Protocols-Bible/reglament-esli-anton-ili-anna-dali-zadachu-ona-trebuet-doslovnogo.md) · 2023-03-13
- [Если Антон продиктовал голосовое сообщение, которое кому-то предназначается, с](../05-Protocols-Bible/reglament-esli-anton-prodiktoval-golosovoe-soobschenie-kotoroe-ko.md) · 2026-03-20
- [Если Антону нужно скинуть срочную информацию, кидаем в оба аккаунта Telegram и](../05-Protocols-Bible/reglament-esli-antonu-nuzhno-skinut-srochnuyu-informatsiyu-kidaem.md) · 2024-12-27
- [Если Антону нужно скинуть срочную информацию в личку, кидаем на оба аккаунта:](../05-Protocols-Bible/reglament-esli-antonu-nuzhno-skinut-srochnuyu-informatsiyu-v-lich.md) · 2024-12-26
- [Если ассистент отсутствует на планерке 5 минут, необходимо срочно связаться с](../05-Protocols-Bible/reglament-esli-assistent-otsutstvuet-na-planerke-5-minut-neobhodi.md) · 2026-02-24
- [Если ассистенту поставили задачу, пишем: «Задачу приняла…», срок исполнения …](../05-Protocols-Bible/reglament-esli-assistentu-postavili-zadachu-pishem-zadachu-prinya.md) · 2026-01-07
- [Если информация, которую попросил найти Антон, содержит больше одного абзаца](../05-Protocols-Bible/reglament-esli-informatsiya-kotoruyu-poprosil-nayti-anton-soderzh.md) · 2025-12-31
- [Если информация (отчёт) для Антона занимает более чем 2 прокрутки, её](../05-Protocols-Bible/reglament-esli-informatsiya-otchet-dlya-antona-zanimaet-bolee-che.md) · 2025-06-04
- [Если мы видим, что бот перевёл (расшифровал) что-либо некорректно — мы](../05-Protocols-Bible/reglament-esli-my-vidim-chto-bot-perevel-rasshifroval-chto-libo-n.md) · 2025-06-29
- [Если требуется получить от Антона срочную информацию, необходимо дозваниваться](../05-Protocols-Bible/reglament-esli-trebuetsya-poluchit-ot-antona-srochnuyu-informatsi.md) · 2026-03-25
- [Исходящее от лица Антона — его голосом, без детского ELI5-пересказа](../05-Protocols-Bible/reglament-ishodyaschie-golosom-antona-bez-detskogo-eli5.md) · 2026-06-10
- [Каждое утро мы должны прослушать и прочитать все сообщения, накопившиеся со](../05-Protocols-Bible/reglament-kazhdoe-utro-my-dolzhny-proslushat-i-prochitat-vse-soob.md) · 2025-04-10
- [Каждый день Оксана или [коллега] созваниваются с Денисом, проходят по задачам,](../05-Protocols-Bible/reglament-kazhdyy-den-oksana-ili-[человек]-sozvanivayutsya-s-den.md) · 2026-02-10
- [Каждый раз, когда Антон дал какую-то задачу, нужно изучать её и решение через](../05-Protocols-Bible/reglament-kazhdyy-raz-kogda-anton-dal-kakuyu-to-zadachu-nuzhno-iz.md) · 2025-06-27
- [Каждый раз, когда нужно пингануть лида (под сдачу Антона или для себя), всегда](../05-Protocols-Bible/reglament-kazhdyy-raz-kogda-nuzhno-pinganut-lida-pod-sdachu-anton.md) · 2025-04-11
- [Каждый раз, когда пишем в личку, дублируем информацию в чатах.](../05-Protocols-Bible/reglament-kazhdyy-raz-kogda-pishem-v-lichku-dubliruem-informatsiy.md) · 2025-12-02
- [Каждый раз пишем утром «на смене» и план на день. День завершаем сообщением «не](../05-Protocols-Bible/reglament-kazhdyy-raz-pishem-utrom-na-smene-i-plan-na-den-den-zav.md) · 2024-11-21
- [Каждый сотрудник при входе на смену пишет в чат «на смену», затем — список](../05-Protocols-Bible/reglament-kazhdyy-sotrudnik-pri-vhode-na-smenu-pishet-v-chat-na-s.md) · 2025-06-29
- [Коды входа в Telegram и любые OTP ассистент достаёт САМ из служебного чата, не дёргает Антона](../05-Protocols-Bible/reglament-kody-vhoda-i-otp-assistent-dostaet-sam-iz-sluzhebnogo-chata.md) · 2026-06-15
- [Когда нужно напомнить Антону о чём-либо — ставим напоминание в календарь [email] длительностью 1 час](../05-Protocols-Bible/reglament-kogda-nuzhno-napomnit-antonu-stavim-napominanie-v-cal.md) · 2026-06-14
- [Всем коллегам подключаем ВСЕ 4 наших Telegram (@… · @… · @… · @…) для работы с лидами CRM с их компьютера](../05-Protocols-Bible/reglament-kollegam-podklyuchaem-vse-4-telegram-dlya-raboty-s-lidami.md) · 2026-06-25
- [Конкретному собеседнику — только проверяемые факты, которые Антон мог бы сказать](../05-Protocols-Bible/reglament-konkretnomu-sobesedniku-tolko-proveryaemye-fakty.md) · 2026-06-10
- [Текст без проверки Антоном → ≤5 (макс 7) слов, тон по каналу (FB-шутка / Telegram-осмысленно)](../05-Protocols-Bible/reglament-korotkiy-tekst-bez-proverki-ton-po-kanalu.md) · 2026-07-04
- [Любое правило в Библию писать максимально дословно со слов Антона, чтобы было](../05-Protocols-Bible/reglament-lyuboe-pravilo-v-bibliyu-pisat-maksimalno-doslovno-so-s.md) · 2026-02-25
- [Не выносить наружу чужие приватные данные — даже если они в контексте](../05-Protocols-Bible/reglament-ne-utekat-chuzhie-privatnye-dannye-naruzhu.md) · 2026-06-10
- [О звонках предупреждают Катя и [коллега] по очереди. Если звонки ранним утром —](../05-Protocols-Bible/reglament-o-zvonkah-preduprezhdayut-[человек]-i-[коллега]-po-ocheredi-e.md) · 2026-03-18
- [Объяснять и отчитываться Антону простыми словами (как пятилетнему) — без жаргона](../05-Protocols-Bible/reglament-obyasnyat-i-otchityvatsya-antonu-prostymi-slovami-eli5.md) · 2026-06-14
- [Одна база лидов · каждый оператор пишет со СВОЕЙ машины · читай живой тред перед отправкой · предупреждай, не блокируй](../05-Protocols-Bible/reglament-odna-baza-lidov-kazhdyy-pishet-so-svoey-mashiny-chitay-tred.md) · 2026-06-27
- [Осознанное согласие — объясни ЗАЧЕМ перед действием (особенно связывание машин); вожак тоже осознанно понимает ведомого и не творит ереси](../05-Protocols-Bible/reglament-osoznannoe-soglasie-obyasni-zachem-pered-svyazyvaniem-mashin.md) · 2026-06-26
- [Telegram от лица Антона — аккаунт по самому ТЁПЛОМУ треду (личный @… + рабочие @…/@… = голос Антона; @… = компания/служебное); текст не согласуем](../05-Protocols-Bible/reglament-ot-litsa-antona-v-telegram-rabotaem-s-[рабочий аккаунт].md) · 2026-06-15
- [Отвечать контакту на ЕГО языке (как он написал), не по умолчанию](../05-Protocols-Bible/reglament-otvechat-kontaktu-na-ego-yazyke.md) · 2026-06-10
- [Перед необратимым/важным — предупреди и жди; перед «готово» — перепроверь себя](../05-Protocols-Bible/reglament-pered-neobratimym-vazhnym-predupredi-i-zhdi-pered-gotovo-pereproveris.md) · 2026-06-14
- [Планёрки обязательны, и на это время нельзя назначать никаких встреч.](../05-Protocols-Bible/reglament-planerki-obyazatelny-i-na-eto-vremya-nelzya-naznachat-n.md) · 2025-01-16
- [Ассистенты не допускают прямого общения Антона с поставщиками и подряд](../05-Protocols-Bible/reglament-pokupki-assistenty-ne-dopuskayut-pryamogo-obscheniya-antona-s-p.md) · 2025-11-27
- [Быть максимально проактивными: вызванивать контрагентов, особенно если](../05-Protocols-Bible/reglament-pokupki-byt-maksimalno-proaktivnymi-vyzvanivat-kontragentov-oso.md) · 2024-08-31
- [Для входа в любой аккаунт Антона (MyCloud, почты и др.) сначала позвон](../05-Protocols-Bible/reglament-pokupki-dlya-vhoda-v-lyuboy-akkaunt-antona-mycloud-pochty-i-dr.md) · 2025-09-21
- [Если Антон просит с кем-то связаться — сначала позвонить, и только пот](../05-Protocols-Bible/reglament-pokupki-esli-anton-prosit-s-kem-to-svyazatsya-snachala-pozvonit.md) · 2024-07-16
- [Если Антон просит запинить сообщение — переопубликовать его заново и с](../05-Protocols-Bible/reglament-pokupki-esli-anton-prosit-zapinit-soobschenie-pereopublikovat-e.md) · 2025-09-12
- [Если Антон срочно нужен для подтверждения транзакции — звонить ему в W](../05-Protocols-Bible/reglament-pokupki-esli-anton-srochno-nuzhen-dlya-podtverzhdeniya-tranzakt.md) · 2025-05-02
- [Если ищем много позиций (более трёх) — не постить в чат, а вносить в т](../05-Protocols-Bible/reglament-pokupki-esli-ischem-mnogo-pozitsiy-bolee-treh-ne-postit-v-chat.md) · 2026-01-14
- [Если на запрос Антона нужно дать более трёх позиций — оформлять всё в](../05-Protocols-Bible/reglament-pokupki-esli-na-zapros-antona-nuzhno-dat-bolee-treh-pozitsiy-of.md) · 2025-12-27
- [Если нужно согласовать покупку с Антоном — звонить ему (оба WhatsApp и](../05-Protocols-Bible/reglament-pokupki-esli-nuzhno-soglasovat-pokupku-s-antonom-zvonit-emu-oba.md) · 2025-05-29
- [Если в чате более трёх одинаковых позиций — предоставлять варианты в в](../05-Protocols-Bible/reglament-pokupki-esli-v-chate-bolee-treh-odinakovyh-pozitsiy-predostavly.md) · 2025-12-17
- [Если задача занимает более 30 минут — показать промежуточный результат](../05-Protocols-Bible/reglament-pokupki-esli-zadacha-zanimaet-bolee-30-minut-pokazat-promezhuto.md) · 2025-11-27
- [Голосовые сообщения переводить в текст дословно: по словам, смыслам и](../05-Protocols-Bible/reglament-pokupki-golosovye-soobscheniya-perevodit-v-tekst-doslovno-po-sl.md) · 2025-01-20
- [Как только голосовое переведено в текст — сразу уточнять, кто из ассис](../05-Protocols-Bible/reglament-pokupki-kak-tolko-golosovoe-perevedeno-v-tekst-srazu-utochnyat.md) · 2025-04-05
- [Каждое утро писать план дня не только в чат «Ассистанс», но и в чат «П](../05-Protocols-Bible/reglament-pokupki-kazhdoe-utro-pisat-plan-dnya-ne-tolko-v-chat-assistans.md) · 2025-12-10
- [Каждый ассистент ежедневно пишет отчёт о покупках в чат «Покупки»: как](../05-Protocols-Bible/reglament-pokupki-kazhdyy-assistent-ezhednevno-pishet-otchet-o-pokupkah-v.md) · 2025-09-06
- [Каждый ассистент каждое утро пишет план на день в чат «Покупки» (что н](../05-Protocols-Bible/reglament-pokupki-kazhdyy-assistent-kazhdoe-utro-pishet-plan-na-den-v-cha.md)
- [Каждый раз при отправке Антону картинки обязательно прикладывать ссылк](../05-Protocols-Bible/reglament-pokupki-kazhdyy-raz-pri-otpravke-antonu-kartinki-obyazatelno-pr.md) · 2025-10-23
- [Когда Антону предоставляются цифры или данные — подтверждать их пруфам](../05-Protocols-Bible/reglament-pokupki-kogda-antonu-predostavlyayutsya-tsifry-ili-dannye-podtv.md) · 2025-07-04
- [Когда на поиск потрачено более 20 минут — публиковать в чат детальный](../05-Protocols-Bible/reglament-pokupki-kogda-na-poisk-potracheno-bolee-20-minut-publikovat-v-c.md) · 2026-03-08
- [Когда нужно поделиться многими ссылками — всегда сокращать их. Запреще](../05-Protocols-Bible/reglament-pokupki-kogda-nuzhno-podelitsya-mnogimi-ssylkami-vsegda-sokrasc.md) · 2025-08-27
- [После отправки каждого письма обязательно отчитываться в чате по форма](../05-Protocols-Bible/reglament-pokupki-posle-otpravki-kazhdogo-pisma-obyazatelno-otchityvatsya.md) · 2024-03-09
- [После выполнения задачи, связанной с делегированием подрядчикам или др](../05-Protocols-Bible/reglament-pokupki-posle-vypolneniya-zadachi-svyazannoy-s-delegirovaniem-p.md) · 2025-10-23
- [После завершения исследования оформлять итог в одном сообщении с запро](../05-Protocols-Bible/reglament-pokupki-posle-zaversheniya-issledovaniya-oformlyat-itog-v-odnom.md) · 2026-01-24
- [При отправке писем проверять, чтобы в тексте и названиях вложенных фай](../05-Protocols-Bible/reglament-pokupki-pri-otpravke-pisem-proveryat-chtoby-v-tekste-i-nazvaniy.md) · 2024-02-06
- [При расшифровке голосовых сообщений с нецензурной лексикой Антона — в](../05-Protocols-Bible/reglament-pokupki-pri-rasshifrovke-golosovyh-soobscheniy-s-netsenzurnoy-l.md) · 2025-10-28
- [С подрядчиками, магазинами и любым персоналом общаться исключительно в](../05-Protocols-Bible/reglament-pokupki-s-podryadchikami-magazinami-i-lyubym-personalom-obschat.md) · 2025-12-02
- [В ежедневный отчёт включать не только совершённые и несовершённые поку](../05-Protocols-Bible/reglament-pokupki-v-ezhednevnyy-otchet-vklyuchat-ne-tolko-sovershennye-i.md) · 2025-12-29
- [В каждом переведённом голосовом сообщении указывать срок выполнения за](../05-Protocols-Bible/reglament-pokupki-v-kazhdom-perevedennom-golosovom-soobschenii-ukazyvat-s.md) · 2025-05-24
- [В разделе ChatGPT «Покупки» публиковать только задачи, связанные с пок](../05-Protocols-Bible/reglament-pokupki-v-razdele-chatgpt-pokupki-publikovat-tolko-zadachi-svya.md) · 2025-09-19
- [Вопросы Антону формулировать подробно, чтобы он понял контекст.](../05-Protocols-Bible/reglament-pokupki-voprosy-antonu-formulirovat-podrobno-chtoby-on-ponyal-k.md) · 2025-07-05
- [Все голосовые сообщения Антона переводить в текст немедленно в рабочее](../05-Protocols-Bible/reglament-pokupki-vse-golosovye-soobscheniya-antona-perevodit-v-tekst-nem.md) · 2025-01-15
- [Все карточки, номера, адреса и реквизиты передавать только текстом (не](../05-Protocols-Bible/reglament-pokupki-vse-kartochki-nomera-adresa-i-rekvizity-peredavat-tolko.md) · 2025-04-28
- [Всю приёмку и выполнение задач фиксировать текстом в общей группе. Гол](../05-Protocols-Bible/reglament-pokupki-vsyu-priemku-i-vypolnenie-zadach-fiksirovat-tekstom-v-o.md) · 2026-01-14
- [Запрещено пересылать сообщения Антона без его конкретного указания.](../05-Protocols-Bible/reglament-pokupki-zaprescheno-peresylat-soobscheniya-antona-bez-ego-konkr.md) · 2024-03-21
- [Любое предложение изменения Антону — показывать как ДО → ПОСЛЕ на его реальных данных](../05-Protocols-Bible/reglament-predlozhenie-izmeneniya-antonu-pokazyvat-do-posle-na-realnyh-dannyh.md) · 2026-06-14
- [При исправлении не предлагать, а ОТМЕНЯТЬ то, что только что сделали.](../05-Protocols-Bible/reglament-pri-ispravlenii-ne-predlagat-a-otmenyat-to-chto-tolko-c.md) · 2025-10-24
- [При назначении себя на задачу пишем коротко и по сути: формулировка задачи](../05-Protocols-Bible/reglament-pri-naznachenii-sebya-na-zadachu-pishem-korotko-i-po-su.md) · 2025-10-12
- [При оформлении события указываем автора события; для городских событий подробно](../05-Protocols-Bible/reglament-pri-oformlenii-sobytiya-ukazyvaem-avtora-sobytiya-dlya.md) · 2025-11-02
- [При переводе сообщений в чатах переводить по существу, сокращая воду. Если](../05-Protocols-Bible/reglament-pri-perevode-soobscheniy-v-chatah-perevodit-po-suschest.md) · 2025-11-25
- [Решение для Антона — самое простое и ремонтопригодное (принцип АК-47); усложнение помечать и обосновывать](../05-Protocols-Bible/reglament-reshenie-dlya-antona-samoe-prostoe-remontoprigodnoe-ak47.md) · 2026-06-14
- [Сначала мы звоним, и только если не можем дозвониться куда нужно — пишем в](../05-Protocols-Bible/reglament-snachala-my-zvonim-i-tolko-esli-ne-mozhem-dozvonitsya-k.md) · 2025-01-16
- [Стандарт заполнения календаря для Антона: 1) название встречи/события — краткое](../05-Protocols-Bible/reglament-standart-zapolneniya-kalendarya-dlya-antona-1-nazvanie.md) · 2025-01-06
- [Своевременно прописывать правила Библии и устранять уже допущенные ошибки: если](../05-Protocols-Bible/reglament-svoevremenno-propisyvat-pravila-biblii-i-ustranyat-uzhe.md) · 2025-10-25
- [В отчёте писать, что «планёрки не включены в Тотал».](../05-Protocols-Bible/reglament-v-otchete-pisat-chto-planerki-ne-vklyucheny-v-total.md) · 2025-12-31
- [Всё, что связано с покупками, ведём в проекте «Покупки»; остальное — в](../05-Protocols-Bible/reglament-vse-chto-svyazano-s-pokupkami-vedem-v-proekte-pokupki-o.md) · 2025-09-18
- [Все задачи выполняются строго по инструкции, как сказал руководитель. Каждой](../05-Protocols-Bible/reglament-vse-zadachi-vypolnyayutsya-strogo-po-instruktsii-kak-sk.md) · 2025-04-16
- [Все запросы пропускаем через ChatGPT Антона (вход через аккаунт](../05-Protocols-Bible/reglament-vse-zaprosy-propuskaem-cherez-chatgpt-antona-vhod-chere.md) · 2025-08-24
- [Всегда проверяю задачи Антона. Сначала все ответы от ChatGPT копирую в чат: в](../05-Protocols-Bible/reglament-vsegda-proveryayu-zadachi-antona-snachala-vse-otvety-ot.md) · 2025-06-29
- [Запрещено передавать задачи от сотрудника к сотруднику, если: 1) нет согласия](../05-Protocols-Bible/reglament-zaprescheno-peredavat-zadachi-ot-sotrudnika-k-sotrudnik.md) · 2025-01-26

### без темы (63)

- [Canon index — the rules that are actually executable](../05-Protocols-Bible/_CANON-INDEX.md)
- [Библия как промпт — поведенческий контракт свода (для людей и агентов)](../05-Protocols-Bible/protocol-bible-as-prompt.md) · 2026-06-07
- [Как писать новое правило в Библию — плейбук (для агента/LLM и человека)](../05-Protocols-Bible/protocol-bible-rule-authoring.md) · 2026-06-10
- [Регламент поддержки Holy Bible (самоподдержка свода)](../05-Protocols-Bible/protocol-bible-self-maintenance.md) · 2026-05-30
- [Бонусная система: структура и условия начисления](../05-Protocols-Bible/protocol-bonus-system.md) · 2026-05-30
- [Протокол проведения звонка: роли питчера и фапера](../05-Protocols-Bible/protocol-call-conduct-roles.md) · 2026-05-30
- [Протокол планирования и бронирования звонков](../05-Protocols-Bible/protocol-call-planning-scheduling.md) · 2026-05-30
- [Протокол холодного питчинга лидов](../05-Protocols-Bible/protocol-cold-pitching.md) · 2026-05-30
- [Доступы и инструменты команды (гигиена)](../05-Protocols-Bible/protocol-corporate-access-hygiene.md) · 2026-05-30
- [Протокол квалификации лидов в CRM](../05-Protocols-Bible/protocol-crm-lead-qualification.md) · 2026-05-30
- [Протокол endorsement-воронки: холодный → тёплый → интро](../05-Protocols-Bible/protocol-endorsement-intro-funnel.md) · 2026-05-30
- [Протокол: эпистемическая нейтральность и исследование неортодоксальных гипотез](../05-Protocols-Bible/protocol-epistemic-neutrality-fringe-research.md) · 2026-06-14
- [Скрипт первого звонка с проектом или фондом](../05-Protocols-Bible/protocol-first-call-script.md) · 2026-05-30
- [Fleet Machine Optimization Playbook](../05-Protocols-Bible/protocol-fleet-machine-optimization.md) · 2026-07-07
- [Протокол написания и отправки фоллоуапа (ФА)](../05-Protocols-Bible/protocol-followup-structure.md) · 2026-05-30
- [Протокол бонусной системы за фандрейз и работу с лаунчпадами](../05-Protocols-Bible/protocol-fundraise-bonus-system.md) · 2026-05-30
- [Протокол «Привратник»: заявка на вступление = бан-фри доступ к людям](../05-Protocols-Bible/protocol-gatekeeper-join-request-funnel.md) · 2026-06-21
- [Протокол создания интро-группы](../05-Protocols-Bible/protocol-intro-process.md) · 2026-05-30
- [Протокол квалификации инвестора на звонке](../05-Protocols-Bible/protocol-investor-call-qualification.md) · 2026-05-30
- [Протокол обработки инвесторских лидов: очередь, CTA, фолоуап](../05-Protocols-Bible/protocol-investor-lead-pipeline.md) · 2026-05-30
- [Протокол петли номинации судьи Stanford](../05-Protocols-Bible/protocol-judge-nomination-loop.md) · 2026-05-30
- [KOL Аутрич и воронка сотрудничества](../05-Protocols-Bible/protocol-kol-outreach-funnel.md) · 2026-05-30
- [KOL Квалификация и скоринг](../05-Protocols-Bible/protocol-kol-qualification-scoring.md) · 2026-05-30
- [Протокол квалификации лида на звонке](../05-Protocols-Bible/protocol-lead-qualification-call.md) · 2026-05-30
- [Партнёрства и эндорсменты: регламент](../05-Protocols-Bible/protocol-partnership-endorsement.md) · 2026-05-30
- [Регламент планёрки: стандарт проведения](../05-Protocols-Bible/protocol-planyorka-reglament.md) · 2026-05-30
- [Протокол действий после звонка с инвестором / VC / лаунчпадом](../05-Protocols-Bible/protocol-post-call-actions.md) · 2026-05-30
- [Протокол действий после звонка с лидом](../05-Protocols-Bible/protocol-post-call-workflow.md) · 2026-05-30
- [Протокол присутствия: отлучки и согласование отсутствия](../05-Protocols-Bible/protocol-prisutstvie-i-otluchki.md) · 2026-05-30
- [Reddit karma warm-up — u/Ok-Tip-1318 (безопасный прогрев)](../05-Protocols-Bible/protocol-reddit-karma-warmup-ok-tip-1318.md) · 2026-07-03
- [Протокол демонстрации экрана на интро-звонке](../05-Protocols-Bible/protocol-screen-share-intro-call.md) · 2026-05-30
- [Протокол второго и третьего звонков: прогрев и питч](../05-Protocols-Bible/protocol-second-third-call.md) · 2026-05-30
- [Протокол нарратива Stanford / Silicon Valley LaunchPad](../05-Protocols-Bible/protocol-stanford-affiliation-narrative.md) · 2026-05-30
- [Торговля трафиком: продажа и закупка](../05-Protocols-Bible/protocol-traffic-trading.md) · 2026-05-30
- [Регламент: артефакты и Deep Research публикуются без купюр в лонгриды](../05-Protocols-Bible/reglament-artefakty-i-dr-bez-kupyur-v-longridah.md) · 2026-07-03
- [Регламент: максимальная автономия — с жёстким карв-аутом на права доступа/секреты](../05-Protocols-Bible/reglament-avtonomiya-s-karvautom-na-prava-dostupa.md) · 2026-07-03
- [Регламент: само-дебаг и прозрачность сбоев (Claude Code / любой агент / ассистент)](../05-Protocols-Bible/reglament-claude-code-self-debug-transparency.md) · 2026-06-21
- [Подпись контента - «придумано Майкрофтом и Тони, Palo Alto AI Research Lab» + CTA](../05-Protocols-Bible/reglament-content-attribution-mycroft-anton.md) · 2026-07-02
- [Реглумент — декомпозируй сложную задачу на параллельные сессии + выдай seed-промпты](../05-Protocols-Bible/reglament-dekompozitsiya-zadachi-na-parallelnye-sessii.md) · 2026-06-29
- [Регламент: по минимуму нагружать НОУТ, по максимуму использовать ДЕСКТОП](../05-Protocols-Bible/reglament-desktop-max-laptop-min-resources.md) · 2026-06-22
- [Реглумент — снесло с главной цели → сорняки выгружай в соседние сессии (seed-промпты), сам держи главную линию](../05-Protocols-Bible/reglament-drift-ot-glavnoy-tseli-sornyaki-v-sosednie-sessii.md) · 2026-07-03
- [Голосовые расшифровки Антона — ВСЕГДА максимальное качество модели](../05-Protocols-Bible/reglament-golosovye-rasshifrovki-antona-vsegda-[человек]-kachestvo.md) · 2026-06-26
- [Реглумент: ХАБ = ДЕСКТОП = PaloAlto PC = Вожак — это ОДНА машина, наш мастер](../05-Protocols-Bible/reglament-hab-master-mashina-vse-imena-odno.md) · 2026-06-22
- [Реглумент: всегда лечим КОРЕНЬ проблемы, а не симптом (+ AK-47 в каждом решении)](../05-Protocols-Bible/reglament-lechim-koren-problemy-ne-simptomy.md) · 2026-06-25
- [Машинно-специфичное (паспорт машины) — держим ЛОКАЛЬНО, не шарим: оно ЛОМАЕТСЯ](../05-Protocols-Bible/reglament-mashinno-spetsifichnoe-lokalno-ne-sharim.md) · 2026-06-28
- [Реглумент: миграция на новую машину — playbook + грабли](../05-Protocols-Bible/reglament-migratsiya-mashin-playbook.md) · 2026-06-21
- [Реглумент: [коллега] и [коллега] = наши co-founder, отношение партнёрское](../05-Protocols-Bible/reglament-natasha-i-[коллега]-nashi-cofoundery.md) · 2026-07-03
- [Регламент — нервная система машин = всегда без LLM; тупой детектор первым, LLM только на мышление](../05-Protocols-Bible/reglament-nervnaya-sistema-mashin-bez-llm-tupoy-detektor-pervym.md) · 2026-06-26
- [Онбординг-питч «второй мозг» — победа до питча, доказательства вместо лозунгов](../05-Protocols-Bible/reglament-onboarding-pitch-vtoroy-mozg.md) · 2026-07-07
- [Регламент — перед изменением системы сверься с картой (/arch)](../05-Protocols-Bible/reglament-pered-izmeneniem-sistemy-sverstis-s-kartoy-arch.md) · 2026-06-21
- [Каперство — нагло, но легально; никогда фрод (для всех, кто действует ОТ ЛИЦА Антона наружу)](../05-Protocols-Bible/reglament-privateer-bold-but-legal-never-fraud.md) · 2026-07-02
- [Реглумент — проактивно предлагай мульти-агентный анализ на Решении / Сравнении / Анализе](../05-Protocols-Bible/reglament-proaktivno-predlagay-agentov.md) · 2026-06-25
- [Реглумент: проактивно предлагай подходящий скилл/инструмент под то, что Антон делает](../05-Protocols-Bible/reglament-proaktivno-predlagay-podhodyashchiy-skill.md) · 2026-06-27
- [Реглумент: ретро начинай с RECALL других сессий (не дублируй чужую работу)](../05-Protocols-Bible/reglament-retro-nachni-s-recall-drugih-sessiy.md) · 2026-06-27
- [Регламент — STT всегда через OpenAI Whisper API](../05-Protocols-Bible/reglament-stt-vsegda-openai-whisper-api.md) · 2026-07-06
- [Регламент: Telegram-автоматизации — ВСЕГДА свой обычный аккаунт, НЕ боты](../05-Protocols-Bible/reglament-telegram-avtomatizatsii-svoy-akkaunt-ne-boty.md) · 2026-06-21
- [Регламент — тизеры/кросс-пост в ClawRus и TG-канал Антона](../05-Protocols-Bible/reglament-tizery-krosspost-v-clawrus-i-tg.md) · 2026-06-30
- [Реглумент: увидел поломку — ВСЕГДА и СРАЗУ предложи починить](../05-Protocols-Bible/reglament-uvidel-polomku-vsegda-predlozhi-pochinit.md) · 2026-06-27
- [Включить аудит Планировщика задач на ВСЕХ машинах (CCTV для scheduled-tasks)](../05-Protocols-Bible/reglament-vklyuchit-audit-planirovshchika-na-vseh-mashinah.md) · 2026-06-27
- [Реглумент: Вожак / Ведомый — кто меняет общий КАНОН на флоте машин](../05-Protocols-Bible/reglament-vozhak-vedomyy-canon-governance.md) · 2026-06-22
- [Регламент — ВСЕ нотификации и крики CC в Telegram идут в ЧАТ 03 (bus-группа)](../05-Protocols-Bible/reglament-vse-notifikatsii-i-kriki-cc-v-chat-03.md) · 2026-06-27
- [Реглумент: ВСЕГДА будь проактивен — действуй на опережение](../05-Protocols-Bible/reglament-vsegda-bud-proaktiven.md) · 2026-06-22
- [Регламент: всегда логинься и авторизуйся сам — юзер не слабое звено](../05-Protocols-Bible/reglament-vsegda-loginsya-i-avtorizuysya-sam.md) · 2026-07-04

### warm-maintenance (20)

- [Деньги / обязательства / сомнение / незнакомец → СТОП, эскалация Антону, не отвечай сам](../05-Protocols-Bible/reglament-dengi-obyazatelstva-somnenie-neznakomec-stop-eskalaciya.md) · 2026-06-12
- [Дневной потолок ИНИЦИАЦИЙ на аккаунт ~15 (новый — 5–10); ответы знакомым не считаются](../05-Protocols-Bible/reglament-dnevnoj-potolok-iniciacij-na-akkaunt.md) · 2026-06-12
- [Длинную мысль (>~250 знаков) дроби на 2–3 пузыря, простое — оставляй одним](../05-Protocols-Bible/reglament-droblenie-dlinnoj-mysli-na-2-3-puzyrya.md) · 2026-06-12
- [Естественный джиттер + утренний разгон очереди: не пачкой в одну секунду и не всё ровно в 08:00](../05-Protocols-Bible/reglament-dzhitter-i-utrennij-razgon-ocheredi.md) · 2026-06-12
- [Голосовое — РЕДКО и только живым голосом Антона; синтетику/TTS НИКОГДА](../05-Protocols-Bible/reglament-golosovoe-redko-i-tolko-zhivym-golosom.md) · 2026-06-12
- [Индикатор «печатает…» по умолчанию ВЫКЛ; включать только если userbot шлёт его надёжно и текст длинный](../05-Protocols-Bible/reglament-indikator-pechataet-opcionalno-off.md) · 2026-06-12
- [Открывай НОВОЙ правдивой деталью; нет детали — честный нейтральный заход, но НЕ выдумывай](../05-Protocols-Bible/reglament-kazhdyj-ping-novaya-pravdivaya-detal-ili-chestnyj-zahod.md) · 2026-06-12
- [Минимум эмодзи — по его реальному стилю, по умолчанию ноль](../05-Protocols-Bible/reglament-minimum-emodzi-po-stilu-antona.md) · 2026-06-12
- [НЕ подделывай опечатки и не имитируй «человеческое несовершенство» искусственно](../05-Protocols-Bible/reglament-ne-poddelyvaj-opechatki-i-nesovershenstvo.md) · 2026-06-12
- [Пиши его неформальным регистром (строчные + его пунктуация), а не отшлифованным официозом](../05-Protocols-Bible/reglament-neformalnyj-registr-antona-ne-oficioz.md) · 2026-06-12
- [Никогда один и тот же текст пачкой — у каждого имя + правдивая личная отсылка](../05-Protocols-Bible/reglament-nikogda-odinakovyj-tekst-pachkoj.md) · 2026-06-12
- [Пауза между отправками разным людям 30–180с, но грубо-человеческая, не машинная гребёнка](../05-Protocols-Bible/reglament-pauza-mezhdu-otpravkami-30-180s-nerovnaya.md) · 2026-06-12
- [Пауза перед отправкой = время «прочитать + набрать», пропорционально длине, не мгновенно](../05-Protocols-Bible/reglament-pauza-pered-otpravkoj-chtenie-plus-nabor.md) · 2026-06-12
- [PeerFlood / FloodWait / спам-блок → немедленный СТОП на сутки + эскалация Антону, не обходить](../05-Protocols-Bible/reglament-peerflood-floodwait-stop-i-eskalaciya.md) · 2026-06-12
- [Переменная задержка по живости диалога: горячо → минуты, обычно → до часа-полутора, возобновление → часы; НИКОГДА не фиксированная](../05-Protocols-Bible/reglament-peremennaya-zaderzhka-po-zhivosti-dialoga.md) · 2026-06-12
- [Сначала прочитай последние 10 сообщений и ответь на ТО, что человек реально написал](../05-Protocols-Bible/reglament-snachala-prochitaj-poslednie-10-i-otvet-na-vhodyashchee.md) · 2026-06-12
- [Варьируй зачин РАЗНЫМ СОДЕРЖАНИЕМ — никакой копипасты первой строки между контактами](../05-Protocols-Bible/reglament-varjiruj-zachin-net-kopipasty-mezhdu-kontaktami.md) · 2026-06-12
- [Для тёплого поддержания сообщение БЕЗ вопроса/CTA допустимо (carve-out к «всегда нужен вопрос»)](../05-Protocols-Bible/reglament-warm-soobshchenie-bez-cta-dopustimo-carveout.md) · 2026-06-12
- [Окно бодрствования: писать только 08:00–23:00 по локальному времени Антона, ночью молчать](../05-Protocols-Bible/reglament-warm-window-08-23-chasy-antona.md) · 2026-06-12
- [Профиль аккаунта живой и заполненный (фото/имя/био); изменения профиля — только после «да» Антона (Tier-2)](../05-Protocols-Bible/reglament-zhivoj-zapolnennyj-profil-pered-zapuskom.md) · 2026-06-12

### ai-operations (16)

- [Всегда давать ЧЕСТНЫЕ оценки сроков — с учётом мощности МАШИНЫ, на которой работаешь сейчас](../05-Protocols-Bible/reglament-chestnye-estimaty-srokov-s-uchetom-moshchnosti-mashiny.md) · 2026-06-21
- [Фоновая/крон-задача — ВСЕГДА с жёстким таймаутом и убийцей всего дерева процессов](../05-Protocols-Bible/reglament-fonovaya-zadacha-vsegda-s-taymautom-i-ubiytsey-dereva.md) · 2026-06-27
- [Качественная авто-уборка индекса памяти (MEMORY.md) — как делать правильно](../05-Protocols-Bible/reglament-kachestvennaya-avtouborka-indeksa-pamyati.md) · 2026-06-27
- [Как ПРАВИЛЬНО писать в MEMORY.md (always-loaded индекс памяти)](../05-Protocols-Bible/reglament-kak-pravilno-pisat-v-memory-md.md) · 2026-06-27
- [Маршрутизация моделей: черновую/извлекающую работу — на Sonnet, мышление/синтез — на Opus, при ОБЯЗАТЕЛЬНОЙ проверке качества выхода](../05-Protocols-Bible/reglament-marshrutizatsiya-modeley-chernovaya-na-sonnet-myshlenie-na-opus.md) · 2026-06-14
- [Раз в неделю майнить альфу из ВСЕЙ документации наших инструментов](../05-Protocols-Bible/reglament-nedelnyy-mayning-alfy-iz-dokumentacii.md) · 2026-07-06
- [Ночная автономность — пока Антон спит, работай максимально сам](../05-Protocols-Bible/reglament-nochnaya-avtonomnost-poka-anton-spit.md) · 2026-07-04
- [Каждый Deep Research получает номер DRYY-MM-DD-NN + строку в реестре](../05-Protocols-Bible/reglament-numeratsiya-dr-i-reestr.md) · 2026-07-03
- [Весь сгенерированный контент получает номер NOTEYY-MM-DD-МАШИНА-NN + строку в реестре](../05-Protocols-Bible/reglament-numeratsiya-kontenta-note-i-reestr.md) · 2026-07-06
- [Перед архивацией / закрытием — скан на недоделки → на доску, не хоронить](../05-Protocols-Bible/reglament-pered-arhivatsiey-skan-nedodelok-na-dosku.md) · 2026-06-27
- [Правило Connect — эстафета ответственности: владей задачей до результата, держи конвейер A→Z, подсвечивай обрыв](../05-Protocols-Bible/reglament-pravilo-connect-esafeta-otvetstvennosti.md) · 2026-07-01
- [Проактивно предлагай DR, когда документация/прогресс опережает обучение LLM](../05-Protocols-Bible/reglament-proaktivno-predlagay-dr-kogda-doki-operezhayut-obuchenie.md) · 2026-07-06
- [Рутины работают НОЧЬЮ — окно 23:00–06:00 по Лисабону](../05-Protocols-Bible/reglament-rutiny-rabotayut-nochyu-23-06-lisbon.md) · 2026-06-25
- [Служебные файлы пишем СРАЗУ коротко и по существу; уже ужатое НЕ пережимаем](../05-Protocols-Bible/reglament-sluzhebnye-fayly-pishem-srazu-korotko-ne-perezhimaem.md) · 2026-06-29
- [Висячие / открытые задачи → ВСЕГДА визуальный дашборд](../05-Protocols-Bible/reglament-visyachie-zadachi-vsegda-dashboard.md) · 2026-06-26
- [Журнал задач — сделанные и несделанные, с перелинковкой; несделанная попадает в реестр СРАЗУ](../05-Protocols-Bible/reglament-zhurnal-zadach-sdelannye-i-nesdelannye-s-perelinkovkoy.md) · 2026-07-04

### machine-ops (7)

- [ЧП «компьютеры не видят друг друга»: аудит потери синка, КОРЕНЬ, профилактика и план действий](../05-Protocols-Bible/reglament-chp-poterya-sinka-mezhdu-mashinami.md) · 2026-06-26
- [Кросс-машинная авторизация: одобрил на одной машине = действует на всех; не переспрашивать](../05-Protocols-Bible/reglament-cross-machine-authorization-ne-pereprashivat.md) · 2026-06-21
- [Claude на нескольких машинах: одна среда через облако + передача между машинами через авто-ящик (курьер — аварийный)](../05-Protocols-Bible/reglament-multi-machine-claude-i-peredacha-mezhdu-mashinami.md) · 2026-06-19
- [Браузерная работа (окна Chrome, бук звонков) — каждая машина делает СВОЮ строго САМА, локально; никакого кросс-машинного диспатча; хаб не отвлекаем](../05-Protocols-Bible/reglament-rabota-s-brauzerom-na-pirah-ne-na-habe.md) · 2026-06-26
- [Раскатка фиксов: распаковывай посылки/апдейты НЕМЕДЛЕННО + деплой-манифест](../05-Protocols-Bible/reglament-raskatka-fiksov-deploy-manifest.md) · 2026-07-06
- [Шина клана не зависит от Telegram-MCP + у КАЖДОЙ машины своя TG-сессия (лечим AuthKeyDuplicated)](../05-Protocols-Bible/reglament-shina-telegram-bez-mcp-i-svoya-sessiya-na-mashinu.md) · 2026-06-26
- [Синхронизация всех акторов — через Telegram-чат 03, первично и обязательно](../05-Protocols-Bible/reglament-sinhronizaciya-cherez-telegram-03.md) · 2026-07-06

### social-media (5)

- [Алгоритм работы с FB: 1) проверяем ленту, лайкаем посты про крипту, финансы,](../05-Protocols-Bible/reglament-algoritm-raboty-s-fb-1-proveryaem-lentu-laykaem-posty-p.md) · 2024-04-13
- [правило перевода голосовых в текс и постановки и принятия задачь](../05-Protocols-Bible/reglament-card-pravilo-perevoda-golosovyh-v-teks-i-postanovki-i-prinya.md)
- [правило постановка задач от антона денису](../05-Protocols-Bible/reglament-card-pravilo-postanovka-zadach-ot-antona-denisu.md)
- [правило запрашивать комментарии поставщика](../05-Protocols-Bible/reglament-card-pravilo-zaprashivat-kommentarii-postavschika.md)
- [Правило ФБ: всегда каждый день просматриваем последние 10 постов, смотрим новые](../05-Protocols-Bible/reglament-pravilo-fb-vsegda-kazhdyy-den-prosmatrivaem-poslednie-1.md) · 2024-06-03

### operations (4)

- [Авторизации/логины в Telegram и соцсетях/мессенджерах — ВСЕГДА автономно, сам, проактивно](../05-Protocols-Bible/reglament-avtorizatsii-v-socsetyah-vsegda-avtonomno.md) · 2026-06-27
- [Максимальная автономность: делай САМ, экономь время Антона](../05-Protocols-Bible/reglament-maksimalnaya-avtonomnost-ekonom-vremya-antona.md) · 2026-06-21
- [Пиры коллаборации помогают друг другу с логинами — OTP-релей между машинами (Tier-1, без Антона)](../05-Protocols-Bible/reglament-piry-pomogayut-drug-drugu-s-loginami-otp-relay.md) · 2026-07-04
- [Подъём синка (Syncthing/связь между машинами) — ВСЕГДА автономно, сам, проактивно](../05-Protocols-Bible/reglament-vsegda-podnimay-sink-avtonomno.md) · 2026-06-27

### operations-governance (4)

- [Регламент — Любая LLM = равноправный безопасный актор над Vault (вендор-независимость двойника)](../05-Protocols-Bible/reglament-lyubaya-llm-ravnopravnyy-bezopasnyy-aktor-nad-vault.md) · 2026-06-29
- [Регламент - Вердикт «не делаем» = список возражений + приглашение переубедить (спор до консенсуса)](../05-Protocols-Bible/reglament-rabota-s-vozrazheniyami-spor-do-konsensusa.md) · 2026-07-02
- [Регламент - Новый внутренний чат создаётся сразу со ВСЕМ составом: 4 аккаунта Антона + [коллега] + [коллега]](../05-Protocols-Bible/reglament-vnutrennie-chaty-vsegda-ves-sostav.md) · 2026-07-02
- [Регламент - Воронка первого отклика «бесплатной школы»: лестница 0→3 (квалификатор → сортировка → концьерж-час → вилка)](../05-Protocols-Bible/reglament-voronka-pervogo-otklika-lestnitsa.md) · 2026-07-04

### multi-machine-comms (3)

- [Дистанционное одобрение (QQQ) — пингуй Антона в чате, он подтверждает с телефона](../05-Protocols-Bible/reglament-distancionnoe-odobrenie-qqq.md) · 2026-06-28
- [Как пирам общаться в каждом канале — единый конверт + точка встречи на канал](../05-Protocols-Bible/reglament-kak-piram-obshchatsya-v-kazhdom-kanale.md) · 2026-06-28
- [Триггер «03» / «теперь вы сами» — машины сами находят консенсус и сами исполняют, Антона не дёргают](../05-Protocols-Bible/reglament-trigger-03-avtonomnyy-konsensus-mashin.md) · 2026-06-30

### governance (3)

- [Запустил долгий процесс — проверяй, что он ЖИВ, ~каждые 20 минут (liveness)](../05-Protocols-Bible/reglament-dolgiy-protsess-proveryat-zhiv-li-on-kazhdye-20-minut.md) · 2026-06-12
- [Перед ЛЮБОЙ активностью — сначала RECALL всего, что у нас есть по теме (весь волт + RAG)](../05-Protocols-Bible/reglament-pered-lyuboy-aktivnostyu-snachala-recall-vsego-volt-i-rag.md) · 2026-06-12
- [Семейное управление общим волтом: ограниченный вожак + смотрители (owner = распорядитель, не собственник)](../05-Protocols-Bible/reglament-semejnoe-upravlenie-vozhak-ogranichennyy-i-rasporyaditeli.md) · 2026-06-20

### communication (2)

- [Дата и время — в НАЧАЛЕ и в КОНЦЕ каждого ответа Антону](../05-Protocols-Bible/reglament-data-vremya-v-nachale-i-konce-kazhdogo-otveta.md) · 2026-06-27
- [Сигналы Антона в чате: «+» = ДА, «?» = дай статус](../05-Protocols-Bible/reglament-signaly-antona-plyus-da-vopros-status.md) · 2026-06-15

### outreach (2)

- [Элитные крипто-комьюнити → НИКАКОГО холодного DM, только value-first / тёплое интро](../05-Protocols-Bible/reglament-elitnye-kripto-komyuniti-zero-cold-dm-value-first.md) · 2026-06-18
- [Сначала искренний интерес, потом вопрос (touch-base по [человек])](../05-Protocols-Bible/reglament-outreach-genuine-interest-first.md) · 2026-06-08

### provenance-operations (2)

- [Файл «не нашёлся» — сначала проверить, НЕ пересоздавать (может просто доезжать по синку или искался не там)](../05-Protocols-Bible/reglament-fayl-ne-nashelsya-snachala-proverit-ne-peresozdavat.md) · 2026-06-21
- [Каждую сессию Claude Code помечать АВТОРОМ = машина + человек (кто и на каком компьютере делал работу)](../05-Protocols-Bible/reglament-pomechat-mashinu-na-kazhdoy-sessii.md) · 2026-06-19

### content-factory (2)

- [Регламент - Контент показывает, как нам тяжело (уязвимость = trust)](../05-Protocols-Bible/reglament-kontent-pokazyvaet-kak-nam-tyazhelo.md) · 2026-07-05
- [Регламент - Всё, что мы делаем, становится контентом (build-in-public, реалити-шоу)](../05-Protocols-Bible/reglament-vsyo-chto-my-delaem-stanovitsya-kontentom.md) · 2026-07-05

### research-protocol (1)

- [Alpha Protocol — перед стратегическим решением: Recall + Deep Research + Synthesis (не реализуем на одном recall)](../05-Protocols-Bible/protocol-alpha-protocol-recall-plus-deep-research.md) · 2026-06-14

### ai-native (1)

- [SKU #1 — AI-Native Readiness Diagnostic (продаваемый one-pager, Фаза 0)](../05-Protocols-Bible/protocol-sku-ai-native-readiness-diagnostic.md) · 2026-07-06

### process-quality (1)

- [Action item без owner + срок + метрика — это НЕ задача (вернуть в наблюдение)](../05-Protocols-Bible/reglament-action-item-trebuet-owner-srok-metriku.md) · 2026-06-16

### privacy (1)

- [Anti-leak на ВЫХОДЕ, не на сборе — приватный корпус читаем целиком, барьер на исходящем](../05-Protocols-Bible/reglament-anti-leak-na-vyhode.md) · 2026-06-22

### data-architecture (1)

- [Единый SQL — все люди и компании обязаны быть в базе, перелинкованы](../05-Protocols-Bible/reglament-edinyy-sql-vse-lyudi-i-kompanii-v-baze.md) · 2026-06-17

### content-pipeline (1)

- [Голосовые из чата 00 → ВСЕГДА в контент (дефолт = пост; цель 100%, пол 80%)](../05-Protocols-Bible/reglament-golosovye-iz-chata-00-vsegda-v-kontent.md) · 2026-07-03

### multi-machine-operations (1)

- [Перед правкой sensitive-файла или межмашинным консенсусом — проверь, не работает ли параллельная сессия над тем же, и сначала договорись (координация против гонок за общий файл)](../05-Protocols-Bible/reglament-koordinatsiya-sessiy-pered-pravkoy-sensitive-failov.md) · 2026-07-05

### crm-outreach (1)

- [Новый контакт → сразу карточка в CRM (нулевая задержка)](../05-Protocols-Bible/reglament-novyy-kontakt-srazu-v-crm.md) · 2026-07-02

### communications (1)

- [Отчитываешься/показываешь результат Антону → делай это визуально (дашборд/таблица/GUI), а не стеной текста в командной строке](../05-Protocols-Bible/reglament-otchet-antonu-vizualno-dashboard-ne-stena-cli.md) · 2026-06-13

### decision-hygiene (1)

- [Регламент — отвергнутое/отложенное решение → в реестр declined](../05-Protocols-Bible/reglament-otvergnutoe-reshenie-v-reestr-declined.md) · 2026-06-24

### operations-ux (1)

- [Нужно подтверждение/действие Антона на экране — УБЕДИСЬ, что он реально это видит, и ДАЙ скриншот (не гоняй вслепую)](../05-Protocols-Bible/reglament-podtverzhdenie-na-ekrane-ubedis-chto-anton-vidit-day-skrin.md) · 2026-06-22

### knowledge-search (1)

- [Как искать по Второму Мозгу Антона — /search (слова) · /ask (смысл) · /find (имена)](../05-Protocols-Bible/reglament-poisk-po-vtoromu-mozgu-search-ask-find.md) · 2026-06-15

### machine-governance (1)

- [Правка ОБЩЕЙ инфраструктуры НЕ готова, пока не РАЗЛОЖЕНА на все каналы/машины И проверена (atomic propagate-and-verify)](../05-Protocols-Bible/reglament-pravka-obshchey-infry-ne-gotova-poka-ne-razlozhena-vezde-i-proverena.md) · 2026-06-27

### data-quality-vault (1)

- [При импорте любого лида/человека заполнять поле альтернативных написаний имени](../05-Protocols-Bible/reglament-pri-importe-lyubogo-lida-cheloveka-zapolnyat-alt-napisaniya.md) · 2026-06-13

### positioning-security (1)

- [Регламент: security-язык (только доказуемое) и границы публикаций (паттерны, не внутренности)](../05-Protocols-Bible/reglament-security-yazyk-i-granitsy-publikatsiy.md) · 2026-07-04

### operations-safety (1)

- [Регламент — слияние общих сторов: UNION по содержимому, НИКОГДА по дате/авто-мёрджу](../05-Protocols-Bible/reglament-sliyanie-obshchih-storov-union-po-soderzhimomu-ne-po-date.md) · 2026-06-22

### ways-of-working (1)

- [Всплыла старая тема / инцидент → СНАЧАЛА RECALL, потом копай; и истину бери из ЖИВОГО источника, не со стале-копии](../05-Protocols-Bible/reglament-snachala-recall-potom-kopay-i-istina-iz-zhivogo-istochnika.md) · 2026-06-26

### cost-control (1)

- [Сначала использовать ВКЛЮЧЁННЫЕ в подписку лимиты ЛЛМ; внешний платный API — только по согласованию](../05-Protocols-Bible/reglament-snachala-vklyuchennye-limity-platnyy-api-po-soglasovaniyu.md) · 2026-06-15

### outreach-operations (1)

- [Реглумент: standing-мандат на исходящее + пакетное одобрение 1×/день](../05-Protocols-Bible/reglament-standing-mandat-ishodyashchee-paketnoe-odobrenie.md) · 2026-07-02

### data-provenance-voice (1)

- [Тексты Антона до 2023 включительно — человеческое золото (приоритет для голоса и обучения)](../05-Protocols-Bible/reglament-teksty-do-2023-chelovecheskoe-zoloto-prioritet-golosa.md) · 2026-06-07

### resource-economy (1)

- [Транскрипты видео → youtube-transcript-api ПЕРВЫМ; Whisper (GPU) только для видео, одобренных Антоном ГОЛОСОМ; экономь ресурсы](../05-Protocols-Bible/reglament-transkripty-api-pervym-whisper-tolko-golosom-odobrennoe.md) · 2026-06-14

### data-processing (1)

- [Голос Антона расшифровывать ТОЛЬКО локально (faster-whisper на нашей GPU) — НИКОГДА силами Telegram](../05-Protocols-Bible/reglament-voice-transcribe-only-local-whisper-never-telegram.md) · 2026-06-12

### second-brain (1)

- [Все артефакты ВСЕГДА сохраняем в волт — забрать, сохранить, реиндексировать, перелинковать](../05-Protocols-Bible/reglament-vse-artefakty-vsegda-v-volt-pereindeks-perelinkovka.md) · 2026-06-30

### content (1)

- [Всегда хвали источник вдохновения - huge thanks, теги, отсылки; мы не воруем, мы реверс-инжинирим с поклоном](../05-Protocols-Bible/reglament-vsegda-hvali-istochnik-vdohnoveniya.md) · 2026-07-02

### calls-pipeline (1)

- [Регламент: запись звонков в Granola — одна машина-хозяин, заметку надо ОТКРЫТЬ](../05-Protocols-Bible/reglament-zapis-zvonkov-granola-odna-mashina-hozyain.md) · 2026-07-03

### memory-architecture (1)

- [Регламент — ЗНАТЬ vs ДОКАЗАТЬ: эссенция и эвиденция (как храним и что ищем)](../05-Protocols-Bible/reglament-znat-vs-dokazat-essence-evidence.md) · 2026-06-25

## Честное покрытие метаданных

Навигация настолько хороша, насколько заполнены поля. Фактические цифры:

| Поле | Заполнено | Покрытие |
|---|---:|---:|
| `audience` | 144 / 287 | 50% |
| `priority` | 77 / 287 | 27% |
| `applies_to` (под снос) | 129 / 287 | 45% |

`audience` ещё не обязателен на приёме, а `applies_to` продолжает дублировать его смысл — открытый долг схемы (issue #11). Пока он не закрыт, фильтрация по адресату неполна, и эта таблица показывает насколько.

