# -*- coding: utf-8 -*-
"""
Shared render kit for the Karani blog engine. Pulls the site's CSS, mobile-root,
script and logos out of index.html at runtime so generated pages always match the
live design, and exposes nav/footer/head + the blog and article builders.

Root-absolute URLs (/, /blog.html, /posts/<slug>.html, /assets/...) so pages work
from both the site root and the /posts/ subdirectory.
"""
import re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))          # content-engine/  (repo root when deployed)
INDEX = os.path.join(ROOT, "index.html")

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')

BLOGCSS = """
<style>
.blog-hero{padding:56px 0 8px;text-align:center}
.blog-hero .eyebrow{margin-bottom:12px}
.blog-hero h1{font-size:52px;letter-spacing:-.03em}
.blog-hero p{color:var(--ink2);font-size:18px;max-width:560px;margin:18px auto 0}
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:42px 0 10px}
.post{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:22px;overflow:hidden;box-shadow:var(--shadow-card);transition:transform .2s,box-shadow .2s;text-decoration:none}
.post:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.post .thumb{height:172px;background:var(--brand);position:relative;overflow:hidden}
.post .thumb img{width:100%;height:100%;object-fit:cover;display:block}
.post .thumb span{position:absolute;bottom:12px;left:14px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(30,44,56,.42);backdrop-filter:blur(3px);padding:5px 10px;border-radius:100px}
.post .pbody{padding:20px 20px 22px;display:flex;flex-direction:column;flex:1}
.post h3{font-size:19px;margin-bottom:8px;line-height:1.25;color:var(--ink)}
.post p{font-size:14px;color:var(--ink2);flex:1}
.post .meta{display:flex;align-items:center;justify-content:space-between;margin-top:16px;font-size:12.5px;color:var(--ink3)}
.post .meta b{color:var(--brand-deep);font-weight:600}
.article{max-width:720px;margin:0 auto;padding:40px 0 10px}
.article .eyebrow{margin-bottom:12px}
.article .cover{width:100%;height:auto;aspect-ratio:1200/630;border-radius:20px;margin:8px 0 26px;box-shadow:var(--shadow-card)}
.article h1{font-size:44px;letter-spacing:-.03em;line-height:1.08;margin-bottom:14px}
.article .amenu{color:var(--ink3);font-size:14px;margin-bottom:28px}
.article .lead{font-size:19px;color:var(--ink);line-height:1.6;margin-bottom:24px}
.article h2{font-size:26px;margin:34px 0 12px}
.article p{font-size:16.5px;color:var(--ink);line-height:1.75;margin-bottom:18px}
.article blockquote{border-left:3px solid var(--brand);padding:4px 0 4px 22px;margin:26px 0;font-family:var(--display);font-weight:500;font-size:20px;color:var(--brand-deep);line-height:1.42}
.article .back{display:inline-flex;gap:8px;align-items:center;color:var(--brand-deep);font-weight:600;margin-bottom:22px}
.article .back svg{width:16px;height:16px}
.faq{max-width:720px;margin:10px auto 0;padding:8px 0 0}
.faq h2{font-size:26px;margin:30px 0 10px}
.faq .qa{border-top:1px solid var(--line);padding:18px 0}
.faq .qa h3{font-size:17px;margin-bottom:6px;color:var(--ink)}
.faq .qa p{font-size:15.5px;color:var(--ink2);line-height:1.7}
.artcta{max-width:720px;margin:30px auto 0}
.related{max-width:720px;margin:34px auto 0;border-top:1px solid var(--line);padding-top:20px}
.related h4{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);margin-bottom:12px}
.related a{display:block;color:var(--brand-deep);font-weight:600;padding:6px 0;text-decoration:none}
@media(max-width:900px){.posts{grid-template-columns:1fr}.blog-hero h1{font-size:38px}.article h1{font-size:32px}}
</style>"""

DOCTOP = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width, initial-scale=1">')
COMMONMETA = ('<link rel="icon" type="image/png" href="/assets/favicon.png">'
  '<link rel="apple-touch-icon" href="/assets/favicon.png">'
  '<meta name="theme-color" content="#557790">'
  '<meta property="og:site_name" content="Karani">'
  '<meta name="twitter:card" content="summary_large_image">')

def load_site():
    h = open(INDEX, encoding="utf-8").read()
    style = re.search(r"<style>.*?</style>", h, re.S).group(0)
    mroot = re.search(r'(<div class="mroot".*?)\s*<script>', h, re.S).group(1)
    script = re.search(r"<script>.*?</script>", h, re.S).group(0)
    navy = re.search(r'<div class="brand"[^>]*><img src="(data:image/png;base64,[^"]+)"', h).group(1)
    cream = re.search(r'<div class="bb"><img src="(data:image/png;base64,[^"]+)"', h).group(1)
    return dict(style=style, mroot=mroot, script=script, navy=navy, cream=cream)

def nav(navy, active=""):
    def cls(x): return ' class="active"' if x == active else ''
    return ('<header id="hdr"><div class="wrap nav">'
      '<a class="brand" href="/" data-brand style="text-decoration:none"><img src="'+navy+'" alt="Karani"><b>Karani</b></a>'
      '<nav class="navlinks">'
      '<a href="/">Home</a>'
      '<a href="/how-it-works.html"'+cls("how")+'>How it works</a>'
      '<a href="/safety.html"'+cls("safety")+'>Safety</a>'
      '<a href="/platform.html"'+cls("platform")+'>Dashboard</a>'
      '<a href="/blog.html"'+cls("blog")+'>Blog</a>'
      '</nav>'
      '<div class="cta"><a class="btn btn-ghost navlogin" href="/profile.html">Client login</a>'
      '<button class="btn btn-brand" data-modal="signup">Request access '+ARROW+'</button></div>'
      '<button class="btn btn-brand navpill" data-modal="signup">Request access</button>'
      '<button class="menu-btn" aria-label="Open menu" onclick="openNav()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>'
      '</div></header>'
      '<div class="mnav" id="mnav" aria-hidden="true">'
      '<button class="mclose" aria-label="Close menu" onclick="closeNav()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>'
      '<a href="/">Home</a><a href="/how-it-works.html">How it works</a><a href="/safety.html">Safety</a><a href="/platform.html">Dashboard</a><a href="/blog.html">Blog</a>'
      '<a href="/profile.html">Client login</a>'
      '<button class="mcta" data-modal="signup" onclick="closeNav()">Request access</button></div>')

def footer(cream):
    return ('<footer><div class="wrap"><div class="foot-grid">'
      '<div class="foot-brand"><div class="bb"><img src="'+cream+'" alt="Karani"><b>Karani</b></div>'
      '<p>A disciplined, automated trading system for the S&amp;P 500 futures, built to run hands-off, with you in control.</p></div>'
      '<div class="fcol"><h5>Product</h5><a href="/how-it-works.html">How it works</a><a href="/safety.html">Safety</a><a href="/platform.html">Dashboard</a><a href="/blog.html">Blog</a></div>'
      '<div class="fcol"><h5>Company</h5><a href="/about.html">About</a><a href="#" data-modal="pricing">Pricing</a><a href="#" data-modal="contact">Contact</a></div>'
      '<div class="fcol"><h5>Account</h5><a href="/profile.html">Client login</a><a href="#" data-modal="signup">Request access</a></div>'
      '</div><div class="foot-bottom">'
      '<p class="disc">Trading futures involves substantial risk of loss and is not suitable for every investor. Nothing here is financial advice. Past performance is not indicative of future results.</p>'
      '<span class="cp">&copy; 2026 Karani</span></div></div></footer>')

def esc(s):
    return html.escape(s, quote=False)
