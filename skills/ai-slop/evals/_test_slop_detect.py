# -*- coding: utf-8 -*-
"""Регресс-сетка детектора слопа. Каждый кейс = оплаченная граблина.

Запуск: python3 _test_slop_detect.py   (exit 0 чисто, 1 есть падения)
"""
import os, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slop_detect as sd

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        FAILS.append(name)


def cat(text, **kw):
    return set(sd.analyse(text, **kw)["hits"])


print("регресс slop_detect")

# 1. Граблина 31.07: «является» находилось внутри «появляется».
#    Ловилось на живой статье habr-02 и было её единственным «нарушением».
check("подстрока внутри слова не считается канцеляритом",
      "kantselyarit" not in cat("Кнопка появляется. Задача проявляется в логе."))

# 2. Обратная сторона той же правки: настоящий канцелярит обязан ловиться.
check("настоящий канцелярит ловится",
      "kantselyarit" in cat("Данный подход является решением."))

# 3. Основы без правого якоря обязаны ловить любое окончание.
check("основа ловит окончание", "inflation" in cat("Это революционное решение."))

# 4. Граблина 31.07: YAML-шапка заметки Obsidian полна служебных 🔴✅🟢 и «ё».
#    Читателю они не видны, а детектор объявлял их нарушениями тела.
fm = "---\nstatus: 🔴 блок\nverdict: \"всё ещё\"\n---\n\nЧистый текст статьи.\n"
check("frontmatter не считается", sd.analyse(fm)["violations"] == 0,
      str(sd.analyse(fm)["hits"]))

# 5. Тело после шапки продолжает проверяться.
check("тело после шапки проверяется",
      "emoji" in cat("---\ntitle: x\n---\n\nТекст со смайлом 🔥 внутри."))

# 6. Порог «не больше трёх пунктов» адресован короткому посту, не лонгриду.
lst = "Текст.\n\n- раз\n- два\n- три\n- четыре\n"
check("список из 4 пунктов: короткому нельзя", "bullets_over_3" in cat(lst))
check("список из 4 пунктов: лонгриду можно",
      "bullets_over_3" not in cat(lst, short_form=False))

# 7. Заголовки: то же разделение.
check("заголовок в коротком посте ловится", "headings_in_short" in cat("## Итоги\n\nТекст."))
check("заголовок в лонгриде законен",
      "headings_in_short" not in cat("## Итоги\n\nТекст.", short_form=False))

# 8. Защищённые зоны: ё/тире/латиница законны в коде, URL и путях.
check("код не считается", sd.analyse("Текст.\n\n```\nx = 'ёмкость — да'\n```\n")["violations"] == 0)
check("путь не считается", sd.analyse("Лежит в /Users/<имя>/ёлка")["violations"] == 0)

# 9-бис. Граблина 15.08: ё и длинное тире это маркеры РУССКОГО нейрослога.
#    В английском em dash законен (замер: 141 штука в 40 живых лонгридах репо).
check("em dash в английском тексте законен",
      "em_dash" not in cat("The fix was one line — and it held. We shipped it that night."))
check("em dash в русском тексте ловится",
      "em_dash" in cat("Починка была в одну строку — и она держится."))
check("смешанный текст с кириллицей судится как русский",
      "yo" in cat("Агент читает logs и пишет отчёт в ledger каждые пять минут."))

# 9. Базовые маркеры живы.
check("длинное тире ловится", "em_dash" in cat("Текст — продолжение."))
check("ё ловится", "yo" in cat("Ещё один текст."))
check("негативный параллелизм ловится",
      "neg_parallel" in cat("Это не просто инструмент, а целая система."))

print(f"\nитог: {'ВСЁ ЗЕЛЁНОЕ' if not FAILS else f'{len(FAILS)} падений: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
