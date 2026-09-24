# -*- coding: utf-8 -*-
"""Убрать управляющие байты, попавшие в регексы run_one.py из-за схлопывания \\ в heredoc.
Запускать ТОЛЬКО как файл (python fix_bytes.py) — через heredoc сам патч мангается."""
import sys, ast

BAD = {8: "\\b", 12: "\\f", 13: "\\r", 9: "\\t", 7: "\\a", 11: "\\v"}
p = sys.argv[1] if len(sys.argv) > 1 else "run_one.py"
raw = open(p, "rb").read()
before = len(raw)
fixed = {}
for code, repl in BAD.items():
    if code == 13:
        continue  # \r = штатный CRLF, не трогаем
    b = bytes([code])
    n = raw.count(b)
    if n:
        raw = raw.replace(b, repl.encode())
        fixed[repl] = n
open(p, "wb").write(raw)
chk = open(p, "rb").read()
ast.parse(chk.decode("utf-8"))
left = {repr(bytes([c])): chk.count(bytes([c])) for c in BAD if c != 13 and chk.count(bytes([c]))}
print(f"{p}: {before} -> {len(chk)} bytes; fixed={fixed}; left={left}; syntax OK")
for line in chk.decode("utf-8").splitlines():
    if "Pronouns" in line or "^Gender" in line:
        print("  ", line.strip()[:110])
