# -*- coding: utf-8 -*-
"""Append the shared CTA footer to the end of every skills/*/SKILL.md.

Input : docs/SKILL-FOOTER.md, the single source of the footer text. Everything
        between the BEGIN-FOOTER and END-FOOTER lines is copied verbatim.
Output: each SKILL.md ends with that block, starting at the <!--kit-footer-->
        marker.
Idempotent: the marker and everything after it is dropped before re-appending,
        so repeated runs never stack copies and an edit to the template
        propagates to all skills.
Never touches the YAML frontmatter: `description` is what an agent reads to
        decide whether to load a skill, and catalogs strip promo text from it.

Run: python engines/insert_footer.py [--check]
     --check exits 1 if any skill is missing or has a stale footer (for CI).
Called by: the kit grooming routine, and by hand after editing the template.
updated: 2026-09-09
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'docs', 'SKILL-FOOTER.md')
SKILLS = os.path.join(ROOT, 'skills')
MARKER = '<!--kit-footer-->'
# The kit used to end each skill with a separate contact block. The footer absorbed it,
# so both markers are cut points: whichever appears first is where the old tail begins.
LEGACY_MARKERS = ('<!-- CONTACT-FOOTER -->',)


def load_footer():
    text = io.open(TEMPLATE, encoding='utf-8').read()
    m = re.search(r'^BEGIN-FOOTER\r?\n(.*?)^END-FOOTER\s*$', text, re.S | re.M)
    if not m:
        sys.exit('SKILL-FOOTER.md: BEGIN-FOOTER/END-FOOTER block not found')
    block = m.group(1).strip('\n')
    if MARKER not in block:
        sys.exit('SKILL-FOOTER.md: footer block must contain %s' % MARKER)
    return block


def main():
    check = '--check' in sys.argv
    footer = load_footer()
    written, already, stale = [], [], []
    for name in sorted(os.listdir(SKILLS)):
        path = os.path.join(SKILLS, name, 'SKILL.md')
        if not os.path.isfile(path):
            continue
        body = io.open(path, encoding='utf-8', newline='').read()
        cuts = [body.find(m) for m in (MARKER,) + LEGACY_MARKERS]
        cuts = [c for c in cuts if c != -1]
        stripped = body[:min(cuts)] if cuts else body
        # the legacy block was preceded by its own horizontal rule; drop it too
        stripped = re.sub(r'\n-{3,}[ \t]*\n\s*$', '\n', stripped)
        want = stripped.rstrip('\n') + '\n\n' + footer + '\n'
        if want == body:
            already.append(name)
            continue
        stale.append(name)
        if not check:
            io.open(path, 'w', encoding='utf-8', newline='\n').write(want)
            written.append(name)

    if check:
        print('footer current: %d, stale/missing: %d' % (len(already), len(stale)))
        if stale:
            print('stale: %s' % ', '.join(stale))
            return 1
        return 0
    print('footer written: %d, already current: %d' % (len(written), len(already)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
