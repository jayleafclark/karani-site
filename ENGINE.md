# Karani content engine

An always-on SEO + GEO blog engine for karanimarkets.com. Each weekday it drafts one
on-brand, keyword-targeted article as **Karani Markets**, runs it through a language
checker, generates a free on-brand cover image, and publishes it with full structured
data. Hands-off after setup.

Built on the `automated-seo-geo-content` method (keyword research → on-brand draft →
GEO layer → publish → verify → repeat) with the Dr. Leaf language rules adapted for a
trading site (anti-AI-slop, no em dashes, no "not X, it's Y" cadence, no hype, no
compliance-risky claims).

## Layout (lives at repo root)

    scripts/
      generate_post.py   the daily tick: pick next backlog topic, draft via Anthropic
                         API, language-gate (regenerate on any violation), cover, write
                         posts/<slug>.html with Article + FAQ + Breadcrumb JSON-LD
      build_index.py     rebuild blog.html, sitemap.xml, llms.txt from content/log.json
      make_cover.py      free PIL cover image (cream/navy brand card, candlestick motif)
      rules_check.py     the language gate (banned puffery, contrast cadence, em dash,
                         hype, LLM leaks, trading-compliance red flags)
      template.py        shared render kit (pulls CSS/nav/footer/logo from index.html)
    content/
      backlog.json       ordered keyword queue {keyword,kd,sv,intent,category,slug,title,angle,status}
      log.json           publish ledger (dedupe + audit trail)
      voice.md           the writer's system brief (voice + rules + output contract)
    posts/<slug>.html    generated articles
    assets/covers/*.png  generated covers
    assets/Jost.ttf, k_navy.png, k_light.png   brand assets for cover generation
    .github/workflows/publish.yml   the weekday cron

## Cadence

One post each weekday (`cron: 0 14 * * 1-5`). Aggressive but human-looking: a brand-new
domain that dumps hundreds of posts at once trips Google's scaled-content-abuse signal, so
we drip. 262 topics in the backlog ≈ a year of weekdays.

## Run it

    # one post (next pending backlog topic)
    ANTHROPIC_API_KEY=... KARANI_MODEL=claude-sonnet-5 python scripts/generate_post.py
    python scripts/build_index.py

    # force a specific topic (testing): pass its slug
    python scripts/generate_post.py some-slug
    # point at alternate files (testing): KARANI_BACKLOG / KARANI_LOG env vars

The GitHub Action commits as "Karani Markets" (no personal name appears anywhere). It
needs one repo secret: `ANTHROPIC_API_KEY`.

## Done-condition

A post is only logged after it is written to disk and passes the language gate. The Action
publishes by committing; GitHub Pages serves it. Re-run `build_index.py` any time posts
change to refresh the blog index, sitemap, and llms.txt.
