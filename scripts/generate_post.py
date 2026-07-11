# -*- coding: utf-8 -*-
"""
The daily tick: take the next pending topic from the backlog, draft one on-brand
article via the Anthropic API, gate it through the Karani language checker
(regenerate on any violation), generate a free cover image, and write the post as
a fully SEO+GEO-structured HTML page (Article + FAQPage + BreadcrumbList JSON-LD).

Env:
  ANTHROPIC_API_KEY   required
  KARANI_MODEL        default claude-sonnet-5
  KARANI_DATE         override publish date (YYYY-MM-DD); default = today (UTC)

Usage:
  python generate_post.py            # next pending topic
  python generate_post.py <slug>     # force a specific backlog slug (testing)
Exit 0 on publish, 3 if backlog empty, 1 on hard failure.
"""
import os, sys, json, re, time, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CONTENT = os.path.join(ROOT, "content")
POSTS = os.path.join(ROOT, "posts")
COVERS = os.path.join(ROOT, "assets", "covers")
BACKLOG = os.environ.get("KARANI_BACKLOG") or os.path.join(CONTENT, "backlog.json")
LOG = os.environ.get("KARANI_LOG") or os.path.join(CONTENT, "log.json")
VOICE = os.path.join(CONTENT, "voice.md")

sys.path.insert(0, HERE)
import rules_check
from make_cover import make_cover
import template as T

MODEL = os.environ.get("KARANI_MODEL", "claude-sonnet-5")
SITE = "https://karanimarkets.com"

def _load(path, default):
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return default

def _save(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def call_api(system, messages, max_tokens=4000):
    key = os.environ["ANTHROPIC_API_KEY"]
    payload = {"model": MODEL, "max_tokens": max_tokens, "system": system, "messages": messages}
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
            return "".join(b.get("text", "") for b in data.get("content", []))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(8 * (attempt + 1)); continue
            try: detail = e.read().decode()[:400]
            except Exception: detail = ""
            raise RuntimeError(f"API HTTP {e.code}: {detail}")
    raise RuntimeError("API failed")

def parse_json(txt):
    txt = txt.strip()
    txt = re.sub(r"^```(json)?", "", txt).strip()
    txt = re.sub(r"```$", "", txt).strip()
    a, b = txt.find("{"), txt.rfind("}")
    return json.loads(txt[a:b+1])

def article_text_for_check(a):
    parts = [a.get("lead", ""), a.get("pullquote", "")]
    for s in a.get("sections", []):
        parts.append(s.get("h2", "")); parts += s.get("paras", [])
    for f in a.get("faq", []):
        parts.append(f.get("q", "")); parts.append(f.get("a", ""))
    return "\n".join(parts)

def draft(topic, system):
    user = (f"Write the article for this topic.\n\n"
            f"Primary keyword: {topic['keyword']}\n"
            f"Title: {topic['title']}\n"
            f"Category: {topic['category']}\n"
            f"Search intent: {topic.get('intent','informational')}\n"
            f"Angle / brief: {topic.get('angle','')}\n\n"
            f"Return only the JSON object per the contract.")
    msgs = [{"role": "user", "content": user}]
    for attempt in range(4):
        raw = call_api(system, msgs)
        try:
            art = parse_json(raw)
        except Exception as e:
            msgs += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": f"That was not valid JSON ({e}). Return ONLY the JSON object, no fence, no prose."}]
            continue
        hits = rules_check.scan(article_text_for_check(art), is_html=False)
        if not hits:
            return art
        uniq = sorted({f"[{c}] {m!r}" for c, m in hits})
        print(f"  attempt {attempt+1}: {len(uniq)} language violation(s), regenerating")
        msgs += [{"role": "assistant", "content": raw},
                 {"role": "user", "content":
                  "The draft broke these hard language rules:\n" + "\n".join(uniq) +
                  "\nRewrite the WHOLE article fixing every one. Do not paraphrase a banned "
                  "phrase into a near-synonym; say the real thing plainly. No em dashes, no "
                  "\"not X, it's Y\" cadence. Return only the JSON object."}]
    return art  # last attempt (may still have hits; caller decides)

def build_html(topic, art, date_iso):
    site = T.load_site()
    slug = topic["slug"]; cat = topic["category"]; title = topic["title"]
    cover_url = f"/assets/covers/{slug}.png"
    # body sections + mid pull-quote
    secs = art.get("sections", [])
    mid = max(1, len(secs)//2)
    body = ""
    for i, s in enumerate(secs):
        body += f'<h2>{T.esc(s["h2"])}</h2>'
        for p in s.get("paras", []):
            body += f"<p>{p}</p>"
        if i == mid-1 and art.get("pullquote"):
            body += f'<blockquote>{T.esc(art["pullquote"])}</blockquote>'
    # faq
    faq_html = ""
    faq = art.get("faq", [])
    if faq:
        faq_html = '<section class="faq"><div class="wrap"><h2>Common questions</h2>'
        for f in faq:
            faq_html += f'<div class="qa"><h3>{T.esc(f["q"])}</h3><p>{f["a"]}</p></div>'
        faq_html += "</div></section>"
    back = ('<a class="back" href="/blog.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>Back to blog</a>')
    amenu = f'{art.get("read_time","6 min read")} &middot; {T.esc(cat)} &middot; By Karani Markets'
    article = ('<article class="article reveal">' + back +
        f'<div class="eyebrow">{T.esc(cat)}</div>'
        f'<h1>{T.esc(title)}</h1>'
        f'<div class="amenu">{amenu}</div>'
        f'<img class="cover" src="{cover_url}" alt="{T.esc(title)}" width="1200" height="630">'
        f'<p class="lead">{art["lead"]}</p>' + body + '</article>')
    cta = ('<div class="artcta"><div style="background:linear-gradient(160deg,var(--brand-deep),var(--brand-night));'
           'border-radius:22px;padding:28px 30px;color:#fff">'
           '<h3 style="font-family:var(--display);font-weight:600;font-size:22px;margin-bottom:6px">Karani runs the disciplined part for you</h3>'
           '<p style="color:rgba(255,255,255,.82);font-size:15px;max-width:520px;margin-bottom:16px">A tested, rules-based system on the S&amp;P 500 futures, with hard risk limits and a kill switch you control. Access is invite-only.</p>'
           '<button class="btn btn-brand" data-modal="signup">Request access ' + T.ARROW + '</button></div></div>')

    desc = T.esc(art.get("meta_description", title))
    # JSON-LD
    ld_article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": art.get("meta_description", title),
        "image": SITE + cover_url,
        "author": {"@type": "Organization", "name": "Karani Markets", "url": SITE},
        "publisher": {"@type": "Organization", "name": "Karani",
                      "logo": {"@type": "ImageObject", "url": SITE + "/assets/favicon.png"}},
        "datePublished": date_iso, "dateModified": date_iso,
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE}/posts/{slug}.html"},
        "articleSection": cat,
    }
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog.html"},
        {"@type": "ListItem", "position": 3, "name": title, "item": f"{SITE}/posts/{slug}.html"}]}
    lds = [ld_article, ld_bc]
    if faq:
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", f["a"])}}
            for f in faq]})
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)

    head = (T.DOCTOP + f'<title>{T.esc(title)} — Karani</title>'
        f'<meta name="description" content="{desc}">'
        f'<link rel="canonical" href="{SITE}/posts/{slug}.html">'
        '<meta property="og:type" content="article">'
        f'<meta property="og:title" content="{T.esc(title)}">'
        f'<meta property="og:description" content="{desc}">'
        f'<meta property="og:url" content="{SITE}/posts/{slug}.html">'
        f'<meta property="og:image" content="{SITE + cover_url}">'
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        f'<meta name="twitter:title" content="{T.esc(title)}">'
        f'<meta name="twitter:image" content="{SITE + cover_url}">'
        + T.COMMONMETA + ld_html + site["style"] + T.BLOGCSS + "</head><body>")
    doc = (head + T.nav(site["navy"], "blog")
        + '<section class="sec" style="padding-top:24px"><div class="wrap">' + article + "</div></section>"
        + faq_html
        + '<section class="sec" style="padding-top:6px"><div class="wrap">' + cta + "</div></section>"
        + T.footer(site["cream"]) + site["mroot"] + site["script"] + "</body></html>")
    return doc

def main():
    backlog = _load(BACKLOG, [])
    log = _load(LOG, [])
    if not backlog:
        print("backlog empty - need keyword research"); sys.exit(3)
    published_slugs = {e["slug"] for e in log}
    force = sys.argv[1] if len(sys.argv) > 1 else None
    topic = None
    if force:
        topic = next((t for t in backlog if t["slug"] == force), None)
        if not topic: print("slug not in backlog:", force); sys.exit(1)
    else:
        topic = next((t for t in backlog if t.get("status") == "pending"
                      and t["slug"] not in published_slugs), None)
    if not topic:
        print("no pending topic"); sys.exit(3)

    date_iso = os.environ.get("KARANI_DATE") or datetime.datetime.utcnow().strftime("%Y-%m-%d")
    print(f"Generating: {topic['slug']}  (kw: {topic['keyword']})  model={MODEL}")
    system = open(VOICE, encoding="utf-8").read()
    art = draft(topic, system)

    # final hard gate
    hits = rules_check.scan(article_text_for_check(art), is_html=False)
    if hits:
        uniq = sorted({f"[{c}] {m!r}" for c, m in hits})
        print("FAILED language gate after retries:\n  " + "\n  ".join(uniq)); sys.exit(1)

    os.makedirs(POSTS, exist_ok=True)
    make_cover(topic["slug"], topic["category"], topic["title"],
               os.path.join(COVERS, topic["slug"] + ".png"))
    doc = build_html(topic, art, date_iso)
    out = os.path.join(POSTS, topic["slug"] + ".html")
    open(out, "w", encoding="utf-8").write(doc)

    log.append({"slug": topic["slug"], "keyword": topic["keyword"], "title": topic["title"],
                "category": topic["category"], "kd": topic.get("kd"), "sv": topic.get("sv"),
                "excerpt": art.get("meta_description", ""), "read_time": art.get("read_time", ""),
                "date": date_iso, "url": f"/posts/{topic['slug']}.html"})
    _save(LOG, log)
    for t in backlog:
        if t["slug"] == topic["slug"]:
            t["status"] = "published"
    _save(BACKLOG, backlog)
    print(f"PUBLISHED {out}  ({round(len(doc)/1024)} KB)")

if __name__ == "__main__":
    main()
