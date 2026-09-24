"""Lever ATS toolkit (wave16, [машина флота]). Plain-HTML forms on jobs.lever.co.

Rail: fresh headless Firefox per job (ats_lib.new_driver). Fields addressed by
name= attribute. Radios/checkboxes clicked via JS (custom-styled inputs are
visually hidden). Cards not matching the selected opportunityLocationId are
display:none and must NOT be filled.
"""
from __future__ import annotations
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

CANON = {
    "name": "Anton Dziatkovskii",
    "email": "dzyatkovskiy.a@gmail.com",
    "phone": "+1 341 222 9178",
    "org": "Palo Alto AI Research Lab (Founder); Platinum VC & Incubator (Co-Founder)",
    "github": "https://github.com/tonydzi",
    "portfolio": "https://tonydzi.github.io/",
    "twitter": "https://x.com/Tony_Stef_",
    "scholar": "https://scholar.google.com/citations?user=b8gKHiMAAAAJ",
    "loc_us": "Palo Alto, CA",
    "loc_eu": "Lisbon, Portugal",
}

CV = {
    "product": "/Users/<имя>/Obsidian/Anton-Knowledge/04-Projects/Pipe-A-Batches/sent-2026-09-01/Anton-Dziatkovskii-CV-Product.pdf",
    "founder-bd": "/Users/<имя>/Obsidian/Anton-Knowledge/04-Projects/Pipe-A-Batches/sent-2026-09-01/Anton-Dziatkovskii-CV-BD-Partnerships.pdf",
    "fde": "/Users/<имя>/Obsidian/Anton-Knowledge/04-Projects/Pipe-A-Batches/sent-2026-09-01/Anton-Dziatkovskii-CV-FDE.pdf",
}


def js_hidden(d, el):
    return d.execute_script(
        "for(let p=arguments[0];p;p=p.parentElement){if(getComputedStyle(p).display==='none')return true}return false",
        el)


def named(d, name, only_visible=True):
    els = d.find_elements(By.CSS_SELECTOR, f"[name='{name}']")
    if only_visible:
        els = [e for e in els if not js_hidden(d, e)]
    return els


def fill_named(d, name, value):
    els = named(d, name)
    els = [e for e in els if e.tag_name in ("input", "textarea")
           and (e.get_attribute("type") or "text") not in ("radio", "checkbox", "hidden", "file")]
    if not els:
        return f"NO-FIELD:{name}"
    el = els[0]
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except Exception:
        d.execute_script("arguments[0].focus();", el)
    time.sleep(0.2)
    d.execute_script(
        "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", el)
    el.send_keys(value)
    time.sleep(0.3)
    got = el.get_attribute("value") or ""
    return "OK" if got.strip() == value.strip() else f"MISMATCH:{name}:got={got!r}"


def set_select(d, name, visible_text):
    els = [e for e in named(d, name) if e.tag_name == "select"]
    if not els:
        return f"NO-SELECT:{name}"
    try:
        Select(els[0]).select_by_visible_text(visible_text)
    except Exception:
        # enclave iframe may overlay the select — set via JS + change event
        ok = d.execute_script(
            "const s=arguments[0], t=arguments[1].trim();"
            "const o=[...s.options].find(x=>x.text.trim()===t);"
            "if(!o) return false; s.value=o.value;"
            "s.dispatchEvent(new Event('change',{bubbles:true})); return true;",
            els[0], visible_text)
        if not ok:
            return f"NO-OPTION:{name}:{visible_text}"
    time.sleep(0.5)
    got = Select(els[0]).first_selected_option.text
    return "OK" if got.strip() == visible_text.strip() else f"MISMATCH:{name}:got={got!r}"


def click_radio(d, name, value):
    """JS-click input[name][value]; skip if its card is display:none."""
    els = d.find_elements(By.CSS_SELECTOR, f"input[name='{name}'][value='{value}']")
    if not els:
        # value may contain quotes/spaces — fall back to scanning
        els = [e for e in d.find_elements(By.CSS_SELECTOR, f"input[name='{name}']")
               if (e.get_attribute("value") or "") == value]
    if not els:
        return f"NO-RADIO:{name}:{value}"
    el = els[0]
    if js_hidden(d, el):
        return f"HIDDEN:{name}"
    d.execute_script("arguments[0].click();", el)
    time.sleep(0.3)
    return "OK" if d.execute_script("return arguments[0].checked;", el) else f"NOT-CHECKED:{name}"


def click_checkbox(d, name, value=None, want=True):
    els = d.find_elements(By.CSS_SELECTOR, f"input[type='checkbox'][name='{name}']")
    if value is not None:
        els = [e for e in els if (e.get_attribute("value") or "") == value]
    if not els:
        return f"NO-CHECKBOX:{name}"
    el = els[0]
    if js_hidden(d, el):
        return f"HIDDEN:{name}"
    cur = d.execute_script("return arguments[0].checked;", el)
    if cur != want:
        d.execute_script("arguments[0].click();", el)
        time.sleep(0.3)
    got = d.execute_script("return arguments[0].checked;", el)
    return "OK" if got == want else f"TOGGLE-FAIL:{name}"


def upload_resume(d, path, settle=12):
    els = d.find_elements(By.CSS_SELECTOR, "input[type=file][name='resume']")
    if not els:
        return "NO-FILE-INPUT"
    els[0].send_keys(path)
    fname = path.rsplit("/", 1)[-1]
    for _ in range(settle):
        time.sleep(1)
        txt = d.execute_script(
            "const c=document.querySelector('.application-field-resume,.resume-upload,"
            "[class*=resume]');return c?c.innerText:'';") or ""
        body = d.execute_script("return document.body.innerText.slice(0,4000);")
        if "Success" in txt or fname in txt or fname in body:
            return "OK"
    return f"CHIP-UNCONFIRMED:{fname}"


def fill_location(d, city):
    els = named(d, "location")
    if not els:
        return "NO-FIELD:location"
    el = els[0]
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click()
    time.sleep(1.5)  # Lever geo-IP autofill fires on focus — let it land, then wipe it
    d.execute_script(
        "arguments[0].value='';"
        "const s=document.querySelector('input[name=selectedLocation]'); if(s) s.value='';"
        "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", el)
    time.sleep(0.3)
    el.send_keys(city)
    time.sleep(2.5)
    # try clicking first typeahead suggestion
    picked = d.execute_script(r"""
      const cands = Array.from(document.querySelectorAll(
        '[class*=dropdown] li, [class*=dropdown] div, ul[class*=location] li, [class*=result]'));
      const vis = cands.filter(e => e.offsetParent !== null && (e.innerText||'').trim().length > 2
                                    && !(e.innerText||'').includes('\n'));
      const want = arguments[0].toLowerCase().split(',')[0];
      const hit = vis.find(e => e.innerText.toLowerCase().includes(want));
      if (hit) { hit.click(); return hit.innerText.trim().slice(0,80); }
      return null;
    """, city)
    time.sleep(0.8)
    sel = d.execute_script(
        "const s=document.querySelector('input[name=selectedLocation]');return s?s.value.slice(0,120):'';")
    val = el.get_attribute("value")
    return f"OK:typed={val!r}:picked={picked!r}:selectedLocation={sel[:80]!r}"


def form_errors(d):
    return d.execute_script(r"""
      const out = [];
      document.querySelectorAll('[class*=error], .invalid, [aria-invalid=true]').forEach(e => {
        if (e.offsetParent === null) return;
        const t = (e.innerText || '').trim();
        if (t && t.length < 200) out.push(t);
        else if (e.name) out.push('invalid-field:' + e.name);
      });
      return Array.from(new Set(out)).slice(0, 15);
    """)


def submit(d):
    btns = d.find_elements(By.ID, "btn-submit")
    if not btns:
        return "NO-SUBMIT-BUTTON"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
    try:
        btns[0].click()
        return "CLICKED"
    except Exception as e:
        if "hcaptcha-enclave" in str(e) or "obscures" in str(e):
            # transparent hcaptcha background frame overlays the button; JS-click the
            # button itself (captcha still runs its own invisible flow afterwards)
            d.execute_script("arguments[0].click();", btns[0])
            return "CLICKED-JS(enclave-overlay)"
        raise


def outcome_after_submit(d, wait=25):
    for _ in range(wait):
        time.sleep(1)
        url = d.current_url
        body = ""
        try:
            body = d.execute_script("return document.body.innerText.slice(0,3000);") or ""
        except Exception:
            pass
        if "/thanks" in url or "Application submitted" in body or "Thank you for applying" in body:
            return "APPLIED", url, body[:400]
        # visible captcha challenge? (iframe OR the enclave-mode overlay div)
        cap = d.execute_script(r"""
          const f = Array.from(document.querySelectorAll('iframe'))
            .filter(i => /hcaptcha|recaptcha/i.test(i.src||'') && i.offsetParent !== null
                    && i.clientHeight > 60);
          if (f.length) return 'iframe';
          const div = Array.from(document.querySelectorAll('div,section'))
            .find(e => e.offsetParent !== null && e.clientHeight > 200 && e.clientWidth > 200
                  && /find items|select all|please click|verify you are human/i.test(e.innerText||'')
                  && (e.innerText||'').length < 600);
          return div ? 'overlay' : '';
        """)
        if cap:
            return "CAPTCHA-CHALLENGE", url, body[:400]
    errs = form_errors(d)
    return "NO-CONFIRM", d.current_url, "errors=" + repr(errs)


def page_text(d, limit=1500):
    try:
        return d.find_element(By.TAG_NAME, "body").text[:limit]
    except Exception as e:
        return f"ERR:{e}"
