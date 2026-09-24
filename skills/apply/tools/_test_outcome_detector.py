"""Сетка детектора исхода подачи — класс «вежливый отказ читается как успех».

Замер 04.09 (волна 24, Decagon): страница отдала
  «We couldn't submit your application | Thank you for your interest in opportunities at Decagon!»
Фраза «thank you for your interest» — часть ОТКАЗА, но детектор печатал OUTCOME: success.
Заявка не ушла, а в реестре стояло бы applied: Антон считал бы себя поданным, повторно не подал бы.

D1 отказной баннер Decagon → НЕ успех
D2 кап Ramp («reached your application limit») → НЕ успех
D3 кап Sierra («unable to accept an additional application») → НЕ успех
D4 спам-флаг Ashby → НЕ успех
D5 «You have already applied» → НЕ успех
D6 чистый успех Ashby → успех
D7 успех с «Thank you for applying» → успех
D8 успех, где рядом в сайдбаре слово «successful candidate» → НЕ успех (старая грабля, не регрессировать)

Прогон: python3 _test_outcome_detector.py   ·  Кто дёргает: /tt после правки apply_generic.py / gh_lib.py.
Updated: 2026-09-04.
"""
import re
import sys

REJECT = ("couldn't submit", "could not submit", "unable to accept",
          "we limit the number of applications", "application limit",
          "flagged as possible spam", "already applied", "reached this limit",
          "unable to submit")
SUCCESS = ("successfully submitted", "application was successfully",
           "thank you for applying", "application has been submitted",
           "thank you for submitting your application")


def classify(page_text):
    """Тот же порядок, что в боевых раннерах: ОТКАЗ проверяется ПЕРВЫМ."""
    low = page_text.lower()
    hit = next((r for r in REJECT if r in low), None)
    if hit:
        return "rejected:" + hit
    if any(p in low for p in SUCCESS):
        return "success"
    return "unconfirmed"


CASES = [
    ("D1 Decagon: отказ с вежливой фразой внутри",
     "We couldn't submit your application | Thank you for your interest in opportunities at Decagon! "
     "To ensure a fair and focused hiring process, we limit the number of applications", False),
    ("D2 Ramp: кап заявок",
     "We couldn't submit your application - Thank you for considering Ramp! You have reached your "
     "application limit. a total of 2 over a span of 60 days.", False),
    ("D3 Sierra: кап компании",
     "We couldn't submit your application - Thank you for your continued interest. We see you've applied "
     "multiple times recently ... we are unable to accept an additional application at this time", False),
    ("D4 Ashby: спам-флаг",
     "We couldn't submit your application - Your application submission was flagged as possible spam.", False),
    ("D5 уже подавались",
     "We couldn't submit your application - You have already applied to this role in the past few months.", False),
    ("D6 чистый успех Ashby",
     "Success | Your application was successfully submitted. We'll contact you if there are next steps.", True),
    ("D7 успех через «thank you for applying»",
     "Success | Thank you for applying to MaintainX!", True),
    ("D9 Parallel: успех своей формулировкой (детектор её не знал, сказал unconfirmed)",
     "Success - Thank you for submitting your application! We will be in touch if there is a fit.", True),
    ("D8 сайдбарная проза про successful candidate",
     "About the role | The successful candidate will own the roadmap | Apply below", False),
]


def main():
    fails = []
    for name, text, want_success in CASES:
        got = classify(text)
        ok = (got == "success") == want_success
        print(("  ✅ " if ok else "  ❌ ") + name + ("" if ok else f" — детектор сказал {got!r}"))
        if not ok:
            fails.append(name)

    # порядок проверок в боевом коде должен совпадать с этой сеткой
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for fn, rej_mark, suc_mark in (("apply_generic.py", "REJECTED-BANNER", "SUCCESS after"),
                                   ("gh_lib.py", '"rejected:" + _rej', '"success", body')):
        src = open(os.path.join(here, fn), encoding="utf-8").read()
        ok = rej_mark in src and suc_mark in src and src.index(rej_mark) < src.index(suc_mark)
        print(("  ✅ " if ok else "  ❌ ") + f"{fn}: проверка отказа стоит ПЕРЕД проверкой успеха")
        if not ok:
            fails.append(fn)

    print(f"\n{'ВСЁ ЗЕЛЁНОЕ' if not fails else 'КРАСНОЕ: ' + ', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
