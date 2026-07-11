# -*- coding: utf-8 -*-
"""
One-off patcher: repoint the old homepage-anchor nav/footer links in the
already-generated posts/*.html to the real standalone pages, and add the new
"Dashboard" nav link so their chrome matches the updated template.

Idempotent: safe to run more than once (it only touches the old anchor hrefs
and only inserts Dashboard where it is missing).
"""
import os, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
POSTS = glob.glob(os.path.join(ROOT, "posts", "*.html"))

REPL = [
    ('href="/#how"', 'href="/how-it-works.html"'),
    ('href="/#safety"', 'href="/safety.html"'),
    ('href="/#dashboard"', 'href="/platform.html"'),
]
# Insert a Dashboard link after Safety in the top nav and the mobile nav.
DASH_NAV = '<a href="/platform.html">Dashboard</a>'
INSERTS = [
    ('<a href="/safety.html">Safety</a><a href="/blog.html" class="active">Blog</a>',
     '<a href="/safety.html">Safety</a>' + DASH_NAV + '<a href="/blog.html" class="active">Blog</a>'),
    ('<a href="/safety.html">Safety</a><a href="/blog.html">Blog</a>',
     '<a href="/safety.html">Safety</a>' + DASH_NAV + '<a href="/blog.html">Blog</a>'),
]

total_href = 0
total_dash = 0
for f in POSTS:
    s = open(f, encoding="utf-8").read()
    orig = s
    for a, b in REPL:
        n = s.count(a); total_href += n
        s = s.replace(a, b)
    for a, b in INSERTS:
        # a already contains the new /safety.html href (REPL ran above);
        # b is idempotent because it is not a substring pattern we re-scan.
        if a in s:
            cnt = s.count(a)
            s = s.replace(a, b); total_dash += cnt
    if s != orig:
        open(f, "w", encoding="utf-8").write(s)

# Report residual old anchors across posts (should be zero)
residual = 0
for f in POSTS:
    s = open(f, encoding="utf-8").read()
    residual += len(re.findall(r'href="/#(?:how|safety|dashboard)"', s))

print(f"posts patched: {len(POSTS)} files")
print(f"anchor hrefs repointed: {total_href}")
print(f"Dashboard links inserted: {total_dash}")
print(f"residual old /# anchors in posts: {residual}")
