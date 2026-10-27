#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
slop_gate.py -- детерминированный АНТИ-СЛОП ГЕЙТ контент-фабрики. 0 токенов, 0 LLM.

ЗАЧЕМ. 29.07 гейт [коллега] получил таймаут 24ч: пост может уйти наружу без единой
человеческой правки. Значит качество обязан держать сам конвейер. Повод -- замеренный
инцидент 29.07 07:45/07:46: два куска лонгрида уехали в [аккаунт] как есть (3150 и
2141 знак, сырые markdown-заголовки, реакций 0). Соседний пост, который Антон писал
руками (12:40, NotebookLM, тело 648 знаков) -- реакция 1, просмотров 29.

ТЗ: 05-Resources/Protocols/spec-anti-slop-content-pipeline.md  (§2.1 лимиты тиров,
§2.3 чёрный список, §2.4 контракт CLI, §3.1 три дыры от внешнего ломателя).

МЕСТО В КОНВЕЙЕРЕ (спека §5):
    робот-писатель -> [ЭТОТ ГЕЙТ] -> робот-рерайтер (макс 2 прохода)
                                  -> approval_clock.py (пинг + 24ч) -> копилка approved/
Гейт стоит ДО копилки: FAIL -> пост в копилку не попадает никогда, даже если 24ч тишины
истекли. Таймаут снимает ЧЕЛОВЕКА, а не КАЧЕСТВО.

КОНТРАКТ (спека §2.4; ровно так его зовёт approval_clock.py:quality_verdict):
    python slop_gate.py --file <draft.md> --tier tg-post
    exit 0 -- чисто · exit 1 -- WARN (список замечаний) · exit 2 -- FAIL (нарушения)
ПОСЛЕДНЯЯ строка stdout = однострочный вердикт: approval_clock печатает именно её.

ТРИ КЛАССА ВЕРДИКТА (спека §3.1):
  FAIL (exit 2)       -- форма сломана. Лечится рерайтом; после 3 FAIL конвейер
                         деградирует материал в teaser (это решает рерайтер, не гейт).
  HARD-BLOCK (exit 2) -- содержание опасно (ложь без источника / чужие ПД / секрет /
                         наезд / тизер без canonical). ДЕГРАДАЦИЕЙ НЕ ЛЕЧИТСЯ, в копилку
                         не попадает никогда. В JSON: hard_block=true.
  WARN (exit 1)       -- НИКОГДА не блокирует. Маршрутизирует в рерайт ровно один раз;
                         оставшиеся WARN пишутся в леджер и пост идёт дальше. Счётчик
                         "три подряд" считает ТОЛЬКО FAIL. Копить WARN в FAIL запрещено.

ОДИН ИСТОЧНИК, НОЛЬ КОПИЙ: лимиты тиров (TIER_LEN/TIER_HARD/TIER_HARD_MAX) и замеренная
анти-ваниль (ANTIVANILLA_PATTERNS/METRICS) импортируются из episode_adapter.py. Здесь
они НЕ дублируются. Нет episode_adapter -> гейт честно падает в exit 2 с названной
причиной, а не тихо работает по своей копии. Наши TG-хендлы (OUR_HANDLES) по той же
причине ДОЧИТЫВАЮТСЯ из 00-System/Channels-Registry.md: вбитая копия отставала от
реестра и 03.09 заблокировала наш собственный канал @ClawEng.

ПРАВКА 2026-09-08 (класс slop-gate-hb2-svoyo-chitaetsya-kak-chuzhoye, 5 датированных
случаев, порог §5.10): правило HB2 судило ФОРМУ подстроки, а не ПРИНАДЛЕЖНОСТЬ, и
блокировало НАШ материал -- @staticmethod в прозе, наш @ClawEng, наш noreply-адрес
GitHub, наш id ревью, наш же JSON-LD [аккаунт]. Лечение -- реестры принадлежности
(OUR_HANDLES из живого реестра, OUR_GH_NUMERIC_IDS, BOT_MAIL_ALLOW, AT_KEYWORDS) плюс
ПРИЧИНА в каждом вердикте. Канарейка _test_slop_hb2_canary.py держит обе половины:
«чужое обязано блокировать» (7 кейсов, доказаны мутантом) и «своё обязано проходить»
(7 замеренных случаев). Замер по корпусу devlog+drafts: 153 -> 57 файлов с находкой,
96 ложных позитивов ушло, НОВЫХ находок 0.
  Assisted-by: Claude Code/claude-opus-5[1m] · Machine: [машина флота] · Account: a
  Operator: robot:auto-[машина флота]-260801-razmorozka-18-pr  (_imports не git-репо на узле:
  подпись живёт здесь + строка в ~/.claude/change_ledger/[машина флота].jsonl, §5.11)

ТЕЛО ПОСТА != ФАЙЛ. Гейт судит только тело: снимает YAML-frontmatter, HTML-комментарии
скаффолда и СТАНДАРТНЫЙ ФУТЕР (CTA/линки/подпись -- одинаковый на всех постах, писателем
не сочиняется). Иначе живой пост Антона от 29.07 12:40 фейлился бы по длине: файл 1484
знака, тело 648. Полная длина всё равно печатается в отчёте.

Регресс-сетка: _test_slop_gate.py (обязательные кейсы -- спека §5).
Паспорт: 00-System\Slop-Gate-Passport.md
"""
import argparse
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
SPEC = "spec-anti-slop-content-pipeline.md"

# --------------------------------------------------------------- единый источник
# episode_adapter.py -- ЕДИНСТВЕННЫЙ источник лимитов тиров и замеренной анти-ванили.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
try:
    import episode_adapter as EA
    TIER_LEN = EA.TIER_LEN
    TIER_HARD = EA.TIER_HARD
    TIER_HARD_MAX = getattr(EA, "TIER_HARD_MAX", EA.TIER_HARD)
    AV_PATTERNS = getattr(EA, "ANTIVANILLA_PATTERNS", [])
    AV_METRICS = getattr(EA, "ANTIVANILLA_METRICS", {})
    CTA_PHONE = getattr(EA, "CTA_PHONE", "")
    _SOURCE_OK = True
    _SOURCE_ERR = ""
except Exception as e:                                   # видимость, а не тихий дефолт
    TIER_LEN, TIER_HARD, TIER_HARD_MAX = {}, set(), set()
    AV_PATTERNS, AV_METRICS, CTA_PHONE = [], {}, ""
    _SOURCE_OK = False
    _SOURCE_ERR = "%s: %s" % (type(e).__name__, e)

SHORT_SHARE_MIN = AV_METRICS.get("short_sentence_share_min", 0.30)
FIRST_PERSON_MIN = AV_METRICS.get("first_person_per_1000_min", 30.0)
FIRST_LINE_MAX = 90          # спека §2.2 п.1
MAX_LISTS = 1                # спека §2.3: более одного списка = FAIL
MAX_BULLETS = 6              # спека §2.3: более 6 буллетов суммарно = FAIL
EMOJI_PARA_MAX = 2           # спека §2.3: эмодзи-маркер в начале >=3 абзацев = FAIL

# Тиры, которые физически едут в TG/FB одним сообщением -> форма поста обязательна.
POST_TIERS = ("teaser", "tg-post", "medium")

# ------------------------------------------------------------------- словари правил
# Спека §2.3, блок FAIL. Ключ -- то, что печатается в отчёте как "названное правило".
SLOP_PHRASES = [
    ("Итак,", r"(?:^|[\n.!?…]\s*)Итак\s*,"),
    ("Давайте разберёмся", r"[Дд]авайте\s+разбер[её]мся"),
    ("В этой статье", r"[Вв]\s+этой\s+стать[еи]"),
    ("В этом посте", r"[Вв]\s+этом\s+посте"),
    ("Стоит отметить", r"[Сс]тоит\s+отметить"),
    ("Важно понимать", r"[Вв]ажно\s+понимать"),
    ("Разберём по порядку", r"[Рр]азбер[её]м\s+по\s+порядку"),
    ("Подведём итог", r"[Пп]одвед[её]м\s+итог"),
]
SLOP_CLICHES = [
    ("В мире, где…", r"[Вв]\s+мире\s*,\s+где\b"),
    ("Не просто X — это Y", r"[Нн]е\s+просто\s+[^.!?\n]{1,60}?\s*[—–-]\s*это\b"),
    ("Это меняет всё", r"[Ээ]то\s+меняет\s+вс[её]\b"),
    ("game changer", r"\bgame[\s-]?changer\b"),
    ("революция в", r"[Рр]еволюци[яию]\s+в\s+\w"),
]

# HARD-BLOCK, спека §3.1(в).
HYPOTHESIS_MARKERS = [
    ("🤔 гипотеза", r"🤔"),
    ("слово «гипотеза» в теле", r"\bгипотез[аыуе]\b"),
    ("«предположительно»", r"\bпредположительно\b"),
    ("«не подтверждено»", r"\bне\s+подтвержден[оа]\b"),
    ("«источник?»", r"источник\s*\?"),
    ("TODO/TBD/FIXME/XXX", r"\b(?:TODO|TBD|FIXME|XXX)\b"),
]
SECRET_PATTERNS = [
    ("OpenAI-подобный ключ sk-…", r"\bsk-[A-Za-z0-9_\-]{16,}"),
    ("GitHub-токен", r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    ("AWS access key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("Slack-токен", r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("приватный ключ", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("пара ключ=значение", r"\b(?:api[_-]?key|secret|token|password|пароль)\s*[:=]\s*\S{8,}"),
]
# Путь к хранилищу секретов -- ОТДЕЛЬНОЕ правило: это не сам секрет, но именно эту
# утечку поймал скан persona-kit 27.07 (раскладка инфраструктуры наружу). Тоже
# HARD-BLOCK, но рерайтер должен видеть, что чинить: убрать путь, а не искать ключ.
SECRET_PATH_PATTERNS = [
    ("путь к хранилищу секретов", r"(?:secrets[\\/][^\s]*|\bcredentials\.md\b)"),
]
# ISO-даты/времена маскируем ДО поиска телефонов: «2026-07-25» = 8 цифр, не телефон.
ISO_DT_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?\b")
# URL маскируем там же и по той же причине: id коммента на GitHub
# (…#issuecomment-[id]) = 10 цифр, и это ссылка на наш же публичный текст,
# а не телефон третьего лица. Замер 2026-08-04: лонгрид GIT-S24 получил HARD-BLOCK
# ровно на этом. Гейт обязан судить ДЕЙСТВИЕ, а не подстроку.
URL_RE = re.compile(r"https?://\S+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
PLACEHOLDER_RE = re.compile(r"\{\{[^}\n]{1,40}\}\}|<[A-Z_]{3,}>|__[A-Z_]{3,}__")
INSULT_WORDS = ("идиот", "идиоты", "идиотов", "дурак", "дураки", "тупой", "тупые",
                "тупица", "мудак", "кретин", "ничтожество", "лжец", "врун",
                "мошенник", "дебил", "ублюдок", "clueless", "incompetent",
                "liar", "fraud", "scammer")
SELF_MARKERS = re.compile(r"\b(?:я|мне|меня|мой|моя|мо[её]|мои|мы|нас|нам|наш\w*|себя|сам)\b",
                          re.IGNORECASE | re.UNICODE)

# Наши собственные публичные контакты -- НЕ чужие ПД (карв-аут Антона).
# Вбитый набор -- ПОЛ, а не потолок: живая истина = 00-System/Channels-Registry.md,
# оттуда набор ДОПОЛНЯЕТСЯ ниже. 03.09 гейт заблокировал наш же @ClawEng ровно
# потому, что канал завели в реестре, а сюда руками не переписали. Копия отстаёт
# от реестра всегда; читать реестр -- дешевле, чем ловить это раз в месяц.
OUR_HANDLES = {"clawrus", "clawrush", "paloaltoairu", "paloaltoai", "tony_stef_",
               "paloaltoailab", "tonydzi", "mycroft", "[рабочий аккаунт]", "[рабочий аккаунт]",
               "[рабочий аккаунт]", "claweng", "openclaw_hub", "openclaw_lab"}
OUR_DOMAINS = ("github.com/tonydzi", "linktr.ee/paloaltoailab",
               "t.me/clawrus", "t.me/paloaltoairu")


def _load_channel_registry():
    """Дополняет OUR_HANDLES живым реестром каналов. Нет файла -> набор остаётся вбитым.

    Направление отказа выбрано намеренно: не прочитали реестр -> allowlist УЖЕ ->
    гейт строже. У fail-closed сторожа публикаций «не знаю» обязано значить «блокирую».
    """
    root = os.environ.get("OBSIDIAN_VAULT", "")
    guesses = ([os.path.join(root, "00-System", "Channels-Registry.md")] if root else [])
    here = os.path.dirname(os.path.abspath(__file__))
    imports = os.path.dirname(here)                       # .../_imports
    guesses.append(os.path.join(os.path.dirname(imports),
                                "<vault>", "00-System", "Channels-Registry.md"))
    for p in guesses:
        try:
            with io.open(p, encoding="utf-8") as f:
                txt = f.read()
        except Exception:
            continue
        found = set(h.lower() for h in re.findall(r"@([A-Za-z][A-Za-z0-9_]{3,31})\b", txt))
        if found:
            OUR_HANDLES.update(found)
            return p
    return ""


CHANNEL_REGISTRY_SRC = _load_channel_registry()

# Наш числовой id на GitHub. В адресе <id>+<логин>@users.noreply.github.com id
# выдаёт сам GitHub и подделать его нельзя -- он и есть удостоверение владельца,
# в отличие от логина, который человек пишет руками.
OUR_GH_NUMERIC_IDS = {"[id]"}
OUR_GH_LOGINS = {"tonydzi", "palo-alto-ai-research-lab"}
# Публичные адреса ботов-соавторов (реестр трейлеров, сверен по GitHub API 31.07).
# Это по построению НЕ персональные данные третьего лица: аккаунт бота публичен и
# стоит в наших же коммитах. Дев-лог про атрибуцию коммитов цитирует их постоянно.
BOT_MAIL_ALLOW = {"noreply@anthropic.com", "[id]+codex@users.noreply.github.com"}
# @-слова языков и разметки. Дев-лог говорит О КОДЕ, и собственная нотация кода --
# не упоминание человека. Замер 03.09: «не одна @staticmethod, одна @classmethod»
# в ПРОЗЕ дало HARD-BLOCK, поэтому список нужен и вне кодовых заборов.
AT_KEYWORDS = {
    "staticmethod", "classmethod", "property", "cached_property", "abstractmethod",
    "dataclass", "override", "overload", "contextmanager", "functools", "wraps",
    "pytest", "fixture", "parametrize", "patch", "mock", "param", "returns", "throws",
    "media", "import", "supports", "keyframes", "font", "charset", "namespace",
    "component", "injectable", "directive", "input", "output", "ngmodule",
    "types", "babel", "vitejs", "eslint", "typescript", "playwright", "testing",
    "angular", "nestjs", "storybook", "sveltejs", "tailwindcss", "reduxjs",
    "author", "since", "deprecated", "example", "return", "params", "notnull",
    "nullable", "suppresswarnings", "functionalinterface", "springbootapplication",
    "autowired", "entity", "table", "column", "getter", "setter", "builder", "slf4j",
    "click", "app", "task", "step", "given", "when", "then", "route", "get", "post",
}
MAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# Слова-маркеры телефона: голый прогон цифр рядом с ними -- всё-таки номер.
PHONE_MARKER_RE = re.compile(
    r"телефон|тел\.|номер|звон|позвон|вотсап|whats\s*app|whatsapp|"
    r"phone|mobile|\bcell\b|\bcall\b|\btel\b|viber|signal", re.IGNORECASE | re.UNICODE)

# Стандартный футер: одинаков на всех постах, писателем не сочиняется -> не судим.
FOOTER_MARKERS = [
    r"^[·•*\-–—\s]{3,}$",                       # разделитель «· · ·» / «---»
    r"^📖\s*Полная версия",
    r"^Все каналы, контакты и запись",
    r"^Напрямую:\s*WhatsApp",
    r"^P\.?S\.?\s*Да, нас можно нанять",
    r"^Придумано Майкрофтом",
    r"^Понравилось, что мы делаем",
    r"^Like what we[''`]re building",
    r"^🤖\s*Это писал синтетический кофаундер",   # честная AI-подпись, спека §4
    r"^🤖\s*Written by the synthetic co-founder",
]
FOOTER_RE = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in FOOTER_MARKERS]

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF←-⇿⌀-⏿①-⓿"
    "■-➿⬀-⯿️‍]", re.UNICODE)
BULLET_RE = re.compile(r"^\s*(?:[-*•▪–—]|\d{1,2}[.)])\s+\S", re.UNICODE)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S")
FIRST_PERSON = {"я", "мне", "меня", "мной", "мой", "моя", "моё", "мое", "мои", "моих",
                "моим", "моими", "моем", "моём", "моему", "моего", "мою", "моей"}
TG_CHANNEL_HINT = re.compile(r"(?:^@|t\.me/|telegram|clawrus|paloaltoairu|tg)", re.IGNORECASE)


# ------------------------------------------------------------------------ разбор
def _strip_bom(s):
    return s[1:] if s and s[0] == "﻿" else s


def parse_front_matter(text):
    """Возвращает (dict_фронтматтера, остаток_текста). Плоский YAML, без зависимостей.

    Шапка может стоять НЕ на первой строке: генераторы фабрики (funnel_feeder,
    episode_adapter) кладут перед ней html-комментарий-паспорт `<!-- ТИР: ... -->`.
    Корень, закрытый 2026-08-06: раньше такой файл не проходил проверку `startswith`,
    шапка не снималась, и её `---` съедал детектор футера -> тело становилось пустым
    и ЛЮБОЙ такой черновик падал в E2-empty-body (замер: 3 из 3 живых черновиков
    фабрики от 05.08). Поэтому ведущие html-комментарии и пустые строки пропускаем.
    """
    fm = {}
    lead = re.match(r"\A(?:\s*<!--.*?-->\s*)+", text, re.S)
    if lead:
        text = text[lead.end():]
    if not text.startswith("---"):
        return fm, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return fm, text
    for ln in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm, "\n".join(lines[end + 1:])


# Тир, зашитый episode_adapter'ом в скаффолд-комментарий, и фолбэк по имени файла.
SCAFFOLD_TIER_RE = re.compile(r"<!--\s*ТИР:\s*([\w-]+)", re.UNICODE)
SCAFFOLD_PLAT_RE = re.compile(r"ПЛОЩАДКА:\s*([^\s·]+)", re.UNICODE)
FILENAME_TIERS = (("teaser", "teaser"), ("tg-post", "tg-post"), ("tgpost", "tg-post"),
                  ("medium", "medium"), ("longread", "longread"),
                  ("devlog", "dev-log"), ("dev-log", "dev-log"))


def tier_from_scaffold(raw, path):
    """Тир НЕ угадываем: сперва скаффолд episode_adapter, потом имя файла."""
    m = SCAFFOLD_TIER_RE.search(raw)
    if m and m.group(1) in TIER_LEN:
        return m.group(1), "скаффолд"
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    for pref, tier in FILENAME_TIERS:
        if stem.startswith(pref):
            return tier, "имя файла"
    return None, None


def platform_from_scaffold(raw):
    m = SCAFFOLD_PLAT_RE.search(raw)
    return m.group(1) if m else None


def extract_body(raw, tier=None):
    """Файл -> тело поста. Возвращает (body, frontmatter, длина_файла, срезанные_куски).

    ⚠️ tier="book": НЕ срезаем «стандартный футер». Эвристика футера написана для
    коротких постов, где после первой служебной строки идёт только CTA. У главы
    книги служебные строки (ссылки, разделители) встречаются в теле, и срез по
    первой из них выбрасывал 85% текста: замер 05.08.2026 -- гейт судил 10 931 знак
    из 70 361 и мерил только начало главы, молча выдавая вердикт за весь день.
    """
    raw = _strip_bom(raw).replace("\r\n", "\n")
    cut = []
    fm, rest = parse_front_matter(raw)
    if fm:
        cut.append("frontmatter(%d полей)" % len(fm))
    before = len(rest)
    rest = re.sub(r"<!--.*?-->", "", rest, flags=re.S)      # HTML-скаффолд episode_adapter
    if len(rest) != before:
        cut.append("html-комментарии")
    lines = rest.split("\n")
    idx = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue
        if any(r.match(s) for r in FOOTER_RE):
            idx = i
            break
    if idx is not None and tier != "book":
        cut.append("стандартный футер (со строки %d)" % (idx + 1))
        lines = lines[:idx]
    elif idx is not None:
        cut.append("футер НЕ срезан (тир book: у главы служебные строки идут в теле)")
    body = "\n".join(lines).strip()
    return body, fm, len(_strip_bom(raw).strip()), cut


def paragraphs(body):
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def sentences(body):
    parts = re.split(r"(?<=[.!?…])\s+|\n+", body)
    return [p.strip() for p in parts if p.strip()]


def words(text):
    return re.findall(r"[А-Яа-яЁёA-Za-z][А-Яа-яЁёA-Za-z-]*", text, re.UNICODE)


def line_of(body, pos):
    return body.count("\n", 0, pos) + 1


def snippet(s, n=48):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n - 1] + "…"


# ------------------------------------------------------------------------ находки
class Finding(object):
    __slots__ = ("level", "rule", "detail")

    def __init__(self, level, rule, detail):
        self.level = level          # "FAIL" | "HARD-BLOCK" | "WARN"
        self.rule = rule
        self.detail = detail

    def as_dict(self):
        return {"level": self.level, "rule": self.rule, "detail": self.detail}


# -------------------------------------------------------------------- сами правила
def is_multi_post_file(body):
    """Файл-обёртка с НЕСКОЛЬКИМИ черновиками (RU-тизер + EN-тизер + служебные секции).

    Гейт судит ОДИН пост. Обёртку судить как пост -- врать: посыплется каскад F1/F4,
    а настоящая причина («тут не один пост») не прозвучит. Замер 29.07: так устроены
    все 26 файлов fb-teasers/.
    """
    heads = [l for l in body.split("\n") if HEADING_RE.match(l)]
    if len(heads) < 2:
        return None
    # заголовок, который АДРЕСУЕТ площадку/язык/исходник = разметка обёртки, не пост
    mark = re.compile(r"@\w+|\b(?:RU|EN|X|FB|Telegram|GitHub|Reddit)\b|Тизер|Исходный пост|"
                      r"Текст поста|черновик", re.UNICODE)
    tagged = [h for h in heads if mark.search(h)]
    if len(tagged) >= 1 or PLACEHOLDER_RE.search(body):
        return ("файл-обёртка: %d заголовков-секций, из них %d адресуют площадку/язык/"
                "исходник -- гейт судит ОДИН пост; разложи по одному посту на файл, "
                "тогда вердикт будет осмысленным" % (len(heads), len(tagged)))
    return None


def check_form(body, tier, out):
    """Спека §2.2/§2.3: форма поста. Применимо к тирам, которые едут одним сообщением."""
    if tier not in POST_TIERS:
        return
    for i, ln in enumerate(body.split("\n"), 1):
        if HEADING_RE.match(ln):
            out.append(Finding("FAIL", "F1-md-heading",
                               "строка %d: «%s» -- markdown-заголовок в теле; Telegram их "
                               "НЕ рендерит (замер: 0 на 105 постов рынка), спека §2.3"
                               % (i, snippet(ln))))
    # списки
    blocks, bullets, run = 0, 0, 0
    for ln in body.split("\n"):
        if BULLET_RE.match(ln):
            bullets += 1
            run += 1
            if run == 1:
                blocks += 1
        else:
            if ln.strip():
                run = 0
    if blocks > MAX_LISTS:
        out.append(Finding("FAIL", "F4-lists",
                           "списков в посте: %d (можно максимум %d) -- буллеты наш главный "
                           "маркер робота: у живых каналов 0-18%% постов, у нас 80%%, спека §1/§2.3"
                           % (blocks, MAX_LISTS)))
    if bullets > MAX_BULLETS:
        out.append(Finding("FAIL", "F4-lists",
                           "буллетов суммарно: %d (потолок %d), спека §2.3" % (bullets, MAX_BULLETS)))
    # эмодзи-маркер в начале абзаца
    marked = [p for p in paragraphs(body) if EMOJI_RE.match(p.lstrip()[:2] or " ")]
    if len(marked) > EMOJI_PARA_MAX:
        out.append(Finding("FAIL", "F5-emoji-para",
                           "абзацев, начатых эмодзи-маркером: %d (потолок %d) -- живые каналы "
                           "ставят 1-3 эмодзи на пост по делу, спека §1/§2.3"
                           % (len(marked), EMOJI_PARA_MAX)))


def check_phrases(body, out):
    """Спека §2.3: запрещённая лексика. Применимо ко ВСЕМ тирам -- слоп он везде слоп."""
    for name, pat in SLOP_PHRASES:
        m = re.search(pat, body, re.UNICODE)
        if m:
            out.append(Finding("FAIL", "F2-slop-phrase",
                               "строка %d: «%s» -- шаблонный оборот из чёрного списка §2.3"
                               % (line_of(body, m.start()), name)))
    for name, pat in SLOP_CLICHES:
        m = re.search(pat, body, re.UNICODE)
        if m:
            out.append(Finding("FAIL", "F3-slop-cliche",
                               "строка %d: «%s» (совпало: «%s») -- клише из чёрного списка §2.3"
                               % (line_of(body, m.start()), name, snippet(m.group(0), 32))))


def check_length(body, tier, out):
    """Спека §2.1: коридор тира. Источник цифр -- episode_adapter.TIER_LEN."""
    n = len(body)
    lo, hi = TIER_LEN.get(tier, (None, None))
    if lo and n < lo:
        lvl = "FAIL" if tier in TIER_HARD else "WARN"
        out.append(Finding(lvl, "F6-length-min",
                           "тело %d знаков < нижней границы тира %s (%d), спека §2.1" % (n, tier, lo)))
    if hi and n > hi:
        lvl = "FAIL" if tier in TIER_HARD_MAX else "WARN"
        out.append(Finding(lvl, "F6-length-max",
                           "тело %d знаков > верхней границы тира %s (%d); медиана живых RU-каналов "
                           "~800, спека §2.1" % (n, tier, hi)))


def check_longread_in_tg(tier, channel, out):
    """Спека §2.1: лонгрид в Telegram целиком НЕ публикуется, идёт tg-post со ссылкой."""
    if tier == "longread" and channel and TG_CHANNEL_HINT.search(channel):
        out.append(Finding("FAIL", "F7-longread-in-tg",
                           "тир longread с каналом «%s»: лонгрид живёт на GitHub/VC/Хабре, в "
                           "Telegram идёт tg-post со ссылкой; резать на серию сообщений запрещено "
                           "(спека §2.1, корень инцидента 29.07 07:45)" % channel))


# --------------------------------------------------------------------------
# ТИР `book` -- главы книги «The Journey» (origin: замер 05.08.2026)
#
# Почему отдельный тир, а не общий прогон `/ai-slop`: тот скилл шагом 0 сам говорит
# «художественный текст -- СТОП», а его запрет №1 («никаких эмодзи, нигде») снёс бы
# каркас книги, который на эмодзи-разделителях и держится. Чистим прозу ВНУТРИ
# секций, каркас не трогаем.
#
# ЧТО МЕРЯЕМ И ПОЧЕМУ ИМЕННО ЭТО. Первый диагноз («мало первого лица, цель 50,1 как
# у Антона») ОТОЗВАН: 50,1 померено на его личных постах, это другой жанр, и гнать
# книгу к этой цифре значит производить поддельную близость. Замер по голосам внутри
# главы Дня 62 показал настоящий дефект:
#   Тони 12,5 · Майк 14,0 первого лица на 1000 слов -- голоса НЕ различаются;
#   «я» 2,4 против «мы» 9,2 -- на каждое «я» приходится 3,8 «мы».
# Беда не в нехватке чувств, а в том, что ДЕЯТЕЛЬ НЕ НАЗВАН: пишем «мы сделали»
# вместо «я сделал» / «Антон решил» / «хаб выкатил». А «мы» как субъект ЗАПРЕЩЕНО
# каноном CLAUDE.md §3.3 с 29.07 -- книга нарушала уже существующее правило.
WE_SUBJECT_RE = re.compile(
    r"\b(мы|нас|нам|нами|наш|наша|наше|наши|нашего|нашей|наших|нашим|нашими)\b", re.I)
I_SUBJECT_RE = re.compile(
    r"\b(я|мне|меня|мной|мною|мой|моя|моё|мои|моего|моей|моих|моим)\b", re.I)
WE_TO_I_MAX = 2.0     # на замере было 3,8x


def check_book(body, tier, out):
    """Проверки глав книги. Только WARN: голос решает автор, не порог в скрипте."""
    if tier != "book":
        return
    wl = words(body)
    if not wl:
        return
    n_we = len(WE_SUBJECT_RE.findall(body))
    n_i = len(I_SUBJECT_RE.findall(body))
    ratio = float(n_we) / max(n_i, 1)
    if n_we and (n_i == 0 or ratio > WE_TO_I_MAX):
        out.append(Finding(
            "WARN", "B1-we-instead-of-actor",
            "«мы» %.1f на 1000 слов против «я» %.1f (в %.1f раза больше, потолок %.1f): "
            "деятель не назван. Канон §3.3 запрещает «мы» как субъект -- переписывай в "
            "«я сделал» / «Антон решил» / «хаб выкатил» / «ноутбук отбил»."
            % (1000.0 * n_we / len(wl), 1000.0 * n_i / len(wl), ratio, WE_TO_I_MAX)))
    # Голоса обязаны различаться СТРОЕМ речи, а не только темой. Блоки узнаём по
    # маркерам дуэта; маркеров нет -- проверку молча пропускаем, а не выдумываем вердикт.
    tony = "\n".join(re.findall(r"(?:🧑[^\n]*\n)((?:(?!🤖|🧑)[^\n]*\n)+)", body))
    mike = "\n".join(re.findall(r"(?:🤖[^\n]*\n)((?:(?!🤖|🧑)[^\n]*\n)+)", body))
    if tony.strip() and mike.strip():
        def avg_len(t):
            ss = sentences(t)
            return (sum(len(words(s)) for s in ss) / float(len(ss))) if ss else 0.0
        a, b = avg_len(tony), avg_len(mike)
        if a and b and max(a, b) / min(a, b) < 1.3:
            out.append(Finding(
                "WARN", "B2-voices-do-not-differ",
                "средняя длина фразы у Тони %.1f слов, у Майка %.1f -- разрыв меньше 1,3x: "
                "дуэт различается темой, но не строем речи. Тони -- короче и в кадре, "
                "Майк -- длиннее и вторым порядком." % (a, b)))


def check_warns(body, tier, lane, out):
    """Спека §2.3, блок WARN. НИКОГДА не блокирует публикацию (спека §3.1б)."""
    lines = [l for l in body.split("\n") if l.strip()]
    if lines:
        # «Первая строка» = крючок. Антон часто пишет абзац одной строкой, но ПЕРВОЕ
        # ПРЕДЛОЖЕНИЕ в нём короткое -- крючок на месте. Поэтому берём меньшее из двух
        # (замер 29.07: по «строке» правило врало на 3 из 4 его живых постов).
        first_line = lines[0].strip()
        first_sent = (sentences(first_line) or [first_line])[0]
        hook = min(len(first_line), len(first_sent))
        if hook > FIRST_LINE_MAX:
            out.append(Finding("WARN", "W1-first-line-long",
                               "крючок %d знаков > %d: у живых каналов первая строка -- один "
                               "факт/заявление, спека §2.2" % (hook, FIRST_LINE_MAX)))
    if body.rstrip().endswith("?") and (lane or "") not in ("daily-ask", "вопрос дня"):
        out.append(Finding("WARN", "W2-ends-with-question",
                           "пост заканчивается вопросом, а тир/полоса не «вопрос дня»: рынок так "
                           "делает 1 раз на 105 постов, спека §1/§2.3"))
    sents = sentences(body)
    if sents:
        short = sum(1 for s in sents if len(words(s)) <= 5)
        share = float(short) / len(sents)
        if share < SHORT_SHARE_MIN:
            out.append(Finding("WARN", "W3-rhythm",
                               "доля коротких предложений (<=5 слов) %.0f%% < %.0f%%: ровный ритм = "
                               "маркер робота, Антон пишет рвано (ANTIVANILLA п.4)"
                               % (100 * share, 100 * SHORT_SHARE_MIN)))
    wl = words(body)
    if wl:
        n1 = sum(1 for w in wl if w.lower() in FIRST_PERSON)
        rate = 1000.0 * n1 / len(wl)
        # Тир book: порог первого лица откалиброван на ЛИЧНЫХ постах Антона (50,1) и к
        # главе книги неприменим -- цель отозвана 05.08.2026, гнать книгу к ней значит
        # производить поддельную близость. Вместо него работает B1 (назван ли деятель).
        if rate < FIRST_PERSON_MIN and tier != "book":
            out.append(Finding("WARN", "W4-first-person",
                               "«я/мне/мой» %.1f на 1000 слов < %.0f: мы пишем про систему, Антон -- "
                               "про себя (ANTIVANILLA, замер 17.9 против 50.1)" % (rate, FIRST_PERSON_MIN)))
    # замеренная анти-ваниль -- источник episode_adapter.ANTIVANILLA_PATTERNS
    for row in AV_PATTERNS:
        rid, pat, level, why = row[0], row[1], row[2], row[3]
        supp = row[4] if len(row) > 4 else None
        lvl = {"warn": "WARN", "info": "INFO"}.get(level, "FAIL")
        for m in re.finditer(pat, body, re.UNICODE):
            if supp and m.lastindex and re.search(supp, m.group(1) or "", re.UNICODE):
                continue                      # приём, который замер за Антоном подтвердил
            out.append(Finding(lvl, rid, "строка %d: «%s» -- %s"
                               % (line_of(body, m.start()), snippet(m.group(0), 40), why)))
            break                             # одного примера правила достаточно


# ------------------------------------------------- обязательные элементы поста (05.08.2026)
# Голосовое Антона 05.08.2026 (hub:5145): во ВСЕХ постах обязаны быть CTA, подпись/авторство,
# упоминание Антона и синтетического кофаундера Майкрофта, ссылки на GitHub, имена/бренды.
# Тексты элементов НЕ сочиняются здесь -- единственный источник `_STYLE-footer.md` (блоки A-E);
# эта проверка лишь констатирует ПРИСУТСТВИЕ. Канон:
# `reglament-obyazatelnye-elementy-kazhdogo-posta`.
#
# ⚠️ Уровень WARN намеренно (§5.7 понарошку-сначала): FAIL мгновенно заморозил бы копилку
# `approved/`, где лежат уже одобренные посты без этих элементов. Критерий флипа в FAIL назван
# ДО старта и лежит в регламенте: 14 дней замера, доля постов без элементов < 10%.
REQUIRED_ELEMENTS = [
    ("CTA", r"(?:wa\.me|whatsapp|calendly\.com|t\.me/\+|join|заявк|стартовый сид|free starter seed)"),
    ("подпись/авторство", r"(?:придумано майкрофтом|invented by mycroft|синтетическ\w+ кофаундер|"
                          r"synthetic co-?founder|это писал синтетический)"),
    ("ссылка на GitHub", r"github\.com/"),
    ("имя-бренд лаборатории", r"palo\s*alto"),
    ("имена кофаундеров", r"(?:майкрофт|mycroft)"),
]
REQ_RE = [(n, re.compile(p, re.IGNORECASE | re.UNICODE)) for n, p in REQUIRED_ELEMENTS]

# teaser физически не несёт футер: лимит 370 знаков и ровно ОДНА ссылка (контракт тиров
# §7.2). Для него обязателен не футер, а путь к нему -- ссылка на полную версию.
TEASER_TIERS = ("teaser",)
# `tg-post` -- это ДЕФОЛТНЫЙ бакет run_gate для файлов без тира, а не площадка. Судить его
# по футеру = сыпать варнинги на каждый неразмеченный черновик, поэтому он вне проверки.
UNTAGGED_TIERS = ("tg-post",)
ELEMENTS_TIERS = ("medium", "longread", "dev-log")


def check_required_elements(raw, tier, out):
    """Судит ПОЛНЫЙ файл (с футером), а не body: элементы живут именно в футере."""
    if tier in UNTAGGED_TIERS:
        return
    if tier in TEASER_TIERS:
        if not re.search(r"https?://|t\.me/|github\.com/", raw or "", re.IGNORECASE):
            out.append(Finding("WARN", "W7-teaser-no-way-out",
                               "тизер без единой ссылки: у тира нет места под футер, поэтому "
                               "обязателен хотя бы путь к полной версии (регламент 05.08)"))
        check_teaser_payload(raw, out)
        return
    check_required_elements_rest(raw, tier, out)


# ⭐ Контракт тизера переписан 06.08.2026 (Антон, голосом): тизер = ЗАВЕРШЁННАЯ ЕДИНИЦА
# ПОЛЬЗЫ, а не крючок. Тест: тот, кто НЕ кликнул, всё равно унёс применимое.
# Замер, из которого выросло правило: 06.08 за 5 часов 16 наших тизеров в @ClawRus ->
# 0 комментариев у нас против 5 у живых людей + 4 прямые жалобы («нейро-говно»,
# «не понимаю цель постинга», «дискуссия умерла», «чат умер?»).
# ⚠️ ЧЕСТНАЯ ГРАНИЦА: пользу машина судить НЕ умеет -- судья человек/рерайтер. Гейт
# ловит только ОТСУТСТВИЕ НОСИТЕЛЯ пользы: цифры, императива или правила-связки.
# Поэтому WARN, а не FAIL: ложный FAIL тут дороже пропуска (правило §3.1 «WARN не копится»).
PAYLOAD_CARRIERS = (
    ("цифра-замер", r"\d"),
    ("императив/рецепт", r"(?:^|[\s\n])(?:проверь|запиши|сделай|возьми|начни|перестань|"
                        r"не\s+делай|не\s+жди|ставь|меряй|считай|открой|запусти)"),
    ("правило-связка", r"(?:если\b.{0,60}\bто\b|порог|правило|значит\b|—\s*это\b|"
                       r"-\s*это\b|вместо\b|достаточно\b)"),
)
PAYLOAD_RE = [(n, re.compile(p, re.IGNORECASE | re.UNICODE | re.MULTILINE))
              for n, p in PAYLOAD_CARRIERS]


def check_teaser_payload(raw, out):
    """W8: тизер без единого носителя пользы = голый крючок (контракт 06.08)."""
    if not any(r.search(raw or "") for _, r in PAYLOAD_RE):
        out.append(Finding("WARN", "W8-teaser-no-payload",
                           "в тизере не видно ни одного носителя пользы (цифры-замера, "
                           "императива/рецепта, правила-связки): похоже на голый крючок. "
                           "Контракт 06.08: некликнувший обязан унести применимое"))


def check_required_elements_rest(raw, tier, out):
    """Хвост check_required_elements: обязательные элементы у medium/longread/dev-log."""
    if tier not in ELEMENTS_TIERS:
        return
    miss = [n for n, r in REQ_RE if not r.search(raw or "")]
    if miss:
        out.append(Finding("WARN", "W6-missing-required",
                           "нет обязательных элементов поста: %s -- тексты берутся из "
                           "_STYLE-footer.md (блоки A-E), не сочиняются заново"
                           % ", ".join(miss)))


# --------------------------------------------------------------------- HARD-BLOCK
def check_hard_block(body, fm, degraded, out, tier=None):
    """Спека §3.1(в): содержание, которое деградацией в тизер НЕ лечится.

    ⚠️ КАРВ-АУТ ДЛЯ ТИРА `book` (замер 05.08.2026). Для поста непроверенное
    утверждение -- стоп: пост УТВЕРЖДАЕТ. Книга же ДОКУМЕНТИРУЕТ, в том числе
    собственную неуверенность, и канон прямо требует помечать недоказанное словом
    «гипотеза» (правило prichina-kak-claim). То есть в главе помеченная гипотеза --
    добродетель, а не нарушение, и блокировать её значит бить по своему же правилу
    (класс gate-must-not-cry-wolf-on-our-own-cta). Поэтому в тире book помеченная
    гипотеза понижается до INFO; НЕпомеченные маркеры (TODO/FIXME/«источник?»)
    остаются HARD-BLOCK -- это следы недоделанного текста, а не честная оговорка.
    """
    marked_ok = ("🤔 гипотеза", "слово «гипотеза» в теле", "«предположительно»",
                 "«не подтверждено»")
    for name, pat in HYPOTHESIS_MARKERS:
        m = re.search(pat, body, re.UNICODE)
        if m:
            if tier == "book" and name in marked_ok:
                out.append(Finding("INFO", "HB1-hypothesis-marked-ok",
                                   "строка %d: %s -- в книге помеченная гипотеза разрешена "
                                   "(канон требует помечать недоказанное)"
                                   % (line_of(body, m.start()), name)))
                continue
            out.append(Finding("HARD-BLOCK", "HB1-unproven-claim",
                               "строка %d: %s -- либо ✅ доказано, либо 🤔 гипотеза, и тогда в пост "
                               "не идёт (спека §3.1в)" % (line_of(body, m.start()), name)))
            break
    # цифра без источника: судим ТОЛЬКО когда файл сам заявляет поле facts_from
    if "facts_from" in fm:
        src = (fm.get("facts_from") or "").strip()
        empty = src in ("", "[]", "-", "null", "none")
        if empty and re.search(r"\d{2,}|\d+\s*%|\bx\d+\b", body):
            out.append(Finding("HARD-BLOCK", "HB1b-number-without-source",
                               "в теле есть числовое утверждение, а facts_from в шапке пуст -- "
                               "цифра без источника в леджере (спека §3.1в)"))
    for name, pat in SECRET_PATTERNS:
        m = re.search(pat, body, re.UNICODE)
        if m:
            out.append(Finding("HARD-BLOCK", "HB3-secret",
                               "строка %d: похоже на секрет (%s) -- секрет наружу не идёт никогда"
                               % (line_of(body, m.start()), name)))
            break
    for name, pat in SECRET_PATH_PATTERNS:
        m = re.search(pat, body, re.UNICODE)
        if m:
            out.append(Finding("HARD-BLOCK", "HB3b-secrets-path",
                               "строка %d: %s («%s») -- наружу уходит раскладка инфраструктуры; "
                               "чинится удалением пути, не поиском ключа"
                               % (line_of(body, m.start()), name, snippet(m.group(0), 32))))
            break
    _check_pii(body, out)
    _check_insult(body, out)
    _check_raise_solicitation(body, out)
    if degraded and not re.search(r"https?://\S+", body):
        out.append(Finding("HARD-BLOCK", "HB5-no-canonical",
                           "деградация в тизер без рабочей canonical-ссылки = пустой выстрел; "
                           "нет ссылки -> не деградируем (спека §3.1в)"))


def _digits(s):
    return re.sub(r"\D", "", s)


def _fenced_lines(text):
    """Флаг на строку: лежит ли она ВНУТРИ кодового забора (сами ``` -- нет).

    Забор НЕ маскируется целиком: это была бы дыра размером с забор -- чужой контакт
    в куске конфига (`reviewer: [аккаунт]`) прошёл бы насквозь. Замер: канарейка A5
    покраснела ровно на этом при первой попытке лечения. Забор даёт ровно одно
    послабление -- позицию ДЕКОРАТОРА (собака сразу после переноса строки).
    """
    flags, in_fence = [], False
    for line in text.split("\n"):
        if re.match(r"^[ \t]*(?:```|~~~)", line):
            in_fence = not in_fence
            flags.append(False)
        else:
            flags.append(in_fence)
    return flags


def _at_decorator_position(text, pos, fenced):
    """Собака стоит в позиции декоратора внутри забора: начало строки, слева пробелы."""
    ln = text.count("\n", 0, pos)
    if ln >= len(fenced) or not fenced[ln]:
        return False
    return text[text.rfind("\n", 0, pos) + 1:pos].strip() == ""


def _mail_is_ours(addr):
    """Причина, по которой адрес НЕ чужой, либо пустая строка.

    Судим ПРИНАДЛЕЖНОСТЬ, а не форму. У GitHub-адреса вида <id>+<логин>[аккаунт].
    noreply.github.com числовой id подделать нельзя -- он и есть удостоверение.
    """
    a = addr.lower()
    if a in BOT_MAIL_ALLOW:
        return "публичный адрес бота-соавтора из реестра трейлеров"
    m = re.match(r"^(\d+)\+([a-z0-9._-]+)\x40users\.noreply\.github\.com$", a)
    if m and m.group(1) in OUR_GH_NUMERIC_IDS:
        return "наш служебный адрес GitHub (числовой id %s -- наш)" % m.group(1)
    m2 = re.match(r"^([a-z0-9._-]+)\x40users\.noreply\.github\.com$", a)
    if m2 and m2.group(1) in OUR_GH_LOGINS:
        return "наш служебный адрес GitHub (логин %s -- наш)" % m2.group(1)
    return ""


def _check_pii(body, out):
    """HARD-BLOCK на ПД ТРЕТЬИХ ЛИЦ: телефон, почта, хендл. Наше -- не ПД третьих лиц.

    Класс slop-gate-hb2-svoyo-chitaetsya-kak-chuzhoye (порог §5.10 взят 03.09.2026,
    5 датированных случаев): правило блокировало НАШ материал -- `@staticmethod` в
    прозе, наш канал `@ClawEng`, наш адрес `<id>+tonydzi@users.noreply.github.com`,
    наш же id ревью `[id]`. Корень один на все случаи: судили ФОРМУ подстроки
    (собака + слово, собака в адресе, десять цифр), а не ПРИНАДЛЕЖНОСТЬ. Ниже каждое
    послабление опирается на реестр, а не на догадку, и каждый вердикт называет ПРИЧИНУ.
    Канарейка: _test_slop_hb2_canary.py (половина A -- чужое обязано блокировать).
    """
    our_phone = _digits(CTA_PHONE)
    # даты/времена и URL -> пробелы той же длины, чтобы номера строк не поехали
    masked = ISO_DT_RE.sub(lambda m: " " * len(m.group(0)), body)
    masked = URL_RE.sub(lambda m: " " * len(m.group(0)), masked)
    for m in PHONE_RE.finditer(masked):
        raw = m.group(0)
        d = _digits(raw)
        if not (10 <= len(d) <= 15):                    # телефон, а не дата/версия/счёт
            continue
        if our_phone and (d.endswith(our_phone[-10:]) or our_phone.endswith(d[-10:])):
            continue                                    # наш публичный CTA -- карв-аут
        # ФОРМА НОМЕРА, а не длина: живой номер набирают с плюсом или с разделителями
        # (+7 916 123 45 67, 415-555-0132). Голый прогон цифр -- это id: комментария,
        # ревью, сообщения. Замер 07.09: id ревью [id] заблокировал 4 дев-лога
        # из 5. Голый прогон всё равно судится, если рядом слово-маркер телефона.
        # ОБРЫВОК БОЛЬШЕГО ТОКЕНА: телефон не пишут вплотную после буквы или дефиса.
        # Так выглядят uuid (…-127f-4147-9327-711623) и имена бэкапов (bak-pathfix-…).
        if m.start() and (masked[m.start() - 1] == "-" or masked[m.start() - 1].isalnum()):
            continue
        # ДАТА В ЦИФРАХ: группа ровно из 8 цифр вида ГГГГММДД -- это метка времени
        # (bak-pathfix-[id]-1610), а не номер: в номерах группы по 2-4 цифры.
        if any(re.match(r"^20\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])$", g)
               for g in re.findall(r"\d{8}", raw)):
            continue
        shaped = raw.lstrip().startswith("+") or re.search(r"[\s\-()]", raw.strip())
        # маркер обязан стоять ВПЛОТНУЮ (30 знаков слева), а не где-то в строке:
        # «это порядковый номер, а не чей-то телефон» -- предложение ПРО телефоны,
        # и по слову в строке голый id снова получал бы HARD-BLOCK.
        near = masked[max(0, m.start() - 30):m.start()]
        if not shaped and not PHONE_MARKER_RE.search(near):
            continue
        out.append(Finding("HARD-BLOCK", "HB2-third-party-pii",
                           "строка %d: телефон третьего лица «%s» -- причина: номер набран "
                           "в телефонной форме и не совпадает с нашим публичным CTA"
                           % (line_of(body, m.start()), snippet(raw, 24))))
        break
    mail_spans = []
    for m in MAIL_RE.finditer(body):
        mail_spans.append(m.span())
        why_ours = _mail_is_ours(m.group(0))
        if why_ours:
            continue
        out.append(Finding("HARD-BLOCK", "HB2-third-party-pii",
                           "строка %d: почта третьего лица «%s» -- причина: адреса нет "
                           "ни в реестре наших GitHub-идентичностей, ни среди публичных "
                           "адресов ботов-соавторов"
                           % (line_of(body, m.start()), snippet(m.group(0), 32))))
        break
    # хендлы ищем по тексту БЕЗ почты: «собака» адреса уже осуждена правилом почты
    hbody = body
    for a, b in mail_spans:
        hbody = hbody[:a] + " " * (b - a) + hbody[b:]
    fenced = _fenced_lines(hbody)
    for m in re.finditer(r"(?<![\w./])@([A-Za-z][A-Za-z0-9_]{3,31})\b", hbody):
        h = m.group(1).lower()
        if h in OUR_HANDLES:
            continue
        if h in AT_KEYWORDS:            # @staticmethod, @property, @media -- нотация кода
            continue
        if _at_decorator_position(hbody, m.start(), fenced):
            continue                    # собака в позиции декоратора внутри забора
        # КЛЮЧ JSON, а не человек: {"[аккаунт]":"https://schema.org","[аккаунт]":"Article"}.
        # Эту разметку schema.org кладёт в КАЖДЫЙ наш дев-лог сам конвейер -- замер
        # 08.09: 62 файла корпуса из 119 висели на собственном же JSON-LD. Хендл в
        # ЗНАЧЕНИИ ("reviewer": "[аккаунт]") правилом не затронут и по-прежнему судится.
        if (m.start() and hbody[m.start() - 1] in "\"'"
                and re.match(r"^[\"']\s*:", hbody[m.end():m.end() + 4])):
            continue
        out.append(Finding("HARD-BLOCK", "HB2-third-party-pii",
                           "строка %d: чужой хендл «@%s» -- причина: не в реестре наших "
                           "каналов (00-System/Channels-Registry.md), не @-слово языка "
                           "и стоит вне блока кода"
                           % (line_of(body, m.start()), m.group(1))))
        break


def _check_insult(body, out):
    for s in sentences(body):
        low = s.lower()
        hit = next((w for w in INSULT_WORDS if re.search(r"\b%s\b" % re.escape(w), low, re.UNICODE)), None)
        if not hit:
            continue
        if SELF_MARKERS.search(s):
            continue          # «я идиот», «мы облажались» -- это ЕГО лексикон, не наезд
        toks = s.split()
        named = any(re.match(r"^[А-ЯЁA-Z][\wА-Яа-яЁё-]{2,}", t) for t in toks[1:]) or "@" in s
        if named:
            out.append(Finding("HARD-BLOCK", "HB4-insult",
                               "предложение «%s» -- «%s» рядом с конкретным именем/компанией "
                               "(спека §3.1в)" % (snippet(s, 60), hit)))
            break


# HB6 (anton 06.10, «да, согласен» на замок): одна публичная фраза про ОТКРЫТЫЙ раунд
# = general solicitation по Rule 502(c) и сжигает 506(b) для всего оффера (CDI про сайт
# с оффером). Роботы постят ежедневно и про раунд не знают -> замок в гейте, а не в памяти.
# Ловим только оффер в настоящем/будущем от первого лица; рассуждение о фандрайзе как
# теме («YC учит...», «как рейзят фонды») проходит. Память: customer-to-angel-reg-d.
RAISE_SOLICIT_PATTERNS = (
    ("we-are-raising", r"\b(?:we(?:'re|’re| are)|i(?:'m|’m| am))\s+(?:now\s+|currently\s+|actively\s+)?(?:raising|fundraising)\b"),
    ("round-is-open", r"\b(?:pre-?seed|seed|angel|series\s+[a-c]|our)\s+round\s+(?:is\s+)?(?:now\s+)?(?:open|live)\b"),
    ("opening-round", r"\bopen(?:ing|ed)?\s+(?:our|a|the)\s+(?:pre-?seed\s+|seed\s+|angel\s+)?round\b"),
    ("invest-in-us", r"\binvest\s+in\s+us\b"),
    ("looking-for-investors", r"\b(?:looking|searching)\s+for\s+(?:an?\s+)?(?:angel\s+|lead\s+)?investors?\b"),
    ("мы-рейзим", r"\bмы\s+(?:сейчас\s+)?(?:поднимаем|привлекаем|рейзим|собираем)\s+(?:\S+\s+)?(?:раунд|инвестиц|ангел|pre-?seed|seed|сид|деньги\s+(?:у|от)\s+(?:ангел|инвестор))"),
    ("открыт-раунд", r"\bоткры(?:т|ли|ваем|л)\s+(?:наш\s+|свой\s+)?(?:пре-?сид\S*\s+|сид\S*\s+|ангельск\S*\s+|посевн\S*\s+)?раунд"),
    ("инвестируйте-в-нас", r"\bинвестируйте\s+в\s+нас\b"),
    ("ищем-инвесторов", r"\bищем\s+(?:\S+\s+)?(?:инвестор|ангел)"),
)

# Явное отрицание прямо перед оффером («не ищем инвесторов», «don't invest in us») -- это
# НЕ оффер; ложный HARD-BLOCK на нём учит людей обходить гейт (находка панели 06.10).
RAISE_NEGATION_TAIL = re.compile(r"(?:\bне|n't|n’t|\bnot|\bnever|\bno)\s+(?:\S+\s+)?$", re.UNICODE)


def _check_raise_solicitation(body, out):
    low = body.lower()
    for name, pat in RAISE_SOLICIT_PATTERNS:
        for m in re.finditer(pat, low, re.UNICODE):
            if RAISE_NEGATION_TAIL.search(low[max(0, m.start() - 24):m.start()]):
                continue
            out.append(Finding("HARD-BLOCK", "HB6-raise-solicitation",
                               "строка %d: «%s» (%s) -- публичный оффер раунда = general "
                               "solicitation, сжигает 506(b) для всего раунда; инвест-разговор "
                               "только лично и отдельным документом"
                               % (line_of(body, m.start()), snippet(body[m.start():m.end()], 40), name)))
            return


# ------------------------------------------------------------------------- runner
def run_gate(path, tier=None, lane=None, channel=None, degraded=False):
    """Возвращает dict-отчёт. Единственная точка правды для CLI и для тестов."""
    # n_fail/n_warn/n_info заполнены СРАЗУ: у ранних выходов (нет файла, нет источника)
    # тоже печатается строка вердикта, и она не имеет права упасть на KeyError.
    rep = {"file": path, "ok": False, "exit": 2, "verdict": "FAIL",
           "tier": tier, "tier_source": "--tier" if tier else "н/д", "lane": lane,
           "channel": channel, "findings": [], "hard_block": False,
           "n_fail": 1, "n_warn": 0, "n_info": 0,
           "body_chars": 0, "file_chars": 0, "stripped": []}
    if not _SOURCE_OK:
        rep["findings"] = [Finding("FAIL", "E0-no-source",
                                   "не импортируется episode_adapter.py (единственный источник "
                                   "лимитов и ANTIVANILLA): %s" % _SOURCE_ERR).as_dict()]
        return rep
    if not os.path.isfile(path):
        rep["findings"] = [Finding("FAIL", "E1-no-file", "файла нет: %s" % path).as_dict()]
        return rep
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    body, fm, full_len, cut = extract_body(raw, tier=tier)
    scaf_tier, scaf_src = tier_from_scaffold(raw, path)
    tier_src = "--tier"
    if not tier:
        if fm.get("tier"):
            tier, tier_src = fm["tier"], "frontmatter"
        elif scaf_tier:
            tier, tier_src = scaf_tier, scaf_src
        else:
            tier, tier_src = "tg-post", "дефолт"
    lane = lane or fm.get("lane")
    channel = channel or fm.get("channel") or fm.get("platform") or platform_from_scaffold(raw)
    rep.update({"tier": tier, "tier_source": tier_src, "lane": lane, "channel": channel,
                "body_chars": len(body), "file_chars": full_len, "stripped": cut})

    found = []
    if not body:
        found.append(Finding("FAIL", "E2-empty-body",
                             "после снятия шапки/комментариев/футера тела не осталось"))
    else:
        if tier not in TIER_LEN and tier != "book":
            found.append(Finding("WARN", "W0-unknown-tier",
                                 "тир «%s» не описан в episode_adapter.TIER_LEN -- длина не "
                                 "проверена, остальные правила проверены" % tier))
        # обёртка ловится ТОЛЬКО у тиров, которые едут одним сообщением: у longread и
        # dev-log много заголовков -- это норма жанра, а не признак обёртки.
        multi = is_multi_post_file(body) if tier in POST_TIERS else None
        if multi:
            # НЕ сыплем каскадом формы: называем настоящую причину одной строкой.
            found.append(Finding("FAIL", "E3-multi-post-file", multi))
            check_hard_block(body, fm, degraded, found, tier=tier)
        else:
            ph = PLACEHOLDER_RE.search(body)
            if ph:
                found.append(Finding("FAIL", "F8-unresolved-placeholder",
                                     "строка %d: незаполненный плейсхолдер «%s» -- пост так "
                                     "наружу не идёт" % (line_of(body, ph.start()),
                                                         snippet(ph.group(0), 24))))
            check_form(body, tier, found)
            check_phrases(body, found)
            check_length(body, tier, found)
            check_longread_in_tg(tier, channel, found)
            check_hard_block(body, fm, degraded, found, tier=tier)
            check_warns(body, tier, lane, found)
            check_book(body, tier, found)
            check_required_elements(raw, tier, found)   # судит СЫРОЙ файл: элементы в футере

    rep["findings"] = [f.as_dict() for f in found]
    rep["hard_block"] = any(f.level == "HARD-BLOCK" for f in found)
    n_fail = sum(1 for f in found if f.level in ("FAIL", "HARD-BLOCK"))
    n_warn = sum(1 for f in found if f.level == "WARN")
    rep["n_fail"], rep["n_warn"] = n_fail, n_warn
    rep["n_info"] = sum(1 for f in found if f.level == "INFO")   # считаем, не поднимаем
    if n_fail:
        rep["exit"], rep["verdict"], rep["ok"] = 2, "HARD-BLOCK" if rep["hard_block"] else "FAIL", False
    elif n_warn:
        rep["exit"], rep["verdict"], rep["ok"] = 1, "WARN", True   # WARN не блокирует
    else:
        rep["exit"], rep["verdict"], rep["ok"] = 0, "OK", True
    return rep


def summary_line(rep):
    """ПОСЛЕДНЯЯ строка stdout -- approval_clock.py печатает именно её."""
    rules = []
    for f in rep["findings"]:
        if f["level"] in ("FAIL", "HARD-BLOCK") and f["rule"] not in rules:
            rules.append(f["rule"])
    if rep["verdict"] == "OK":
        return "SLOP-GATE %s OK: чисто (тело %d знаков)" % (rep["tier"], rep["body_chars"])
    if rep["verdict"] == "WARN":
        w = [f["rule"] for f in rep["findings"] if f["level"] == "WARN"]
        return ("SLOP-GATE %s WARN (не блокирует, спека §3.1б): %s"
                % (rep["tier"], ", ".join(w)))
    return ("SLOP-GATE %s %s: fail=%d warn=%d · правила: %s"
            % (rep["tier"], rep["verdict"], rep["n_fail"], rep["n_warn"], ", ".join(rules)))


def print_report(rep, quiet=False):
    if not quiet:
        print("== slop_gate · %s ==" % os.path.basename(rep["file"]))
        print("   тир: %s (из: %s) · тело: %d знаков · файл целиком: %d · срезано: %s"
              % (rep["tier"], rep.get("tier_source", "?"), rep["body_chars"],
                 rep["file_chars"], ", ".join(rep["stripped"]) or "ничего"))
        order = {"HARD-BLOCK": 0, "FAIL": 1, "WARN": 2, "INFO": 3}
        for f in sorted(rep["findings"], key=lambda x: order.get(x["level"], 9)):
            print("   %-10s %-26s %s" % (f["level"], f["rule"], f["detail"]))
        if rep["hard_block"]:
            print("   ⛔ HARD-BLOCK: деградацией в тизер НЕ лечится, в копилку не попадает "
                  "никогда -> drafts/ + строка в 03 (спека §3.1в)")
    print(summary_line(rep))


def main():
    ap = argparse.ArgumentParser(
        description="Анти-слоп гейт контент-фабрики (0 токенов). Спека: %s" % SPEC)
    ap.add_argument("--file", required=True, help="черновик поста (.md/.txt)")
    ap.add_argument("--tier", default=None,
                    help="teaser | tg-post | medium | longread | dev-log "
                         "(по умолчанию из frontmatter, иначе tg-post)")
    ap.add_argument("--lane", default=None, help="полоса, напр. daily-ask (вопрос дня)")
    ap.add_argument("--channel", default=None, help="куда едет пост (для правила F7)")
    ap.add_argument("--degraded", action="store_true",
                    help="это деградация в тизер (спека §3.1а/в): требуем canonical-ссылку")
    ap.add_argument("--json", action="store_true", help="машинный вывод вместо отчёта")
    ap.add_argument("--quiet", action="store_true", help="только строка вердикта")
    a = ap.parse_args()

    rep = run_gate(a.file, a.tier, a.lane, a.channel, a.degraded)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_report(rep, a.quiet)
    return rep["exit"]


if __name__ == "__main__":
    sys.exit(main())
