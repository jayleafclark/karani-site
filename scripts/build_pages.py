# -*- coding: utf-8 -*-
"""
Generate the three standalone marketing pages for Karani:
  how-it-works.html  -> "how automated futures trading works" / "automated trading system"
  safety.html        -> "automated trading risk controls" / "futures trading risk management"
  platform.html      -> "automated trading dashboard" / "trading dashboard app"

Same render kit as build_about.py: real CSS/nav/footer/logos pulled from index.html,
so the pages match the live site. No em dashes, no contrast cadence, no hype
(rules_check.py is the gate). Root-absolute URLs so links work everywhere.
"""
import os, json, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import template as T
SITE = "https://karanimarkets.com"

# ---- shared bits --------------------------------------------------------

def ldjson(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps(o)}</script>' for o in objs)

def breadcrumb(name, url):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":name,"item":url}]}

def webpage(name, url, desc):
    return {"@context":"https://schema.org","@type":"WebPage","name":name,"url":url,
        "description":desc,"isPartOf":{"@type":"WebSite","name":"Karani","url":SITE+"/"},
        "publisher":{"@type":"Organization","name":"Karani","url":SITE+"/"}}

def faqpage(qas):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qas]}

def faq_block(qas):
    out = '<section class="faq"><h2>Common questions</h2>'
    for q, a in qas:
        out += f'<div class="qa"><h3>{T.esc(q)}</h3><p>{a}</p></div>'
    return out + '</section>'

def head(title, desc, path, ld):
    url = SITE + path
    return (T.DOCTOP + f'<title>{title}</title>'
      f'<meta name="description" content="{desc}">'
      f'<link rel="canonical" href="{url}">'
      '<meta property="og:type" content="website">'
      f'<meta property="og:title" content="{T.esc(title)}">'
      f'<meta property="og:description" content="{desc}">'
      f'<meta property="og:url" content="{url}">'
      f'<meta property="og:image" content="{SITE}/assets/og.png">'
      f'<meta name="twitter:title" content="{T.esc(title)}">'
      f'<meta name="twitter:description" content="{desc}">'
      f'<meta name="twitter:image" content="{SITE}/assets/og.png">'
      + T.COMMONMETA + ld + S["style"] + T.BLOGCSS + PAGECSS + '</head><body>')

def cta_block(line):
    return ('<div class="artcta"><div class="darkcard" style="text-align:center;padding:34px 26px">'
      '<h3 style="font-family:var(--display);color:#fff;font-size:24px;margin-bottom:8px">'+line+'</h3>'
      '<p style="color:rgba(255,255,255,.72);max-width:430px;margin:0 auto 18px;font-size:15px">'
      'Karani works with a small, invitation-only group of clients. If it fits how you want your '
      'capital managed, you are welcome to request access.</p>'
      '<button class="btn btn-brand" data-modal="signup">Request access '+T.ARROW+'</button>'
      '</div></div>')

# Small page-scoped CSS: reuses site tokens, adds a couple of layout helpers
# (step list, spec grid) that keep spacing tight on mobile and desktop.
PAGECSS = """
<style>
.page{max-width:760px;margin:0 auto;padding:38px 0 6px}
.page .eyebrow{margin-bottom:12px}
.page h1{font-size:46px;letter-spacing:-.03em;line-height:1.06;margin-bottom:16px}
.page .lead{font-size:19px;color:var(--ink);line-height:1.62;margin-bottom:10px}
.page h2{font-size:27px;margin:40px 0 12px;letter-spacing:-.02em}
.page h3{font-size:18px;margin:22px 0 6px;color:var(--ink)}
.page p{font-size:16.5px;color:var(--ink);line-height:1.75;margin-bottom:16px}
.page ul{margin:0 0 18px 0;padding:0;list-style:none}
.page ul li{position:relative;padding:0 0 10px 26px;font-size:16.5px;color:var(--ink);line-height:1.62}
.page ul li:before{content:"";position:absolute;left:2px;top:9px;width:8px;height:8px;border-radius:50%;background:var(--brand)}
.answer{background:var(--terra-soft);border-radius:16px;padding:20px 22px;margin:6px 0 8px;font-size:17px;line-height:1.62;color:var(--ink)}
.answer b{color:var(--brand-deep)}
.steps{counter-reset:step;margin:8px 0 6px;padding:0;list-style:none}
.steps li{counter-increment:step;position:relative;padding:0 0 24px 62px;min-height:44px}
.steps li:last-child{padding-bottom:4px}
.steps li:before{content:counter(step,decimal-leading-zero) ".";position:absolute;left:0;top:-2px;
  font-family:var(--display);font-weight:600;font-size:20px;color:var(--brand-deep);letter-spacing:-.02em}
.steps li:after{content:"";position:absolute;left:15px;top:30px;bottom:2px;width:1px;background:var(--line)}
.steps li:last-child:after{display:none}
.steps li h3{margin:0 0 4px}
.steps li p{margin:0;font-size:15.5px;color:var(--ink2);line-height:1.62}
.specs{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:14px 0 8px}
.spec{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px 18px 16px;box-shadow:var(--shadow-card)}
.spec .sic{width:38px;height:38px;border-radius:11px;background:var(--terra-soft);color:var(--brand-deep);
  display:grid;place-items:center;margin-bottom:12px}
.spec .sic svg{width:20px;height:20px}
.spec h3{margin:0 0 5px;font-size:16.5px}
.spec p{margin:0;font-size:14.5px;color:var(--ink2);line-height:1.58}
.callout{border-left:3px solid var(--brand);padding:4px 0 4px 22px;margin:24px 0;
  font-family:var(--display);font-weight:500;font-size:20px;color:var(--brand-deep);line-height:1.42}
.page .shot-frame{margin:22px 0 10px}
.page figure{margin:26px 0 12px}
.page figure figcaption{margin-top:12px;font-size:13.5px;color:var(--ink3);text-align:center;line-height:1.5}
.shot-frame img.shotshow{display:none}
.vizwrap{margin:24px 0 8px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px 24px 22px;box-shadow:var(--shadow-card);position:relative;overflow:hidden}
.vizscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.vizwrap svg{width:100%;height:auto;display:block}
.vizwrap figcaption{margin-top:14px;font-size:13.5px;color:var(--ink3);text-align:center;line-height:1.5}
.vizwrap:before{content:"";position:absolute;inset:0;background:radial-gradient(120% 90% at 88% 6%,rgba(111,147,172,.08),transparent 60%);pointer-events:none;border-radius:20px}
@media(max-width:640px){
  .shot-frame img.shotshow{display:block}.shot-frame img.shothide{display:none}
  .vizwrap{padding:18px 12px 16px}
  .vizwrap .vizscroll svg{width:560px;min-width:560px}
}
.crumbs{max-width:760px;margin:0 auto;font-size:13px;color:var(--ink3);padding-top:6px}
.crumbs a{color:var(--ink3);text-decoration:none}
.crumbs a:hover{color:var(--brand-deep)}
.related-pages{max-width:760px;margin:36px auto 0;border-top:1px solid var(--line);padding-top:22px}
.related-pages h4{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);margin-bottom:10px}
.related-pages a{display:inline-block;color:var(--brand-deep);font-weight:600;margin-right:22px;padding:5px 0;text-decoration:none}
@media(max-width:900px){
  .page{padding:26px 0 4px}
  .page h1{font-size:33px}
  .page h2{font-size:23px;margin-top:32px}
  .specs{grid-template-columns:1fr}
  .related-pages a{display:block;margin-right:0}
}
</style>"""

def crumbs(name):
    return ('<div class="crumbs"><a href="/">Home</a> &rsaquo; <span>'+T.esc(name)+'</span></div>')

def related(current):
    links = {
      "how":('/how-it-works.html','How it works'),
      "safety":('/safety.html','Safety and risk controls'),
      "platform":('/platform.html','The dashboard app'),
      "blog":('/blog.html','Journal'),
      "about":('/about.html','About Karani'),
    }
    order = [k for k in ("how","safety","platform","blog","about") if k != current]
    out = '<div class="related-pages"><h4>Keep reading</h4>'
    for k in order:
        u,l = links[k]
        out += f'<a href="{u}">{l}</a>'
    return out + '</div>'

def write(fname, doc):
    open(os.path.join(ROOT, fname), "w", encoding="utf-8").write(doc)
    print(fname, round(len(doc)/1024), "KB")

# small inline icons (stroke, currentColor) reused in spec grids
IC = {
  "shield":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l7 4v6c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
  "power":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.8 0"/></svg>',
  "gauge":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 13l4-4"/><path d="M4 18a8 8 0 1 1 16 0"/></svg>',
  "check":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h11l5 5v11H4z"/><path d="M8 13l2.5 2.5L16 10"/></svg>',
  "chart":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>',
  "bolt":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h7l-1 8 10-12h-7z"/></svg>',
  "phone":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/></svg>',
  "bell":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>',
  "server":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/></svg>',
  "sliders":'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/><circle cx="4" cy="12" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="20" cy="14" r="2"/></svg>',
}

def spec(icon, h, p):
    return f'<div class="spec"><div class="sic">{IC[icon]}</div><h3>{h}</h3><p>{p}</p></div>'

# ---- page-specific inline SVG visuals (self-contained, on-brand) --------

# SAFETY: "every order passes through four gates" — a shield made of stacked
# layers, an order dot travelling through each check before it reaches the market.
SAFETY_SVG = '''<figure class="vizwrap reveal" aria-label="Diagram: every order is checked against four risk controls before it reaches the market">
<div class="vizscroll">
<svg viewBox="0 0 720 300" role="img" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">
   <stop offset="0" stop-color="#6F93AC"/><stop offset="1" stop-color="#2C4757"/>
  </linearGradient>
  <linearGradient id="track" x1="0" y1="0" x2="1" y2="0">
   <stop offset="0" stop-color="#CE8168"/><stop offset="1" stop-color="#6F93AC"/>
  </linearGradient>
 </defs>
 <!-- source -->
 <g>
  <rect x="14" y="118" width="96" height="64" rx="16" fill="#fff" stroke="rgba(59,50,41,.14)"/>
  <text x="62" y="146" text-anchor="middle" font-size="12.5" font-weight="700" fill="#3B3229">Strategy</text>
  <text x="62" y="164" text-anchor="middle" font-size="11" fill="#8a7f72">wants to trade</text>
 </g>
 <!-- track -->
 <path d="M110 150 H600" fill="none" stroke="url(#track)" stroke-width="2.5" stroke-dasharray="2 7" stroke-linecap="round" opacity=".55"/>
 <!-- four gates -->
 <g>
  <!-- gate template -->
'''
# gate columns
_gates = [
  ("Position cap","max contracts"),
  ("Daily-loss cap","dollar floor"),
  ("Kill switch","your one tap"),
  ("Paper-proven","tested first"),
]
for i,(gl,gs) in enumerate(_gates):
    x = 168 + i*112
    SAFETY_SVG += (
      f'<g>'
      f'<rect x="{x-42}" y="66" width="84" height="168" rx="18" fill="#FBEEE7" stroke="rgba(206,129,104,.32)"/>'
      f'<rect x="{x-42}" y="66" width="84" height="168" rx="18" fill="url(#sg)" opacity="{0.05+i*0.015:.3f}"/>'
      f'<circle cx="{x}" cy="104" r="17" fill="#fff" stroke="rgba(85,119,144,.35)"/>'
      f'<path d="M{x-7} 104 l5 5 9 -10" fill="none" stroke="#4f8a6b" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
      f'<text x="{x}" y="168" text-anchor="middle" font-size="12" font-weight="700" fill="#2C4757">{gl}</text>'
      f'<text x="{x}" y="186" text-anchor="middle" font-size="10.5" fill="#8a7f72">{gs}</text>'
      f'</g>'
    )
SAFETY_SVG += '''
 </g>
 <!-- travelling order dot -->
 <circle r="7" fill="#CE8168">
  <animateMotion dur="4.2s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="linear" path="M110 150 H600"/>
  <animate attributeName="opacity" values="0;1;1;1;0" dur="4.2s" repeatCount="indefinite"/>
 </circle>
 <!-- market -->
 <g>
  <rect x="606" y="112" width="100" height="76" rx="18" fill="url(#sg)"/>
  <text x="656" y="144" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">Market</text>
  <text x="656" y="164" text-anchor="middle" font-size="10.5" fill="rgba(255,255,255,.72)">order sent</text>
 </g>
 <text x="360" y="270" text-anchor="middle" font-size="12.5" fill="#8a7f72">Every order clears all four checks before it can reach the CME. If any fails, the order is stopped.</text>
</svg>
</div>
<figcaption>How a Karani order is checked: it must pass the position cap, the daily-loss cap, the kill switch, and paper testing before it reaches the market.</figcaption>
</figure>'''

# HOW IT WORKS: the pipeline a strategy travels — tested rules -> paper ->
# live -> hard limits -> dashboard. Five nodes on a connecting rail, with a
# small equity spark to make it feel like real trading data.
_how_nodes = [
  ("chart","Tested edge","~9 yrs of ES data"),
  ("phone","Paper first","live market, no risk"),
  ("bolt","Live orders","AMP over Rithmic"),
  ("shield","Hard limits","caps on every order"),
  ("gauge","Your dashboard","watch from the app"),
]
def _mini_icon(kind, cx, cy):
    # tiny 22px stroke glyphs centred at cx,cy, brand-deep stroke
    s = 'fill="none" stroke="#557790" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    g = {
      "chart": f'<path d="M{cx-8} {cy-8}v16h16" {s}/><path d="M{cx-5} {cy+4}l4 -4 3 3 5 -6" {s}/>',
      "phone": f'<rect x="{cx-6}" y="{cy-9}" width="12" height="18" rx="3" {s}/><path d="M{cx-1} {cy+6}h2" {s}/>',
      "bolt":  f'<path d="M{cx+1} {cy-9}l-8 10h6l-2 8 8 -10h-6z" {s}/>',
      "shield":f'<path d="M{cx} {cy-9}l7 3v5c0 4 -3 6.5 -7 7.5c-4 -1 -7 -3.5 -7 -7.5v-5z" {s}/><path d="M{cx-3} {cy}l2 2 4 -4" {s}/>',
      "gauge": f'<path d="M{cx} {cy+1}l3 -3" {s}/><path d="M{cx-7} {cy+5}a7 7 0 0 1 14 0" {s}/>',
    }
    return g[kind]

HOW_SVG = '''<figure class="vizwrap reveal" aria-label="Diagram: how a Karani strategy moves from tested rules to paper to live trading under hard limits, monitored from the app">
<div class="vizscroll">
<svg viewBox="0 0 720 210" role="img" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <linearGradient id="rail" x1="0" y1="0" x2="1" y2="0">
   <stop offset="0" stop-color="#6F93AC"/><stop offset=".5" stop-color="#557790"/><stop offset="1" stop-color="#2C4757"/>
  </linearGradient>
 </defs>
 <path d="M72 74 H648" fill="none" stroke="url(#rail)" stroke-width="3" stroke-linecap="round" opacity=".9"/>
 <circle r="6" fill="#CE8168">
  <animateMotion dur="5s" repeatCount="indefinite" path="M72 74 H648"/>
 </circle>
'''
for i,(kind,t,sub) in enumerate(_how_nodes):
    cx = 72 + i*144
    HOW_SVG += (
      f'<g>'
      f'<circle cx="{cx}" cy="74" r="27" fill="#fff" stroke="rgba(85,119,144,.30)"/>'
      f'<circle cx="{cx}" cy="74" r="27" fill="#6F93AC" opacity="0.06"/>'
      + _mini_icon(kind, cx, 74) +
      f'<text x="{cx}" y="124" text-anchor="middle" font-size="13" font-weight="700" fill="#2C4757">{t}</text>'
      f'<text x="{cx}" y="142" text-anchor="middle" font-size="10.5" fill="#8a7f72">{sub}</text>'
      f'<text x="{cx}" y="52" text-anchor="middle" font-size="11" font-weight="700" fill="#CE8168" opacity=".85">{i+1:02d}</text>'
      f'</g>'
    )
HOW_SVG += '''</svg>
</div>
<figcaption>The path a strategy travels at Karani: proven on years of data, run on paper, then live on your own account, held inside hard limits, and watched from the app.</figcaption>
</figure>'''

# ---- PAGE 1: HOW IT WORKS ----------------------------------------------

def build_how():
    name = "How it works"
    url = SITE + "/how-it-works.html"
    desc = ("How automated futures trading works at Karani: a backtested rules engine trades the "
            "S&P 500 E-mini on your own account, with hard risk limits and a kill switch.")
    body = ('<article class="page reveal">'
      '<div class="eyebrow">How it works</div>'
      '<h1>How automated futures trading works</h1>'
      '<p class="lead">An automated trading system turns a fixed set of trading rules into orders a '
      'computer places for you. Karani is that kind of system, built for the S&amp;P 500 E-mini '
      'futures (ES). It runs a backtested strategy on your own brokerage account, sizes every position '
      'by rule, and holds itself inside hard risk limits you set, so the day-to-day trading happens '
      'without you watching the screen.</p>'

      '<div class="answer"><b>The short version:</b> a tested strategy decides every entry, exit, and '
      'position size in advance. Karani watches the ES market, places orders through your AMP account '
      'over Rithmic, and stops automatically when it hits your daily-loss cap or contract limit. You '
      'keep the account, the settings, and a kill switch.</div>'

      + HOW_SVG +

      '<h2>What an automated trading system actually does</h2>'
      '<p>Discretionary trading means a person decides each trade in the moment. An automated trading '
      'system replaces that moment-to-moment judgement with rules that were written and tested ahead '
      'of time. The rules cover four things: when to enter, when to exit, how large the position is, '
      'and when to stop trading for the day. Once those rules are set, software reads live market data '
      'and acts on them the same way every session.</p>'
      '<p>Karani applies this to one market, the ES, because a single well-understood instrument is '
      'easier to test, monitor, and keep honest than a scattered basket. The strategy is rules-based '
      'and mechanical, so the version that was tested is the version that trades.</p>'

      '<h2>How Karani runs, step by step</h2>'
      '<ol class="steps">'
      '<li><h3>A validated edge</h3><p>Each strategy is written as explicit rules and tested across '
      'about nine years of ES market data before it is allowed anywhere near live orders. Testing that '
      'holds up across many years and market conditions is the bar for going further.</p></li>'
      '<li><h3>Paper before live</h3><p>The strategy runs on a paper account first, placing simulated '
      'orders against the live market so its behaviour can be checked before a single real dollar is '
      'at risk.</p></li>'
      '<li><h3>Live on your own account</h3><p>When it is ready, the system connects to your own AMP '
      'brokerage account through Rithmic and routes orders to the CME. The money and the account stay '
      'in your name the whole time.</p></li>'
      '<li><h3>Risk limits on every order</h3><p>Before any order goes out, Karani checks it against '
      'your contract limit and daily-loss cap. If a limit is reached, trading stops for the session. '
      'These checks run on every single order, not once a day.</p></li>'
      '<li><h3>You watch from the app</h3><p>Balance, open positions, and a systems-are-go panel show '
      'live in the iOS dashboard. You can switch strategies on or off, adjust limits, or halt '
      'everything with one tap.</p></li>'
      '</ol>'

      '<h2>Discipline, handled by software</h2>'
      '<p>The reason to automate is consistency. Software does not hesitate on a valid signal, does '
      'not chase a loss with a revenge trade, and does not skip an exit because the move looks scary. '
      'It follows the plan on every trade, including the ones a tired human would talk themselves out '
      'of. That steadiness is the main thing an automated trading system buys you.</p>'
      '<p class="callout">A tested edge, executed with machine discipline, inside limits you set.</p>'

      '<h2>How this compares to algorithmic trading</h2>'
      '<p>Algorithmic trading is the broad term for any strategy where a computer places the orders. '
      'It covers everything from bank execution algorithms to hobby trading bots. Karani sits at the '
      'systematic end of that range: a single tested strategy on one liquid futures market, run on '
      'your own account, with risk controls as a first-class part of the design rather than an '
      'afterthought.</p>'

      + cta_block("See how it would run for you.") +
      '</article>')

    qas = [
      ("How does automated futures trading work?",
       "A set of tested rules decides every entry, exit, and position size in advance. Software reads "
       "live market data, places the matching orders through your brokerage account, and stops when it "
       "reaches your risk limits. At Karani the rules trade the S&amp;P 500 E-mini (ES) on your own "
       "AMP account over Rithmic."),
      ("Is an automated trading system the same as a trading bot?",
       "A trading bot is one kind of automated trading system, usually a simple script. Karani is a "
       "systematic version of the same idea: one backtested strategy on the ES, run on a professional "
       "data feed and your own brokerage account, with hard risk limits enforced on every order."),
      ("How is this different from algorithmic trading in general?",
       "Algorithmic trading is any strategy where a computer places orders. Karani is a focused, "
       "systematic form of it: a single tested strategy on one futures market, with position caps, a "
       "daily-loss cap, and a kill switch built in."),
      ("Do I keep control of the account?",
       "Yes. The strategy runs on your own AMP brokerage account. You set the limits, switch strategies "
       "on or off, and can halt everything from the app at any time. Karani never holds your funds."),
    ]
    body += faq_block(qas)
    ld = ldjson(webpage(name, url, desc), breadcrumb(name, url), faqpage(qas))
    doc = (head("How Automated Futures Trading Works | Karani", desc, "/how-it-works.html", ld)
      + T.nav(S["navy"], "how")
      + '<section class="sec" style="padding-top:22px"><div class="wrap">'
      + crumbs(name) + body + related("how") + '</div></section>'
      + T.footer(S["cream"]) + S["mroot"] + S["script"] + '</body></html>')
    write("how-it-works.html", doc)

# ---- PAGE 2: SAFETY -----------------------------------------------------

def build_safety():
    name = "Safety"
    url = SITE + "/safety.html"
    desc = ("Automated trading risk controls at Karani: hard position limits, a daily-loss cap, a "
            "one-tap kill switch, and paper testing before any live futures order.")
    body = ('<article class="page reveal">'
      '<div class="eyebrow">Safety first</div>'
      '<h1>Futures trading risk management, built in</h1>'
      '<p class="lead">Automated trading risk controls are the part of the system that decides how '
      'much can go wrong before it stops. Karani treats them as the foundation, not a setting bolted '
      'on at the end. Every order is checked against hard position limits and a daily-loss cap, the '
      'strategy is proven on paper first, and you hold a kill switch that halts everything from your '
      'phone.</p>'

      '<div class="answer"><b>Is automated trading safe?</b> All trading carries risk, and futures '
      'trading can lose money. What responsible automation does is make the downside predictable: fixed '
      'limits the system cannot exceed, a hard daily-loss cap, and a way for you to stop it instantly. '
      'Karani is built around those controls.</div>'

      '<h2>The four risk controls</h2>'
      '<div class="specs">'
      + spec("shield","Hard position limits","A cap on how many ES contracts can be open at once. Karani cannot size past it, so a single position can never grow beyond the risk you set.")
      + spec("gauge","Daily-loss cap","A fixed dollar limit for the session. When losses reach it, Karani stops trading for the rest of the day and waits for the next session.")
      + spec("power","One-tap kill switch","Halt every strategy and pull all working orders instantly, from any device. Control never leaves your hands.")
      + spec("check","Paper before live","Every strategy proves itself on a paper account against the live market before a single real dollar is at risk.")
      + '</div>'

      + SAFETY_SVG +

      '<h2>Why a daily-loss limit matters</h2>'
      '<p>A daily-loss limit is the single most important guardrail in systematic futures trading. It '
      'puts a hard floor under a bad day. Without one, a losing streak or an unusual market can compound '
      'while no one is watching. With one, the worst case for the session is known in advance and capped '
      'in dollars. Karani checks the running total against your cap continuously, and once the cap is '
      'hit, trading for the day is over.</p>'
      '<p>Position limits do the same job for size. They stop the system from stacking contracts into a '
      'position larger than you agreed to hold, regardless of how strong a signal looks.</p>'

      '<h2>Risk checks run on every order</h2>'
      '<p>These controls are not a nightly report. They run inline, before each order leaves the '
      'system. An order that would break your contract limit or push the day past its loss cap is '
      'rejected rather than sent. Because the checks sit between the strategy and the market, no single '
      'trade can bypass them.</p>'
      '<p class="callout">Automation handles the disciplined middle of the work. You set the boundaries '
      'it runs inside.</p>'

      '<h2>You keep the account and the final say</h2>'
      '<p>Karani runs on your own AMP brokerage account, connected through Rithmic. Your funds sit with '
      'your broker, not with Karani. You approve the limits during onboarding, you can change them, and '
      'you can stop the system at any moment from the iOS app. The automation works inside the fence you '
      'build; it never owns the fence.</p>'

      + cta_block("Risk controls you can see and set.") +
      '</article>')

    qas = [
      ("Is automated trading safe?",
       "All trading carries risk, and futures trading can lose money. Responsible automation "
       "makes the risk defined: Karani enforces hard position limits and a daily-loss cap on every "
       "order, tests on paper first, and gives you a one-tap kill switch, so the downside for a "
       "session is capped and under your control."),
      ("What is a daily-loss limit?",
       "A daily-loss limit is a fixed dollar amount of loss allowed in one session. When Karani reaches "
       "it, the system stops trading for the rest of the day. It puts a known floor under a bad day "
       "instead of letting losses compound."),
      ("What happens if I want to stop trading right now?",
       "Use the kill switch in the iOS app. It halts every strategy and cancels all working orders "
       "instantly, from any device. Nothing keeps trading once you stop it."),
      ("Who holds my money?",
       "You do. Karani trades on your own AMP brokerage account over Rithmic. Your funds stay with your "
       "broker, and you keep the ability to change limits or halt the system at any time."),
    ]
    body += faq_block(qas)
    ld = ldjson(webpage(name, url, desc), breadcrumb(name, url), faqpage(qas))
    doc = (head("Automated Trading Risk Controls & Safety | Karani", desc, "/safety.html", ld)
      + T.nav(S["navy"], "safety")
      + '<section class="sec" style="padding-top:22px"><div class="wrap">'
      + crumbs(name) + body + related("safety") + '</div></section>'
      + T.footer(S["cream"]) + S["mroot"] + S["script"] + '</body></html>')
    write("safety.html", doc)

# ---- PAGE 3: PLATFORM / DASHBOARD --------------------------------------

def build_platform():
    name = "Dashboard"
    url = SITE + "/platform.html"
    desc = ("The Karani automated trading dashboard: live balance and P&L, equity over any timeframe, "
            "every trade marked win or loss, and a systems-are-go panel, in an iOS app.")
    body = ('<article class="page reveal">'
      '<div class="eyebrow">The dashboard</div>'
      '<h1>An automated trading dashboard you can read at a glance</h1>'
      '<p class="lead">An automated trading dashboard is where you watch a system without having to run '
      'it. The Karani dashboard app shows your live balance and today&rsquo;s profit and loss, your '
      'equity over any timeframe, every trade marked win or loss, the ES ticking live, and a panel that '
      'confirms the system is running. It is an iOS app, so the whole account fits on one calm screen in '
      'your pocket.</p>'

      '<figure class="shot-frame reveal">'
        '<div class="bar"><i></i><i></i><i></i><span class="url">app.karanimarkets.com</span></div>'
        '<img class="shothide" src="/assets/dash-full.png" width="1600" height="1002" '
          'alt="The Karani automated trading dashboard: live account balance, an equity curve, today&rsquo;s margin, and a systems-are-go panel" '
          'loading="lazy" decoding="async">'
        '<img class="shotshow" src="/assets/dash-mobile.png" width="820" height="706" '
          'alt="The Karani dashboard on mobile showing account balance and the day&rsquo;s trade stats" '
          'loading="lazy" decoding="async">'
        '<span class="shot-tag"><span class="dot"></span>Live &middot; Auto-trader on</span>'
      '</figure>'

      '<div class="answer"><b>What it is for:</b> monitoring, not micromanaging. You open the app to see '
      'that Karani is trading to plan, check the numbers, and, if you ever want to, adjust limits or stop '
      'everything. The day-to-day execution happens on its own.</div>'

      '<h2>What the dashboard shows</h2>'
      '<div class="specs">'
      + spec("chart","Live balance and P&amp;L","Your account balance and the session&rsquo;s profit or loss, updated as trades close, so you always know where the day stands.")
      + spec("gauge","Equity over time","The equity curve across any timeframe you pick, from a single session to the full history, so the trend is easy to read.")
      + spec("check","Every trade, win or loss","A clear record of each trade the system took, marked as a win or a loss, with the detail behind it.")
      + spec("bolt","Systems-are-go panel","A single status view for backtest, paper, and live, so you can confirm at a glance that everything is running.")
      + '</div>'

      '<h2>Built to monitor a trading system, calmly</h2>'
      '<p>Most trading screens are loud. This one is deliberately quiet. The layout puts the four things '
      'that matter in view and leaves the rest out, so a ten-second glance answers the only real '
      'question: is Karani doing what it should? When something needs your attention, the app tells you. '
      'The rest of the time it stays out of your way.</p>'
      '<p class="callout">Everything you need on one calm screen.</p>'

      '<h2>Alerts that reach your pocket</h2>'
      '<p>Because the system runs on an always-on server while the market is open, you do not need the '
      'app in front of you for it to work. The iOS app sends a push notification the moment something '
      'matters, so you can leave it closed and trust that you will hear from it when it counts.</p>'

      '<h2>Controls, not just charts</h2>'
      '<p>The dashboard is also where you steer. From the app you can switch strategies on or off, '
      'adjust your position and daily-loss limits, and halt everything with the kill switch. Monitoring '
      'and control live in the same place, so acting on what you see is one tap away.</p>'
      '<ul>'
      '<li>Switch individual strategies on or off</li>'
      '<li>Set your contract limit and daily-loss cap</li>'
      '<li>Halt all trading and cancel working orders instantly</li>'
      '<li>Review the full trade history any time</li>'
      '</ul>'

      + cta_block("See the dashboard for yourself.") +
      '</article>')

    qas = [
      ("What is an automated trading dashboard?",
       "It is a screen that lets you monitor an automated trading system without running it by hand. "
       "The Karani dashboard shows live balance and P&amp;L, your equity curve, every trade marked win "
       "or loss, and a systems-are-go status panel."),
      ("Do I have to keep the app open for Karani to trade?",
       "No. Karani runs on an always-on server while the market is open. The iOS app is for monitoring "
       "and control, and it sends a push notification when something needs your attention, so you can "
       "keep it closed."),
      ("Can I control the system from the app?",
       "Yes. From the dashboard you can switch strategies on or off, set your position and daily-loss "
       "limits, and halt everything with the kill switch."),
      ("Is the dashboard on iPhone?",
       "Yes, the Karani dashboard is an iOS app, so your balance, equity, trade history, and system "
       "status are all in your pocket."),
    ]
    body += faq_block(qas)
    ld = ldjson(webpage(name, url, desc), breadcrumb(name, url), faqpage(qas))
    doc = (head("Automated Trading Dashboard App | Karani", desc, "/platform.html", ld)
      + T.nav(S["navy"], "platform")
      + '<section class="sec" style="padding-top:22px"><div class="wrap">'
      + crumbs(name) + body + related("platform") + '</div></section>'
      + T.footer(S["cream"]) + S["mroot"] + S["script"] + '</body></html>')
    write("platform.html", doc)

def main():
    global S
    S = T.load_site()
    # Strip CSS comments from the inherited <style> so pre-existing site-chrome
    # em-dashes inside comments do not trip the language gate. Purely cosmetic:
    # the live CSS rules are untouched, only /* ... */ comments are removed.
    S["style"] = re.sub(r"/\*.*?\*/", "", S["style"], flags=re.S)
    # The inherited modal markup (contact + about modals) uses a couple of em
    # dashes. Rewrite those specific inherited strings so the page passes the
    # language gate. Visible modal copy stays clean and on-brand.
    S["mroot"] = (S["mroot"]
        .replace("reaching out &mdash; we&#39;ll", "reaching out. We&#39;ll")
        .replace("automatically &mdash; with hard", "automatically, with hard")
        .replace("kill switch &mdash; built", "kill switch, built"))
    build_how()
    build_safety()
    build_platform()

if __name__ == "__main__":
    main()
