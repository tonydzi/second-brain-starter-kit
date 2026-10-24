#!/usr/bin/env python3
"""Ввод человека для логин-скриптов: ТОЛЬКО через secret_prompt.sh (окно macOS, проверка формата до сети).
Чтение из терминала (input, getpass) в логин-скриптах запрещено: оператор может не видеть вкладок терминала,
а набранное в терминале сессии агента попадает в её журнал. Нет графической сессии = отказ, без отката.

  ask(имя, regex, пояснение, hidden=True, tries=3) -> строка, которая прошла проверку формата

Значение идёт от secret_prompt.sh по каналу (дескриптор, открытый здесь), а не через stdout, аргументы или окружение.
"""
import os, re, subprocess, sys
from pathlib import Path

PROMPT = Path(__file__).resolve().parent / "secret_prompt.sh"   # onboard-intel-mac.sh кладёт его в стор рядом с этим файлом

def ask(name, regex, text, hidden=True, tries=3):
    if not PROMPT.is_file():
        print(f"нет {PROMPT}: окно ввода показать нечем. Ввод «{name}» остановлен ДО обращения к сети."); sys.exit(5)
    r, w = os.pipe()
    cmd = ["/bin/bash", str(PROMPT)] + ([] if hidden else ["--visible"]) + ["--text", text, "--tries", str(tries), "--fd", str(w), name, regex]
    try:
        p = subprocess.run(cmd, pass_fds=(w,), stdout=subprocess.DEVNULL)   # «ok, длина N» здесь не нужен; значение только в канале
    finally:
        os.close(w)
    with os.fdopen(r) as f:
        lines = f.read().split("\n")
    val = lines[0]
    if len([x for x in lines if x]) > 1 or "\r" in val:   # значение из нескольких строк = негодное (дверь ввода обязана была отказать)
        val = None
    if p.returncode != 0 or val is None or not re.fullmatch(regex, val):   # второй слой: формат проверен и здесь
        print(f"ввод «{name}» не получен (код {p.returncode}): вход остановлен ДО обращения к сети."); sys.exit(p.returncode or 4)
    return val
