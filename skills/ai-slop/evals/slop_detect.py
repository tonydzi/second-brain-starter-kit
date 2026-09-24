# -*- coding: utf-8 -*-
"""Детерминированный детектор AI-слопа по ban-листу скилла /ai-slop.

Считает нарушения, НЕ переписывает. Судья, а не переписчик.
Единственный источник правил — <negative_constraints> в ~/.claude/skills/ai-slop/SKILL.md.
Правило меняется там -> меняется здесь, и наоборот. Расхождение = баг.

Usage:
  python slop_detect.py --file <путь>            # один файл
  python slop_detect.py --text "..."             # строка
  python slop_detect.py --file a.md --json       # машинный вывод
"""
import argparse, json, re, sys, unicodedata

# --- 1. эмодзи -------------------------------------------------------------
def _is_emoji(ch: str) -> bool:
    o = ord(ch)
    return (0x1F300 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF
            or 0x1F000 <= o <= 0x1F2FF or o in (0x2B50, 0x2B55, 0xFE0F, 0x203C, 0x2049))

# --- вспомогательное: не трогаем код, URL, точные цитаты -------------------
CODE_BLOCK = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://\S+|\b[\w.-]+\.(?:com|ru|org|io|dev|ai)\b\S*")
PATH = re.compile(r"[A-Za-z]:\\[^\s]+|/(?:Users|home|root|var|etc)/[^\s]+")
# YAML-шапка заметки Obsidian: служебные поля (status, verdict_*, tags) полны
# эмодзи-статусов 🔴✅🟢 и «ё» — читателю они не видны, а детектор без этой
# резки объявлял их нарушениями ТЕЛА статьи. Замер 31.07: 22 нарушения на
# vcru-01, из них 12 из шапки. Судья обязан мерить то, что уйдёт наружу.
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)

def strip_frontmatter(t: str) -> str:
    return FRONTMATTER.sub("", t, count=1)

def strip_protected(t: str) -> str:
    """Убирает зоны, где ё/тире/латиница законны (грабля из hard_invariants)."""
    t = strip_frontmatter(t)
    for pat in (CODE_BLOCK, INLINE_CODE, URL, PATH):
        t = pat.sub(" ", t)
    return t

# --- ban-лист --------------------------------------------------------------
KANTSELYARIT = ["является", "осуществление", "реализация", "данный подход",
                "стоит отметить", "важно понимать", "важно помнить",
                "в современном мире", "играет ключевую роль",
                "позволяет повысить эффективность"]

OPENERS_CLOSERS = ["итак", "давайте разбер", "в этой статье", "подведем итог",
                   "подведём итог", "в заключение", "таким образом"]

EN_SLOP = ["delve", "tapestry", "multifaceted", "paradigm", "[человек]",
           "testament to", "seamless", "robust", "pivotal", "intricate",
           "meticulous", "realm", "showcase", "underscore", "garner", "boast",
           "commendable", "crucial", "foster", "furthermore", "moreover",
           "additionally", "in today's fast-paced world", "it's worth noting"]

INFLATION = ["революционн", "game changer", "game-changer", "это меняет все",
             "это меняет всё", "прорывн", "уникальн"]

BOT_ARTIFACTS = [":contentReference[oaicite", "[cite_start]",
                 "utm_source=chatgpt.com", "​", "‌", "‍", "﻿"]

NEG_PARALLEL = re.compile(
    r"не\s+просто\s+[^,.;]{2,40},\s*а\s|это\s+не\s+[^,.;]{2,40},\s*это\s",
    re.I)

BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.M)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.M)
SENT_SPLIT = re.compile(r"[.!?…]+[\s\n]|\n{2,}")


def analyse(text: str, short_form: bool = True) -> dict:
    """short_form=True -> текст короткий (пост/коммент): заголовки запрещены."""
    body = strip_protected(text)
    low = body.lower()
    hits = {}

    def add(cat, items):
        if items:
            hits[cat] = items

    # «ё» и длинное тире — маркеры РУССКОГО нейрослога (Антон их не пишет).
    # В английском em dash это законная пунктуация: замер 15.08 по 40 живым
    # лонгридам репозитория дал 141 штуку. Судить EN-текст русскими правилами
    # значит ломать нормальный текст под метрику, поэтому смотрим на язык.
    cyr = len(re.findall(r"[а-яёА-ЯЁ]", body))
    lat = len(re.findall(r"[a-zA-Z]", body))
    is_ru = cyr > lat * 0.3

    add("emoji", [c for c in body if _is_emoji(c)])
    if is_ru:
        add("em_dash", re.findall(r"—", body))
        add("yo", re.findall(r"[ёЁ]", body))
    # Границу слова слева ставим ВСЕГДА: без неё «является» находилось внутри
    # «появляется», «данный подход» — внутри «переданный подход» и т.п.
    # Замер 31.07 на habr-02: единственное «нарушение» статьи было именно таким.
    # Справа границы нет намеренно — часть записей это основы («уникальн»,
    # «прорывн», «давайте разбер»), они обязаны ловить любое окончание.
    def _stems(words):
        return [w for w in words if re.search(r"(?<![а-яёa-z])" + re.escape(w), low)]

    add("kantselyarit", _stems(KANTSELYARIT))
    add("opener_closer", _stems(OPENERS_CLOSERS))
    add("en_slop", [w for w in EN_SLOP if re.search(r"\b" + re.escape(w), low)])
    add("inflation", _stems(INFLATION))
    add("bot_artifact", [w for w in BOT_ARTIFACTS if w in text])
    add("neg_parallel", NEG_PARALLEL.findall(body))

    # «не больше одного списка и трёх пунктов» — правило ban-листа для КОРОТКОГО
    # текста. В статье на 700 слов список из четырёх пунктов это нормальная
    # структура, а не признак робота; для лонгрида порог не применяем.
    bullets = BULLET.findall(body)
    if short_form and len(bullets) > 3:
        hits["bullets_over_3"] = [f"{len(bullets)} пунктов"]
    heads = HEADING.findall(body)
    if short_form and heads:
        hits["headings_in_short"] = [f"{len(heads)} заголовков"]

    # ритм: метроном = ровные предложения
    sents = [s.strip() for s in SENT_SPLIT.split(body) if s.strip()]
    lens = [len(s.split()) for s in sents if s.split()]
    words = sum(lens)
    rhythm = {}
    if len(lens) >= 4:
        mean = words / len(lens)
        var = sum((x - mean) ** 2 for x in lens) / len(lens)
        sd = var ** 0.5
        rhythm = {
            "sentences": len(lens),
            "mean_words": round(mean, 1),
            "burstiness_sd": round(sd, 1),
            "share_over_20w": round(sum(1 for x in lens if x > 20) / len(lens), 2),
            "share_under_8w": round(sum(1 for x in lens if x < 8) / len(lens), 2),
        }

    total = sum(len(v) for v in hits.values())
    return {
        "violations": total,
        "per_1000w": round(total / words * 1000, 1) if words else 0.0,
        "words": words,
        "hits": {k: v[:8] for k, v in hits.items()},
        "rhythm": rhythm,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--text")
    ap.add_argument("--long-form", action="store_true",
                    help="лонгрид/дев-лог: заголовки законны")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = open(a.file, encoding="utf-8").read() if a.file else (a.text or sys.stdin.read())
    r = analyse(src, short_form=not a.long_form)
    if a.json:
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"нарушений: {r['violations']}  ({r['per_1000w']} на 1000 слов, слов {r['words']})")
        for k, v in r["hits"].items():
            print(f"  {k}: {len(v)}  {v[:5]}")
        if r["rhythm"]:
            print("  ритм:", r["rhythm"])
    # exit-контракт: 0 чисто, 1 нашёл
    sys.exit(1 if r["violations"] else 0)


if __name__ == "__main__":
    main()
