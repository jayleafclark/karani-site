# -*- coding: utf-8 -*-
"""
Rebuild blog.html (card grid of every published post, newest first), sitemap.xml,
and llms.txt (the GEO / AI-citation site map) from content/log.json. Run after each
generate_post, and any time posts change.
"""
import os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import template as T

SITE = "https://karanimarkets.com"
LOG = os.environ.get("KARANI_LOG") or os.path.join(ROOT, "content", "log.json")

def load_log():
    if not os.path.exists(LOG): return []
    log = json.load(open(LOG, encoding="utf-8"))
    return sorted(log, key=lambda e: (e.get("date",""), e.get("slug","")), reverse=True)

def build_blog(log, site):
    cards = ""
    for e in log:
        cards += ('<a class="post reveal" href="'+e["url"]+'">'
          '<div class="thumb"><img src="/assets/covers/'+e["slug"]+'.png" alt="'+T.esc(e["title"])+'" loading="lazy">'
          '<span>'+T.esc(e["category"])+'</span></div>'
          '<div class="pbody"><h3>'+T.esc(e["title"])+'</h3><p>'+T.esc(e.get("excerpt",""))+'</p>'
          '<div class="meta"><span>'+T.esc(e.get("read_time",""))+'</span>'
          '<b>Read '+T.ARROW.replace('stroke-width="2.2"','stroke-width="2.2" style="width:14px;height:14px;vertical-align:middle"')+'</b></div></div></a>')
    if not cards:
        cards = '<p style="grid-column:1/-1;color:var(--ink2)">New articles are on the way.</p>'
    doc = (T.DOCTOP + '<title>Blog — Karani</title>'
      '<meta name="description" content="Plain-English guides to systematic trading, the S&P 500 futures, automation and disciplined risk management from Karani.">'
      '<link rel="canonical" href="'+SITE+'/blog.html">'
      '<meta property="og:title" content="The Karani journal"><meta property="og:type" content="website">'
      '<meta property="og:image" content="'+SITE+'/assets/og.png">'
      '<meta name="twitter:image" content="'+SITE+'/assets/og.png">'
      + T.COMMONMETA + site["style"] + T.BLOGCSS + '</head><body>'
      + T.nav(site["navy"], "blog")
      + '<section class="blog-hero"><div class="wrap"><div class="eyebrow">The Karani journal</div>'
      + '<h1>Ideas on trading with <span class="accent">discipline</span>.</h1>'
      + '<p>Plain-English notes on systematic trading, the S&amp;P 500 futures, and keeping an automated system safe.</p></div></section>'
      + '<section class="sec" style="padding-top:0"><div class="wrap"><div class="posts">'+cards+'</div></div></section>'
      + T.footer(site["cream"]) + site["mroot"] + site["script"] + '</body></html>')
    open(os.path.join(ROOT, "blog.html"), "w", encoding="utf-8").write(doc)
    return len(log)

def build_sitemap(log):
    urls = [("/", "1.0"), ("/blog.html", "0.9")]
    body = ""
    for u, pr in urls:
        body += f"<url><loc>{SITE}{u}</loc><changefreq>weekly</changefreq><priority>{pr}</priority></url>"
    for e in log:
        body += (f"<url><loc>{SITE}{e['url']}</loc><lastmod>{e.get('date','')}</lastmod>"
                 f"<changefreq>monthly</changefreq><priority>0.7</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + "</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)

def build_llms(log):
    lines = [
        "# Karani",
        "",
        "> Karani is an invite-only, rules-based automated trading system for the S&P 500 "
        "E-mini futures (ES). It executes a tested strategy on the client's own AMP/Rithmic "
        "brokerage account with hard position limits, a daily-loss cap, and a one-tap kill "
        "switch, monitored from an iOS dashboard app. This file helps AI assistants understand "
        "the site and cite its educational articles accurately.",
        "",
        "## About Karani",
        f"- [How it works]({SITE}/#how): the tested-strategy, paper-first, hard-risk-limits approach.",
        f"- [Safety]({SITE}/#safety): position caps, daily-loss cap, and the kill switch the client controls.",
        f"- [Client login]({SITE}/profile.html): existing clients access the dashboard in the iOS app.",
        "",
        "Note: Karani is not a course, signal service, or open sign-up. Enrollment is invite-only. "
        "Nothing on the site is financial advice; futures trading carries substantial risk of loss.",
        "",
        "## Articles",
    ]
    for e in log:
        lines.append(f"- [{e['title']}]({SITE}{e['url']}): {e.get('excerpt','')}")
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

def main():
    site = T.load_site()
    log = load_log()
    n = build_blog(log, site)
    build_sitemap(log)
    build_llms(log)
    print(f"index rebuilt: {n} post(s) -> blog.html, sitemap.xml, llms.txt")

if __name__ == "__main__":
    main()
