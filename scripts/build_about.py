# -*- coding: utf-8 -*-
"""Generate a real, indexable /about.html (entity anchor for the brand SERP)."""
import os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import template as T
SITE = "https://karanimarkets.com"

def main():
    s = T.load_site()
    body = ('<article class="article reveal">'
      '<div class="eyebrow">About</div>'
      '<h1>About Karani</h1>'
      '<p class="lead">Karani is a private, systematic trading system for the S&amp;P 500 E-mini futures (ES). '
      'It runs a backtested strategy automatically, with hard risk limits and a one-tap kill switch, built to '
      'operate hands-off while keeping its owner fully in control.</p>'
      '<h2>A rules-based approach</h2>'
      '<p>Karani trades by a fixed, tested set of rules rather than by feel. Every entry, exit, and position '
      'size is decided in advance, validated across years of market data, and run on a paper account before a '
      'single real dollar is at risk. The strategy that was tested is the strategy that actually runs, executed '
      'with a consistency no human can match: no hesitation, no revenge trades, no missed exits.</p>'
      '<h2>Safety comes first</h2>'
      '<p>Before any trade, Karani enforces hard boundaries: a cap on how many ES contracts can be open at once, '
      'a daily-loss cap that stops trading for the rest of the session, and a kill switch the account holder can '
      'hit at any moment. The system runs on the client&rsquo;s own brokerage account (AMP, connected through '
      'Rithmic), so the money and the final say stay with the client. Automation handles the disciplined middle '
      'of the work. You set the boundaries it operates within.</p>'
      '<h2>Invitation only</h2>'
      '<p>Karani works with a small, invitation-only group of clients. Terms are tailored to each client and '
      'shared privately during onboarding. If you would like to be considered, you are welcome to request access.</p>'
      '<blockquote>A tested edge, executed with machine discipline, inside limits you set.</blockquote>'
      '<div style="margin-top:30px"><button class="btn btn-brand" data-modal="signup">Request access ' + T.ARROW + '</button></div>'
      '</article>')
    ld_org = {"@context":"https://schema.org","@type":"Organization","name":"Karani",
        "url":SITE+"/","logo":SITE+"/assets/favicon.png",
        "description":"Karani is an invite-only, rules-based automated trading system for the S&P 500 E-mini futures (ES), with hard position limits, a daily-loss cap, and a one-tap kill switch.",
        "knowsAbout":["S&P 500 futures","E-mini futures","automated trading","systematic trading","futures risk management"]}
    ld_page = {"@context":"https://schema.org","@type":"AboutPage","name":"About Karani",
        "url":SITE+"/about.html","description":"About Karani, a private systematic trading system for the S&P 500 E-mini futures.",
        "mainEntity":{"@type":"Organization","name":"Karani","url":SITE+"/"}}
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (ld_org, ld_page))
    head = (T.DOCTOP + '<title>About Karani — a systematic S&P 500 futures system</title>'
      '<meta name="description" content="Karani is a private, invitation-only automated trading system for the S&P 500 E-mini futures (ES), built on tested rules with hard risk limits and a kill switch.">'
      '<link rel="canonical" href="'+SITE+'/about.html">'
      '<meta property="og:type" content="website"><meta property="og:title" content="About Karani">'
      '<meta property="og:url" content="'+SITE+'/about.html"><meta property="og:image" content="'+SITE+'/assets/og.png">'
      '<meta name="twitter:image" content="'+SITE+'/assets/og.png">'
      + T.COMMONMETA + ld + s["style"] + T.BLOGCSS + '</head><body>')
    doc = (head + T.nav(s["navy"]) + '<section class="sec" style="padding-top:24px"><div class="wrap">'
      + body + '</div></section>' + T.footer(s["cream"]) + s["mroot"] + s["script"] + '</body></html>')
    open(os.path.join(ROOT, "about.html"), "w", encoding="utf-8").write(doc)
    print("about.html", round(len(doc)/1024), "KB")

if __name__ == "__main__":
    main()
