"""Greenhouse (job-boards.greenhouse.io new UI) fill helpers, selenium rail.

Playbook recipe: address fields by id; combos = focus -> type full string ->
pause -> Enter, then VERIFY the chosen text appears near the field (react-select
keeps input.value empty). Phone Country is a separate widget and must be set.
"""
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def entry_text(d, qid):
    return d.execute_script("""
      const el = document.getElementById(arguments[0]);
      if (!el) return 'NO-EL';
      const box = el.closest('div[class*="field"], div[class*="Field"], fieldset') || el.parentElement.parentElement;
      return (box.innerText || '').slice(0, 400);
    """, qid)


def _stale_retry(fn):
    """React-формы Greenhouse перерисовывают DOM: элемент протухает между find и действием."""
    def wrapped(*a, **kw):
        from selenium.common.exceptions import StaleElementReferenceException
        for attempt in range(3):
            try:
                return fn(*a, **kw)
            except StaleElementReferenceException:
                if attempt == 2:
                    return f"STALE-3X:{a[1] if len(a) > 1 else '?'}"
                time.sleep(1.2)
    return wrapped


@_stale_retry
def gh_text(d, qid, value):
    try:
        el = d.find_element(By.ID, qid)
    except Exception:
        return f"NO-EL:{qid}"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except Exception:
        d.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));")
        d.execute_script("arguments[0].focus();", el)
    time.sleep(0.3)
    d.execute_script("arguments[0].select && arguments[0].select();", el)
    el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE)
    el.send_keys(value); time.sleep(0.3)
    got = el.get_attribute("value") or ""
    return "OK" if got.strip() == value.strip() else f"MISMATCH:{qid}:got={got[:60]!r}"



@_stale_retry
def gh_combo(d, qid, candidates, verify_snippets=None):
    """Try each candidate string until the entry shows it (or a verify snippet)."""
    if isinstance(candidates, str):
        candidates = [candidates]
    verify_snippets = verify_snippets or [c[:25] for c in candidates]
    try:
        el = d.find_element(By.ID, qid)
    except Exception:
        return f"NO-EL:{qid}"
    def close_menus():
        try:
            el.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        time.sleep(0.3)
    for cand in candidates:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            el.click()
        except Exception:
            d.execute_script("arguments[0].focus(); arguments[0].click && arguments[0].click();", el)
        time.sleep(0.6)
        el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE)
        el.send_keys(cand); time.sleep(1.6)
        el.send_keys(Keys.ENTER)
        hit = None
        for _ in range(4):
            time.sleep(0.7)
            txt = entry_text(d, qid)
            for sn in verify_snippets:
                if sn.lower() in txt.lower():
                    hit = cand
                    break
            if hit:
                break
        close_menus()
        if hit:
            return f"OK:{hit}"
    return f"NO-MATCH:{qid}:tried={candidates}:entry={entry_text(d, qid)[:80]!r}"


def gh_resume(d, path, settle=12):
    inp = d.find_elements(By.CSS_SELECTOR, "input[type=file]#resume") or \
          d.find_elements(By.CSS_SELECTOR, "input[type=file]")
    if not inp:
        return "NO-FILE-INPUT"
    inp[0].send_keys(path)
    time.sleep(settle)
    fname = path.rsplit("/", 1)[-1]
    body = d.find_element(By.TAG_NAME, "body").text
    return "OK" if fname in body else f"CHIP-MISSING:{fname}"


def gh_submit(d):
    btns = d.find_elements(By.XPATH, "//button[contains(., 'Submit application') or contains(., 'Submit Application')]")
    if not btns:
        return "NO-SUBMIT"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[-1])
    btns[-1].click()
    return "CLICKED"


def gh_wait_outcome(d, rounds=10, pause=4):
    """Returns (outcome, page_text). Detects success, the email-code anti-bot gate, and errors."""
    for _ in range(rounds):
        time.sleep(pause)
        body = d.find_element(By.TAG_NAME, "body").text
        low = body.lower()
        if "verification code" in low or "enter the 8-character" in low:
            return "code-gate", body[:1200]
        # ⛔ ОТКАЗ БЬЁТ УСПЕХ — вежливые фразы живут внутри отказных баннеров (Decagon 04.09)
        _rej = next((r for r in ("couldn't submit", "could not submit", "unable to accept",
                                 "we limit the number of applications", "application limit",
                                 "flagged as possible spam", "already applied",
                                 "reached this limit", "unable to submit") if r in low), None)
        if _rej:
            return "rejected:" + _rej, body[:1200]
        if "thank you for submitting your application" in low:
            return "success", body[:1200]
        if "thank you" in low and "applying" in low:
            return "success", body[:1200]
        if "application submitted" in low or "successfully submitted" in low:
            return "success", body[:1200]
        errs = d.execute_script("""
          return Array.from(document.querySelectorAll('[class*="error"], [role="alert"], [aria-invalid="true"]'))
            .map(e => (e.innerText || e.id || '').trim()).filter(Boolean).slice(0, 10);
        """)
        if errs:
            return "errors:" + "|".join(errs)[:300], body[:1200]
    return "unconfirmed", body[:1200]


def gh_pick_first_option(d, qid, wait=1.5):
    """Open a react-select combo and click its first option by id; verify by placeholder gone."""
    try:
        el = d.find_element(By.ID, qid)
    except Exception:
        return f"NO-EL:{qid}"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except Exception:
        d.execute_script("arguments[0].focus(); arguments[0].click && arguments[0].click();", el)
    time.sleep(wait)
    opt = d.find_elements(By.ID, f"react-select-{qid}-option-0")
    if not opt:
        try:
            el.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return f"NO-OPTION:{qid}"
    opt[0].click()
    time.sleep(0.8)
    txt = entry_text(d, qid)
    return "OK" if "Select..." not in txt else f"PLACEHOLDER-STILL:{qid}:{txt[:70]!r}"
