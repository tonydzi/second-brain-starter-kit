# -*- coding: utf-8 -*-
"""Перепись полей ЖИВОЙ формы: python form_census.py <url> [фрагмент-фильтр]

Зачем: runs/<slug>_dump.json врёт (kind=text при радио-группе, opts=[] при живых опциях, а у Greenhouse
часть вопросов приходит вообще без label — только question_<id>). Истина = живой DOM.

Два прохода:
  1) Ashby-контейнеры (_fieldEntry / ashby-application-form-field-entry);
  2) УНИВЕРСАЛЬНЫЙ обход всех input/select/textarea с поиском подписи (for= / обёртка / ближайший
     предыдущий label|legend) и склейкой радио-групп по атрибуту name. Включается, если первый дал <3 полей.
"""
import sys, os, tempfile, time, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
sys.path.insert(0, r"[путь владельца]")
import firefox_selenium as fs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

url = sys.argv[1]
needle = sys.argv[2].lower() if len(sys.argv) > 2 else None
if "ashbyhq.com" in url and not url.rstrip("/").endswith("application"):
    url = url.rstrip("/") + "/application"

SRC = r"[путь владельца] 1"
prof = fs.clone_profile(SRC, os.path.join(tempfile.gettempdir(), "ff_census_%d" % os.getpid()))
o = Options(); o.add_argument("-headless"); o.add_argument("-profile"); o.add_argument(prof)
d = webdriver.Firefox(options=o); d.set_window_size(1380, 2600)
print("URL:", url)
d.get(url); time.sleep(12)
d.execute_script("window.scrollTo(0, document.body.scrollHeight);"); time.sleep(3)

ASHBY_PASS = r"""
  const entries = Array.from(document.querySelectorAll(
    '[class*="_fieldEntry"], .ashby-application-form-field-entry'));
  return JSON.stringify(entries.map(c => {
    const lab = c.querySelector('label, legend');
    const radios = c.querySelectorAll('input[type=radio]');
    const boxes  = c.querySelectorAll('input[type=checkbox]');
    const sel    = c.querySelectorAll('select');
    const combo  = c.querySelectorAll('[role=combobox]');
    const texts  = c.querySelectorAll('input[type=text], input[type=email], input[type=tel], textarea');
    let widget = 'unknown';
    if (radios.length) widget = 'radio x' + radios.length;
    else if (boxes.length) widget = 'checkbox x' + boxes.length;
    else if (sel.length) widget = 'select';
    else if (combo.length) widget = 'combobox';
    else if (texts.length) widget = texts[0].tagName === 'TEXTAREA' ? 'textarea' : 'text';
    const optLabels = Array.from(c.querySelectorAll('label'))
      .map(l => (l.innerText || '').trim()).filter(t => t && t.length < 140).slice(1, 12);
    return {
      label: lab ? (lab.innerText || '').trim().slice(0, 130) : '(нет label)',
      widget: widget,
      required: !!c.querySelector('[class*="_required"], [aria-required="true"]'),
      opts: optLabels,
    };
  }));
"""

GENERIC_PASS = r"""
  function labelFor(el) {
    if (el.id) {
      const l = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
      if (l && (l.innerText || '').trim()) return l.innerText.trim();
    }
    const wrap = el.closest('label');
    if (wrap && (wrap.innerText || '').trim()) return wrap.innerText.trim();
    const fs = el.closest('fieldset');
    if (fs) {
      const lg = fs.querySelector('legend');
      if (lg && (lg.innerText || '').trim()) return lg.innerText.trim();
    }
    let n = el, hops = 0;
    while (n && hops < 6) {
      let p = n.previousElementSibling;
      while (p) {
        if (/^(LABEL|LEGEND|H2|H3|H4|P|DIV|SPAN)$/.test(p.tagName)) {
          const t = (p.innerText || '').trim();
          if (t && t.length < 220) return t;
        }
        p = p.previousElementSibling;
      }
      n = n.parentElement; hops++;
    }
    return el.name || el.id || '(без подписи)';
  }
  const out = [], seenGroup = {};
  const all = Array.from(document.querySelectorAll('input, select, textarea'));
  for (const el of all) {
    const t = (el.type || '').toLowerCase();
    if (t === 'hidden' || t === 'submit' || t === 'button') continue;
    if (t === 'radio' || t === 'checkbox') {
      const key = el.name || labelFor(el);
      if (seenGroup[key]) continue;
      seenGroup[key] = true;
      const group = Array.from(document.querySelectorAll(
        '[name="' + CSS.escape(el.name || '') + '"]')).filter(x => x.type === t);
      const opts = group.map(g => {
        const l = g.id ? document.querySelector('label[for="' + CSS.escape(g.id) + '"]') : null;
        const w = g.closest('label');
        return ((l && l.innerText) || (w && w.innerText) || '').trim().slice(0, 110);
      }).filter(Boolean);
      out.push({label: labelFor(el).slice(0, 130), widget: t + ' x' + Math.max(group.length, 1),
                required: !!(el.required || el.getAttribute('aria-required') === 'true'), opts: opts.slice(0, 12)});
    } else if (el.tagName === 'SELECT') {
      out.push({label: labelFor(el).slice(0, 130), widget: 'select',
                required: !!(el.required || el.getAttribute('aria-required') === 'true'),
                opts: Array.from(el.options).map(o => (o.text || '').trim()).filter(Boolean).slice(0, 12)});
    } else {
      out.push({label: labelFor(el).slice(0, 130),
                widget: el.tagName === 'TEXTAREA' ? 'textarea' : (t || 'text'),
                required: !!(el.required || el.getAttribute('aria-required') === 'true'), opts: []});
    }
  }
  return JSON.stringify(out);
"""

fields = json.loads(d.execute_script(ASHBY_PASS))
mode = "ashby"
if len(fields) < 3:
    fields = json.loads(d.execute_script(GENERIC_PASS))
    mode = "generic"
print(f"полей: {len(fields)} (проход: {mode})\n")
for f in fields:
    if needle and needle not in f["label"].lower():
        continue
    req = "REQ" if f["required"] else "   "
    print(f"[{req}] {f['widget']:<12} | {f['label']}")
    for o_ in f["opts"]:
        print(f"            · {o_[:110]}")
d.quit()
print("CENSUS-DONE")
