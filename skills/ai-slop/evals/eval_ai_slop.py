# -*- coding: utf-8 -*-
"""Харнес качества скилла /ai-slop. Меряет 4 оси, две из них деterминированно.

Ось 1 — слоп-остаток: сколько маркеров в тексте ПОСЛЕ переписки.
Ось 2 — сохранность смысла: все ли числа/имена/даты из ДО дожили до ПОСЛЕ.
Ось 4 — не портит ли живого автора: ban-лист по НЕтронутым текстам Антона.
Ось 3 (неотличимость) не автоматизируется — слепой судья, отдельный прогон.

Ось 4 — единственная, что работает без единого токена LLM, поэтому она первая.

Usage:
  python eval_ai_slop.py --axis4                       # ban-лист по живому Антону
  python eval_ai_slop.py --axis4 --limit 200
  python eval_ai_slop.py --axis2 --before a.md --after b.md
"""
import argparse, glob, json, os, re, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slop_detect

PROJECTS = os.path.expanduser("~/.claude/projects")

# что НЕ является напечатанным Антоном текстом.
# ⚠️ Первый прогон 31.07 дал 70% "слопа" — оказалось, в корпус попали вставки
# скиллов, экспорт FB и whisper-пересказы голосовых. Их писал не Антон.
SKIP = ("<command-name>", "<command-message>", "<local-command",
        "<system-reminder>", "caveat:", "<bash-", "тool_result",
        "this session is being continued", "[request interrupted",
        "<user-prompt-submit-hook>", "<task-notification>",
        "base directory for this skill",      # инжект тела скилла
        "personal audio summary",             # пересказ голосовой роботом
        "transcribed by whisper",
        "messenger chats search",             # дамп экспорта FB
        "summary: gpt-")


def _looks_pasted(t: str) -> bool:
    """Вставленный документ, а не набранное в чате сообщение."""
    if "```" in t or len(t) > 3000:
        return True
    lines = t.splitlines()
    heads = sum(1 for l in lines if l.lstrip().startswith("#"))
    bullets = sum(1 for l in lines if re.match(r"\s*[-*|]\s", l))
    return heads >= 2 or bullets >= 5 or t.lstrip().startswith("---")


def _text_of(rec):
    msg = (rec.get("message") or {}).get("content")
    if isinstance(msg, list):
        msg = " ".join(p.get("text", "") for p in msg
                       if isinstance(p, dict) and p.get("type") == "text")
    return msg if isinstance(msg, str) else None


def anton_messages(limit=None, min_chars=60):
    """Сырые сообщения, напечатанные Антоном руками, из транскриптов сессий.

    ⚠️ Роль "user" != слова Антона: он постоянно цитирует мой текст обратно
    («++++» + моя фраза). Поэтому строки, ранее написанные ассистентом в этом
    же файле, вычитаются. Без этого замер меряет МОЙ стиль, а не его.
    """
    out, seen = [], set()
    files = sorted(glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True),
                   key=os.path.getmtime, reverse=True)
    for path in files:
        try:
            recs = []
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        recs.append(json.loads(line))
                    except Exception:
                        continue
            mine = set()
            for rec in recs:
                if rec.get("type") == "assistant":
                    tx = _text_of(rec) or ""
                    for ln in tx.splitlines():
                        ln = ln.strip()
                        if len(ln) > 25:
                            mine.add(ln)
            for rec in recs:
                    if rec.get("type") != "user":
                        continue
                    msg = _text_of(rec)
                    if not isinstance(msg, str):
                        continue
                    # вычесть процитированный мой текст
                    msg = "\n".join(ln for ln in msg.splitlines()
                                    if ln.strip() not in mine)
                    t = msg.strip()
                    low = t.lower()
                    if len(t) < min_chars or any(s in low for s in SKIP):
                        continue
                    if t.startswith("/") or t.startswith("{"):
                        continue
                    if _looks_pasted(t):
                        continue
                    # кириллица должна доминировать: это текст Антона, не вставка лога
                    cyr = sum(1 for c in t if "а" <= c.lower() <= "я" or c in "ёЁ")
                    if cyr < len(t) * 0.35:
                        continue
                    key = t[:120]
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({"text": t, "file": os.path.basename(path)})
                    if limit and len(out) >= limit:
                        return out
        except Exception:
            continue
    return out


def axis4(limit, dump):
    """Ban-лист по НЕтронутым текстам Антона. Каждое срабатывание = ложная тревога."""
    msgs = anton_messages(limit=limit)
    if not msgs:
        print("корпус пуст — нечего мерить"); return 3
    agg, dirty, words_total, viol_total = {}, 0, 0, 0
    samples = {}
    for m in msgs:
        r = slop_detect.analyse(m["text"], short_form=True)
        words_total += r["words"]; viol_total += r["violations"]
        if r["violations"]:
            dirty += 1
        for k, v in r["hits"].items():
            agg[k] = agg.get(k, 0) + len(v)
            samples.setdefault(k, [])
            if len(samples[k]) < 3:
                samples[k].append((v[:2], m["text"][:90].replace("\n", " ")))
    print(f"ОСЬ 4 — ban-лист по живому Антону")
    print(f"корпус: {len(msgs)} сообщений, {words_total} слов (напечатано руками)")
    print(f"помечено как слоп: {dirty}/{len(msgs)} = {dirty/len(msgs)*100:.0f}%")
    print(f"нарушений всего: {viol_total} ({viol_total/max(words_total,1)*1000:.1f} на 1000 слов)")
    print("\nпо категориям (это ЛОЖНЫЕ срабатывания — текст писал человек):")
    for k, n in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"  {k:22} {n:5}")
        for hit, ctx in samples.get(k, []):
            print(f"       {hit} <- \"{ctx}\"")
    if dump:
        with open(dump, "w", encoding="utf-8") as fh:
            json.dump({"n": len(msgs), "dirty": dirty, "words": words_total,
                       "violations": viol_total, "by_cat": agg}, fh, ensure_ascii=False, indent=1)
        print(f"\nсырое -> {dump}")
    return 0


NUM = re.compile(r"\b\d[\d\s.,:/-]*\d\b|\b\d\b")
CAPWORD = re.compile(r"\b[A-ZА-Я][\w-]{2,}\b")


def axis2(before_p, after_p):
    """Сохранность смысла: числа и имена собственные из ДО обязаны быть в ПОСЛЕ."""
    b = open(before_p, encoding="utf-8").read()
    a = open(after_p, encoding="utf-8").read()
    lost_n = [x for x in set(NUM.findall(b)) if x.strip() and x not in a]
    lost_w = [x for x in set(CAPWORD.findall(b)) if x not in a]
    print("ОСЬ 2 — сохранность смысла")
    print(f"  чисел потеряно: {len(lost_n)}  {sorted(lost_n)[:12]}")
    print(f"  имен/сущностей потеряно: {len(lost_w)}  {sorted(lost_w)[:12]}")
    print(f"  сжатие: {len(b)} -> {len(a)} знаков ({(1-len(a)/max(len(b),1))*100:.0f}%)")
    return 1 if lost_n else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis4", action="store_true")
    ap.add_argument("--axis2", action="store_true")
    ap.add_argument("--before"); ap.add_argument("--after")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--dump")
    a = ap.parse_args()
    if a.axis4:
        return axis4(a.limit, a.dump)
    if a.axis2:
        if not (a.before and a.after):
            print("нужны --before и --after"); return 3
        return axis2(a.before, a.after)
    ap.print_help(); return 3


if __name__ == "__main__":
    # CRASH-GUARD (CLAUDE.md §5.5): 1 = нашёл и доложил, 4 = сам упал.
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        sys.exit(4)
