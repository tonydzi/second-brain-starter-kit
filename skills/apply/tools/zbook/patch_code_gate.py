# -*- coding: utf-8 -*-
"""python patch_code_gate.py tests|patch — правка движка gh_code_gate (хаб, синкается) по классу 08.09:
письмо с кодом отброшено, потому что имя компании в теме ≠ слаг доски
('Pure Storage'/'Everpure' vs 'purestorage', 'Spring Health' vs 'springhealth66') -> 150с ожидания и no-code-email.
Шаг tests добавляет красные кейсы в _test_gh_code_gate.py, шаг patch чинит модуль. Пишется файлом,
не heredoc'ом: в правках есть обратные слэши."""
import io, sys, os
D = r"[путь владельца]"
MOD = os.path.join(D, "gh_code_gate.py")
TST = os.path.join(D, "_test_gh_code_gate.py")
mode = sys.argv[1]

if mode == "tests":
    t = io.open(TST, encoding="utf-8").read()
    old = 'def t_field():'
    new = '''def t_company_slug():
    # 08.09 (ZBOOKG8): слаг доски против имени в теме письма — раньше 150 с ожидания и no-code-email
    S = "Security code for your application to %s"
    chk("company:slug-vs-name", G.company_matches(S % "Spring Health", "springhealth66"), True)
    chk("company:slug-nospace", G.company_matches(S % "Pure Storage", "purestorage"), True)
    chk("company:slug-still-foreign", G.company_matches(S % "Ripple", "Stripe"), False)
    chk("company:slug-short-guard", G.company_matches(S % "Ab", "abc123"), False)


def t_orphan():
    # 08.09: доска purestorage шлёт код от имени «Everpure» — по имени не сматчить никак.
    # Ровно одно чужое письмо строго новее метки сабмита = наш код; два разных имени = не гадаем.
    S = "Security code for your application to %s"
    one = FakeGmail([{"id": "ev", "subject": S % "Everpure", "body": HTML, "epoch": 2000}])
    chk("orphan:single-taken", G.find_code_email("purestorage", 1500, svc=one), ("On48rPa7", "ev", 2000))
    chk("orphan:stale-ignored", G.find_code_email("purestorage", 2500, svc=one), ("", "", 0))
    two = FakeGmail([{"id": "ev", "subject": S % "Everpure", "body": HTML, "epoch": 2000},
                     {"id": "rp", "subject": S % "Ripple", "body": TEXT, "epoch": 2100}])
    chk("orphan:two-names-refused", G.find_code_email("purestorage", 1500, svc=two), ("", "", 0))
    # своё имя совпало — сирота не нужна, берём именной даже если сирота свежее
    chk("orphan:named-wins", G.find_code_email("Ripple", 1500, svc=two), ("Q7mk2Zb9", "rp", 2100))


def t_field():'''
    assert old in t and "def t_company_slug" not in t
    t = t.replace(old, new, 1)
    # регистрация в прогоне: найти вызовы t_company() и добавить рядом
    if "t_company_slug()" not in t:
        import re
        m = re.search(r"^(\s*)t_company\(\)\s*$", t, re.M)
        assert m, "не нашёл вызов t_company()"
        t = t[:m.end()] + "\n" + m.group(1) + "t_company_slug()\n" + m.group(1) + "t_orphan()" + t[m.end():]
    t = t.replace("  6. слать код строкой в боксовый виджет          -> в форму уедет ОДНА буква (GitLab 05.09)",
                  "  6. слать код строкой в боксовый виджет          -> в форму уедет ОДНА буква (GitLab 05.09)\n"
                  "  7. снять матч слага без пробелов/цифр           -> springhealth66 ждёт 150 с при живом письме (08.09)\n"
                  "  8. снять фолбэк одной сироты                    -> purestorage/«Everpure» = no-code-email (08.09)")
    t = t.replace("updated: 2026-09-05", "updated: 2026-09-08")
    io.open(TST, "w", encoding="utf-8", newline="\n").write(t)
    print("tests added")

elif mode == "patch":
    s = io.open(MOD, encoding="utf-8").read()
    old_cm = '''    a, b = norm_company(m.group(1)), norm_company(company)
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a)
'''
    new_cm = '''    a, b = norm_company(m.group(1)), norm_company(company)
    if not a or not b:
        return False
    if a == b or a.startswith(b) or b.startswith(a):
        return True
    # 08.09: entry несёт СЛАГ доски ('springhealth66', 'purestorage'), а тема — имя ('Spring Health');
    # сравниваем ключи без пробелов и цифр, короче 4 букв не сравниваем (ложные совпадения)
    ka, kb = _slugkey(a), _slugkey(b)
    if len(ka) < 4 or len(kb) < 4:
        return False
    return ka == kb or ka.startswith(kb) or kb.startswith(ka)


def _slugkey(name):
    """Ключ для сравнения слага доски с именем компании: только буквы, без пробелов и цифр."""
    return re.sub(r"[^a-z]", "", (name or "").lower())
'''
    assert old_cm in s, "company_matches: ожидаемый кусок не найден"
    s = s.replace(old_cm, new_cm, 1)

    old_find = '''    best = ("", "", 0)
    for ref in res.get("messages", []) or []:
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        internal = int(msg.get("internalDate", 0)) // 1000
        if internal <= after_epoch:
            continue
        hdrs = {h["name"].lower(): h["value"] for h in (msg.get("payload") or {}).get("headers", [])}
        if not company_matches(hdrs.get("subject", ""), company):
            continue
        code = extract_code(_walk_body(msg.get("payload")))
        if code and internal > best[2]:
            best = (code, ref["id"], internal)
    return best
'''
    new_find = '''    best = ("", "", 0)
    orphans = {}  # имя из темы -> свежайшее чужое письмо новее метки
    for ref in res.get("messages", []) or []:
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        internal = int(msg.get("internalDate", 0)) // 1000
        if internal <= after_epoch:
            continue
        hdrs = {h["name"].lower(): h["value"] for h in (msg.get("payload") or {}).get("headers", [])}
        subj = hdrs.get("subject", "")
        if not company_matches(subj, company):
            m = _RE_SUBJ.search(subj or "")
            if m:
                nm = norm_company(m.group(1))
                if internal > orphans.get(nm, (None, None, 0))[2]:
                    orphans[nm] = (ref["id"], msg, internal)
            continue
        code = extract_code(_walk_body(msg.get("payload")))
        if code and internal > best[2]:
            best = (code, ref["id"], internal)
    if best[0]:
        return best
    # 08.09 (ZBOOKG8): доска purestorage шлёт код от имени «Everpure» — имя в письме ≠ слаг доски,
    # по имени не сматчить никак. Ровно ОДНО чужое имя строго новее метки сабмита = наш код
    # (письмо уходит в ту же секунду, что и сабмит). Два разных имени = параллельные лейны, не гадаем.
    if len(orphans) == 1:
        (msgid, msg, internal), = orphans.values()
        code = extract_code(_walk_body(msg.get("payload")))
        if code:
            return (code, msgid, internal)
    return best
'''
    assert old_find in s, "find_code_email: ожидаемый кусок не найден"
    s = s.replace(old_find, new_find, 1)
    s = s.replace("updated: 2026-09-05", "updated: 2026-09-08 (матч слага + фолбэк одной сироты, ZBOOKG8)")
    io.open(MOD, "w", encoding="utf-8", newline="\n").write(s)
    print("module patched")
