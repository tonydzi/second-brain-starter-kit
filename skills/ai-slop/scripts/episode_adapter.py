#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
episode_adapter.py - deterministic scaffolder for a content "episode"
(content-factory v2, S5 tier adapters). Implements the §7.2 TIER CONTRACT of
decision-content-pipeline-reality-show 1:1. Draft-first, 0 tokens.

WHAT IT DOES (deterministic only):
  - `new`        : create an episode bundle = one draft file PER (tier, platform)
                   from the §7.2 contract, with length/platform/lang/voice/model/
                   cross_links/canonical baked into each file + meta.json.
                   PHASE-1 platforms by default; --with-phase2 adds VC.ru/Хабр/Reddit.
  - `list`/`show`: bundle status.
  - `set-status` : draft|review|published.
  - `check`      : VISIBILITY LAYER - lint each written draft vs its tier length
                   budget (teaser 200-250 = HARD) + canonical/CTA presence, so a
                   broken draft is caught BEFORE review.
  - `export`     : bridge a reviewed bundle into the EXISTING publish path
                   (drafts/ -> content_approve.py -> approved/ -> content_publish.py)
                   for the Telegram/FB/X registers. GitHub/Reddit/VC.ru/Хабр are
                   listed for manual gh/native publish (content_publish does TG only).
                   We REUSE that path; we do NOT fork a second publisher.

WRITING each draft = the in-session LLM step:
  voice=авторский -> Anton's author voice = Fable 5 (Opus = fallback). Sonnet FORBIDDEN.
                     MUST read _STYLE.md (★ЭТАЛОН) + _CRAFT.md before writing, and obey
                     the ANTI-VANILLA negative list baked into every author-voice draft.
  dev-log         -> Sonnet scaffold + Opus coherence (technical, impersonal).
  scaffold/length-check/export = pure Python (0 tokens).
NOTHING here publishes outward. Publishing stays a separate, approved, Tier-2 step.

§7.2 TIER CONTRACT (decision-content-pipeline-reality-show v2, 2026-06-30):
  | tier     | length        | platforms (this build)     | lang        | voice          | model            |
  | teaser   | 200-250 chars | @ClawRus(RU) · X(EN)       | RU TG, EN X | author         | Fable 5 (Opus fb)|
  | medium   | 800-2000 HARD | FB(RU) link-in-1st-comment | RU          | author diary   | Fable 5 (Opus fb)|
  | longread | 4000+ narr.   | VC.ru(RU) · GitHub(EN)     | RU & EN     | author r-show  | Fable 5 (Opus fb)|
  | dev-log  | dry log       | GitHub(EN, canonical)      | EN          | tech impersonal| Sonnet + Opus    |
  * canonical = GitHub-markdown on every platform (one source of truth for AI).
  * NO copy-paste: each platform = a NATIVE rewrite (the writer's job, per-file).
  * cross-links DOWN the tiers: teaser->longread; medium->longread(1st comment);
    longread<-teaser ->dev-log; dev-log->longread + anchors to our Deep Research.
  * PHASE 2 (deferred per Anton 2026-06-30): VC.ru, Хабр (RU GEO), Reddit (EN GEO),
    Substack. Defined here, scaffolded only with --with-phase2.
  * ⭐ TEASER CONTRACT REWRITTEN 2026-08-06 (Anton, voice): a teaser is a COMPLETE
    UNIT OF USE, not a hook. Test: a reader who does NOT click still walks away with
    something applicable. Cliffhanger-without-payload = forbidden (that was the
    engine of the slop). The link stops being the price of the answer and becomes
    "and here is how it works inside".
  * S3 narrative overlay ([[style-reality-show]]): teaser=cold open+cliffhanger;
    medium=full episode arc; longread=extended episode+recap; dev-log=raw footage, no drama.

Bundles live in:  [путь владельца]

Usage:
  python episode_adapter.py new --slug courier-between-two-ais \
         --title "How I was a courier between two AIs" --source "hub:3448"
  python episode_adapter.py new --slug <slug> --title "..." --with-phase2
  python episode_adapter.py list
  python episode_adapter.py show  --slug <slug>
  python episode_adapter.py check --slug <slug>
  python episode_adapter.py export --slug <slug>          # -> drafts/episode-<slug>.md
  python episode_adapter.py set-status --slug <slug> --status draft|review|published
"""
import argparse, json, os, re, sys, datetime

# Windows console is cp1252 -> force UTF-8 so Cyrillic previews/status print safely.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.join(BASE, "episodes")
DRAFTS = os.path.join(BASE, "drafts")
GITHUB_REPO = "github.com/tonydzi/clawrush"  # repo slug stays until Anton renames
sys.path.insert(0, os.path.dirname(BASE))  # _imports (идиом #edacea43)
try:
    from _paths import github_repo as _github_repo
    REPO_CLONE = _github_repo("clawrush")  # local clone ON THIS MACHINE (GITHUB_ROOT -> ~/GitHub -> hub [путь владельца])
except Exception:
    REPO_CLONE = (r"[путь владельца]" if os.path.isdir(r"[путь владельца]")
                  else os.path.expanduser(os.path.join("~", "GitHub", "clawrush")))
GH_SUBDIR = {"longread": "longreads", "dev-log": "devlog"}  # where each tier lands in the repo
# RU posting target = @ClawRus megagroup. Resolve STRICTLY by this numeric id, never by
# name: @clawrush (similar name) is a STRANGER's channel we must never post to.
CLAWRUS_TG_ID = -[id]

# --- co-founder CTA (standing Anton rule; memory cofounder-cta-public-contact).
# The WhatsApp number is an EXPLICITLY Anton-authorized PUBLIC contact -> privacy
# exception, never strip. NB: §7.2 does not list a CTA column -> we keep it as a
# standing rule and check it as WARN (not a hard FAIL the contract didn't mandate).
CTA_PHONE = "+1 341 222 9178"
# 06.10.2026 anton, голосом: «мы никогда никому ничего не продаем» -> контакт остаётся,
# повелительные «зафолловьте / пишите» убраны (память blog-never-sells). Тире убраны тоже.
CTA_RU = ("Кофаундер на связи в WhatsApp " + CTA_PHONE + ". "
          "Занят, шестеро детей, но всё равно ответит.")
CTA_EN = ("The co-founder is on WhatsApp " + CTA_PHONE + ". "
          "Busy, six kids, still replies.")

# --- ★ГОЛОСОВОЙ КАМЕРТОН (задача «рерайтер пишет ванильно», 28.07.2026) -----------
# Диагноз замерен на 42 наших черновиках против реальных текстов Антона (★ЭТАЛОН 06.06
# + 3 его FB-поста + DM-корпус 3273 реплики). Что подтвердилось как маркер робота и что
# ОПРОВЕРГНУТО — в памяти [[vanilla-voice-markers]] и в /taste-check (P26-P30).
try:
    from _paths import VAULT as _VAULT  # sys.path уже дополнен выше (REPO_CLONE)
except Exception:
    _VAULT = (r"[путь владельца]" if os.path.isdir(r"[путь владельца]")
              else os.path.expanduser(os.path.join("~", "Obsidian", "<vault>")))
_FBDIR = os.path.join(_VAULT, "04-Projects", "personal", "facebook-diary-auto")
STYLE_ETALON = os.path.join(_FBDIR, "_STYLE.md")
CRAFT_FILE = os.path.join(_FBDIR, "_CRAFT.md")

# --- ★БЕЗ КУПЮР (голосовая Антона 05.08.2026, hub:5155; origin: anton) -----------
# Родня ANTIVANILLA, но это ДРУГАЯ болезнь. Анти-ваниль лечит «мы пишем не его ходами».
# Этот блок лечит «мы вычищаем его собственные слова»: писатель по своей воле смягчает
# резкость и подправляет политкорректность, и никакая регулярка этого не ловит -- сравнить
# не с чем, источник у писателя в контексте, а не в файле. Поэтому лечение = директива,
# а не гейт. Канон: Библия reglament-golosovye-antona-bez-kupyur, память
# [[voice-verbatim-no-sanitizing]]. Дверь, которая краснеет при удалении: _test_anticensor.py.
ANTICENSOR = (
    "<!-- ⛔ БЕЗ КУПЮР (Антон, голосовая 05.08.2026 hub:5155, origin: anton). "
    "Его формулировки переносятся ДОСЛОВНО: не смягчать, не «улучшать», не подшлифовывать, "
    "не подправлять политкорректность, не убирать резкость и неприязнь. Его слова: "
    "«если я сказал „говно“ или сказал про цвет кожи и так далее - значит, так и надо говорить»; "
    "«запрещено изменять смысл, улучшать, подшлифовывать, потому что таким образом убирается "
    "эмоциональная сила этого поста»; «у меня в принципе этого нет, но даже если робот показал, "
    "что она есть, - он не прав». "
    "Рерайт под площадку = ФОРМА (длина, структура, язык площадки), НЕ смысл и НЕ острота. "
    "⚠️ ЧЕСТНАЯ ГРАНИЦА: правила площадки - это решение о ПУБЛИКАЦИИ (куда и в каком виде "
    "идёт текст), а НЕ разрешение редактировать смысл. Конфликт -> текст остаётся как есть, "
    "а вопрос «постить сюда или нет» уходит Антону; втихую редактурой не решается. "
    "⛔ Это НЕ мандат генерировать оскорбления ОТ СЕБЯ: правило про СЛОВА АНТОНА. -->"
)

# Негативный список: ЗАМЕРЕНО, что этих ходов у Антона НЕТ, а у нас они частые.
# Частоты на 1000 слов: наши черновики -> его тексты.
ANTIVANILLA = (
    "<!-- ⛔ АНТИ-ВАНИЛЬ (замер 28.07, наши 42 черновика vs тексты Антона; на 1000 слов). "
    "Пять ходов, которых у него НЕТ, а у нас они частые: "
    "(1) зеркальная антитеза «X, а не Y» - у нас 1.82, у него 0.00; "
    "(2) «это не X, это Y» - у нас 0.48, у него 0.00; "
    "(3) триада «A, B и C» - у нас 2.77, у него 0.00; "
    "(4) ровный ритм: коротких предложений (<=5 слов) у нас 24%, у него 33-50% - рви ритм, "
    "он пишет «Вообще. Совсем. Ноль.»; "
    "(5) ЕГО ЛЕКСИКОН - у нас 1.62, у него 18.21 (в 11 раз меньше): видюха, второй мозг, "
    "openclaw, ЧАТжпт, промудохался, спойлер, блин, облажался, стыдно, идиот. "
    "Плюс первое лицо: «я/мне/мой» у нас 17.9, у него 50.1 - он пишет про СЕБЯ, мы про систему. "
    "⚠️ НЕ запрещено (замер опроверг): «не X, а Y» это ЕГО приём (он 3.03-5.21, мы 2.93) и "
    "афоризм в конце абзаца (он 20%, мы 17.6%) - не трогать. "
    "Заголовки ## в теле поста для FB/TG запрещены (у него их нет). -->"
)

# --- ★МАШИНОЧИТАЕМАЯ форма того же замера (добавлено 29.07 под slop_gate.py) -----
# ANTIVANILLA выше = промпт ДЛЯ ПИСАТЕЛЯ (человекочитаемый). Ровно те же пять ходов
# в виде регулярок = вход ДЛЯ ГЕЙТА (slop_gate.py импортирует ОТСЮДА, у себя не дублирует
# -- правило «один источник, ноль копий»). Меняешь замер -> меняешь ОБА блока разом.
# Формат: (rule_id, regex, level, why, suppress_on_group1)
#   suppress_on_group1 != None -> regex ОБЯЗАН иметь группу 1 = клауза перед оборотом;
#   если в этой клаузе нашлось suppress_on_group1 -- срабатывание ГАСИТСЯ (ложный
#   позитив на приёме, который замер за Антоном ПОДТВЕРДИЛ).
# level: "warn" = маркер робота (в лог рерайтеру), не блокирует публикацию;
#        "info" = считаем и показываем, но НЕ поднимаем -- правило не воспроизвело замер.
# Спека: 05-Resources/Protocols/spec-anti-slop-content-pipeline.md §2.3.
#
# ⚠️ ЗАМЕР-КОНТРОЛЬ 29.07 (ground truth, а не вера): регулярки прогнали по корпусу
# 209 наших черновиков (72к слов) ПРОТИВ 5 живых TG-постов Антона (759 слов).
# AV1 и AV3 показали ОБРАТНЫЙ знак: у Антона 3.95/1000, у нас 1.10/1000 -- то есть
# «ход, которого у него нет» встречается у него ЧАЩЕ. Значит эти две регулярки НЕ
# воспроизводят исходный замер 28.07 (он считался другим способом). Ставить их в
# активные WARN нельзя: рерайтер начнёт вычищать ЕГО СОБСТВЕННЫЙ голос. Поэтому
# level="info" до перезамера. Прозрачных цифр ради -- обе остаются и считаются.
ANTIVANILLA_PATTERNS = [
    # (1) зеркальная антитеза «X, а не Y» (замер 28.07: мы 1.82 / он 0.00).
    #     ⚠️ НЕ путать с «не X, а Y» -- это ЕГО приём, замер его ОПРАВДАЛ -> гасим,
    #     если «не» уже стоит в клаузе ПЕРЕД запятой.
    #     Контроль 29.07: он 3.95 / мы 1.10 -> знак обратный -> info, не warn.
    ("AV1-mirror-antithesis", r"(?:^|[.!?…\n])\s*([^.!?…\n]{0,160}?),\s+а\s+не\s+\w",
     "info", "зеркальная антитеза «X, а не Y» (замер 28.07: мы 1.82/1000, он 0.00; "
             "контроль 29.07 дал обратный знак -- правило не блокирует и не WARNит)",
     r"\bне\b"),
    # (2) «это не X, это Y» (замер 28.07: мы 0.48 / он 0.00; контроль 29.07: мы 0.03, он 0.00).
    ("AV2-not-x-this-y", r"\bэто\s+не\s+[^,.!?]{1,60},\s*это\b",
     "warn", "оборот «это не X, это Y» (замер: у нас 0.48/1000, у Антона 0.00)", None),
    # (3) триада «A, B и C» (замер 28.07: мы 2.77 / он 0.00).
    #     Контроль 29.07: он 3.95 / мы 1.10 -> знак обратный -> info, не warn.
    ("AV3-triad", r"\b[\w-]+,\s+[\w-]+\s+и\s+[\w-]+\b",
     "info", "триада «A, B и C» (замер 28.07: мы 2.77/1000, он 0.00; контроль 29.07 дал "
             "обратный знак -- правило не блокирует и не WARNит)", None),
]
# (4) ритм и (5) лексикон/первое лицо -- это НЕ регулярки, а метрики; их пороги ниже,
# гейт считает их сам (W-rhythm, W-first-person). Здесь только источник цифр:
ANTIVANILLA_METRICS = {
    # доля предложений <= 5 слов: у Антона 33-50%, у нас 24% -> порог 30%
    "short_sentence_share_min": 0.30,
    # «я/мне/мой» на 1000 слов: у Антона 50.1, у нас 17.9 -> порог 30
    "first_person_per_1000_min": 30.0,
}
# Лексикон Антона (мы 1.62 / он 18.21) -- сигнал «живого» текста, НЕ запрет.
ANTIVANILLA_LEXICON = ("видюха", "второй мозг", "openclaw", "чатжпт", "промудохался",
                       "спойлер", "блин", "облажался", "стыдно", "идиот")

# --- §7.2 tier length budgets (chars). (min, max); None = unbounded. -------------
TIER_LEN = {
    # ⭐⭐ 200-250 -- число Антона (голос 06.08.2026): «тизеры в новом формате должны
    # быть до 200-250 символов, чтобы умещались в твиттер и чтобы их было НЕ ЛЕНИВО
    # ЧИТАТЬ». Обе границы жёсткие и обе осмысленны: 250 = влезает всюду (X, чат,
    # канал), 200 = ниже этого в тизер физически не помещается ПОЛЬЗА, остаётся
    # голый крючок -- ровно то, что мы этим правилом и убиваем.
    # История: 120-240 (30-31.07, «в чатах до 240») <- 240-370 (контракт 30.06).
    "teaser":   (200, 250),    # HARD per contract (Антон 06.08: влезть в X + не лень читать)
    "tg-post":  (500, 1200),   # HARD, цель 800 (спека анти-слоп §2.1, 29.07)
    "medium":   (800, 2000),   # HARD выше 2000 (было 2500; спека §2.1, 29.07)
    "longread": (4000, None),  # soft minimum (4000+ narrative)
    "dev-log":  (None, None),  # dry log, no cap
    # ⭐ peer-dm -- ПЕРЕПИСКА С ПИРОМ/ЛИДОМ в личке и рабочей группе. Добавлен 11.09.2026,
    # открытым пунктом висел с 04.09. Это НЕ пост и НЕ площадка: адресат один, он читает
    # не ленту, а нашу работу. Ограничителя длины нет осознанно -- в такое письмо штатно
    # входит кусок конфига, команда расписания, скелет CLAUDE.md, и это САМА ОТДАВАЕМАЯ
    # ВЕЩЬ, а не форматирование. Судя его тиром tg-post, гейт дважды заворачивал письма,
    # НА КОТОРЫЕ ЛИД ОТВЕЧАЛ (замеры 04.09 и 11.09), то есть мерил не тем прибором.
    # В POST_TIERS его НЕ добавлять: там живут правила одного сообщения в ленту
    # (F1-md-heading, F4-lists), и для передачи файла они дают ложный красный.
    # Что для peer-dm остаётся в силе и не ослаблено: чёрные списки слопа (F2/F3),
    # правило абзацев, запрет выдуманных цифр, приватность.
    "peer-dm":  (None, None),
    # ⭐ 240-500 -- число Антона (21.08.2026, постановка ДР-полосы): "Длина тизера по
    # дипресерчам 240-500 символов". Это ОТДЕЛЬНАЯ полоса, а не замена "teaser": обычный
    # тизер по-прежнему 200-250 (контракт 06.08, влезть в X). У ДР-тизера две обязательные
    # половины -- зачем гнали ресёрч и что получили -- в 250 знаков они не помещаются.
    # Ссылка и раскрытие авторства в лимит НЕ входят, идут отдельной строкой.
    # В X эта полоса едет укороченной версией + короткая ссылка на корпус целиком.
    "dr-teaser": (240, 500),   # HARD, обе границы
}
TIER_HARD = {"teaser", "tg-post", "dr-teaser"}  # обе границы жёсткие -> FAIL; иначе WARN
# ⭐ 25.08.2026: medium сюда НЕ добавлять -- у него жёсткий только ПОТОЛОК (TIER_HARD_MAX),
# пол мягкий, и это осознанно. Замер хаба: из 61 готового FB-medium черновика 22 (36%)
# перелетели 2000, медиана популяции 1993 -- подпись писателя, который целится В потолок
# без жёсткого стопа. Корень был не здесь, а в двух местах ниже: lenhint() судил жёсткость
# ТОЛЬКО по TIER_HARD и печатал писателю «800-2000 знаков» без (HARD), хотя потолок бьёт
# насмерть; и ветка потолка в check() тоже смотрела в TIER_HARD, расходясь со slop_gate.
# Дверь: _test_tier_contract_hardness.py.
# Верхняя граница жёсткая ещё и у medium (спека §2.1: «HARD выше 2000»), нижняя -- нет.
TIER_HARD_MAX = {"teaser", "tg-post", "medium", "dr-teaser"}

TIER_GEO = {"teaser": "низкий", "tg-post": "низкий", "medium": "низкий",
            "dr-teaser": "низкий",
            "longread": "высокий", "dev-log": "максимальный"}
TIER_NARRATIVE = {  # S3 overlay ([[style-reality-show]])
    "teaser":   "завершённая польза + дверь (некликнувший унёс применимое; "
                "клиффхэнгер без пользы ЗАПРЕЩЁН -- Антон 06.08)",
    "tg-post":  "один факт -> почему важно -> деталь -> ссылка (спека §2.2)",
    "medium":   "полный эпизод с дугой (ставки → поворот → крючок)",
    "longread": "«расширенная серия» + recap арки",
    "dev-log":  "«сырьё со съёмочной площадки», БЕЗ драматизации",
}

# --- the §7.2 draft set: one file per (tier, platform). phase=1 = this build. ----
# register = which content_publish.py register on export (tg/fb/x), or None for
# GitHub/Reddit/VC.ru/Хабр (published via gh / native, not content_publish).
PARTS = [
    # ---- teaser (200-250) ----
    {"file": "teaser-ru.md", "tier": "teaser", "platform": "@ClawRus", "lang": "ru",
     "voice": "авторский", "model": "Fable 5 (Opus = fallback)", "register": "tg", "phase": 1,
     "canonical": GITHUB_REPO, "cta": False,
     "cross": "→ свой longread (longread-ru, в канале @ClawRus); 🇬🇧 EN-версия на X"},
    {"file": "teaser-en.md", "tier": "teaser", "platform": "X", "lang": "en",
     "voice": "авторский", "model": "Fable 5 (Opus = fallback)", "register": "x", "phase": 1,
     "canonical": GITHUB_REPO, "cta": False,
     "cross": "→ EN longread (GitHub canonical); 🇷🇺 RU version: Telegram (@ClawRus)"},

    # ---- medium (800-2000 HARD, FB RU only, link in 1st comment) ----
    {"file": "medium-fb.md", "tier": "medium", "platform": "FB", "lang": "ru",
     "voice": "авторский дневник", "model": "Fable 5 (Opus = fallback)", "register": "fb", "phase": 1,
     "canonical": GITHUB_REPO, "cta": True,
     "cross": "ссылка → longread в 1-м КОММЕНТАРИИ + вопрос для обсуждения (НЕ в теле — FB душит охват ссылок)"},
    # ⭐ 26.08.2026, приказ Антона: «должна быть РУ и АНГЛ версия на каждый пост».
    # До этого дня medium был единственным тиром БЕЗ языковой пары (замер: 58 из 117
    # непарных позиций очереди - ровно он). Площадка EN-версии = dev.to (матрица:
    # medium разрешён, аудитория = EN-инженеры Mission-2). Бэклог догнан воркфлоу
    # lang-pairs-backlog; эта строка чинит СТАНОК, чтобы дырка не открылась заново.
    # ⭐ 03.09.2026 ПЕРЕЦЕЛЕНО с dev.to на [аккаунт]. Причина честная: учётки dev.to у нас
    # НЕТ вовсе (secrets: «no stored creds; sign up when doing that surface»), а заводить
    # аккаунты я не имею права — рельса была мертворождённой, и 58 готовых EN-medium висели
    # с «площадка не в таблице маршрутов». [аккаунт] — живой EN-канал (~169k, замер 03.09:
    # 5 постов за день, 47-66 просмотров), лимита нет, маршрут уже был в ROUTES.
    # dev.to вернём, когда у Антона появится аккаунт и API-ключ.
    {"file": "medium-en.md", "tier": "medium", "platform": "[аккаунт]", "lang": "en",
     "voice": "авторский дневник", "model": "Fable 5 (Opus = fallback)", "register": None, "phase": 1,
     "canonical": GITHUB_REPO, "cta": True,
     "cross": "EN-пара medium-fb: смысл 1:1, футер по матрице площадки; ← teaser-en; → longread-en"},

    # ---- longread (4000+) ----
    # ⭐ ПЛОЩАДКА ИСПРАВЛЕНА 14.08.2026: было «@ClawRus». Лонгрид ЦЕЛИКОМ в TG-канал
    # запрещён с 31.07 (регламент матрицы площадок, origin: anton) — в канал идёт
    # teaser-ru + ссылка. 01.08 по этому правилу перечинили 24 готовых файла, но САМУ
    # фабрику не тронули, и она продолжила рождать нарушение: к 14.08 набежало ещё три.
    # Чинить выход, не чиня станок, = подписаться на бесконечную уборку.
    {"file": "longread-ru.md", "tier": "longread", "platform": "VC.ru", "lang": "ru",
     "voice": "авторский reality-show", "model": "Fable 5 (Opus = fallback)", "register": "tg", "phase": 1,
     "canonical": GITHUB_REPO, "cta": True,
     "cross": "← teaser-ru (он и идёт в канал со ссылкой сюда); → dev-log; canonical → GitHub (longread-en)"},
    {"file": "longread-en.md", "tier": "longread", "platform": "GitHub", "lang": "en",
     "voice": "авторский reality-show", "model": "Fable 5 (Opus = fallback)", "register": None, "phase": 1,
     "canonical": "self (GitHub canonical)", "cta": True,
     "cross": "← teaser-en; → dev-log; this IS the GitHub canonical other platforms point to"},

    # ---- dev-log (dry, GitHub EN canonical) ----
    {"file": "devlog.md", "tier": "dev-log", "platform": "GitHub", "lang": "en",
     "voice": "технический, безличный", "model": "Sonnet (скаффолд) + Fable 5/Opus (связность)",
     "register": None, "phase": 1, "canonical": "self (GitHub canonical)", "cta": False,
     "cross": "→ longread; стабильные anchor-ссылки на наши Deep Research"},

    # ---- longread RU GEO adapters (phase 1 since 2026-07-04, style-files built) ----
    {"file": "longread-vcru.md", "tier": "longread", "platform": "VC.ru", "lang": "ru",
     "voice": "авторский reality-show", "model": "Fable 5 (Opus = fallback)", "register": None, "phase": 1,
     "canonical": GITHUB_REPO, "cta": True, "style": "_STYLE-vcru.md",
     "cross": "← teaser-ru; → dev-log; canonical → GitHub",
     "note": "бизнес-кейс/история/топ-лист, минимум кода. Публикация вручную (не content_publish)."},
    {"file": "longread-habr.md", "tier": "longread", "platform": "Хабр", "lang": "ru",
     "voice": "авторский reality-show", "model": "Fable 5 (Opus = fallback)", "register": None, "phase": 1,
     "canonical": GITHUB_REPO, "cta": True, "style": "_STYLE-habr.md",
     "cross": "← teaser-ru; → dev-log; canonical → GitHub",
     "note": "технический deep-dive: код, Q&A-заголовки, TL;DR. Публикация вручную (не content_publish)."},

    # ==== PHASE 2 (deferred; scaffolded only with --with-phase2) ====
    {"file": "devlog-reddit.md", "tier": "dev-log", "platform": "Reddit", "lang": "en",
     "voice": "технический, безличный", "model": "Sonnet (скаффолд) + Fable 5/Opus (связность)",
     "register": None, "phase": 2, "canonical": GITHUB_REPO, "cta": False,
     "cross": "→ longread; canonical → GitHub",
     "note": "нативный рерайт обязателен (спам-гейт Reddit); участвуй-первым."},
]


def lenhint(tier):
    lo, hi = TIER_LEN.get(tier, (None, None))
    if lo and hi:
        hard = tier in TIER_HARD or tier in TIER_HARD_MAX
        return "%d–%d знаков%s" % (lo, hi, " (HARD)" if hard else "")
    if lo and not hi:
        return ">= %d знаков" % lo
    return "без лимита (сухой лог)"


def ensure():
    os.makedirs(EPI, exist_ok=True)


def slug_dir(slug):
    return os.path.join(EPI, slug)


def cta_text(part):
    return CTA_RU if part["lang"] == "ru" else CTA_EN


def make_placeholder(part, material=""):
    lines = [
        "<!-- DRAFT (draft-first, НЕ опубликовано). НИКАКОГО copy-paste — нативный рерайт под площадку. -->",
        "<!-- ТИР: %s · ПЛОЩАДКА: %s · ЯЗЫК: %s -->" % (part["tier"], part["platform"], part["lang"]),
        "<!-- ГОЛОС: %s · МОДЕЛЬ: %s -->" % (part["voice"], part["model"]),
        "<!-- ДЛИНА: %s · GEO-приоритет: %s -->" % (lenhint(part["tier"]), TIER_GEO.get(part["tier"], "?")),
        "<!-- НАРРАТИВ (S3 [[style-reality-show]]): %s -->" % TIER_NARRATIVE.get(part["tier"], ""),
        "<!-- КРОСС-ССЫЛКИ: %s -->" % part["cross"],
        "<!-- CANONICAL → %s -->" % part["canonical"],
    ]
    if part.get("style"):
        lines.append("<!-- СТИЛЬ-ФАЙЛ (подгрузить на Generate): %s -->" % part["style"])
    lines.append("<!-- ПОЗИЦИОНИРОВАНИЕ (anton 2026-07-07, ВСЕ тиры): подгрузить _STYLE-positioning.md — "
                 "шоу и работа в Anthropic/OpenAI = ОДНА машина; не-кодер+AI-кофаундер = козырь; "
                 "веди артефактом, не «hire me» (missionary, не mercenary). -->")
    if part.get("cta"):
        lines.append("<!-- CTA co-founder (правило Антона, в конце): %s -->" % cta_text(part))
    if part["tier"] != "teaser":
        lines.append("<!-- ФУТЕР §7.7 (anton 03.07): собрать блоки из _STYLE-footer.md — "
                     "medium=A+B+C+E · longread=A+B+C+D+E · dev-log=A+C+D+E; "
                     "на FB весь футер в 1-м КОММЕНТЕ; в блок B только ЖИВЫЕ ссылки из реестра. -->")
    if part.get("note"):
        lines.append("<!-- ЗАМЕТКА АДАПТЕРА: %s -->" % part["note"])
    if part["tier"] == "medium":
        lines.append("<!-- FB-СПЕЦИФИКА: тело БЕЗ ссылки; ссылку на longread + вопрос — отдельным блоком «1-Й КОММЕНТАРИЙ» ниже. -->")
    lines.append("<!-- ПРИВАТНОСТЬ: чужие имена/@/суммы/лиды/ключи/DM — обобщать. "
                 "Карв-аут: WhatsApp co-founder " + CTA_PHONE + " = авторизованный ПУБЛИЧНЫЙ контакт, оставлять. -->")
    if part.get("voice", "").startswith("авторский"):
        # ⚠️ ЭТАЛОН ОБЯЗАТЕЛЕН. До 28.07 здесь стоял список вики-ссылок, из которого
        # [[fb-diary-voice]] = мёртвая ссылка (это память на C:, а не заметка волта), а
        # _STYLE.md — единственный файл, где лежит ПРАВКА САМОГО АНТОНА (★ЭТАЛОН 06.06) и
        # его лексикон — не был указан ВООБЩЕ. Писатель получал прилагательные («авторский
        # reality-show») вместо камертона. Даём абсолютные пути, а не вики-ссылки.
        # Проверяем, что камертон реально лежит на диске: впечатать мёртвый путь = та же
        # болезнь, что мы лечим (писатель «загрузил палитру», которой нет). Нашёл Codex T3.
        miss = [p for p in (STYLE_ETALON, CRAFT_FILE) if not os.path.exists(p)]
        lines.append("<!-- ★ЭТАЛОН ГОЛОСА (ПРОЧИТАТЬ ЦЕЛИКОМ ДО ПЕРВОЙ БУКВЫ, не пересказ): "
                     + STYLE_ETALON + " (правка Антона 06.06 + лексикон + few-shot) · "
                     + CRAFT_FILE + " (10 законов + типология крючков + чек-лист). "
                     "Плюс палитра: [[style-reality-show]] + [[style-gershuni-influence]]. -->")
        if miss:
            lines.append("<!-- ❗ЭТАЛОН НЕ НАЙДЕН НА ДИСКЕ: " + " · ".join(miss) +
                         " . Проверь OBSIDIAN_VAULT. Писать авторский голос БЕЗ камертона "
                         "запрещено: найди файлы или подними вопрос, не пиши вслепую. -->")
            print("WARN эталон голоса не найден: %s (проверь OBSIDIAN_VAULT)" % ", ".join(miss),
                  file=sys.stderr)
        lines.append(ANTIVANILLA)
    # БЕЗ КУПЮР -- на ВСЕ тиры, а не только на авторский голос: дев-лог тоже может нести
    # его цитату, и вычистить её там так же запрещено.
    lines.append(ANTICENSOR)
    if material:
        safe = material.replace("-->", "--&gt;").strip()
        lines.append("<!-- ИСХОДНЫЙ МАТЕРИАЛ (S4 seed — писать ИЗ него, нативно под площадку, "
                     "приватное обобщить, НЕ копипаст). ⛔ «Нативно под площадку» = форма, "
                     "не смысл: формулировки Антона из материала переносятся дословно (см. "
                     "БЕЗ КУПЮР выше). Обобщать разрешено ТОЛЬКО приватное (чужие имена, "
                     "суммы, лиды, ключи) -- не резкость: %s -->" % safe)
    body = "\n".join(lines) + "\n\n(черновик ещё не написан)\n"
    if part["tier"] == "medium":
        body += "\n\n—— 1-Й КОММЕНТАРИЙ (ссылка + вопрос, НЕ в теле поста) ——\n(ссылка на longread + вопрос для обсуждения)\n"
    return body


def cmd_new(a):
    ensure()
    # --- S4 -> S5 stitch: read the episode seed and auto-fill the bundle -----------
    material, visibility, lang_hint = "", "public", ""
    if getattr(a, "from_seed", ""):
        if not os.path.exists(a.from_seed):
            print("ERR no such seed: %s" % a.from_seed); sys.exit(2)
        with open(a.from_seed, encoding="utf-8") as f:
            seed = json.load(f)
        # explicit CLI flags win over seed fields; else take from seed
        a.slug = a.slug or seed.get("slug", "")
        a.title = a.title or seed.get("title", "")
        a.source = a.source or seed.get("source", "")
        material = seed.get("material", "")
        visibility = seed.get("visibility", "public")
        lang_hint = seed.get("lang_hint", "")
    if not a.slug or not a.title:
        print("ERR need --slug and --title (or a --from-seed carrying them)"); sys.exit(2)
    # PRIVACY GATE (HANDOFF contract): private never becomes a public episode.
    if visibility == "private":
        print("BLOCKED seed is PRIVATE -> never a public episode. Personal lane only."); sys.exit(3)
    d = slug_dir(a.slug)
    if os.path.exists(d):
        print("ERR slug exists: %s" % a.slug); sys.exit(2)
    parts = [p for p in PARTS if p["phase"] == 1 or a.with_phase2]
    # personal = life-as-story: RU-only, generalized; keep OUT of dev-log + GitHub +
    # EN showcase (HANDOFF: "personal ⛔ НЕ на публичный GitHub/дев-лог/X").
    dropped = []
    if visibility == "personal":
        keep = [p for p in parts if p["lang"] == "ru" and p["platform"] != "GitHub" and p["tier"] != "dev-log"]
        dropped = [p["file"] for p in parts if p not in keep]
        parts = keep
    os.makedirs(d)
    when = a.when or datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    meta = {
        "slug": a.slug, "title": a.title, "source": a.source or "",
        "created": when, "status": "draft",
        "decision": "decision-content-pipeline-reality-show",
        "contract": "§7.2 v2 (2026-06-30)",
        "visibility": visibility, "lang_hint": lang_hint,
        "from_seed": os.path.basename(a.from_seed) if getattr(a, "from_seed", "") else "",
        "material": material,
        "phase2_included": bool(a.with_phase2),
        "canonical_repo": GITHUB_REPO,
        "parts": [],
    }
    for p in parts:
        with open(os.path.join(d, p["file"]), "w", encoding="utf-8") as f:
            f.write(make_placeholder(p, material))
        meta["parts"].append({
            "file": p["file"], "tier": p["tier"], "platform": p["platform"],
            "lang": p["lang"], "voice": p["voice"], "model": p["model"],
            "register": p["register"], "phase": p["phase"],
            "canonical": p["canonical"], "cross_links": p["cross"], "cta": p["cta"],
            "style": p.get("style"),
        })
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("created episode bundle: %s (%d drafts, visibility=%s, phase2=%s)" % (
        a.slug, len(parts), visibility, bool(a.with_phase2)))
    if material:
        print("material injected from seed (%d chars) -> writer writes FROM it" % len(material))
    if dropped:
        print("privacy gate (personal): dropped %d public/EN/dev-log tiers: %s" % (len(dropped), ", ".join(dropped)))
    print("dir: %s" % d)
    print("next: write each draft (voice per file), then `check --slug %s`" % a.slug)


def load_meta(slug):
    mp = os.path.join(slug_dir(slug), "meta.json")
    if not os.path.exists(mp):
        print("ERR no such slug: %s" % slug); sys.exit(2)
    with open(mp, encoding="utf-8") as f:
        return mp, json.load(f)


def cmd_list(_):
    if not os.path.isdir(EPI):
        print("(no episodes yet)"); return
    rows = []
    for s in sorted(os.listdir(EPI)):
        mp = os.path.join(EPI, s, "meta.json")
        if os.path.exists(mp):
            with open(mp, encoding="utf-8") as f:
                m = json.load(f)
            rows.append((s, m.get("status", "?"), len(m.get("parts", [])), m.get("created", "?")))
    if not rows:
        print("(no episodes yet)"); return
    for s, st, n, cr in rows:
        print("%-40s status=%-10s parts=%-2d created=%s" % (s, st, n, cr))


def cmd_show(a):
    mp, _ = load_meta(a.slug)
    with open(mp, encoding="utf-8") as f:
        print(f.read())


def cmd_set_status(a):
    mp, m = load_meta(a.slug)
    m["status"] = a.status
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    print("status %s -> %s" % (a.slug, a.status))


# --- body extraction: strip scaffolding HTML comments + placeholder lines --------
_COMMENT = re.compile(r"<!--.*?-->", re.S)


def written_body(path):
    """Return human-written text (no HTML-comment scaffolding, no placeholder stubs)."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return None
    txt = _COMMENT.sub("", raw)
    for stub in ("(черновик ещё не написан)",
                 "(ссылка на longread + вопрос для обсуждения)",
                 "—— 1-Й КОММЕНТАРИЙ (ссылка + вопрос, НЕ в теле поста) ——"):
        txt = txt.replace(stub, "")
    return txt.strip()


def _tier_of(part, fname):
    t = part.get("tier")
    if t:
        return t
    n = fname.lower()
    if "teaser" in n:
        return "teaser"
    if "longread" in n:
        return "longread"
    if "devlog" in n or "dev-log" in n:
        return "dev-log"
    return "medium"


def cmd_check(a):
    """VISIBILITY LAYER: lint each written draft vs its tier budget + canonical/CTA."""
    _, m = load_meta(a.slug)
    d = slug_dir(a.slug)
    print("EPISODE %s  (status=%s, contract=%s)" % (a.slug, m.get("status", "?"), m.get("contract", "?")))
    print("%-18s %-9s %-7s %-7s %s" % ("file", "tier", "chars", "verdict", "note"))
    print("-" * 78)
    fails = warns = empty = 0
    for part in m.get("parts", []):
        f = part["file"]
        tier = _tier_of(part, f)
        body = written_body(os.path.join(d, f))
        if not body:
            empty += 1
            print("%-18s %-9s %-7s %-7s %s" % (f, tier, "0", "EMPTY", "черновик не написан"))
            continue
        n = len(body)
        lo, hi = TIER_LEN.get(tier, (None, None))
        notes, verdict = [], "OK"
        if lo and n < lo:
            verdict = "FAIL" if tier in TIER_HARD else "WARN"
            notes.append("короче минимума %d" % lo)
        elif hi and n > hi:
            verdict = "FAIL" if tier in TIER_HARD_MAX else "WARN"
            notes.append("длиннее максимума %d" % hi)
        # CTA presence (standing rule; WARN, not contract-mandated FAIL)
        if part.get("cta") and CTA_PHONE not in body:
            if verdict == "OK":
                verdict = "WARN"
            notes.append("нет CTA co-founder")
        # footer §7.7 presence (anton 03.07): calendly = cheapest proxy for the footer
        if tier != "teaser" and "calendly.com/paloaltolab" not in body:
            if verdict == "OK":
                verdict = "WARN"
            notes.append("нет футера §7.7 (_STYLE-footer.md)")
        if verdict == "FAIL":
            fails += 1
        elif verdict == "WARN":
            warns += 1
        print("%-18s %-9s %-7d %-7s %s" % (f, tier, n, verdict, "; ".join(notes)))
    print("-" * 78)
    print("summary: FAIL=%d  WARN=%d  EMPTY=%d  (of %d parts)" % (fails, warns, empty, len(m.get("parts", []))))
    print("note: teaser length is HARD; medium/longread length + CTA + footer §7.7 are WARN-level.")
    if fails:
        sys.exit(1)


def cmd_export(a):
    """Bridge a bundle into the EXISTING publish path. Telegram-postable registers
    (tg/fb/x) go into drafts/episode-<slug>.md that content_approve.py +
    content_publish.py already understand. GitHub/Reddit/VC.ru/Хабр are listed for
    manual gh/native publish (content_publish posts to Telegram Saved only)."""
    _, m = load_meta(a.slug)
    d = slug_dir(a.slug)
    by_reg, github, native = {}, [], []
    for part in m.get("parts", []):
        body = written_body(os.path.join(d, part["file"]))
        if not body:
            continue
        reg = part.get("register")
        label = "%s/%s (%s)" % (part.get("tier", "?"), part.get("platform", "?"), part.get("lang", "?"))
        if reg in ("tg", "fb", "x"):
            by_reg.setdefault(reg, []).append((label, body))
        elif part.get("platform") == "GitHub":
            github.append(part)          # -> ready-to-run git commands (Q4: manual gh)
        else:
            native.append("%s -> %s" % (part["file"], part.get("platform", "?")))  # VC.ru/Хабр/Reddit
    manual = ["%s -> GitHub" % p["file"] for p in github] + native
    if not by_reg and not manual:
        print("nothing written yet — fill the drafts before export."); sys.exit(2)
    os.makedirs(DRAFTS, exist_ok=True)
    out = os.path.join(DRAFTS, "episode-%s.md" % a.slug)
    when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    reg_head = {"tg": "TG-канал", "fb": "FB", "x": "X-тред"}
    lines = [
        "---", "type: content-factory-draft", "source: episode-%s" % a.slug,
        "title: %s" % json.dumps(m.get("title", a.slug), ensure_ascii=False),
        "canonical: %s" % m.get("canonical_repo", GITHUB_REPO),
        "exported: %s" % when, "status: review", "---", "",
        "<!-- Экспорт эпизода в общий путь публикации (draft-first). Одобрение = "
        "content_approve.py; постинг = content_publish.py (по умолчанию -> Saved). "
        "GitHub/Reddit/VC.ru/Хабр публикуются вручную (gh / нативно), не через content_publish. -->", "",
    ]
    for reg in ("tg", "x", "fb"):
        if reg not in by_reg:
            continue
        lines += ["## -> %s" % reg_head[reg], ""]
        for label, body in by_reg[reg]:
            lines += ["<!-- %s -->" % label, body, ""]
    gh_cmds = []
    if github:
        for p in github:
            sub = GH_SUBDIR.get(p.get("tier"), "longreads")
            src = os.path.join(d, p["file"])
            dst = "%s\\%s\\%s.md" % (REPO_CLONE, sub, a.slug if p["tier"] != "dev-log" else a.slug + "-devlog")
            gh_cmds.append('copy "%s" "%s"' % (src, dst))
        gh_cmds.append('cd /d "%s" && git add -A && git commit -m "episode: %s" && git push  # Tier-2 outbound: ТОЛЬКО по «публикуем»' % (REPO_CLONE, a.slug))
    if manual:
        lines += ["", "<!-- MANUAL PUBLISH (вне content_publish, канон=GitHub): -->"]
        lines += ["<!--   %s -->" % x for x in manual]
    if gh_cmds:
        lines += ["", "<!-- GitHub-публикация (ручной gh, draft-first — запускать ТОЛЬКО по «публикуем»):"]
        lines += ["     %s" % c for c in gh_cmds]
        lines += ["-->"]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("exported -> %s" % out)
    print("content_publish registers: %s" % (", ".join("%s(%d)" % (r, len(v)) for r, v in by_reg.items()) or "none"))
    if github:
        print("GitHub (manual gh, commands in note): %s" % ", ".join(p["file"] for p in github))
    if native:
        print("native manual (VC.ru/Хабр/Reddit): %s" % "; ".join(native))
    print("next: content_approve.py --serve  ->  content_publish.py --dry-run  (GitHub = run gh block by hand on «публикуем»)")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    n = sub.add_parser("new")
    n.add_argument("--slug", default="")
    n.add_argument("--title", default="")
    n.add_argument("--source", default="")
    n.add_argument("--when", default="")
    n.add_argument("--from-seed", dest="from_seed", default="",
                   help="S4 episode-seed JSON: auto-fills slug/title/source, injects material, applies privacy gate")
    n.add_argument("--with-phase2", action="store_true", dest="with_phase2",
                   help="also scaffold deferred VC.ru / Хабр / Reddit adapters")
    n.set_defaults(func=cmd_new)
    sub.add_parser("list").set_defaults(func=cmd_list)
    sh = sub.add_parser("show"); sh.add_argument("--slug", required=True); sh.set_defaults(func=cmd_show)
    ck = sub.add_parser("check"); ck.add_argument("--slug", required=True); ck.set_defaults(func=cmd_check)
    ex = sub.add_parser("export"); ex.add_argument("--slug", required=True); ex.set_defaults(func=cmd_export)
    ss = sub.add_parser("set-status"); ss.add_argument("--slug", required=True); ss.add_argument("--status", required=True); ss.set_defaults(func=cmd_set_status)
    args = p.parse_args()
    if not getattr(args, "func", None):
        p.print_help(); sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
