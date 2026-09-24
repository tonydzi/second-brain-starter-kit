# -*- coding: utf-8 -*-
"""python patch_code_gate2.py tests|patch — класс 08.09 «Incorrect security code при верно набранном коде»
(Together AI #2, Cribl): строка целиком в бокс 0 визуально раскладывается по боксам, но React-состояние
виджета держит только первый знак -> Greenhouse отвечает Incorrect. Лечение: (1) набор ПО ЗНАКУ в активный
элемент (как человек), проверка по сумме значений семьи боксов; (2) после «Incorrect» Greenhouse шлёт НОВЫЙ код
на каждый клик Submit — второй круг с меткой времени ресабмита."""
import io, os, sys
D = r"[путь владельца]"
MOD = os.path.join(D, "gh_code_gate.py")
TST = os.path.join(D, "_test_gh_code_gate.py")
mode = sys.argv[1]

if mode == "tests":
    t = io.open(TST, encoding="utf-8").read().replace("\r\n", "\n")
    old = '''class FakeDriver:
    """Дубль selenium: своя FakeEl на каждый id (боксовый виджет = 8 разных полей)."""

    def __init__(self, cands, accepts=True, single_char=False):
        self.cands = cands
        self.accepts = accepts
        self.single_char = single_char   # виджет режет ввод до 1 знака (maxlength=1)
        self.els = {}
        self.scripts = []

    def execute_script(self, js, *args):
        self.scripts.append(js[:40])
        if "querySelectorAll('input')" in js:
            return self.cands
        if "arguments[0].value" in js:
            return args[0].value
        return None
'''
    new = '''class _ActiveEl:
    """Активный элемент: виджет с авто-переходом — каждый знак уходит в СВОЙ бокс (typed копит всё)."""

    def __init__(self, drv):
        self.drv = drv

    def send_keys(self, s):
        if s == "\\ue003":          # BACKSPACE
            self.drv.typed = self.drv.typed[:-1]
            return
        self.drv.typed += s


class _SwitchTo:
    def __init__(self, drv):
        self.drv = drv

    @property
    def active_element(self):
        return _ActiveEl(self.drv)


class FakeDriver:
    """Дубль selenium: своя FakeEl на каждый id (боксовый виджет = 8 разных полей)."""

    def __init__(self, cands, accepts=True, single_char=False, react_first_char_only=False):
        self.cands = cands
        self.accepts = accepts
        self.single_char = single_char   # виджет режет ввод до 1 знака (maxlength=1)
        self.react_first_char_only = react_first_char_only  # строка целиком -> в состоянии только 1-й знак
        self.els = {}
        self.scripts = []
        self.typed = ""                  # что реально дошло до состояния виджета через активный элемент
        self.switch_to = _SwitchTo(self)

    def execute_script(self, js, *args):
        self.scripts.append(js[:40])
        if "querySelectorAll('input')" in js:
            return self.cands
        if "FAMILY_VALUES" in js:
            return self.typed if self.react_first_char_only else "".join(e.value for e in self.els.values())
        if "arguments[0].value" in js:
            return args[0].value
        return None
'''
    assert old in t, "FakeDriver: ожидаемый кусок не найден"
    t = t.replace(old, new, 1)
    old2 = '''def t_handle():'''
    new2 = '''def t_perchar():
    # 08.09 Together AI #2 / Cribl: боксы БЕЗ семьи id (только security-input-0 виден кандидатом),
    # строка целиком визуально раскладывается, но состояние держит один знак -> Incorrect security code.
    lone = [{"id": "security-input-0", "name": "", "type": "text", "placeholder": "", "aria": "Security code",
             "label": "Security code", "maxlength": "", "visible": True}]
    d = FakeDriver(lone, single_char=True, react_first_char_only=True)
    rep = G.fill_code(d, "5K0iEETo")
    chk("perchar:ok", rep, "OK:perchar:5K0iEETo")
    chk("perchar:typed-all", d.typed, "5K0iEETo")
    # обычное одиночное поле принимает строку целиком — по знаку НЕ переходим
    plain = [{"id": "security_code", "name": "", "type": "text", "placeholder": "", "aria": "Security code",
              "label": "Security code", "maxlength": "8", "visible": True}]
    d2 = FakeDriver(plain)
    chk("perchar:not-for-plain", G.fill_code(d2, "5K0iEETo"), "OK:id:security_code:5K0iEETo")
    chk("perchar:plain-untouched", d2.typed, "")


def t_handle():'''
    assert old2 in t
    t = t.replace(old2, new2, 1)
    t = t.replace("t_boxes, t_find_email, t_wait, t_fill, t_handle):", "t_boxes, t_find_email, t_wait, t_fill, t_perchar, t_handle):")
    t = t.replace("  8. снять фолбэк одной сироты                    -> purestorage/«Everpure» = no-code-email (08.09)",
                  "  8. снять фолбэк одной сироты                    -> purestorage/«Everpure» = no-code-email (08.09)\n"
                  "  9. слать код строкой в -0 бокс без семьи         -> Incorrect security code при верном коде (Together AI 08.09)")
    io.open(TST, "w", encoding="utf-8", newline="\n").write(t)
    print("tests added")

elif mode == "patch":
    s = io.open(MOD, encoding="utf-8").read().replace("\r\n", "\n")
    old = '''    sel = choose_code_field(cands)
    if not sel:
        return "NO-FIELD"
    el = _el(d, sel)
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.clear()
    except Exception:
        pass
    el.click()
    el.send_keys(code)
    got = d.execute_script("return arguments[0].value || '';", el)
    return ("OK:%s:%s" % (sel, got)) if got.strip().upper() == code.upper() else ("MISMATCH:%s:%r" % (sel, got))
'''
    new = '''    sel = choose_code_field(cands)
    if not sel:
        return "NO-FIELD"
    el = _el(d, sel)
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    m0 = _RE_BOX.match(sel.split(":", 1)[1])
    if m0 and m0.group(2) == "0":
        # 08.09 (Together AI #2, Cribl): нулевой бокс виджета с авто-переходом, семья id не видна кандидатам.
        # Строка целиком визуально раскладывается по боксам, но состояние виджета держит ОДИН знак ->
        # «Incorrect security code» при верном коде. Набираем по знаку в АКТИВНЫЙ элемент, как человек.
        return _fill_per_char(d, el, m0.group(1), code)
    try:
        el.clear()
    except Exception:
        pass
    el.click()
    el.send_keys(code)
    got = d.execute_script("return arguments[0].value || '';", el)
    return ("OK:%s:%s" % (sel, got)) if got.strip().upper() == code.upper() else ("MISMATCH:%s:%r" % (sel, got))


_JS_FAMILY = """
const p = arguments[0];  // FAMILY_VALUES: сумма значений всех боксов семьи по префиксу id
return Array.from(document.querySelectorAll('input')).filter(e => (e.id || '').startsWith(p))
  .sort((a, b) => a.id.localeCompare(b.id, undefined, {numeric: true})).map(e => e.value || '').join('');
"""


def _page_has(d, rx):
    """Текст страницы целиком (tail от gh_wait_outcome = первые 1200 знаков, подпись у виджета кода не входит)."""
    try:
        txt = d.execute_script("return (document.body && document.body.innerText) || '';") or ""
    except Exception:
        return False
    return bool(re.search(rx, txt, re.I))


def _fill_per_char(d, el0, prefix, code):
    """Клик в бокс 0, затем по знаку в активный элемент (виджет сам двигает фокус)."""
    el0.click()
    for _ in range(len(code) + 2):                    # стереть, что уже лежит в боксах
        d.switch_to.active_element.send_keys("\\ue003")  # BACKSPACE
    el0.click()
    for ch in code:
        d.switch_to.active_element.send_keys(ch)
        time.sleep(0.12)
    got = d.execute_script(_JS_FAMILY, prefix) or ""
    tag = "perchar"
    return ("OK:%s:%s" % (tag, got)) if got.strip().upper() == code.upper() else ("MISMATCH:%s:%r" % (tag, got))
'''
    assert old in s, "fill_code: ожидаемый кусок не найден"
    s = s.replace(old, new, 1)
    old_h = '''    log("code-gate: RESUBMIT " + str(gh_lib.gh_submit(d)))
    outcome, tail = gh_lib.gh_wait_outcome(d)
    return {"code": code, "msgid": msgid, "outcome": outcome, "note": tail[:300].replace("\\n", " | ")}
'''
    new_h = '''    resubmitted_at = int(time.time()) - 2
    log("code-gate: RESUBMIT " + str(gh_lib.gh_submit(d)))
    outcome, tail = gh_lib.gh_wait_outcome(d)
    if outcome == "code-gate" and _page_has(d, r"incorrect security code"):
        # 08.09: на каждый клик Submit Greenhouse шлёт НОВЫЙ код — второй круг с меткой ресабмита
        log("code-gate: Incorrect -> жду новый код после ресабмита")
        code2, msgid2 = wait_for_code(company, resubmitted_at, timeout_s=max(60, timeout_s // 2),
                                      poll_s=poll_s, log=log)
        if code2 and code2 != code:
            rep2 = fill_code(d, code2)
            log("code-gate: fill#2 -> %s" % rep2)
            log("code-gate: RESUBMIT#2 " + str(gh_lib.gh_submit(d)))
            outcome, tail = gh_lib.gh_wait_outcome(d)
            code, msgid = code2, msgid2
    return {"code": code, "msgid": msgid, "outcome": outcome, "note": tail[:300].replace("\\n", " | ")}
'''
    assert old_h in s, "handle: ожидаемый кусок не найден"
    s = s.replace(old_h, new_h, 1)
    s = s.replace("updated: 2026-09-08 (матч слага + фолбэк одной сироты, ZBOOKG8)",
                  "updated: 2026-09-08 (матч слага + сирота после 60с + боксы без maxlength + набор по знаку + второй круг после Incorrect, ZBOOKG8)")
    io.open(MOD, "w", encoding="utf-8", newline="\n").write(s)
    print("module patched")
