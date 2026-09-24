# -*- coding: utf-8 -*-
"""One Pipe-A application on ZBOOKG8: hub's auto_apply with the laptop's proven driver
(cookie-rich cloned profile; HEADED=1 env forces a visible window for spam-flag retries)."""
import sys, os, tempfile
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
sys.path.insert(0, r"[путь владельца]")
import firefox_selenium as fs
import ats_lib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

SRC = r"[путь владельца] 1"

def new_driver(headless=True):
    prof = fs.clone_profile(SRC, os.path.join(tempfile.gettempdir(), "ff_slice_%d" % os.getpid()))
    o = Options()
    if os.environ.get("HEADED") != "1":
        o.add_argument("-headless")
    o.add_argument("-profile"); o.add_argument(prof)
    d = webdriver.Firefox(options=o)
    d.set_window_size(1380, 2000)
    return d

ats_lib.new_driver = new_driver

# per-entry answer overrides: entry.json may carry "extra": {label_regex: {"section": "text|combo|yesno", "value": ...}}
import json as _json, re as _re
import answers_canon as _A
_entry = _json.load(open(sys.argv[1], encoding="utf-8"))
_EXTRA = _entry.get("extra") or {}
# универсальные правды — закрывают частые miss-классы на ЛЮБОЙ форме (после entry-extra, до канона)
_DEFAULT_EXTRA = {
    r"how many years of (industry |professional |work |relevant )?experience": {"section": "option", "value": ["15", "More than 10", "10+"]},
    r"are you (currently )?located in the (US|United States)": {"section": "combo", "value": ["Yes", "US"]},
    r"located in the bay area": {"section": "yesno", "value": True},
    r"role applying for|position applying": {"section": "text", "value": _entry.get("title", "")[:80]},
    r"worked in B2B Saas": {"section": "yesno", "value": True},
    r"years of working full.time in a technical": {"section": "yesno", "value": True},
    r"experience working in a fast.paced": {"section": "yesno", "value": True},
    r"willing to work from the required location": {"section": "yesno", "value": True},
    r"native or C2.level in\s+German": {"section": "yesno", "value": False},
    r"year of outbound": {"section": "yesno", "value": True},
    r"AI.native (products?|systems?)": {"section": "text", "value": "A production multi-agent Claude fleet across six machines: durable state-machine orchestration, an approval-gate permission layer (published eval: 0/17 high-risk actions slipped through), a shared machine bus, self-healing sync watchdogs, and a content pipeline that turns the fleet's own failure modes into published field guides. All of it runs daily in production and is documented in public."},
    # ⚠️ порядок важен: «готов ли работать оттуда» = ДА (релокация открыта), и только «где живёшь СЕЙЧАС» = НЕТ.
    # Замер Paxos: вопрос «position is hybrid in New York — able to work from this location?» ловился
    # правилом про NYC и получал «No — I'm unable», то есть робот сам себя снимал с вакансии.
    r"able to work from this location|position is (hybrid|based|onsite)|willing to (relocate|work from)|open to relocat|report to the designated office|can you report to|come in(to)? the office|work from the office|onsite requirement": {"section": "option", "value": ["willing to relocate", "Yes - I'm willing", "I'm able", "I am able", "Yes"]},
    r"identity verification|background check|right to work check": {"section": "checkbox", "value": True},
    # GDPR-хвост Greenhouse: точка передачи данных = где кандидат физически (Пало-Алто) + согласие с политикой
    r"Point of Data Transfer": {"section": "combo", "value": ["United States", "United States of America", "US", "North America"]},
    # правда: Антон не гражданин США (виза O-1) и допуска гостайны не имеет
    r"U\.?S\.? Citizen|United States Citizen": {"section": "combo", "value": ["No"]},
    r"TS/SCI|security clearance|active clearance|government clearance": {"section": "combo", "value": ["No"]},
    # Антон не пишет код сам — честно ставим низкий уровень; варианты перебираются по порядку
    r"classify your experience developing in|experience (developing|coding|programming) in |proficiency (in|with) (Python|JavaScript|SQL)": {"section": "option", "value": ["Beginner", "Basic", "Novice", "Limited", "Some experience", "None"]},
    r"personal information as part of the recruitment|Privacy (Notice|Policy)|privacy notice|data protection notice|consent to (the )?(processing|storage)|gdpr": {"section": "checkbox", "value": True},
    r"commuting distance of NYC|based in or around the New York City|currently located in (London|New York)|do you currently (live|reside) in": {"section": "yesno", "value": False},
    r"work permit.visa support|visa support to work": {"section": "yesno", "value": False},
    r"visa sponsorship": {"section": "yesno", "value": False},
    r"worked in the web3.blockchain.crypto space": {"section": "yesno", "value": True},
    r"proof of authorization to work": {"section": "yesno", "value": True},
    r"current employee.{0,30}employee number": {"section": "text", "value": "N/A - not a current employee"},
    r"happy 4 days office": {"section": "yesno", "value": True},
    r"proficient in financial modeling": {"section": "yesno", "value": True},
    r"2 years with the same company": {"section": "yesno", "value": True},
    r"worked in a startup or built products": {"section": "yesno", "value": True},
    r"legally allowed to work": {"section": "yesno", "value": True},
    r"legally eligible to work": {"section": "yesno", "value": True},
    r"Sponsorship Requirement": {"section": "combo", "value": ["No", "Not required"]},
    r"in.office at our|days/week in.office|days a week in.office|commit to 3 days": {"section": "combo", "value": ["Yes"]},
    r"first-degree relatives|relatives .{0,30}(employed|currently work)": {"section": "combo", "value": ["No"]},
    r"ever worked at .{0,30}(or any of it|subsidiaries)|previously (worked|been employed) (at|by)": {"section": "combo", "value": ["No"]},
    r"salary requirements": {"section": "text", "value": "180000"},
    r"need a visa . work permit|would you need a visa": {"section": "text", "value": "No - I hold an active O-1 visa in the US and an EU (Polish) passport, so I need no sponsorship in the US or the EU."},
    r"three factors that matter most": {"section": "option", "value": ["Hands-on work with AI", "Meaningful professional challenges", "Global company with enterprise customers"]},
    r"familiar with .{0,20} before applying|heard of us before": {"section": "option", "value": ["Yes"]},
    r"language do you want us to communicate|preferred language|language of communication": {"section": "combo", "value": ["English"]},
    r"fluent German speaker|fluent in German": {"section": "combo", "value": ["No"]},
    r"able to travel|willing to travel|travel to client|travel requirement": {"section": "option", "value": ["Yes"]},
    r"target compensation|desired compensation": {"section": "text", "value": "180000"},
    r"consider you for other|other roles at|other opportunities at|future openings": {"section": "option", "value": ["Yes"]},
    # O-1 активна: право работать в США есть, спонсорство не нужно. «authorized» не ловилось ничем — Neon упал.
    r"legally authorized to work|authoriz\w+ to work in the (United States|US|U\.S\.)|work authorization status": {"section": "yesno", "value": True},
    r"commit to (that|this) schedule": {"section": "yesno", "value": True},
    r"favorite tools for prospecting": {"section": "text", "value": "I mostly build my own: a Telegram-native CRM with drip campaigns and budget-capped send rails, GitHub mining for sourcing engineers, IMAP-driven sequencing - outbound as code, run by AI agents I operate in production. Comfortable with the standard stack (Apollo-style enrichment, LinkedIn alternatives) on top."},
    r"experience in the core competencies": {"section": "yesno", "value": True},
    r"three days in the office|hybrid working model": {"section": "yesno", "value": True},
    r"(CV|application form).{0,40}in English": {"section": "yesno", "value": True},
    r"^Gender\b|^Race\b|^Ethnicity": {"section": "combo", "value": ["Decline", "I don't wish", "Prefer not"]},
    r"gender identity|identify as transgender|sexual orientation|ethnicit(y|ies).{0,25}identify|identify with\?": {"section": "option", "value": ["I prefer not to answer", "Prefer not", "Decline", "I don't wish"]},
    r"^Veteran Status": {"section": "combo", "value": ["I am not", "not a protected veteran", "No"]},
    r"Disability Status|disability": {"section": "option", "value": ["I do not want to answer", "I don't wish to answer", "do not wish", "Decline", "Prefer not"]},
    r"^Why you|why should we hire|why are you the right|why do you want to (work|join)|why this (role|company)": {"section": "text", "value": "I have spent fifteen years building companies rather than working inside them - eleven of those running a venture incubator in APAC, where I sourced the deals, negotiated the terms, and stayed accountable for the outcome rather than the handshake. In 2018 I worked with banks and government stakeholders across Southeast Asia on the frameworks for their first stablecoins. Today I run an AI lab whose multi-agent fleet does real operational work in production - sourcing, first-touch outreach under budget-capped rails, CRM hygiene, a daily engineering log - and I publish the failures next to the wins. That combination is what I bring: a founder who owns the result, and someone genuinely fluent with agents running in production rather than in a demo."},
    r"deadlines we should be aware": {"section": "text", "value": "No hard deadlines - I can move at your pace"},
    r"personal pronouns|^Pronouns\b": {"section": "combo", "value": ["He/him", "he/him", "He/Him"]},
    r"full legal name in native": {"section": "text", "value": "Антон Дзятковский"},
    r"full legal name": {"section": "text", "value": "Anton Dziatkovskii"},
    r"(current|most recent).{0,15}title": {"section": "text", "value": "Founder & CEO"},
    r"deemed export": {"section": "combo", "value": ["Yes"]},
    r"linkedin": {"section": "text", "value": "https://tonydzi.github.io/"},
    r"^City\b": {"section": "text", "value": "Palo Alto"},
    r"^State\b": {"section": "combo", "value": ["California"]},
    r"ideal start.?date": {"section": "text", "value": "10/01/2026"},
    r"availab\w* to start|earliest start|notice period|start a new role|timeline for potential start": {"section": "text", "value": "Immediately available, flexible on start date"},
    r"zip code|postal code": {"section": "text", "value": "94301"},
    r"salary expectation|desired (annual )?salary|minimum annual (cash )?salary|compensation expectation|expected (base )?salary|on target earnings|\bOTE\b": {"section": "text", "value": "180000"},
    r"what exceptional work|pushed for excellence|most proud of|greatest (professional )?achievement|most impressive (thing|work|project|accomplishment)|impressive accomplishment": {"section": "text", "value": "I run a production multi-agent Claude fleet across six machines - and I run it in public: published evals (including an approval-gate eval where 0/17 high-risk actions slipped past the permission gate), documented failure modes, and an operating manual written day by day. Before that: eleven years running a venture incubator in APAC - deal flow, cohorts, fundraising end-to-end - and in 2018 I worked with banks and government stakeholders across Southeast Asia on frameworks for their first stablecoins. The common thread: I ship the thing AND write the field guide for it."},
}
# ⛔ ПЕРЕХВАТЧИК: истины об Антоне, которые per-role файлы (их пишут агенты) НЕ имеют права переопределять.
# Замер Paxos 03.09: агентский extra нёс правило про NYC со значением False, оно матчилось на вопрос
# «position is hybrid in NYC — able to work from this location?» и робот отвечал «No - unable»,
# то есть САМ СНИМАЛ Антона с вакансии. Проверяется ПЕРЕД _EXTRA.
_OVERRIDE = {
    r"able to work from this location|position is (hybrid|based|onsite)|report to the designated office|can you report to|come in(to)? the office|work from the office": {"section": "option", "value": ["willing to relocate", "Yes - I am willing", "I am able", "I(.)m able", "Yes"]},
    r"open to relocat|willing to relocat": {"section": "option", "value": ["Yes", "willing to relocate"]},
    # 08.09 Robinhood: опции Yes/No, а общий override давал 4 кандидата без «Yes» (кап _strict_gh_combo[:4]);
    # более длинное совпадение «willing to work from the office» бьёт общий «work from the office»
    r"willing to work from the office|willing to work (on-?site|in the office)": {"section": "option", "value": ["Yes", "Yes - I am willing", "I am able", "willing"]},
}

# поля вида «select the three…» / «select all that apply»: движок кликает ОДИН вариант и уходит,
# форма остаётся незаполненной (замер NICE 03.09). Здесь копим остальные значения на дожатие.
_MULTI = {}
_MULTI_RX = _re.compile(r"select (the )?(three|two|up to|all that apply)|mark all that apply|select all", _re.I)

_orig_map = _A.map_label
_ASHBY_ONLY = {
    r"how did you hear about": {"section": "option", "value": ["Other", "Google", "Job board", "Website", "Search"]},
}
def _patched(label, kind, required, opts, eu_role=False):
    if _entry.get("ats") == "ashby":
        for rx, sp in _ASHBY_ONLY.items():
            if _re.search(rx, label or "", _re.I):
                real_opts = [o for o in (opts or []) if o and o != label]
                if kind in ("text", "textarea"):
                    if real_opts:  # радио-группа под видом text (EF-класс): кликаем правдивую опцию
                        cands = ["External Job Board", "Job board", "Website", "Other", "Google", "Search"]
                        pick = next((o for o in real_opts for v in cands if v.lower() in o.lower()), real_opts[-1])
                        return ("option", [pick])
                    return ("text", "Google search / your public job board")
                if kind == "combo":
                    return ("combo", ["Other", "Google", "LinkedIn", "Twitter", "Word of mouth"])
                return (sp["section"], sp["value"])
    for source in (_OVERRIDE, _EXTRA, _DEFAULT_EXTRA):
        # ⚠️ побеждает САМОЕ ДЛИННОЕ совпадение, а не первое: агенты пишут широкие ключи вроде
        # (acknowledge|consent|agree|certify|confirm), и «agree» внутри «disagree» перехватывал
        # чужой вопрос (замер Ashby SE Manager 03.09 — два круга дожима били мимо).
        if _re.fullmatch(r"question_[0-9]+", (label or "").strip()):
            # подпись = голый номер Greenhouse: матчится ТОЛЬКО точным ключом по номеру. Иначе широкий
            # агентский ключ со словом «question» побеждает по длине (замер Elastic 03.09: в графу
            # про санкционные страны уехало эссе про эмбеддинги).
            matches = [(rx, sp) for rx, sp in source.items() if rx == (label or "").strip()]
        else:
            matches = []
            for rx, sp in source.items():
                m = _re.search(rx, label or "", _re.I)
                if m:
                    matches.append((rx, sp, m))
        if matches:
            # ранжируем по длине СОВПАВШЕГО ТЕКСТА, не шаблона: ключ AI|ML|LLM|RAG (38 симв.) ловил «ai»
            # внутри «Ukrainian» (2 симв.) и по длине шаблона побеждал «Belarus, [человек], Iran…» (32 симв.
            # совпавшего текста). Замер Elastic 04.09, пять кругов дожима в одно поле.
            rx, sp, _m = max(matches, key=lambda kv: len(kv[2].group(0)))
            if True:
                sec, val = sp["section"], sp["value"]
                if sec == "yesno" and kind in ("text", "textarea"):
                    real_opts = [o for o in (opts or []) if o and o != label]
                    if real_opts:  # yes/no-вопрос, но виджет = радио-группа (n8n startup-класс)
                        want = "yes" if val else "no"
                        pick = next((o for o in real_opts if o.lower().startswith(want)),
                                    real_opts[0] if val else real_opts[-1])
                        return ("option", [pick])
                if sec == "option" and isinstance(val, list) and len(val) > 1 and _MULTI_RX.search(label or ""):
                    _MULTI[label] = list(val)
                if sec in ("combo", "option") and kind in ("text", "textarea"):
                    real_opts = [o for o in (opts or []) if o and o != label]
                    if real_opts:  # radio-группа под видом text (Rain-класс) — кликаем опцию
                        vl = val if isinstance(val, list) else [val]
                        pick = next((o for o in real_opts for v in vl if str(v).lower() in o.lower()), real_opts[0])
                        return ("option", [pick])
                    if sec == "option":
                        # явный option при ПУСТЫХ opts: дамп не увидел радио, а в живом DOM оно есть
                        # (Legion work-auth). Деградация в text давала MISMATCH:got='on' — радио уже нажато.
                        return ("option", val if isinstance(val, list) else [val])
                    return ("text", val[0] if isinstance(val, list) else str(val))
                return (sec, val)
    return _orig_map(label, kind, required, opts, eu_role=eu_role)
_A.map_label = _patched

# gh_combo verify лжёт: сниппет ищется в innerText бокса, а бокс содержит сам ВОПРОС
# («US» матчится об «Are you located in the US or London?») — OK при пустом поле.
# Строгая версия: критерий успеха ТОТ ЖЕ, что у приёмки EMPTY-REQUIRED
# (el.value непустой ИЛИ placeholder «Select...» ушёл из бокса).
import gh_lib as _G
import time as _t
from selenium.webdriver.common.by import By as _By
from selenium.webdriver.common.keys import Keys as _K

def _committed(d, qid):
    return d.execute_script("""
      const el = document.getElementById(arguments[0]);
      if (!el) return 'NO-EL';
      if ((el.value||'') !== '') return 'VAL';
      const box = el.closest('div[class*="field"], div[class*="Field"], fieldset') || el.parentElement.parentElement;
      return (box.innerText||'').includes('Select...') ? '' : 'TXT';
    """, qid)

def _strict_gh_combo(d, qid, candidates, verify_snippets=None):
    if isinstance(candidates, str):
        candidates = [candidates]
    candidates = candidates[:4]  # длинный веер кандидатов на чужом поле = минуты впустую
    try:
        el = d.find_element(_By.ID, qid)
    except Exception:
        return f"NO-EL:{qid}"
    for cand in candidates:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try: el.click()
        except Exception: d.execute_script("arguments[0].focus(); arguments[0].click && arguments[0].click();", el)
        _t.sleep(0.6)
        el.send_keys(_G.MOD, "a"); el.send_keys(_K.DELETE)
        el.send_keys(cand)
        # асинхронные пикеры (location) рисуют опции с задержкой — ждём их до 7с
        opts = []
        for _ in range(5):
            _t.sleep(0.6)
            opts = [o for o in d.find_elements(_By.CSS_SELECTOR, "[role='option'], [id*='-option-']") if o.is_displayed()]
            if opts:
                break
        # exact > contains; JS-клик надёжнее Selenium-клика по порталу
        tgt = next((o for o in opts if (o.text or "").strip().lower() == cand.lower()), None) \
              or next((o for o in opts if cand.lower() in (o.text or "").lower()), None)
        if tgt is not None:
            d.execute_script("arguments[0].click();", tgt)
        else:
            el.send_keys(_K.ARROW_DOWN); _t.sleep(0.4); el.send_keys(_K.ENTER)
            _t.sleep(0.4)
            el.send_keys(_K.TAB)  # blur только в клавиатурной ветке: пикер стирает незакоммиченный typed-text
        ok = None
        for _ in range(5):
            _t.sleep(0.7)
            st = _committed(d, qid)
            if st in ("VAL", "TXT"):
                ok = st; break
        if ok:
            return f"OK:{cand}({ok})"
        try: el.send_keys(_K.ESCAPE)  # ESCAPE только при провале — после успеха он способен откатить выбор
        except Exception: pass
        _t.sleep(0.3)
    return f"NO-COMMIT:{qid}:tried={candidates}"

_G.gh_combo = _strict_gh_combo

# та же болезнь на ashby: fill_combo кликает опцию и рапортует OK без проверки коммита
# (async location-пикер: клик по устаревшей/пустой опции -> value пустой -> форма валится на submit)
_orig_fill_combo = ats_lib.fill_combo
def _strict_fill_combo(d, label, value, click_option=True):
    r = _orig_fill_combo(d, label, value, click_option=click_option)
    try:
        c = ats_lib._entry_by_label(d, label)
        inp = c.find_elements(ats_lib.By.CSS_SELECTOR, "input") if c is not None else []
        if inp and not (inp[0].get_attribute("value") or ""):
            el = inp[0]
            el.click(); _t.sleep(0.5)
            el.send_keys(value)
            opts = []
            for _ in range(10):  # async-пикеры (Google Places) дают опции с долгим дебаунсом
                _t.sleep(0.6)
                opts = [o for o in d.find_elements(ats_lib.By.CSS_SELECTOR, "[role='option'], [class*='option']") if o.is_displayed()]
                if opts:
                    break
            if opts:
                tgt = next((o for o in opts if value.lower() in (o.text or "").lower()), None)
                if tgt is not None:  # клик только по СОВПАВШЕЙ опции; opts[0] «в молоко» давал ложный OK (n8n location)
                    d.execute_script("arguments[0].click();", tgt); _t.sleep(0.6)
                else:
                    el.send_keys(_K.ARROW_DOWN); _t.sleep(0.4); el.send_keys(_K.ENTER); _t.sleep(0.6)
            else:
                el.send_keys(_K.ARROW_DOWN); _t.sleep(0.4); el.send_keys(_K.ENTER); _t.sleep(0.6)
                el.send_keys(_K.TAB); _t.sleep(0.6)
            got = el.get_attribute("value") or ""
            return f"{r}|strict:{'OK:'+got[:30] if got else 'STILL-EMPTY'}"
    except Exception as e:
        return f"{r}|strict-exc:{type(e).__name__}"
    return r
ats_lib.fill_combo = _strict_fill_combo

# ashby yes/no: click_yesno кликает кнопку, а aria-pressed не встаёт (verify честно бьёт missing)
_orig_click_yesno = ats_lib.click_yesno
def _strict_click_yesno(d, label, yes):
    r = _orig_click_yesno(d, label, yes)
    try:
        c = ats_lib._entry_by_label(d, label)
        if c is None:
            return r
        want = "yes" if yes else "no"
        ok = d.execute_script("""
          const c = arguments[0], want = arguments[1];
          const pressed = c.querySelector('button[aria-pressed="true"], [aria-checked="true"]');
          if (pressed && pressed.innerText.trim().toLowerCase().startsWith(want)) return 'PRESSED';
          for (const b of c.querySelectorAll('button')) {
            if (b.innerText.trim().toLowerCase() === want) { b.click(); return 'JS-CLICKED'; }
          }
          return 'NO-BTN';
        """, c, want)
        if ok == 'JS-CLICKED':
            _t.sleep(0.4)
            ok2 = d.execute_script("""
              const c = arguments[0];
              const p = c.querySelector('button[aria-pressed="true"], [aria-checked="true"]');
              return p ? 'PRESSED' : 'STILL-OFF';
            """, c)
            return f"{r}|strict:{ok}->{ok2}"
        return f"{r}|strict:{ok}"
    except Exception as e:
        return f"{r}|strict-exc:{type(e).__name__}"
ats_lib.click_yesno = _strict_click_yesno

# дропдауны ashby: опции живут в ПОРТАЛЕ вне контейнера — select_option_in_entry их не видит.
# NO-OPTION -> открыть контрол и кликнуть подходящую (или первую) опцию из document.
_orig_soie = ats_lib.select_option_in_entry
def _strict_soie(d, entry_label, option_text):
    r = _orig_soie(d, entry_label, option_text)
    if entry_label in _MULTI:   # многовыборное поле: дожимаем остальные варианты тем же кликом по подстроке
        rest = [v for v in _MULTI.get(entry_label, []) if v.lower() != str(option_text).lower()]
        done = []
        try:
            c0 = ats_lib._entry_by_label(d, entry_label)
            for v in rest:
                got = d.execute_script("""
                  const c = arguments[0], opt = arguments[1].toLowerCase();
                  const cands = Array.from(c.querySelectorAll('label, button[role=radio], [role=option], [role=checkbox]'));
                  const hit = cands.find(el => (el.innerText || '').toLowerCase().includes(opt));
                  if (!hit) return null;
                  const inp = hit.querySelector('input') || (hit.htmlFor ? document.getElementById(hit.htmlFor) : null);
                  if (inp && inp.checked) return 'ALREADY';
                  hit.scrollIntoView({block:'center'});
                  (inp || hit).click();
                  return (inp ? (inp.checked ? 'ON' : 'OFF') : 'CLICKED');
                """, c0, v)
                if got:
                    done.append(v[:18] + ':' + got)
                _t.sleep(0.3)
        except Exception as e:
            done.append('exc:' + type(e).__name__)
        if done:
            r = str(r) + '|multi:' + ','.join(done)

    if not str(r).startswith("NO-OPTION"):
        return r
    try:
        c = ats_lib._entry_by_label(d, entry_label)
        if c is None:
            return r
        # нативный <select>: опции скрыты, портал не откроется — ставим value + change
        nat = d.execute_script("""
          const sel = arguments[0].querySelector('select');
          if (!sel) return null;
          const want = arguments[1].toLowerCase();
          let hit = [...sel.options].find(o => o.text.trim().toLowerCase() === want) ||
                    [...sel.options].find(o => o.text.toLowerCase().includes(want)) ||
                    [...sel.options].find(o => o.value && !/select|choose/i.test(o.text));
          if (!hit) return 'SELECT-NO-OPT';
          sel.value = hit.value;
          sel.dispatchEvent(new Event('input', {bubbles: true}));
          sel.dispatchEvent(new Event('change', {bubbles: true}));
          return 'SELECT-SET:' + hit.text.slice(0, 30);
        """, c, option_text)
        if nat is not None:
            return f"{r}|native:{nat}"
        # матч по СЕРЕДИНЕ подписи: orig ищет строгое равенство и префикс, а длинные варианты Ashby
        # («I can't code on but am proficient in using AI vibe coding tools…») узнаются только куском.
        mid = d.execute_script("""
          const c = arguments[0], opt = arguments[1].toLowerCase();
          const cands = Array.from(c.querySelectorAll('label, button[role=radio], [role=option]'));
          const hit = cands.find(el => (el.innerText || '').toLowerCase().includes(opt));
          if (!hit) return null;
          hit.scrollIntoView({block:'center'});
          const inp = hit.querySelector('input') || (hit.htmlFor ? document.getElementById(hit.htmlFor) : null);
          (inp || hit).click();
          const on = inp ? inp.checked : hit.getAttribute('aria-checked') === 'true';
          return (on ? 'MID-CLICKED:' : 'MID-UNSURE:') + (hit.innerText || '').trim().slice(0, 40);
        """, c, option_text)
        if mid:
            return f"{r}|{mid}"
        # одиночное радио/чекбокс-подтверждение (DDG «US or Canada Based Only»): текста опции НЕТ,
        # виджет = ровно один input, который надо просто нажать. Ashby помечает такие required.
        solo = d.execute_script("""
          const c = arguments[0];
          const one = c.querySelectorAll('input[type=radio], input[type=checkbox]');
          if (one.length !== 1) return null;
          const i = one[0];
          if (i.checked) return 'ALREADY';
          i.scrollIntoView({block:'center'});
          const lab = i.closest('label') || c.querySelector('label[for="'+i.id+'"]');
          (lab || i).click();
          return i.checked ? 'SOLO-CLICKED' : 'SOLO-FAILED';
        """, c)
        if solo:
            return f"{r}|solo:{solo}"
        d.execute_script("const t=arguments[0].querySelector('input,button,[role=combobox]'); if(t){t.click();}", c)
        _t.sleep(1.0)
        opts = [o for o in d.find_elements(ats_lib.By.CSS_SELECTOR, "[role='option'], [id*='-option-']") if o.is_displayed()]
        if not opts:
            return f"{r}|portal:NO-OPTS"
    except Exception as e:
        return f"{r}|portal-exc:{type(e).__name__}"
    tgt = next((o for o in opts if (o.text or "").strip().lower() == option_text.lower()), None)           or next((o for o in opts if option_text.lower() in (o.text or "").lower()), None) or opts[0]
    txt = (tgt.text or "")[:30]
    d.execute_script("arguments[0].click();", tgt); _t.sleep(0.5)
    return f"{r}|portal:CLICKED:{txt}"
ats_lib.select_option_in_entry = _strict_soie

# чекбокс-подтверждение, которое на самом деле ОДИНОЧНОЕ РАДИО: click_checkbox ищет только
# input[type=checkbox] и честно возвращает NO-CHECKBOX. Дожимаем тем же solo-приёмом.
_orig_click_cb = ats_lib.click_checkbox
def _strict_click_cb(d, label, want=True):
    r = _orig_click_cb(d, label, want)
    if not str(r).startswith("NO-CHECKBOX") or not want:
        return r
    try:
        c = ats_lib._entry_by_label(d, label)
        if c is None:
            return r
        solo = d.execute_script("""
          const c = arguments[0];
          const one = c.querySelectorAll('input[type=radio], input[type=checkbox]');
          if (one.length !== 1) return 'NOT-SOLO:' + one.length;
          const i = one[0];
          if (i.checked) return 'ALREADY';
          i.scrollIntoView({block:'center'});
          const lab = i.closest('label') || c.querySelector('label[for="'+i.id+'"]');
          (lab || i).click();
          return i.checked ? 'SOLO-CLICKED' : 'SOLO-FAILED';
        """, c)
        return f"{r}|solo:{solo}"
    except Exception as e:
        return f"{r}|solo-exc:{type(e).__name__}"
ats_lib.click_checkbox = _strict_click_cb

import auto_apply
auto_apply.new_driver = new_driver
auto_apply.CV_MAP["stablecoin"] = "Stablecoin"
# фирменные обёртки над Greenhouse: своя вёрстка вместо формы (coveo дал «Resume*» из своего DOM,
# careerpuck — вовсе no-form). Слаг проверен живым запросом: embed отдаёт 200 и поля формы.
auto_apply.GH_EMBED_SLUGS["coveo.com"] = "coveoen"
auto_apply.GH_EMBED_SLUGS["careerpuck.com"] = "dominodatalab"  # верно для domino; у другой компании на
# careerpuck слаг будет свой — проверять curl'ом embed/job_app?for=<slug>&token=<gh_jid> до подачи
auto_apply.main()
