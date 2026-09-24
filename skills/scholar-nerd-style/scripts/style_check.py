# -*- coding: utf-8 -*-
"""Style gate for СТИЛЬ УЧЁНОГО ЗАДРОТА.

    python style_check.py <file.html|dir> [...]      exit 0 = conforms, 1 = does not

Checks the things that actually decay: a page quietly growing a CDN dependency,
a tracker, an unreadable measure, a table that scrolls the whole body sideways,
an image with no alt text. It does NOT judge taste — taste is the human's job.

0 tokens, stdlib only, no network.
"""
import io, os, re, sys
from html.parser import HTMLParser

VOID = {'br','img','meta','link','input','hr','source','area','base','col','embed','param','track','wbr'}
TRACKERS = ["google-analytics", "googletagmanager", "gtag(", "plausible.io", "hotjar",
            "connect.facebook.net", "fbq(", "mixpanel", "segment.com/analytics",
            "clarity.ms", "matomo", "yandex.ru/metrika", "ym("]


class Bal(HTMLParser):
    def __init__(self):
        super().__init__(); self.st = []; self.err = []; self.imgs = []
    def handle_starttag(self, t, attrs):
        if t == "img":
            d = dict(attrs)
            if not (d.get("alt") or "").strip():
                self.imgs.append(d.get("src", "?")[:50])
        if t not in VOID:
            self.st.append(t)
    def handle_endtag(self, t):
        if t in VOID:
            return
        if self.st and self.st[-1] == t:
            self.st.pop()
        elif t in self.st:
            while self.st and self.st[-1] != t:
                self.err.append("unclosed <%s>" % self.st.pop())
            self.st.pop()
        else:
            self.err.append("stray </%s>" % t)


EXEMPT = re.compile(r'<!--\s*style-exempt:\s*(.+?)\s*-->', re.S)


def check(path):
    """Return (errors, warnings, exempt_reason) for one html file.

    A page in a deliberately different visual language declares it in the source:
        <!-- style-exempt: recruiter one-pager, sans-serif card layout on purpose -->
    Then only the universal checks (self-contained, no trackers, document hygiene,
    layout traps, structure) apply — the typographic ones are skipped. A gate that
    cries wolf on an intentional choice gets ignored wholesale, so the exemption is
    explicit and must carry a reason.
    """
    s = io.open(path, encoding="utf-8", errors="replace").read()
    head = s.split("</head>", 1)[0]
    E, W = [], []
    m = EXEMPT.search(s)
    exempt = m.group(1).strip() if m else None
    if m and not exempt:
        E.append("style-exempt marker with no reason given")

    # --- self-contained: the page must survive with no network -------------
    for m in re.finditer(r'<script[^>]+src=["\']((?:https?:)?//[^"\']+)', s, re.I):
        E.append("external script: " + m.group(1)[:60])
    for m in re.finditer(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']((?:https?:)?//[^"\']+)', s, re.I):
        E.append("external stylesheet: " + m.group(1)[:60])
    for m in re.finditer(r'@import\s+url\(["\']?((?:https?:)?//[^)"\']+)', s, re.I):
        E.append("remote @import: " + m.group(1)[:60])
    for m in re.finditer(r'src=["\']((?:https?:)?//[^"\']+\.(?:woff2?|ttf|otf))', s, re.I):
        E.append("remote webfont: " + m.group(1)[:60])
    if re.search(r'<iframe', s, re.I):
        W.append("<iframe> present — the page no longer stands alone offline")

    # --- no tracking --------------------------------------------------------
    low = s.lower()
    for t in TRACKERS:
        if t in low:
            E.append("tracker: " + t)

    # --- document hygiene ---------------------------------------------------
    if not re.search(r'<html[^>]+lang=', s, re.I):
        E.append("missing lang= on <html>")
    if not re.search(r'<meta[^>]+charset', head, re.I):
        E.append("missing <meta charset>")
    if not re.search(r'name=["\']viewport["\']', head, re.I):
        E.append("missing viewport meta — unreadable on a phone")
    if not re.search(r'<title>\s*\S', head, re.I):
        E.append("missing or empty <title>")
    if not re.search(r'name=["\']description["\']', head, re.I):
        W.append("no meta description — this is the line a recruiter reads in search results")

    # --- the style itself (skipped for a declared exemption) ----------------
    if not exempt:
        if not re.search(r'Bitstream Charter|Iowan Old Style', s):
            E.append("serif stack missing — this is not the style")
        if not re.search(r'max-width\s*:\s*4[0-9](\.\d+)?rem', s):
            E.append("no body measure cap (expected max-width ~47rem)")
        if re.search(r'background\s*:\s*#fff\b|background\s*:\s*#ffffff\b|background\s*:\s*white\b', s, re.I):
            W.append("pure white background — the style uses off-white (#fdfdfd)")
        if not re.search(r'--paper|#fdfdfd', s):
            W.append("paper colour not found")

    # --- layout traps -------------------------------------------------------
    if "<table" in low and not re.search(r'overflow-x\s*:\s*auto', low):
        E.append("<table> without an overflow-x:auto wrapper — wide tables will scroll the page sideways")
    if "<pre" in low and not re.search(r'pre\s*\{[^}]*overflow-x', low):
        W.append("<pre> without overflow-x — long lines will scroll the page sideways")

    # --- structure ----------------------------------------------------------
    b = Bal(); b.feed(s)
    for t in b.st:
        E.append("unclosed <%s>" % t)
    E += b.err[:5]
    for src in b.imgs:
        E.append("<img> without alt: " + src)
    if 'class="foot"' not in s and not exempt:
        W.append('no .foot block — say how and when the page was produced')

    return E, W, exempt


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    files = []
    for a in args:
        if os.path.isdir(a):
            for root, _, names in os.walk(a):
                if ".git" in root:
                    continue
                files += [os.path.join(root, n) for n in names if n.endswith(".html")]
        else:
            files.append(a)
    if not files:
        print("no .html files found in:", " ".join(args))
        return 2

    bad = 0
    for f in sorted(files):
        E, W, ex = check(f)
        tag = "FAIL" if E else ("warn" if W else "OK  ")
        print("%s %s%s" % (tag, f, ("   [exempt: %s]" % ex) if ex else ""))
        for e in E:
            print("      x %s" % e)
        for w in W:
            print("      ! %s" % w)
        bad += bool(E)
    print("\n%d file(s), %d failing" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
