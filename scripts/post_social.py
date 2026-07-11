# -*- coding: utf-8 -*-
"""
Auto-post the most recently published article to Karani's social accounts
(X + LinkedIn) via the Upload Post API. Runs after publish in the workflow.

GATED: does nothing unless BOTH env vars are set, so it stays inert until Jay
connects Karani's handles:
  UPLOADPOST_API_KEY         Upload Post API key (Authorization: Apikey <key>)
  KARANI_UPLOADPOST_PROFILE  the Upload Post profile name that has Karani's
                             X + LinkedIn connected (e.g. "Karani")
Optional:
  KARANI_SOCIAL_PLATFORMS    comma list, default "x,linkedin"

Setup (one-time, Jay):
  1. Create @KaraniMarkets on X and a Karani Markets LinkedIn *Company Page*.
  2. In Upload Post, add a profile named "Karani" and connect those two accounts.
  3. Set the two repo secrets above (KARANI_UPLOADPOST_PROFILE = "Karani").

Posts the article's cover image + a concise caption (X-safe, <280 chars) with the
live link. Idempotent per run: the workflow calls this once, for the article it
just published (the newest log entry), so there is no re-post risk.
"""
import os, sys, json, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LOG = os.environ.get("KARANI_LOG") or os.path.join(ROOT, "content", "log.json")
SITE = "https://karanimarkets.com"
API = "https://api.upload-post.com/api/upload_photos"

def build_caption(entry):
    title = entry["title"]
    link = SITE + entry["url"]
    tags = "#futures #trading #SP500"
    # X-safe: keep the whole thing under ~280. Title + link + tags first,
    # then add the excerpt only if it still fits.
    base = f"{title}\n\n{link}\n\n{tags}"
    excerpt = entry.get("excerpt", "").strip()
    if excerpt:
        candidate = f"{title}\n\n{excerpt}\n\n{link}\n\n{tags}"
        if len(candidate) <= 275:
            return candidate
    return base

def post(entry, api_key, profile, platforms):
    caption = build_caption(entry)
    cover = f"{SITE}/assets/covers/{entry['slug']}.png"
    # Upload Post multipart form; platform[] repeated; photos[] accepts a public URL.
    fields = [("user", profile), ("title", caption), ("caption", caption)]
    for p in platforms:
        fields.append(("platform[]", p))
    fields.append(("photos[]", cover))
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(API, data=data,
        headers={"Authorization": f"Apikey {api_key}",
                 "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def main():
    api_key = os.environ.get("UPLOADPOST_API_KEY")
    profile = os.environ.get("KARANI_UPLOADPOST_PROFILE")
    if not api_key or not profile:
        print("social posting not configured (no UPLOADPOST_API_KEY / KARANI_UPLOADPOST_PROFILE); skipping")
        return 0
    platforms = [p.strip() for p in os.environ.get("KARANI_SOCIAL_PLATFORMS", "x,linkedin").split(",") if p.strip()]
    if not os.path.exists(LOG):
        print("no log.json; nothing to post"); return 0
    log = json.load(open(LOG, encoding="utf-8"))
    if not log:
        print("log empty; nothing to post"); return 0
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    entry = next((e for e in reversed(log) if e["slug"] == slug), None) if slug else log[-1]
    if not entry:
        print("no matching log entry; skipping"); return 0
    try:
        resp = post(entry, api_key, profile, platforms)
        print(f"posted '{entry['slug']}' to {','.join(platforms)}: {json.dumps(resp)[:200]}")
    except Exception as e:
        # never fail the publish workflow because social posting hiccupped
        print(f"social post failed (non-fatal): {e}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
