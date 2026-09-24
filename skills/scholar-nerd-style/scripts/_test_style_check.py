# -*- coding: utf-8 -*-
"""Offline test for style_check.py. No network, writes only to a temp dir.

    python _test_style_check.py     # exit 0 = pass

Every case below is a defect the gate exists to catch, so the gate must go RED
on each one and stay GREEN on a clean page.
"""
import io, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style_check as S

GOOD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>T</title><meta name="description" content="d">
<style>
body{background:#fdfdfd;font-family:"Bitstream Charter",Georgia,serif;max-width:47rem}
pre{overflow-x:auto}
.tw{overflow-x:auto}
</style></head>
<body><h1>T</h1><p>hi</p>
<div class="tw"><table><tr><td>x</td></tr></table></div>
<img src="a.png" alt="a picture">
<div class="foot">made by hand</div>
</body></html>"""

tmp = tempfile.mkdtemp()
fails = []
total = 0


def run(name, html, want_err_substr=None, want_clean=False):
    global total
    total += 1
    p = os.path.join(tmp, name.replace(" ", "_") + ".html")
    io.open(p, "w", encoding="utf-8").write(html)
    E, W, ex = S.check(p)
    if want_clean:
        ok = not E
        detail = "errors: %s" % E
    else:
        ok = any(want_err_substr in e for e in E)
        detail = "wanted %r, got %s" % (want_err_substr, E or "no errors")
    print(("  PASS " if ok else "  FAIL ") + name + ("" if ok else "  <- " + detail))
    if not ok:
        fails.append(name)


run("clean page passes", GOOD, want_clean=True)
run("catches CDN script", GOOD.replace("<body>", '<body><script src="https://cdn.example.com/x.js"></script>'), "external script")
run("catches CDN stylesheet", GOOD.replace("</head>", '<link rel="stylesheet" href="https://fonts.example.com/c.css"></head>'), "external stylesheet")
run("catches remote webfont", GOOD.replace("<body>", '<body><span src="https://x.com/a.woff2"></span>'), "remote webfont")
run("catches analytics", GOOD.replace("<body>", '<body><script>gtag("js");</script>'), "tracker")
run("catches missing lang", GOOD.replace('<html lang="en">', "<html>"), "missing lang")
run("catches missing viewport", GOOD.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', ""), "missing viewport")
run("catches wrong typeface", GOOD.replace('"Bitstream Charter",Georgia,serif', "Arial,sans-serif"), "serif stack missing")
run("catches missing measure cap", GOOD.replace("max-width:47rem", "width:100%"), "no body measure cap")
run("catches unwrapped table", GOOD.replace('<div class="tw"><table>', "<table>").replace("</table></div>", "</table>").replace(".tw{overflow-x:auto}", "").replace("pre{overflow-x:auto}", ""), "without an overflow-x")
run("catches img without alt", GOOD.replace('alt="a picture"', ""), "without alt")
run("exempt page skips typography checks",
    GOOD.replace('"Bitstream Charter",Georgia,serif', "Arial,sans-serif").replace("max-width:47rem","width:100%")
        .replace("<body>", "<body><!-- style-exempt: recruiter landing, sans-serif on purpose -->"),
    want_clean=True)
run("exempt marker without a reason is rejected",
    GOOD.replace("<body>", "<body><!-- style-exempt: -->"), "no reason given")
run("exempt page still fails on a tracker",
    GOOD.replace("<body>", '<body><!-- style-exempt: landing --><script>gtag("js");</script>'), "tracker")
run("catches unclosed tag", GOOD.replace("<p>hi</p>", "<p>hi"), "unclosed")

print("\n%d/%d passed" % (total - len(fails), total))
if fails:
    print("FAILED:", fails)
sys.exit(1 if fails else 0)
