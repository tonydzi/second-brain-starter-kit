# -*- coding: utf-8 -*-
"""python probe_gh_options.py <url> [фрагмент_лейбла ...] — раскрыть react-select'ы Greenhouse и напечатать
их ОПЦИИ (дамп движка опций у combo не несёт, а строгий combo без совпадения жмёт первую попавшуюся).
0 LLM. Печатает: question_<id> | лейбл | [опции]."""
import sys, time, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
from selenium.webdriver.common.by import By
from ats_lib import new_driver
url = sys.argv[1]
want = [w.lower() for w in sys.argv[2:]]
d = new_driver(headless=True)
try:
    d.get(url); time.sleep(6)
    # job-boards: форма на той же странице; embed — сразу форма
    boxes = d.find_elements(By.CSS_SELECTOR, "input[id^='question_'][role='combobox'], div[id^='question_'] input[role='combobox']")
    print("combobox-ов:", len(boxes))
    for b in boxes:
        bid = b.get_attribute("id") or ""
        lab = ""
        try:
            lab = d.find_element(By.CSS_SELECTOR, f"label[for='{bid}']").text.strip()
        except Exception:
            try:
                lab = b.find_element(By.XPATH, "ancestor::*[label][1]/label").text.strip()
            except Exception:
                pass
        if want and not any(w in lab.lower() for w in want):
            continue
        try:
            d.execute_script("arguments[0].scrollIntoView({block:'center'});", b)
            b.click(); time.sleep(1.2)
            opts = [o.text.strip() for o in d.find_elements(By.CSS_SELECTOR, "[role='option']") if o.text.strip()]
            d.find_element(By.TAG_NAME, "body").send_keys("\ue00c")  # Escape
        except Exception as e:
            opts = [f"ERR {type(e).__name__}"]
        print(f"{bid} | {lab[:110]} | {opts[:25]}")
    print("PROBE-DONE")
finally:
    d.quit()
