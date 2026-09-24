# -*- coding: utf-8 -*-
"""python patch_code_gate3.py tests|patch — класс 08.09 «Gmail API 403 Quota exceeded (Units per minute per user)»:
несколько лейнов флота опрашивают ящик a@ каждые 15 с (list + get(full) x25) под одним проектом -> квота
в минуту исчерпана -> HttpError пробивает handle() -> OUTCOME crash -> раннер РЕТРАИТ форму (второй сабмит).
Лечение: (1) квота-ошибка = «письма пока нет», ждём дальше, не падаем; (2) кэш уже прочитанных сообщений —
повторный опрос не дёргает get() по тем же id; (3) окно поиска newer_than:2h вместо 1d."""
import io, os, sys
D = r"[путь владельца]"
MOD = os.path.join(D, "gh_code_gate.py")
TST = os.path.join(D, "_test_gh_code_gate.py")
mode = sys.argv[1]

if mode == "tests":
    t = io.open(TST, encoding="utf-8").read().replace("\r\n", "\n")
    old = "def t_handle():"
    new = '''def t_quota():
    # 08.09: 403 Quota exceeded от Gmail API = «письма пока нет», а не crash (crash -> раннер ресабмитит форму)
    class QuotaGmail(FakeGmail):
        def list(self, **kw):
            raise Exception("<HttpError 403 when requesting ... returned \\"Quota exceeded for quota metric "
                            "'Total Query Cost' and limit 'Units per minute per user'\\">")
    q = QuotaGmail([])
    chk("quota:no-crash", G.find_code_email("Ripple", 0, svc=q), ("", "", 0))
    chk("quota:wait-returns-empty", G.wait_for_code("Ripple", 0, timeout_s=0, poll_s=0, svc=q,
                                                    log=lambda *_: None), ("", ""))

    class BoomGmail(FakeGmail):
        def list(self, **kw):
            raise RuntimeError("something else entirely")
    try:
        G.find_code_email("Ripple", 0, svc=BoomGmail([]))
        chk("quota:other-errors-still-raise", False, True)
    except RuntimeError:
        chk("quota:other-errors-still-raise", True, True)


def t_handle():'''
    assert old in t and "def t_quota" not in t
    t = t.replace(old, new, 1)
    t = t.replace("t_fill, t_perchar, t_handle):", "t_fill, t_perchar, t_quota, t_handle):")
    io.open(TST, "w", encoding="utf-8", newline="\n").write(t)
    print("tests added")

elif mode == "patch":
    s = io.open(MOD, encoding="utf-8").read().replace("\r\n", "\n")
    old = '''    svc = svc or _gmail_service()
    q = "from:(" + " OR ".join(SENDERS) + ") subject:\\"security code\\" newer_than:1d"
    res = svc.users().messages().list(userId="me", q=q, maxResults=max_msgs).execute()
    best = ("", "", 0)
    orphans = {}  # имя из темы -> свежайшее чужое письмо новее метки
    for ref in res.get("messages", []) or []:
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
'''
    new = '''    svc = svc or _gmail_service()
    q = "from:(" + " OR ".join(SENDERS) + ") subject:\\"security code\\" newer_than:2h"
    try:
        res = svc.users().messages().list(userId="me", q=q, maxResults=max_msgs).execute()
    except Exception as e:  # noqa: BLE001
        if _is_quota_error(e):
            return ("", "", 0)   # 08.09: квота в минуту исчерпана = «письма пока нет», ждём дальше
        raise
    best = ("", "", 0)
    orphans = {}  # имя из темы -> свежайшее чужое письмо новее метки
    for ref in res.get("messages", []) or []:
        msg = _MSG_CACHE.get(ref["id"])
        if msg is None:
            try:
                msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
            except Exception as e:  # noqa: BLE001
                if _is_quota_error(e):
                    return ("", "", 0)
                raise
            _MSG_CACHE[ref["id"]] = msg
'''
    assert old in s, "find_code_email: ожидаемый кусок не найден"
    s = s.replace(old, new, 1)
    old2 = "def find_code_email("
    new2 = '''_MSG_CACHE = {}   # id письма -> payload; письмо с кодом не меняется, повторный опрос не платит за get()


def _is_quota_error(e):
    """403/429 квоты Gmail API (Total Query Cost / Units per minute per user) = временно, не падаем."""
    txt = str(e)
    return ("403" in txt or "429" in txt) and ("quota" in txt.lower() or "rate" in txt.lower())


def find_code_email('''
    assert old2 in s
    s = s.replace(old2, new2, 1)
    io.open(MOD, "w", encoding="utf-8", newline="\n").write(s)
    print("module patched")
