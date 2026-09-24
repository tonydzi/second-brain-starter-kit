"""Selenium ATS toolkit for Pipe-A applications on [машина флота] (Chrome extension dead).

Rail: stock Firefox headless via firefox_selenium.make_driver on a fresh temp
profile (ATS forms need no login). Mechanics mirror the apply-playbook, adapted
to selenium's trusted input events:
  - resume file goes FIRST (send_keys to input[type=file]), then ~18s settle
  - text fields: real click + send_keys (React sees trusted key events)
  - react-select combos: click, type full string, pause, click the option
  - JS verify before submit; submit only via --submit
"""
from __future__ import annotations

import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/.claude/scripts/_shared"))
from firefox_selenium import make_driver  # noqa: E402

from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.common.keys import Keys  # noqa: E402


def new_driver(headless=True):
    if os.environ.get("ATS_HEADED"):
        headless = False
    import tempfile
    prof = tempfile.mkdtemp(prefix="ff_ats_")  # unique per process: shared ff_auto_profile deadlocks parallel agents
    d = make_driver(profile=prof, headless=headless)
    d.set_window_size(1380, 2000)
    return d


def dump_ashby(d):
    """Inventory of Ashby form fields: label, kind, required, options."""
    return d.execute_script(r"""
      const out = [];
      const entries = document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry');
      const seen = new Set();
      const containers = entries.length ? entries : document.querySelectorAll('form label');
      containers.forEach((c) => {
        const labEl = c.querySelector('label') || c;
        let label = (labEl.innerText || labEl.textContent || '').trim().split('\n')[0];
        if (!label || seen.has(label)) return;
        seen.add(label);
        const kind =
          c.querySelector('input[type=file]') ? 'file' :
          c.querySelector('textarea') ? 'textarea' :
          c.querySelector('input[role=combobox], [class*="select"] input') ? 'combo' :
          c.querySelector('button[role=radio], [role=radiogroup]') ? 'radio' :
          c.querySelector('input[type=checkbox]') ? 'checkbox' :
          (Array.from(c.querySelectorAll('button')).some(b => /^(yes|no)$/i.test(b.innerText.trim()))) ? 'yesno' :
          c.querySelector('input') ? 'text' : 'other';
        const required = /\*/.test((c.innerText || '').split('\n')[0]) ||
                         !!c.querySelector('[aria-required="true"], [required]');
        const opts = Array.from(c.querySelectorAll('button[role=radio], [role=option], label'))
          .map(o => o.innerText.trim()).filter(t => t && t.length < 80).slice(0, 12);
        out.push({label, kind, required, opts});
      });
      return out;
    """)


def _entry_by_label(d, label):
    els = d.execute_script(r"""
      const want = arguments[0].toLowerCase();
      const entries = Array.from(document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry'));
      const hit = entries.find(c => {
        const l = c.querySelector('label');
        return l && l.innerText.trim().toLowerCase().startsWith(want);
      });
      return hit ? [hit] : [];
    """, label)
    return els[0] if els else None


def fill_text(d, label, value):
    c = _entry_by_label(d, label)
    if c is None:
        return f"NO-FIELD:{label}"
    inp = c.find_elements(By.CSS_SELECTOR, "textarea") or c.find_elements(By.CSS_SELECTOR, "input")
    if not inp:
        return f"NO-INPUT:{label}"
    el = inp[0]
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click(); time.sleep(0.3)
    el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE)
    el.send_keys(value); time.sleep(0.4)
    got = el.get_attribute("value") if el.tag_name == "input" else el.get_attribute("value")
    return "OK" if (got or "").strip() == value.strip() else f"MISMATCH:{label}:got={got!r}"


def fill_combo(d, label, value, click_option=True):
    c = _entry_by_label(d, label)
    if c is None:
        return f"NO-FIELD:{label}"
    inp = c.find_elements(By.CSS_SELECTOR, "input")
    if not inp:
        return f"NO-INPUT:{label}"
    el = inp[0]
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click(); time.sleep(0.5)
    el.send_keys(value); time.sleep(1.5)
    if click_option:
        opts = d.find_elements(By.CSS_SELECTOR, "[role='option'], [class*='option']")
        target = None
        vl = value.lower()
        for o in opts:
            if (o.text or "").lower().startswith(vl):
                target = o; break
        if target is None:
            for o in opts:
                if vl in (o.text or "").lower():
                    target = o; break
        if target is None and opts:
            target = opts[0]
        if target is None:
            return f"NO-OPTION:{label}:{value}"
        target.click(); time.sleep(0.5)
    return "OK"


def click_yesno(d, label, yes: bool):
    c = _entry_by_label(d, label)
    if c is None:
        return f"NO-FIELD:{label}"
    want = "yes" if yes else "no"
    for b in c.find_elements(By.CSS_SELECTOR, "button"):
        if (b.text or "").strip().lower() == want:
            d.execute_script("arguments[0].scrollIntoView({block:'center'});", b)
            b.click(); time.sleep(0.4)
            return "OK"
    return f"NO-BUTTON:{label}:{want}"


def upload_resume(d, path, settle=18, field="_systemfield_resume"):
    """Прикрепить резюме ИМЕННО в поле резюме.

    ⚠️ Класс «заявка ушла без CV» (замер 04.09, волна 22): раньше при отсутствии
    именованного поля код слепо брал ПЕРВЫЙ input[type=file] на странице — а первым
    на новых формах Ashby идёт виджет «Autofill from resume». Файл уезжал в автозаполнение,
    настоящее поле оставалось пустым, и форма молча отправлялась без резюме (PermitFlow).
    Теперь: именованное поле → поле, чей лейбл говорит resume/cv (кроме автофилла) →
    честный отказ. Слепого фолбэка на первый инпут БОЛЬШЕ НЕТ.
    """
    inp = d.find_elements(By.CSS_SELECTOR, f"input[type=file][name='{field}']")
    if not inp:
        # ищем file-input внутри поля с лейблом про резюме, пропуская автофилл-виджет
        inp = d.execute_script("""
          const bad = /autofill|parse|import/i;
          const boxes = Array.from(document.querySelectorAll(
            '[class*="_fieldEntry"], .ashby-application-form-field-entry, [data-testid*="field"]'));
          for (const b of boxes) {
            const f = b.querySelector('input[type=file]');
            if (!f) continue;
            const txt = ((b.querySelector('label') || {}).innerText || b.innerText || '');
            if (bad.test(txt)) continue;
            if (/resume|cv\b|curriculum/i.test(txt)) return [f];
          }
          return [];
        """) or []
    if not inp:
        return ("RESUME-FIELD-NOT-FOUND (единственный file-input на странице — виджет автозаполнения; "
                "слепо туда НЕ грузим: форма уйдёт без резюме)")
    inp[0].send_keys(path)
    time.sleep(settle)
    fname = path.rsplit("/", 1)[-1]
    txt = d.execute_script("""
      const c = Array.from(document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry'))
        .find(x => x.querySelector('input[type=file]') && /resume/i.test((x.querySelector('label')||{}).innerText || x.innerText));
      return c ? c.innerText : document.body.innerText.slice(0, 500);
    """)
    return "OK" if fname in (txt or "") else f"CHIP-MISSING:{fname}"


def verify_all(d):
    return d.execute_script(r"""
      const rep = [];
      document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry').forEach(c => {
        const l = c.querySelector('label');
        if (!l) return;
        const label = l.innerText.trim().split('\n')[0];
        const inp = c.querySelector('textarea') || c.querySelector('input:not([type=file])');
        const file = c.querySelector('input[type=file]');
        let val = inp ? inp.value : '';
        if (inp && inp.type === 'checkbox') val = 'checked=' + inp.checked;
        if (file) {
          const m = (c.innerText || '').match(/\S+\.(pdf|docx?|txt)/i);
          val = m ? ('FILE:' + m[0]) : 'NO-FILE';
        }
        const pressed = Array.from(c.querySelectorAll('button[aria-pressed="true"], [aria-checked="true"]'))
          .map(b => b.innerText.trim()).join('|');
        rep.push({label, value: val, pressed});
      });
      return rep;
    """)


def submit(d):
    btns = d.find_elements(By.XPATH, "//button[contains(., 'Submit') or contains(., 'Apply')]")
    if not btns:
        return "NO-SUBMIT-BUTTON"
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[-1])
    btns[-1].click()
    return "CLICKED"


def select_option_in_entry(d, entry_label, option_text):
    """Click the option (label/button/radio) whose text matches inside a field entry.
    Works for checkbox-lists, radio-lists and yes/no button groups. Verifies state."""
    res = d.execute_script(r"""
      const want = arguments[0].toLowerCase(), opt = arguments[1].toLowerCase();
      const entries = Array.from(document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry'));
      const c = entries.find(x => {
        const l = x.querySelector('label');
        return l && l.innerText.trim().toLowerCase().startsWith(want);
      });
      if (!c) return 'NO-FIELD';
      const cands = Array.from(c.querySelectorAll('label, button[role=radio], button, [role=option]'));
      const hit = cands.find(el => (el.innerText || '').trim().toLowerCase() === opt) ||
                  cands.find(el => (el.innerText || '').trim().toLowerCase().startsWith(opt));
      if (!hit) return 'NO-OPTION';
      hit.scrollIntoView({block:'center'});
      const inp = hit.querySelector('input') ||
                  (hit.htmlFor ? document.getElementById(hit.htmlFor) : null);
      (inp || hit).click();
      return 'CLICKED';
    """, entry_label, option_text)
    if res != "CLICKED":
        return f"{res}:{entry_label}:{option_text}"
    time.sleep(0.6)
    state = d.execute_script(r"""
      const want = arguments[0].toLowerCase(), opt = arguments[1].toLowerCase();
      const entries = Array.from(document.querySelectorAll('[class*="_fieldEntry"], .ashby-application-form-field-entry'));
      const c = entries.find(x => {
        const l = x.querySelector('label');
        return l && l.innerText.trim().toLowerCase().startsWith(want);
      });
      if (!c) return 'NO-FIELD';
      const on = [];
      c.querySelectorAll('input:checked').forEach(i => {
        const l = i.closest('label') || c.querySelector('label[for="'+i.id+'"]');
        on.push(l ? l.innerText.trim() : 'checked');
      });
      c.querySelectorAll('[aria-pressed="true"], [aria-checked="true"]').forEach(b =>
        on.push((b.innerText || '').trim()));
      return on.join('|');
    """, entry_label, option_text)
    return "OK:" + str(state) if option_text.lower() in str(state).lower() else f"UNVERIFIED:{entry_label}:state={state}"


def page_text(d, limit=1200):
    try:
        return d.find_element(By.TAG_NAME, "body").text[:limit]
    except Exception as e:
        return f"ERR:{e}"


def click_checkbox(d, label, want=True):
    c = _entry_by_label(d, label)
    if c is None:
        return f"NO-FIELD:{label}"
    boxes = c.find_elements(By.CSS_SELECTOR, "input[type=checkbox]")
    if not boxes:
        return f"NO-CHECKBOX:{label}"
    el = boxes[0]
    cur = d.execute_script("return arguments[0].checked;", el)
    if cur != want:
        d.execute_script("arguments[0].click();", el)
        time.sleep(0.4)
    got = d.execute_script("return arguments[0].checked;", el)
    return "OK" if got == want else f"TOGGLE-FAIL:{label}"
