#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
platform_gate.py — ПЛОЩАДОЧНЫЙ гейт контент-фабрики (0 токенов, детерминированно).

ЗАЧЕМ (приказ Антона голосом 30.07 11:24 и 31.07 02:58):
    «Нужно сделать так, чтобы ни один робот не опубликовал ничего,
     если этот пост не согласуется с этим правилом.»

Чем отличается от соседей — три разных вопроса, не дублируем:
    slop_gate.py     — КАК написано (слоп, ритм, длина ТИРА)
    approval_clock.py— МОЖНО ли уже (24ч согласования)
    platform_gate.py — ТУДА ЛИ несём (этот тир на этой площадке вообще разрешён?)

Источник правил: platform_rules.json рядом. Цифры длины тира НЕ дублируются —
берутся из episode_adapter.TIER_LEN (один источник, ноль копий).

FAIL-CLOSED: неизвестная площадка, нечитаемые правила, площадка со статусом
blocked/research — отказ. Молчаливого «ну наверное можно» здесь нет.

Коды возврата (как у slop_gate): 0 = PASS, 1 = WARN, 2 = FAIL, 3 = ошибка гейта.

Использование:
    python platform_gate.py --file draft.md --tier teaser --platform X
    python platform_gate.py --chars 812 --tier medium --platform tg-chat --json
    python platform_gate.py --list                 # вся матрица, для дашборда
    python platform_gate.py --selftest             # прогон регресс-сетки
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.environ.get("PLATFORM_RULES", os.path.join(HERE, "platform_rules.json"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_rules(path=None):
    p = path or RULES_PATH
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def tier_limits():
    """Длины тиров — из episode_adapter, а не своей копией."""
    try:
        sys.path.insert(0, HERE)
        import episode_adapter as EA  # noqa
        return dict(EA.TIER_LEN)
    except Exception:
        return {}


FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


# У FB-постов ссылка и футер по контракту уезжают в ПЕРВЫЙ КОММЕНТАРИЙ, а не в тело
# («FB душит охват ссылок»). Блок лежит в том же файле ниже маркера -- и считать его
# телом поста значит завышать длину: 4 поста из 18 «не влезали» только из-за этого.
# Маркер живёт в трёх начертаниях тире, поэтому тире тут -- класс символов, не литерал.
FIRST_COMMENT_RE = re.compile(
    r"^[ \t]*(?:[-—–=]{2,}|#{1,6})[ \t]*(?:1-Й|ПЕРВЫЙ)\s+КОММЕНТАРИЙ.*$", re.M | re.I)


# ⭐ 25.08.2026, ТРЕТИЙ случай класса «в длину вошло то, что телом не является»
# (22.08 tg_channel_post.body_of, 23.08 platform_gate). Маркер первого комментария живёт
# в ДВУХ начертаниях. Словесное («1-Й КОММЕНТАРИЙ») дверь знала. Второе -- голый
# разделитель «· · ·», за которым идут футерные блоки A/B/C/E -- нет, и им пользуются
# 48 из 61 живого FB-medium черновика. Цена молчания: 19 законных постов висели в
# очереди с FAIL P4-over-platform-cap, медиана их ТЕЛА 1673 при потолке 2000.
# Граница намеренно узкая: голый разделитель сам по себе футером НЕ считается --
# режем, только если ниже есть канонический маркер футера (_STYLE-footer.md).
FOOTER_SEP_RE = re.compile(r"^[ 	]*(?:[·•*·]\s*){3,}[ 	]*$", re.M)
FOOTER_MARKERS = (
    u"linktr.ee/paloaltoailab",
    u"calendly.com/paloaltolab",
    u"Придумано Майкрофтом",
    u"Proudly made in Silicon Valley",
    u"Palo Alto AI Research Lab",
    u"t.me/PaloAltoAiRu",
    u"github.com/tonydzi",
)


def _cut_footer_by_separator(body):
    """Отрезать футерный блок, начинающийся голым разделителем.

    Возвращает тело без футера. Если ниже разделителя футера нет -- тело как было:
    «· · ·» в середине рассказа остаётся частью поста."""
    for m in FOOTER_SEP_RE.finditer(body):
        tail = body[m.end():]
        if any(mark in tail for mark in FOOTER_MARKERS):
            return body[:m.start()]
    return body


def strip_headers(text):
    """Текст БЕЗ служебных шапок: комментарии робота и YAML-frontmatter в ЛЮБОМ порядке.

    26.08.2026: раньше frontmatter резался только когда файл НАЧИНАЛСЯ с «---».
    В живом корпусе половина черновиков открывается комментарием робота
    («<!-- ТИР: medium · ПЛОЩАДКА: facebook -->»), а YAML идёт СЛЕДОМ -- и тогда
    весь YAML (title, funnel_ids, facts_from) попадал в длину тела. Тот же класс,
    что 22.08 у tg_channel_post.body_of и 23.08 здесь же. Поэтому снимаем шапки
    ЦИКЛОМ, пока сверху есть хоть одна: порядок их следования -- не наше дело.
    """
    if not text:
        return ""
    body = text.lstrip("﻿").lstrip()
    while True:
        m = FM_RE.match(body)
        if m:
            body = body[m.end():].lstrip()
            continue
        m = re.match(r"<!--.*?-->\s*", body, flags=re.S)
        if m:
            body = body[m.end():].lstrip()
            continue
        break
    # комментарии робота могут стоять и в середине шапки -- их в теле быть не должно
    return re.sub(r"<!--.*?-->", "", body, flags=re.S)


def post_chars(text, platform=None, rules=None):
    """Знаки ТЕЛА поста. ОДИН источник правила «что считается телом»:
    им пользуются файловый путь (body_chars), публикатор и распределитель.
    Две разные формулы на один вопрос неминуемо разъезжаются, и тогда гейт
    блокирует законный пост -- ровно это и случилось с 19 FB-черновиками.

    platform: где публикуем. Нужен потому, что футер уходит первым комментарием
    НЕ везде -- на FB да (канон _STYLE-footer.md), в TG-канале футер часть поста.
    Не назвали площадку -- режем только по ЯВНОМУ маркеру «1-Й КОММЕНТАРИЙ»,
    догадки по разделителю не применяем.
    """
    if not text:
        return 0
    body = strip_headers(text)
    fc = FIRST_COMMENT_RE.search(body)        # явная воля автора: режем всегда
    if fc:
        body = body[:fc.start()]
    if platform and _footer_goes_to_comment(platform, rules):
        body = _cut_footer_by_separator(body)
    return len(body.strip())


# ⭐ 27.08.2026: ДВА РАЗНЫХ ЧИСЛА, и путать их дорого.
#   post_chars  -- что реально УЙДЁТ: судит потолок ПЛОЩАДКИ (ей всё равно, что мы
#                  считаем обёрткой, она режет по своему лимиту).
#   tier_chars  -- АВТОРСКИЙ ТЕКСТ: судит коридор ТИРА. Тир про то, КАК человек пишет,
#                  а не сколько весит обязательная подпись.
# Замер: 66 из 103 свежих переводов получили WARN «перелёт тира», и ни один не был
# настоящим -- в длину входили строка раскрытия (§3.3 дословно: «в бюджет слов не
# входит») и блок ссылки за «· · ·» (обязательный элемент тизера по slop_gate).
# Систематически неверный WARN хуже отсутствия WARN: он учит не смотреть на прибор.
_WRAPPER_SEP_RE = re.compile(r"^[ 	]*(?:[·•*·]\s*){3,}[ 	]*$", re.M)


def tier_chars(text, platform=None, rules=None):
    """Знаки АВТОРСКОГО ТЕКСТА: без служебных шапок, без строки раскрытия авторства
    и без хвостового блока со ссылкой на полную версию."""
    body = strip_headers(text)
    fc = FIRST_COMMENT_RE.search(body)
    if fc:
        body = body[:fc.start()]
    if platform and _footer_goes_to_comment(platform, rules):
        body = _cut_footer_by_separator(body)
    # хвост «· · ·» + ссылка: обязательная обёртка, не авторский текст. Режем ТОЛЬКО
    # если ниже действительно ссылка -- разделитель посреди рассказа остаётся текстом.
    for m in _WRAPPER_SEP_RE.finditer(body):
        tail = body[m.end():]
        if "http" in tail:
            body = body[:m.start()]
            break
    # строка раскрытия авторства сверху
    lines = body.strip().split(chr(10))
    if lines and _DISCLOSURE_LINE_RE.search(lines[0]):
        lines = lines[1:]
    return len(chr(10).join(lines).strip())


# Регулярку раскрытия держим рядом с гейтом распределителя ОДНУ на всех: правило
# «что считается раскрытием» живёт в slop_gate.REQUIRED_ELEMENTS.
def _disclosure_line_re():
    try:
        import slop_gate
        for name, pat in slop_gate.REQUIRED_ELEMENTS:
            if name == "подпись/авторство":
                return re.compile(pat, re.IGNORECASE | re.UNICODE)
    except Exception:
        pass
    return re.compile(r"(?:синтетическ\w+ кофаундер|synthetic co-?founder)",
                      re.IGNORECASE | re.UNICODE)


_DISCLOSURE_LINE_RE = _disclosure_line_re()


def _footer_goes_to_comment(platform, rules=None):
    """Правда из матрицы, не из головы: у площадки стоит footer_in_first_comment."""
    try:
        rules = rules or load_rules()
        key = resolve_platform(platform, rules)
    except Exception:
        return False
    if not key:
        return False
    return bool(rules.get("platforms", {}).get(key, {}).get("footer_in_first_comment"))


def body_chars(path, platform=None, rules=None):
    """Знаки ТЕЛА файла: без шапок, без 1-го комментария, без футера там, где он в комменте."""
    with open(path, encoding="utf-8") as f:
        return post_chars(f.read(), platform=platform, rules=rules)


# Маршрут ЗАЯВЛЕН в шапке файла: «<!-- ТИР: teaser · ПЛОЩАДКА: X · ЯЗЫК: en -->».
# Раньше дашборд угадывал маршрут по ИМЕНИ файла -- и 38 файлов из 193 не совпали
# ни с одним префиксом, то есть гейт их просто не видел. Невидимый файл не охраняется,
# поэтому источник маршрута теперь один: то, что написано в самом файле.
TIER_RE = re.compile(r"(?:ТИР|TIER)\s*:\s*([A-Za-zА-Яа-я-]+)", re.I)
# «ЦЕЛЬ:» -- формат ранних эпизодов (до контракта §7.2). Читаем оба, иначе старый
# материал молча проходит мимо гейта только из-за возраста шапки.
PLAT_RE = re.compile(r"(?:ПЛОЩАДКА|PLATFORM|ЦЕЛЬ|TARGET)\s*:\s*([^·\n>]+)", re.I)
# Рабочая записка эпизода (README, seed, статусный файл) -- НЕ пост. Помечается
# в самом файле, а не списком имён в коде: иначе список разъедется с реальностью.
NOTPOST_RE = re.compile(r"НЕ\s*ПОСТ|NOT\s*A\s*POST", re.I)

# «Telegram megagroup ClawRus», «Telegram channel @ClawRus» -- у ранних шапок цель
# записана фразой. Отрезаем служебные слова, чтобы осталось имя площадки.
# ⚠️ Слово вырезается ТОЛЬКО когда стоит отдельно. Без охраны по краям регулярка
# съедала «channel» прямо из ключа площадки `tg-channel`, превращая живую шапку
# «tg-channel @ClawRus» в мусор «tg-  @ClawRus» — и гейт отбивал СВОЙ ЖЕ материал.
# Чистильщик, портящий вход, опаснее грязного входа: он ломает то, что было верным.
_NOISE = re.compile(
    r"(?<![-\w])(telegram|megagroup|channel|канал|группа|group)(?![-\w])", re.I)


def is_not_post(path):
    with open(path, encoding="utf-8") as f:
        return bool(NOTPOST_RE.search(f.read(1500)))


def header_route(path):
    """(тир, площадка) из шапки файла; None там, где не заявлено."""
    with open(path, encoding="utf-8") as f:
        head = f.read(4000)
    t = TIER_RE.search(head)
    p = PLAT_RE.search(head)
    plat = None
    if p:
        plat = _NOISE.sub(" ", p.group(1)).strip().rstrip(" -·") or None
    return (t.group(1).strip() if t else None), plat


def resolve_platform(name, rules):
    """Имя канала -> ключ площадки. Регистр не важен (CLAUDE.md §2.6)."""
    if not name:
        return None
    key = name.strip()
    plats = rules.get("platforms", {})
    if key in plats:
        return key
    low = key.lower()
    for k in plats:
        if k.lower() == low:
            return k
    aliases = rules.get("aliases", {})
    if low in aliases and aliases[low] in plats:
        return aliases[low]
    # Живые данные приходят грязными: «ClawRus (TG)», «@ClawRus», «FB / стена».
    # Нормализуем: убираем скобочный хвост и всё, кроме букв и цифр.
    # ⚠️ Только ТОЧНОЕ совпадение после нормализации — «похоже на» тут запрещено,
    # иначе гейт сам себе придумает площадку и пропустит пост не туда.
    def norm(s):
        s = re.sub(r"\(.*?\)", " ", s)
        s = re.sub(r"[^0-9a-zа-яё]+", "", s.lower())
        return s
    # «FB / стена», «X | тред» — разделитель значит «площадка + уточнение».
    # Пробуем целиком, потом каждый кусок, но ВСЕГДА точным совпадением.
    parts = [key] + [t for t in re.split(r"[/|·,]", key) if t.strip()]
    for cand in parts:
        n = norm(cand)
        if not n:
            continue
        for k in plats:
            if norm(k) == n:
                return k
        for a, target in aliases.items():
            if norm(a) == n and target in plats:
                return target
    return None


def check(platform, tier, chars=None, rules=None, tier_chars=None):
    """Возвращает (verdict, findings[]). Чистая функция — её и тестируем."""
    rules = rules or load_rules()
    out = []
    key = resolve_platform(platform, rules)

    if key is None:
        out.append(("FAIL", "P0-unknown-platform",
                    "площадка «%s» не описана в platform_rules.json — "
                    "публикация запрещена (fail-closed)" % platform))
        return "FAIL", out

    p = rules["platforms"][key]
    status = p.get("status", "active")
    if status == "blocked":
        out.append(("FAIL", "P1-platform-blocked",
                    "площадка %s заблокирована: %s" % (key, p.get("note", ""))))
        return "FAIL", out
    if status != "active":
        out.append(("FAIL", "P2-platform-not-ready",
                    "площадка %s в статусе «%s» — автопубликация закрыта до решения. %s"
                    % (key, status, p.get("open_question", ""))))
        return "FAIL", out

    allowed = p.get("allowed_tiers", [])
    if tier not in allowed:
        out.append(("FAIL", "P3-tier-not-allowed",
                    "тир «%s» на площадке %s (%s) запрещён; разрешено: %s. %s"
                    % (tier, key, p.get("kind", "?"), ", ".join(allowed) or "ничего",
                       p.get("note", ""))))

    cap = p.get("max_chars")
    if cap and chars is not None and chars > cap:
        out.append(("FAIL", "P4-over-platform-cap",
                    "%d знаков > потолка площадки %s (%d)" % (chars, key, cap)))

    # мягкие сигналы: не блокируют, но человек должен видеть
    if p.get("open_question"):
        out.append(("WARN", "P5-open-question",
                    "по площадке %s есть нерешённый вопрос: %s" % (key, p["open_question"])))
    lo_hi = tier_limits().get(tier)
    # Коридор тира судим по АВТОРСКОМУ тексту, если он назван; не назван -- по
    # отправляемому, как было раньше (обратная совместимость всех старых вызовов).
    tchars = tier_chars if tier_chars is not None else chars
    if lo_hi and lo_hi[0] and tchars is not None and tchars < lo_hi[0]:
        out.append(("WARN", "P6-under-tier-floor",
                    "%d знаков < нижней границы тира %s (%d) — это забота slop_gate, "
                    "здесь только сигнал" % (tchars, tier, lo_hi[0])))
    # потолок площадки может быть ШИРЕ потолка тира: тизер на 811 знаков влезает в
    # канал (2000), но тизером быть перестал. Без этого сигнала «PASS» врёт человеку.
    if lo_hi and lo_hi[1] and tchars is not None and tchars > lo_hi[1]:
        out.append(("WARN", "P7-over-tier-ceiling",
                    "%d знаков > верхней границы тира %s (%d): по площадке проходит, "
                    "но это уже не %s — решает slop_gate"
                    % (tchars, tier, lo_hi[1], tier)))

    if any(l == "FAIL" for l, _, _ in out):
        return "FAIL", out
    if any(l == "WARN" for l, _, _ in out):
        return "WARN", out
    return "PASS", out


def cmd_list(rules):
    print("МАТРИЦА ПЛОЩАДОК (platform_rules.json v%s)\n" % rules.get("_version"))
    hdr = "%-12s %-12s %-9s %-8s %s" % ("площадка", "тип", "статус", "потолок", "разрешённые тиры")
    print(hdr)
    print("-" * len(hdr))
    for k, p in rules["platforms"].items():
        cap = p.get("max_chars")
        print("%-12s %-12s %-9s %-8s %s" % (
            k, p.get("kind", "?"), p.get("status", "?"),
            str(cap) if cap else "—",
            ", ".join(p.get("allowed_tiers", [])) or "— ничего —"))
    print("\nЕЖЕДНЕВНЫЕ ПОЛОСЫ")
    for k, l in rules.get("daily_lanes", {}).items():
        mark = "обязательно" if l.get("mandatory") else "по наличию"
        # .get(), а не [] : у полос в platform_rules.json нет ключа targets вообще,
        # а у life_post нет и max_chars -> прямой индекс ронял всю команду --list,
        # и ЖЁСТКИЕ ПРАВИЛА ниже не доезжали до человека никогда (найдено 05.08.2026).
        cap = l.get("max_chars")
        print("  %-17s %-6s %-12s -> %s" % (
            k,
            ("≤%s" % cap) if cap else "—",
            mark,
            ", ".join(l.get("targets", [])) or l.get("note", "—")))
    print("\nЖЁСТКИЕ ПРАВИЛА")
    for r in rules.get("hard_rules", []):
        print("  · " + r)
    return 0


# ------------------------------- регресс-сетка -------------------------------

_BAN_WORDS = ("ЗАПРЕЩЕН", "ЗАПРЕЩЁН", "НЕЛЬЗЯ", "НЕ ПОСТИМ")


def hard_rules_consistency(rules):
    """Витрина для людей не должна противоречить машинному полю status.

    Ловит класс, выстрелявший 19.08.2026: substack.status стоял active с 14.08,
    а строка hard_rules того же файла продолжала гласить «Substack — ЗАПРЕЩЕНО
    до отдельного исследования». Строку печатают platform_gate --list и
    pipeline_dashboard, то есть человек читал запрет там, где робот видел
    разрешение, и selftest оставался зелёным.

    Считаем противоречием ТОЛЬКО запрет площадки ЦЕЛИКОМ: строка начинается
    с имени площадки, и до первого ⛔/«;» стоит слово-запрет. Строки вида
    «Лонгрид в Facebook — ЗАПРЕЩЕНО» — это запрет ТИРА, а не площадки, и
    красным не считаются. Возвращает список текстов расхождений (пустой = чисто).
    """
    plats = rules.get("platforms", rules)
    hard = [str(x) for x in rules.get("hard_rules", [])]
    bad = []
    for key, val in plats.items():
        if not isinstance(val, dict) or "status" not in val:
            continue
        if val.get("status") != "active":
            continue
        for line in hard:
            head = line.strip()
            if not head.lower().startswith(str(key).lower()):
                continue
            # смотрим только до первой оговорки про формат
            seg = re.split(r"[⛔;]", head, 1)[0].upper()
            if any(w in seg for w in _BAN_WORDS):
                bad.append("%s: status=active, но hard_rules запрещает площадку целиком :: %s" % (key, head[:120]))
    return bad


def selftest():
    """Каждый кейс ловит КЛАСС ошибки, который уже стрелял или может выстрелить.
    Доказательство полезности теста = мутант краснеет (см. README рядом)."""
    rules = load_rules()
    cases = [
        # (описание, платформа, тир, знаки, ожидаемый вердикт)
        ("тизер в X — норма",                    "X",          "teaser",  200, "PASS"),
        ("тизер в X длиннее 240 — потолок",      "X",          "teaser",  260, "FAIL"),
        ("лонгрид в чат — запрет Антона 30.07",  "tg-chat",    "longread", 9000, "FAIL"),
        ("средний в чат — тоже запрет",          "tg-chat",    "medium",  900, "FAIL"),
        ("тизер в чат — единственное можно",     "tg-chat",    "teaser",  180, "PASS"),
        ("лонгрид в FB — запрет",                "FB",         "longread", 9000, "FAIL"),
        ("средний в FB — норма",                 "FB",         "medium",  1500, "PASS"),
        ("лонгрид в TG-канал целиком — запрет",  "tg-channel", "longread", 9000, "FAIL"),
        ("средний в TG-канал — норма",           "tg-channel", "medium",  1500, "PASS"),
        ("@ClawRus резолвится в tg-channel",     "@ClawRus",   "medium",  1500, "PASS"),
        ("@CLAWRUS — регистр не важен",          "@CLAWRUS",   "medium",  1500, "PASS"),
        ("reddit заблокирован — что угодно",     "reddit",     "teaser",  100, "FAIL"),
        # 14.08.2026: substack research→active по «+» Антона на формат гибрида
        # (decision-2026-08-10-substack-format-i-voronka §3). Лонгрид и medium — можно.
        ("substack active — лонгрид можно",       "substack",   "longread", 9000, "PASS"),
        ("substack — тизер не его формат",        "substack",   "teaser",    200, "FAIL"),
        ("неизвестная площадка — fail-closed",   "mastodon",   "teaser",  100, "FAIL"),
        # живые данные грязные: публикатор отдаёт «ClawRus (TG)», а не «@ClawRus»
        ("«ClawRus (TG)» — грязное имя канала",  "ClawRus (TG)", "teaser", 300, "PASS"),
        ("«FB / стена» — грязное имя ленты",     "FB / стена", "medium", 1500, "PASS"),
        ("похожая, но чужая — НЕ угадываем",     "clawrus-old", "teaser", 100, "FAIL"),
        ("лонгрид на habr — по назначению",      "habr",       "longread", 9000, "PASS"),
        ("тизер на habr — не туда",              "habr",       "teaser",  200, "FAIL"),
        ("threads потолок 500",                  "threads",    "tg-post", 800, "FAIL"),
        ("discord = чат, лонгрид запрещён",      "discord",    "longread", 9000, "FAIL"),
        ("whatsapp = чат, тизер можно",          "whatsapp",   "teaser",  180, "PASS"),
    ]
    green = red = 0
    for desc, plat, tier, n, expect in cases:
        got, findings = check(plat, tier, n, rules)
        # WARN не считаем провалом там, где ждём PASS: открытый вопрос площадки — не запрет
        ok = (got == expect) or (expect == "PASS" and got == "WARN")
        if ok:
            green += 1
        else:
            red += 1
            why = "; ".join(f[2] for f in findings) or "—"
            print("❌ %-38s ждали %s, получили %s :: %s" % (desc, expect, got, why))
    # витрина vs машинное поле (класс 19.08.2026, см. hard_rules_consistency)
    conflicts = hard_rules_consistency(rules)
    if conflicts:
        red += len(conflicts)
        for c in conflicts:
            print("❌ витрина расходится с status :: %s" % c)
    else:
        green += 1
    print("platform_gate selftest: %d зелёных, %d красных" % (green, red))
    return 0 if red == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Гейт «туда ли несём»: тир × площадка")
    ap.add_argument("--file")
    ap.add_argument("--chars", type=int)
    ap.add_argument("--tier")
    ap.add_argument("--platform", "--channel", dest="platform")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    try:
        rules = load_rules()
    except Exception as e:
        sys.stderr.write("platform_gate: правила не читаются (%s) — публикация запрещена\n" % e)
        return 3

    if a.selftest:
        return selftest()
    if a.list:
        return cmd_list(rules)
    if a.file and not os.path.exists(a.file):
        sys.stderr.write("platform_gate: файла нет: %s\n" % a.file)
        return 3

    # Рабочая записка -- не пост. Отдельный вердикт SKIP, а НЕ PASS: иначе записки
    # раздували бы зелёный счётчик и отчёт врал бы про готовность материала.
    if a.file and is_not_post(a.file):
        if a.json:
            print(json.dumps({"verdict": "SKIP", "platform": None, "tier": None,
                              "chars": body_chars(a.file, platform=a.platform,
                                                  rules=rules), "findings": []},
                             ensure_ascii=False, indent=2))
        else:
            print("SKIP  %s — помечен «НЕ ПОСТ» (рабочая записка эпизода)" % a.file)
        return 0

    # маршрут: явные аргументы главнее, иначе -- шапка самого файла
    tier, platform = a.tier, a.platform
    if a.file and (not tier or not platform):
        h_tier, h_plat = header_route(a.file)
        tier = tier or h_tier
        platform = platform or h_plat
    if not platform or not tier:
        if a.file:
            # Fail-closed: файл без заявленного маршрута -- не «наверное можно»,
            # а отказ. Иначе он молча минует гейт, как минули те 38.
            out = [("FAIL", "P8-no-route",
                    "в файле не заявлены ТИР и ПЛОЩАДКА (шапка «<!-- ТИР: … · "
                    "ПЛОЩАДКА: … -->») и не переданы аргументами — публикация запрещена")]
            if a.json:
                print(json.dumps({"verdict": "FAIL", "platform": platform, "tier": tier,
                                  "chars": body_chars(a.file, platform=platform,
                                                      rules=rules),
                                  "findings": [{"level": l, "rule": r, "msg": m}
                                               for l, r, m in out]},
                                 ensure_ascii=False, indent=2))
            else:
                print("FAIL  %s — %s" % (a.file, out[0][2]))
            return 2
        ap.error("нужны --tier и --platform (или --file с шапкой / --list / --selftest)")

    chars = a.chars
    if chars is None and a.file:
        # ⭐ 27.08.2026: площадку ОБЯЗАТЕЛЬНО передаём дальше. Библиотечный
        # post_chars() умеет не считать футер там, где он уходит первым
        # комментарием (FB), а CLI звал body_chars(a.file) БЕЗ площадки -- и
        # то же самое правило работало из кода и не работало из командной
        # строки. Гейт заворачивал законные FB-medium (замер: 2345 из CLI
        # против 1772 из библиотеки на одном файле). Тот же класс, что
        # 26.08 у footer_in_first_comment: два числа на один вопрос.
        chars = body_chars(a.file, platform=platform, rules=rules)

    verdict, findings = check(platform, tier, chars, rules)
    if a.json:
        print(json.dumps({
            "verdict": verdict, "platform": platform, "tier": tier, "chars": chars,
            "findings": [{"level": l, "rule": r, "msg": m} for l, r, m in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print("%s  %s / тир %s / %s знаков" % (verdict, platform, tier,
                                               chars if chars is not None else "?"))
        for l, r, m in findings:
            print("  [%s] %s — %s" % (l, r, m))
    return {"PASS": 0, "WARN": 1, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
