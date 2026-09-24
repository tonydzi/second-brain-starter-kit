"""Generic Ashby application runner. Usage:
  python3 apply_generic.py spec.json [--submit] [--dump-only]

Spec: {url, resume, out_prefix, texts: {label: value}, yesnos: {label: bool},
       combos: {label: value}, required_labels: [labels that must be non-empty]}
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ats_lib import (new_driver, dump_ashby, upload_resume, fill_text, click_yesno,
                     fill_combo, click_checkbox, verify_all, submit, page_text,
                     select_option_in_entry)

spec = json.load(open(sys.argv[1]))
HERE = os.path.dirname(os.path.abspath(__file__))
prefix = spec.get("out_prefix", "run")

d = new_driver()
try:
    d.get(spec["url"]); time.sleep(8)
    print("title:", d.title[:90], flush=True)

    if "--dump-only" in sys.argv:
        fields = dump_ashby(d)
        print(json.dumps(fields, ensure_ascii=False, indent=1), flush=True)
        sys.exit(0)

    print("resume:", upload_resume(d, spec["resume"]), flush=True)
    for label, value in spec.get("texts", {}).items():
        print("text[%s]:" % label[:40], fill_text(d, label, value), flush=True)
    for label, value in spec.get("combos", {}).items():
        print("combo[%s]:" % label[:40], fill_combo(d, label, value), flush=True)
    for label, yes in spec.get("yesnos", {}).items():
        print("yesno[%s]:" % label[:40], click_yesno(d, label, yes), flush=True)
    for label, option in spec.get("check_options", {}).items():
        print("opt[%s]:" % label[:40], select_option_in_entry(d, label, option), flush=True)
    for label, want in spec.get("checkboxes", {}).items():
        print("checkbox[%s]:" % label[:40], click_checkbox(d, label, want), flush=True)

    rep = verify_all(d)
    print(json.dumps(rep, ensure_ascii=False, indent=1), flush=True)

    missing = []
    for lab in spec.get("required_labels", []):
        hit = next((r for r in rep if r["label"].startswith(lab)), None)
        ok = hit and (hit["value"].startswith("FILE:") or len(hit["value"].strip()) > 0 or hit["pressed"])
        if not ok:
            missing.append(lab)
    if missing:
        print("MISSING-REQUIRED:", missing, flush=True)

    if "--submit" in sys.argv and not missing:
        print("SUBMIT:", submit(d), flush=True)
        outcome = "unconfirmed"
        for i in range(10):
            time.sleep(4)
            errs = d.execute_script("""
              return Array.from(document.querySelectorAll('[class*="error"], [role="alert"], [class*="danger"]'))
                .map(e => e.innerText.trim()).filter(Boolean).slice(0,10);
            """)
            if errs:
                print("FORM-ERRORS:", errs, flush=True)
                outcome = "errors"
                break
            low = page_text(d, 3000).lower()
            # ⛔ ОТКАЗ БЬЁТ УСПЕХ (класс instrument-is-a-claim, замер 04.09 волна 24):
            # Decagon отдаёт «We couldn't submit your application ... Thank you for your interest
            # in opportunities at Decagon!» — вежливая фраза сидит ВНУТРИ отказного баннера,
            # и детектор печатал success для НЕотправленной заявки. Сначала ищем отказ.
            REJECT = ("couldn't submit", "could not submit", "unable to accept",
                      "we limit the number of applications", "application limit",
                      "flagged as possible spam", "already applied", "reached this limit",
                      "unable to submit")
            hit_reject = next((r for r in REJECT if r in low), None)
            if hit_reject:
                print(f"REJECTED-BANNER: {hit_reject!r}", flush=True)
                outcome = "rejected:" + hit_reject
                break
            # strict phrases only: sidebar prose like "successful candidate" must NOT match
            if ("successfully submitted" in low or "application was successfully" in low
                    or "thank you for applying" in low or "application has been submitted" in low
                    or "thank you for submitting your application" in low):
                print(f"SUCCESS after {4*(i+1)}s", flush=True)
                outcome = "success"
                break
        print("AFTER-SUBMIT:", page_text(d, 900).replace(chr(10), " | "), flush=True)
        d.save_screenshot(os.path.join(HERE, f"{prefix}_after.png"))
        print("OUTCOME:", outcome, flush=True)
    else:
        d.save_screenshot(os.path.join(HERE, f"{prefix}_filled.png"))
        print("NOT SUBMITTED (missing=%s, flag=%s)" % (missing, "--submit" in sys.argv), flush=True)
finally:
    d.quit()
