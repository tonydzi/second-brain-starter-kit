"""Workable (apply.workable.com) helper for wave18 indices 5-9 ([машина флота]).

Rail probe: react form, fields carry data-ui attributes.
Flow: open /j/<ID> -> go to /apply -> upload resume FIRST (parse ~12s may
autofill) -> dump -> fill/overwrite -> screenshot -> submit -> verify text.
"""
from __future__ import annotations
import os, sys, time, json

sys.path.insert(0, os.path.expanduser("~/.claude/scripts/_shared"))
from firefox_selenium import make_driver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.common.keys import Keys  # noqa: E402

SCRATCH = os.path.dirname(os.path.abspath(__file__))


def new_driver(headless=True):
    import tempfile
    prof = tempfile.mkdtemp(prefix="ff_wk18_")
    d = make_driver(profile=prof, headless=headless)
    d.set_window_size(1380, 2200)
    return d


def open_apply(d, url):
    d.get(url)
    time.sleep(6)
    # cookie banner: prefer decline/essential-only
    try:
        for txt in ("Decline", "Reject", "Only necessary", "Necessary only"):
            btns = [b for b in d.find_elements(By.TAG_NAME, "button") if (b.text or "").strip().lower().startswith(txt.lower())]
            if btns:
                btns[0].click(); time.sleep(1); break
    except Exception:
        pass
    body = ""
    try:
        body = d.find_element(By.TAG_NAME, "body").text
    except Exception:
        pass
    low = body.lower()
    if "no longer accepting" in low or "not accepting applications" in low or "job not found" in low or "404" in (d.title or ""):
        return "CLOSED", body[:600]
    # already a form?
    if d.find_elements(By.CSS_SELECTOR, "form input[type=file], [data-ui='application-form']"):
        return "FORM", body[:600]
    # click Apply button
    for b in d.find_elements(By.XPATH, "//a[contains(., 'Apply')] | //button[contains(., 'Apply')]"):
        t = (b.text or "").strip().lower()
        if t.startswith("apply"):
            try:
                d.execute_script("arguments[0].scrollIntoView({block:'center'});", b)
                b.click(); time.sleep(5)
                break
            except Exception:
                continue
    if d.find_elements(By.CSS_SELECTOR, "form input[type=file], [data-ui='application-form']"):
        return "FORM", ""
    # fallback: direct /apply URL
    u = url.rstrip("/") + "/apply/"
    d.get(u); time.sleep(6)
    if d.find_elements(By.CSS_SELECTOR, "form input[type=file], form input[data-ui], [data-ui='application-form']"):
        return "FORM", ""
    try:
        body = d.find_element(By.TAG_NAME, "body").text[:600]
    except Exception:
        body = ""
    return "NO-FORM", body


def dump_form(d):
    """Inventory all controls: data-ui, label, tag/type, required, options."""
    return d.execute_script(r"""
      const out = [];
      const seen = new Set();
      document.querySelectorAll('form input, form textarea, form select, form [role=radio], form [role=checkbox], form [role=combobox], form [role=listbox], form fieldset').forEach(el => {
        const key = el.getAttribute('data-ui') || el.name || el.id || (el.tagName + out.length);
        const wrap = el.closest('[role=group], fieldset, div[class*="styles"]') || el.parentElement;
        let label = '';
        if (el.id) { const l = document.querySelector('label[for="'+el.id+'"]'); if (l) label = l.innerText.trim(); }
        if (!label && el.getAttribute('aria-label')) label = el.getAttribute('aria-label');
        if (!label && el.getAttribute('aria-labelledby')) {
          const l = document.getElementById(el.getAttribute('aria-labelledby'));
          if (l) label = l.innerText.trim();
        }
        if (!label && wrap) {
          const l = wrap.querySelector('label, legend, [id$="_label"], strong');
          if (l) label = l.innerText.trim().slice(0,160);
        }
        const sig = key + '|' + label + '|' + (el.type||el.tagName);
        if (seen.has(sig)) return;
        seen.add(sig);
        out.push({
          dataui: el.getAttribute('data-ui'),
          name: el.name || null, id: el.id || null,
          tag: el.tagName.toLowerCase(), type: el.type || el.getAttribute('role') || null,
          label: (label||'').slice(0,200),
          required: el.required || el.getAttribute('aria-required') === 'true',
          value: (el.value || '').slice(0,80),
        });
      });
      // group labels for radios/checkboxes via fieldset/spans
      return out;
    """)


def page_labels(d):
    """All visible question labels + radio/checkbox option texts (for custom Qs)."""
    return d.execute_script(r"""
      const qs = [];
      document.querySelectorAll('form [class*="question"], form fieldset, form [role=group]').forEach(g => {
        const t = (g.innerText||'').trim();
        if (t) qs.push(t.slice(0, 500));
      });
      return qs;
    """)


def _input_by_ui(d, ui):
    els = d.find_elements(By.CSS_SELECTOR, f"input[data-ui='{ui}'], textarea[data-ui='{ui}']")
    return els[0] if els else None


def set_text_el(d, el, value):
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
    except Exception:
        d.execute_script("arguments[0].focus();", el)
    time.sleep(0.3)
    el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE); time.sleep(0.2)
    el.send_keys(value); time.sleep(0.4)
    got = el.get_attribute("value") or ""
    def _norm(s):
        return s.replace(",", "").replace(" ", "").strip()
    if got.strip() == value.strip() or (_norm(got) == _norm(value) and _norm(value)):
        return "OK"
    # react-resistant: native setter + events + trusted keystroke
    d.execute_script(r"""
      const el = arguments[0], v = arguments[1];
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
      setter.call(el, v);
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
    """, el, value[:-1] if value else value)
    el.send_keys(value[-1] if value else "")
    time.sleep(0.4)
    got = el.get_attribute("value") or ""
    return "OK" if got.strip() == value.strip() else f"MISMATCH:got={got!r}"


def fill_ui(d, ui, value):
    el = _input_by_ui(d, ui)
    if el is None:
        return f"NO-FIELD:{ui}"
    r = set_text_el(d, el, value)
    return r if r == "OK" else f"{ui}:{r}"


def upload_resume(d, path, settle=14):
    inps = (d.find_elements(By.CSS_SELECTOR, "[data-ui='resume'] input[type=file], input[data-ui='resume'][type=file]")
            or d.find_elements(By.CSS_SELECTOR, "form input[type=file]"))
    if not inps:
        return "NO-FILE-INPUT"
    inps[0].send_keys(path)
    time.sleep(settle)
    fname = path.rsplit("/", 1)[-1]
    body = d.find_element(By.TAG_NAME, "body").text
    return "OK" if fname in body else f"CHIP-MISSING:{fname}"


def set_phone(d, number="[id]", intl="+1 341 222 9178"):
    """Workable intl phone widget: country button + input. Try US then plain."""
    el = _input_by_ui(d, "phone")
    if el is None:
        els = d.find_elements(By.CSS_SELECTOR, "input[type=tel]")
        el = els[0] if els else None
    if el is None:
        return "NO-PHONE"
    # is there a country selector next to it?
    try:
        btns = d.find_elements(By.CSS_SELECTOR, "[data-ui='phone'] button, .iti__selected-flag, [class*='flagContainer'], [class*='PhoneInputCountry']")
        if btns:
            btns[0].click(); time.sleep(1)
            # search field or option list
            opts = d.find_elements(By.XPATH, "//li[contains(., 'United States')] | //*[[аккаунт]='option'][contains(., 'United States')]")
            search = d.find_elements(By.CSS_SELECTOR, "input[type=search], [role='listbox'] input")
            if search:
                search[0].send_keys("United States"); time.sleep(1)
                opts = d.find_elements(By.XPATH, "//li[contains(., 'United States')] | //*[[аккаунт]='option'][contains(., 'United States')]")
            if opts:
                opts[0].click(); time.sleep(0.7)
                return set_text_el(d, el, number)
    except Exception:
        pass
    return set_text_el(d, el, intl)


def click_radio(d, question_frag, option_text):
    """Click radio/checkbox by question text fragment + option label text."""
    res = d.execute_script(r"""
      const qf = arguments[0].toLowerCase(), opt = arguments[1].toLowerCase();
      const groups = Array.from(document.querySelectorAll('form fieldset, form [role=group], form [role=radiogroup], form div'));
      const g = groups.find(x => (x.innerText||'').toLowerCase().includes(qf) &&
                                 x.querySelectorAll('input[type=radio], input[type=checkbox], [role=radio]').length > 0 &&
                                 (x.innerText||'').length < 2000);
      if (!g) return 'NO-GROUP';
      const labs = Array.from(g.querySelectorAll('label, [role=radio], [role=checkbox]'));
      const hit = labs.find(l => (l.innerText||'').trim().toLowerCase() === opt) ||
                  labs.find(l => (l.innerText||'').trim().toLowerCase().startsWith(opt));
      if (!hit) return 'NO-OPTION:' + labs.map(l=>(l.innerText||'').trim()).slice(0,10).join('/');
      hit.scrollIntoView({block:'center'});
      const inp = hit.querySelector('input') || (hit.htmlFor ? document.getElementById(hit.htmlFor) : null);
      (inp || hit).click();
      return 'CLICKED';
    """, question_frag, option_text)
    time.sleep(0.5)
    return res


def verify_snapshot(d):
    return d.execute_script(r"""
      const rep = [];
      document.querySelectorAll('form input:not([type=file]):not([type=radio]):not([type=checkbox]), form textarea').forEach(el => {
        if (el.value) rep.push((el.getAttribute('data-ui')||el.name||el.id||'?') + '=' + el.value.slice(0,60));
      });
      document.querySelectorAll('form input[type=radio]:checked, form input[type=checkbox]:checked').forEach(el => {
        const l = el.closest('label') || document.querySelector('label[for="'+el.id+'"]');
        rep.push('CHECKED:' + (l ? l.innerText.trim().slice(0,60) : el.name || el.id));
      });
      return rep;
    """)


def find_captcha(d):
    """True only for interactive challenge widget, not invisible token."""
    return d.execute_script(r"""
      const f = document.querySelectorAll('iframe[src*="recaptcha/api2/bframe"], iframe[src*="hcaptcha.com"][src*="frame"], .h-captcha iframe, div.g-recaptcha iframe');
      let visible = false;
      f.forEach(x => { const r = x.getBoundingClientRect(); if (r.width > 50 && r.height > 50) visible = true; });
      const chk = document.querySelector('iframe[title*="reCAPTCHA"]');
      if (chk) { const r = chk.getBoundingClientRect(); if (r.width > 50) visible = true; }
      return visible;
    """)


def submit(d):
    btns = d.find_elements(By.CSS_SELECTOR, "button[data-ui='submit-application'], button[type=submit]")
    if not btns:
        btns = [b for b in d.find_elements(By.TAG_NAME, "button") if "submit" in (b.text or "").lower()]
    if not btns:
        return "NO-SUBMIT"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[-1])
    btns[-1].click()
    return "CLICKED"


def success_check(d, wait=8):
    time.sleep(wait)
    body = ""
    try:
        body = d.find_element(By.TAG_NAME, "body").text
    except Exception:
        pass
    low = body.lower()
    ok = ("thank you" in low or "has been submitted" in low or "successfully" in low
          or "application submitted" in low)
    return ok, d.current_url, body[:900]


def submit_and_wait(d, polls=8, step=6):
    """Click submit, then passively poll. Never touches any captcha widget.
    Returns (state, url, body[:900]) with state SUCCESS | TURNSTILE | STUCK."""
    r = submit(d)
    if r != "CLICKED":
        return "NO-SUBMIT", d.current_url, ""
    body = ""
    for _ in range(polls):
        time.sleep(step)
        try:
            body = d.find_element(By.TAG_NAME, "body").text
        except Exception:
            body = ""
        low = body.lower()
        if ("thank you" in low or "has been submitted" in low
                or "successfully" in low or "application submitted" in low):
            return "SUCCESS", d.current_url, body[:900]
        if "verify you are human" in low or "are you human" in low:
            # give managed turnstile a chance to auto-clear, then report
            time.sleep(10)
            try:
                body = d.find_element(By.TAG_NAME, "body").text
            except Exception:
                pass
            low = body.lower()
            if ("thank you" in low or "has been submitted" in low or "successfully" in low):
                return "SUCCESS", d.current_url, body[:900]
            if "verify you are human" in low or "are you human" in low:
                return "TURNSTILE", d.current_url, body[:900]
    return "STUCK", d.current_url, body[:900]


def turnstile_probe(d):
    """Evidence probe: find Cloudflare Turnstile host nodes (shadow DOM hides text)."""
    return d.execute_script(r"""
      const hits = [];
      document.querySelectorAll('iframe').forEach(f => { if (f.src) hits.push('IFRAME:' + f.src.slice(0,120)); });
      document.querySelectorAll('[class*="turnstile"], [id*="turnstile"], [class*="cf-"], [id*="cf-chl"], [data-sitekey]').forEach(e =>
        hits.push('EL:' + e.tagName + '.' + (e.className||'') + '#' + (e.id||'')));
      document.querySelectorAll('*').forEach(e => { if (e.shadowRoot) hits.push('SHADOW-HOST:' + e.tagName + '.' + (e.className||'').toString().slice(0,60)); });
      return hits.slice(0, 20);
    """)


def shot(d, name):
    p = os.path.join(SCRATCH, name)
    d.save_screenshot(p)
    return p
