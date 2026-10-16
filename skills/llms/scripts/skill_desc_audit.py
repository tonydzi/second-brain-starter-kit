#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""КОНТРАКТ ОПИСАНИЙ СКИЛЛОВ -- описание платит за себя КАЖДОЙ сессией, значит оно бюджет.

ЗАЧЕМ (решение кофаундера 11.09.2026 по приказу Антона «решать тебе»). Имя и описание
каждого скилла уезжают в контекст любой сессии узла, позвали скилл или нет. Замер 10-11.09
на хабе: 235 скиллов = 170 451 символ описаний ≈ 48 700 токенов НА СЕССИЮ, при ~690 сессиях
в сутки это ~33 млн токенов в день (верхняя граница, без учёта кэша промпта). Медиана
описания 706 символов, у gstack -- 93. Разница не в качестве, а в жанре: у нас в описание
попала ПРОЦЕДУРА и канон, хотя для выбора скилла нужны только назначение, триггеры и
«не путать».

КОНТРАКТ (≤400 символов, в описании остаётся ровно четыре вещи):
  1. НАЗНАЧЕНИЕ -- одна фраза, что скилл делает;
  2. ТРИГГЕРЫ -- дословные слова и слэш-команды, по которым его зовут;
  3. НЕ ПУТАТЬ -- имена соседних скиллов, если они есть (без них сработает чужой);
  4. ⛔ ГРАНИЦА -- только если её нарушение необратимо (деньги/отправка наружу).
Всё остальное -- шаги, канон, замеры, ссылки на память -- живёт В ТЕЛЕ SKILL.md,
которое грузится ТОЛЬКО когда скилл позвали. Это и есть экономия.

⛔ ЧЕГО ДЕЛАТЬ НЕЛЬЗЯ. Не переносить ключевые слова в поле `triggers:` -- замер 11.09:
оно стоит у 5 скиллов на узле, все пять чужие (gstack), и доказательств, что харнес
читает его при подборе скилла, НЕТ. Перенос вслепую = скилл перестанет вызываться сам,
и мы обменяем токены на молчание.

КАК ЧИТАТЬ:
  python ~/.claude/scripts/skill_desc_audit.py               -- сводка и список нарушителей
  python ~/.claude/scripts/skill_desc_audit.py --check <имя> -- один скилл против контракта
  python ~/.claude/scripts/skill_desc_audit.py --json        -- машине

ЭКЗИТ: 0 контракт держат все · 1 ошибка · 3 есть нарушители (для рутины-слона).

ЧТО ЛОМАЕТСЯ И КАК ПОНЯТЬ. «0 нарушителей» на узле, где скиллов сотни, = смотрю не в ту
папку: печатается путь и число найденных SKILL.md, сверь глазами. Чужие паки со стенда
(маркер .packs-bench.json) в счёт НЕ идут: их описания не наши, править их нельзя.

Тест: scripts/_test_skill_desc_audit.py
Канон: CLAUDE.md §6.4 (улучшение меряем в токенах), §5.1 (АК-47), §5.7 (канарейка+урожай);
память skill-shelf-is-a-standing-context-tax.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKILLS = os.path.expanduser("~/.claude/skills")
LIMIT = 400
CHARS_PER_TOKEN = 3.5
PACK_MARKER = ".packs-bench.json"


def frontmatter(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read(20000)
    except OSError:
        return None
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return m.group(1) if m else None


def описание(head):
    m = re.search(r"^description:\s*(.+(?:\r?\n[ \t]+.+)*)$", head or "", re.M)
    return " ".join(m.group(1).split()) if m else ""


def scan(include_foreign=False):
    out = []
    if not os.path.isdir(SKILLS):
        return out
    for d in sorted(os.listdir(SKILLS)):
        p = os.path.join(SKILLS, d, "SKILL.md")
        if not os.path.isfile(p):
            continue
        foreign = os.path.exists(os.path.join(SKILLS, d, PACK_MARKER))
        if foreign and not include_foreign:
            continue
        head = frontmatter(p)
        if head is None:
            continue
        desc = описание(head)
        raw = re.search(r"^description:[ \t]*(.*)$", head, re.M)
        first = (raw.group(1).strip() if raw else "")
        cons = re.search(r"^consumer:[ \t]*(.+)$", head, re.M)
        out.append({
            "skill": d, "chars": len(desc), "over": len(desc) > LIMIT,
            "folded": first[:1] in (">", "|"),
            "quoted": first[:1] == '"',
            "consumer": (cons.group(1).strip().strip('"') if cons else ""),
            "has_triggers_field": bool(re.search(r"^triggers:", head, re.M)),
            "foreign": foreign,
        })
    return out


def cmd_report(as_json=False):
    rows = scan()
    if not rows:
        print("ПУСТО: ни одного SKILL.md в %s -- смотрю не в ту папку?" % SKILLS)
        return 1
    total = sum(r["chars"] for r in rows)
    over = [r for r in rows if r["over"]]
    saving = sum(r["chars"] - LIMIT for r in over)
    res = {
        "skills_dir": SKILLS, "skills": len(rows), "chars": total,
        "tokens_per_session": int(round(total / CHARS_PER_TOKEN)),
        "limit": LIMIT, "over_limit": len(over),
        "saving_chars": saving, "saving_tokens": int(round(saving / CHARS_PER_TOKEN)),
        "worst": [(r["chars"], r["skill"]) for r in sorted(over, key=lambda x: -x["chars"])[:10]],
    }
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 3 if over else 0
    unquoted = [r for r in rows if not r["quoted"]]
    folded = [r for r in rows if r["folded"]]
    print("ОПИСАНИЯ СКИЛЛОВ · %s" % SKILLS)
    print("  своих скиллов %d · описаний %d симв ~= %d ток/сессия"
          % (res["skills"], total, res["tokens_per_session"]))
    print("  контракт %d симв · нарушают %d · экономия при приведении: %d симв ~= %d ток/сессия"
          % (LIMIT, len(over), saving, res["saving_tokens"]))
    print("  ФОРМА (важнее длины): в кавычках %d · БЕЗ кавычек %d, из них свёрнутых блоков %d"
          % (res["skills"] - len(unquoted), len(unquoted), len(folded)))
    print("  ⚠️ незакавыченное описание харнес может не разобрать и показать вместо него")
    print("     ЗАГОЛОВОК из тела -- триггеры до модели не доезжают, и скилл не зовут сам.")
    print("     Замер 11.09: конверсия 5/5 (tt, fa, retro, local-qa, social-daily) вернула")
    print("     описания в выдачу; community-alpha без кавычек снова показался заголовком.")
    for n, name in res["worst"]:
        print("    %5d  %s" % (n, name))
    return 3 if (over or unquoted) else 0


def cmd_check(name):
    p = os.path.join(SKILLS, name, "SKILL.md")
    if not os.path.isfile(p):
        print("нет такого скилла: %s" % p)
        return 1
    head = frontmatter(p)
    desc = описание(head)
    raw = re.search(r"^description:[ \t]*(.*)$", head or "", re.M)
    first = (raw.group(1).strip() if raw else "")
    cons = re.search(r"^consumer:[ \t]*(.+)$", head or "", re.M)
    bad = []
    if len(desc) > LIMIT:
        bad.append("описание %d симв длиннее контракта %d -- режь прозу и процедуру, "
                   "ОСТАВЬ назначение · триггеры · «не путать» · ⛔границу" % (len(desc), LIMIT))
    if first[:1] != '"':
        bad.append("описание НЕ в кавычках одной строкой: харнес может показать вместо него "
                   "заголовок из тела, и триггеры до модели не доедут")
    if not cons:
        bad.append("нет поля consumer: -- §9.3-тер, скилл без НАЗВАННОГО потребителя не "
                   "существует; впиши, КТО его позовёт (человек · узел · рутина · скилл)")
    print("%s: %s" % (name, "✅ контракт держит" if not bad else "❌ нарушений %d" % len(bad)))
    for b in bad:
        print("   - %s" % b)
    return 0 if not bad else 3


HEAD_N = 24  # столько символов описания доезжает до реестра Codex CLI 0.147 (замер 11.09.2026)


def cmd_heads(as_json=False):
    """ГОЛОВА РАЗЛИЧАЕТ СКИЛЛ. Одинаковое начало = Codex их не отличит.

    Экзит: 0 все головы уникальны · 3 есть коллизии (для рутины и для /tt).
    """
    import collections
    rows = scan()
    heads = [(r["skill"], описание_головы(r["skill"])[:HEAD_N]) for r in rows]
    cnt = collections.Counter(h for _, h in heads)
    dup = {h: n for h, n in cnt.items() if n > 1 and h}
    if as_json:
        import json
        print(json.dumps({
            "total": len(heads), "unique": len(cnt), "collisions": sum(dup.values()),
            "groups": {h: [s for s, hh in heads if hh == h] for h in dup},
        }, ensure_ascii=False, indent=2))
        return 3 if dup else 0
    print("ГОЛОВЫ ОПИСАНИЙ (первые %d символов -- ровно то, что видит Codex)" % HEAD_N)
    print("  скиллов: %d · уникальных голов: %d" % (len(heads), len(cnt)))
    if not dup:
        print("  ✅ коллизий нет -- Codex различает все скиллы по голове")
        return 0
    print("  ⛔ КОЛЛИЗИЙ: %d в %d группах -- у Codex совпадает ГОЛОВА (имя и путь он видит, значит это баг ПОДБОРА, не исполнения):" %
          (sum(dup.values()), len(dup)))
    for h, n in sorted(dup.items(), key=lambda x: -x[1]):
        print("     %dx %r -> %s" % (n, h, ", ".join(s for s, hh in heads if hh == h)))
    print("  ЧИНИТЬ: перенести различающее слово в НАЧАЛО описания (полку НЕ сокращать --")
    print("  срез пер-записный, от числа скиллов не зависит).")
    return 3


def описание_головы(name):
    p = os.path.join(SKILLS, name, "SKILL.md")
    head = frontmatter(p)
    if head is None:
        return ""
    m = re.search(r"^description:[ \t]*(.*)$", head, re.M)
    if not m:
        return ""
    tail = m.group(1).strip()
    if tail in (">", ">-", "|", "|-", ">+", "|+"):
        bm = re.search(r"^[ \t]+(\S.*)$", head[m.end():], re.M)
        return bm.group(1).strip() if bm else ""
    if tail[:1] in ('"', "'") and tail[-1:] == tail[:1] and len(tail) > 1:
        tail = tail[1:-1]
    return tail


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", metavar="SKILL")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--heads", action="store_true",
                    help="различает ли ГОЛОВА описания скиллы (бюджет Codex, 24 симв)")
    a = ap.parse_args()
    if a.heads:
        return cmd_heads(a.json)
    return cmd_check(a.check) if a.check else cmd_report(a.json)


if __name__ == "__main__":
    sys.exit(main())
