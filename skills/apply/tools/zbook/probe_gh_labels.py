# -*- coding: utf-8 -*-
"""python probe_gh_labels.py <url> — сопоставить question_<id> с ТЕКСТОМ вопроса на Greenhouse.

Зачем: движок отдаёт такие поля как 'question_[id]' (подпись не найдена), и правила по тексту
никогда не срабатывают. Здесь поднимаемся по DOM от самого поля и берём первый осмысленный текст.
"""
import sys, os, tempfile, time, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
sys.path.insert(0, r"[путь владельца]")
import firefox_selenium as fs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

url = sys.argv[1]
SRC = r"[путь владельца] 1"
prof = fs.clone_profile(SRC, os.path.join(tempfile.gettempdir(), "ff_ghlab_%d" % os.getpid()))
o = Options(); o.add_argument("-headless"); o.add_argument("-profile"); o.add_argument(prof)
d = webdriver.Firefox(options=o); d.set_window_size(1380, 2600)
print("URL:", url)
d.get(url); time.sleep(12)
d.execute_script("window.scrollTo(0, document.body.scrollHeight);"); time.sleep(3)

out = d.execute_script(r"""
  const res = [];
  const els = Array.from(document.querySelectorAll('[name^="question_"], [id^="question_"]'));
  const seen = {};
  for (const el of els) {
    const key = el.name || el.id;
    if (seen[key]) continue;
    seen[key] = true;
    let block = el, text = '';
    for (let i = 0; i < 6 && block.parentElement; i++) {
      block = block.parentElement;
      const t = (block.innerText || '').trim();
      if (t.length > 12) { text = t; break; }
    }
    res.push({key: key, tag: el.tagName, type: el.type || '',
              text: text.replace(/\s+/g, ' ').slice(0, 190)});
  }
  return JSON.stringify(res);
""")
for r in json.loads(out):
    print(f"{r['key']:<26} {r['tag']:<9} {r['type']:<9} | {r['text']}")
d.quit()
print("PROBE-DONE")
