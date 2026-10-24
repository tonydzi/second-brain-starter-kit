#!/usr/bin/env python3
"""paragraph_lint.py — детерминированный сторож правила «мысль длиннее трёх предложений пишется абзацами».

НАЗНАЧЕНИЕ: ловить «полотно» — блок текста между пустыми строками, в котором больше
трёх предложений подряд. Приказ Антона 31.08.2026 (голосовая hub:5948, дословно:
«Они просто херачат одним полотном»; «запретил сотрудникам писать любую мысль,
если она длиннее трёх предложений, не разделяя её пустой строкой или абзацами»).

ВХОД: один или несколько путей к файлам (.md/.txt) ЛИБО --stdin (текст на вход).
      --max N   порог предложений в абзаце (по умолчанию 3)
      --json    машиночитаемый вывод
ВЫХОД: строки «файл:строка  N предложений в абзаце» + exit-код.
      exit 0 = чисто, exit 1 = найдено полотно, exit 2 = файл не прочитан.

КТО ДЁРГАЕТ: скилл /taste-check (принцип P33) — обязательный прогон перед выдачей
текста Антону или наружу; вручную — любой актор перед отправкой длинного текста.

РЕЛЬСА: 0 LLM, 0 сети, чистый локальный python — ничей оплаченный бак не жжёт (§6.3).

ГРАНИЦА: правило про ФОРМУ, не про длину. Скрипт НИКОГДА не правит текст, только
считает; дописывать ради структуры запрещено (см. /taste-check P32).
Вне счёта: YAML-шапка, фенсед-код, таблицы, списки, заголовки, цитаты (>).

КАНОН: reglament-abzacy-mysl-dlinnee-treh-predlozheniy (волт) · CLAUDE.md §9.10 ·
память paragraphs-three-sentence-rule.
ТЕСТ: scripts/_test_paragraph_lint.py
updated: 2026-09-01
"""
import argparse
import json
import re
import sys

SENT_END = re.compile(r"[.!?…]+(?=\s+|$)")
# продолжение со строчной буквы = точка внутри предложения (сокращение, «и т.д. и т.п.», «млн. рублей»)
OPENS_SENTENCE = "«\"'—-([<"

SKIP_PREFIX = ("#", ">", "|", "- ", "* ", "+ ", "---", "===", "```", "~~~")
LIST_NUM = re.compile(r"^\s*\d+[.)]\s")
TABLE = re.compile(r"^\s*\|")


def _strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:], i + 1
    return lines, 0


def _is_prose(line):
    s = line.strip()
    if not s:
        return False
    if s.startswith(SKIP_PREFIX):
        return False
    if LIST_NUM.match(line) or TABLE.match(line):
        return False
    if line.startswith("    ") or line.startswith("\t"):  # отступ = код
        return False
    return True


def count_sentences(text):
    """Число предложений в куске прозы.

    Конец предложения = [.!?…] + пробел/конец строки, ПОСЛЕ которого идёт заглавная
    буква, цифра, кавычка или конец текста. Точка перед строчной буквой концом НЕ
    считается — так отсеиваются сокращения («и т.д. и т.п.», «млн. рублей») и
    многоточие внутри фразы («ну… ладно»). Эвристика умышленно занижает счёт:
    ложное обвинение автора дороже пропущенного полотна.
    """
    text = text.strip()
    if not text:
        return 0
    n, last = 0, 0
    for m in SENT_END.finditer(text):
        rest = text[m.end():].lstrip()
        if rest:
            first = rest[0]
            if not (first.isupper() or first.isdigit() or first in OPENS_SENTENCE):
                continue
        n += 1
        last = m.end()
    if text[last:].strip():
        n += 1
    return n


def scan_text(text, max_sentences=3):
    """-> список нарушений [{line, sentences, preview}]"""
    lines = text.splitlines()
    lines, offset = _strip_frontmatter(lines)
    hits, block, start, in_fence = [], [], None, False
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            block, start = [], None
            continue
        if in_fence:
            continue
        if _is_prose(raw):
            if start is None:
                start = idx
            block.append(stripped)
            continue
        if block:
            hits += _judge(block, start, offset, max_sentences)
            block, start = [], None
    if block:
        hits += _judge(block, start, offset, max_sentences)
    return hits


def _judge(block, start, offset, max_sentences):
    joined = " ".join(block)
    n = count_sentences(joined)
    if n > max_sentences:
        return [{"line": start + offset, "sentences": n,
                 "preview": joined[:90] + ("…" if len(joined) > 90 else "")}]
    return []


def main():
    ap = argparse.ArgumentParser(description="полотно из >N предложений в одном абзаце")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--json", dest="as_json", action="store_true")
    a = ap.parse_args()

    results, bad_read = {}, False
    if a.stdin:
        results["<stdin>"] = scan_text(sys.stdin.read(), a.max)
    for f in a.files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                results[f] = scan_text(fh.read(), a.max)
        except OSError as e:
            print("не прочитан %s: %s" % (f, e))
            bad_read = True
    if not results:
        ap.print_help()
        return 2

    total = sum(len(v) for v in results.values())
    if a.as_json:
        print(json.dumps({"max": a.max, "violations": total, "files": results},
                         ensure_ascii=False, indent=2))
    else:
        for f, hits in results.items():
            for h in hits:
                print("%s:%d  %d предложений в абзаце  | %s"
                      % (f, h["line"], h["sentences"], h["preview"]))
        print("[paragraph_lint] %s: полотен %d (порог %d предложений)"
              % ("ЧИСТО" if total == 0 else "НАЙДЕНО", total, a.max))
    if bad_read:
        return 2
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
