"""Переигровка code-gated заявок С АНТОНОМ: видимый Firefox, робот заполняет,
Антон вводит 8-символьный код из письма a@ и жмёт Submit. Формы идут по очереди.

Запуск: ATS_HEADED=1 python3 recover_gated.py spec1.json spec2.json ...
Робот код НЕ вводит и НЕ читает — только ждёт результат на странице.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ats_lib import new_driver
from gh_lib import gh_text, gh_combo, gh_resume, gh_submit, gh_pick_first_option, entry_text
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def combo_click(d, qid, want):
    """click-the-option combo для упрямых полей (перенос из apply_stripe.py)."""
    try:
        el = d.find_element(By.ID, qid)
    except Exception:
        return f"NO-EL:{qid}"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click(); time.sleep(0.6)
    el.send_keys(want); time.sleep(1.8)
    opts = d.find_elements(By.CSS_SELECTOR, f"[id^='react-select-{qid}-option']")
    if not opts:
        el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE); time.sleep(1.5)
        opts = d.find_elements(By.CSS_SELECTOR, f"[id^='react-select-{qid}-option']")
    target = None
    for o in opts:
        if (o.text or "").strip().lower() == want.lower():
            target = o; break
    if target is None:
        for o in opts:
            if want.lower() in (o.text or "").lower():
                target = o; break
    if target is None:
        return f"NO-OPTION:{qid}:{want}:seen={[o.text for o in opts[:5]]}"
    target.click(); time.sleep(0.8)
    return f"OK:{entry_text(d, qid)[:60]}"

HERE = os.path.dirname(os.path.abspath(__file__))
SUCCESS_PHRASES = ("successfully submitted", "thank you for applying",
                   "application has been submitted", "application was successfully",
                   "thank you for your application", "application received",
                   "we have received your application")
CODE_PHRASES = ("verification code", "8-character", "security code",
                "code sent to", "check your email for a code", "confirm your email")
ERROR_PHRASES = ("is required", "field is required", "needs corrections",
                 "missing entry", "review the errors", "fix the errors",
                 "is too long", "is too short", "is invalid", "invalid phone")

results = []
specs = [a for a in sys.argv[1:] if a.endswith(".json")]
for n, spath in enumerate(specs, 1):
    spec = json.load(open(spath))
    name = spec.get("out_prefix", spath)
    print(f"\n===== ФОРМА {n}/{len(specs)}: {name} =====", flush=True)
    d = new_driver()
    try:
      try:
        d.get(spec["url"]); time.sleep(8)
        print("title:", d.title[:80], flush=True)
        print("resume:", gh_resume(d, spec["resume"]), flush=True)
        for fid, value in spec.get("texts", {}).items():
            print(f"text[{fid}]:", gh_text(d, fid, value), flush=True)
        for fid, cands in spec.get("combos", {}).items():
            print(f"combo[{fid}]:", gh_combo(d, fid, cands), flush=True)
        for fid, want in spec.get("combo_click", {}).items():
            print(f"cclick[{fid}]:", combo_click(d, fid, want), flush=True)
        for fid in spec.get("pick_first", []):
            print(f"pick[{fid}]:", gh_pick_first_option(d, fid), flush=True)
        for fid in spec.get("checkboxes", []):
            res = d.execute_script("""
              const el = document.getElementById(arguments[0]);
              if (!el) return 'NO-EL';
              if (!el.checked) el.click();
              return el.checked ? 'OK' : 'NOT-CHECKED';
            """, fid)
            print(f"checkbox[{fid}]:", res, flush=True)
            time.sleep(0.3)
        body = d.execute_script("return document.body.innerText;")
        fname = spec["resume"].rsplit("/", 1)[-1]
        if fname not in body:
            print("RESUME-CHIP MISSING — пропускаю форму", flush=True)
            results.append({"form": name, "outcome": "error-no-resume"})
            continue
        print("SUBMIT:", gh_submit(d), flush=True)

        outcome = "unconfirmed"
        code_announced = False
        # приказ Антона 03.09 (скилл /apply): код-гейт НЕ дёргает его — метка и дальше.
        # RECOVER_CODE_WAIT_S=30 для автономного прогона; 720 (дефолт) для присеста с кодами.
        deadline = time.time() + int(os.environ.get("RECOVER_CODE_WAIT_S", "720"))
        while time.time() < deadline:
            time.sleep(4)
            try:
                low = d.execute_script("return document.body.innerText;").lower()
            except Exception as e:
                print("окно закрыто/умерло:", str(e)[:80], flush=True)
                outcome = "window-closed"
                break
            if any(p in low for p in SUCCESS_PHRASES):
                outcome = "applied"
                print(f"✅ SUCCESS: {name}", flush=True)
                break
            if any(p in low for p in CODE_PHRASES):
                if not code_announced:
                    code_announced = True
                    print(f"🔑 ЖДУ КОД ({name}): смотри окно Firefox — введи 8-символьный код "
                          f"из свежего письма на dzyatkovskiy.a@gmail.com и подтверди. Жду до 12 минут.", flush=True)
                continue  # code-gate на экране — ждём Антона, form-errors не проверяем
            if any(p in low for p in ERROR_PHRASES):
                outcome = "form-errors"
                errs = [l for l in low.splitlines() if any(p in l for p in ERROR_PHRASES)][:6]
                print(f"⛔ FORM-ERRORS ({name}), спек устарел — дальше без 12-мин ожидания:", flush=True)
                for l in errs:
                    print("   ", l.strip()[:100], flush=True)
                break
        if outcome == "unconfirmed" and code_announced:
            outcome = "code-gate"   # форма ушла до заслона, код никто не ввёл — 🟡 в таблицу
        results.append({"form": name, "outcome": outcome})
        try:
            d.save_screenshot(os.path.join(HERE, f"{name}_recover_final.png"))
        except Exception:
            pass
      except Exception as e:
        print(f"💥 CRASHED ({name}): {type(e).__name__}: {str(e)[:120]} — еду дальше", flush=True)
        results.append({"form": name, "outcome": "crashed"})
        try:
            d.save_screenshot(os.path.join(HERE, f"{name}_recover_crash.png"))
        except Exception:
            pass
    finally:
        try:
            d.quit()
        except Exception:
            pass

print("\n===== ИТОГ ПЕРЕИГРОВКИ =====", flush=True)
for r in results:
    print(f"{r['outcome']:14} | {r['form']}", flush=True)
json.dump(results, open(os.path.join(HERE, os.environ.get("RECOVER_OUT", "recover_results.json")), "w"), ensure_ascii=False, indent=1)
