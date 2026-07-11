# -*- coding: utf-8 -*-
"""
Free, on-brand blog cover generator for Karani (no paid image credits).

Produces a 1200x630 cover PNG per post: cream/navy brand ground, a subtle
candlestick + trendline motif in the lower band, a category eyebrow, the title
set in Jost, a terracotta accent bar, and the small Karani mark. Palette rotates
deterministically by slug so covers are varied but cohesive.

    python make_cover.py <slug> <category> <title> [out_dir]
    from make_cover import make_cover; make_cover(slug, category, title, out_path)
"""
import sys, os, hashlib
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
W, H = 1200, 630

# brand palette
CREAM   = (251, 247, 239)
CREAM2  = (244, 236, 222)
INK     = (59, 50, 41)
INK2    = (124, 114, 100)
BRAND   = (111, 147, 172)
DEEP    = (85, 119, 144)
NIGHT   = (44, 71, 87)
TERRA   = (206, 129, 104)
CREAMTX = (244, 238, 228)

# (bg, title color, eyebrow color, motif color, logo file, accent)
VARIANTS = [
    (CREAM,  INK,     TERRA, DEEP,  "k_navy.png",  TERRA),
    (CREAM2, INK,     DEEP,  BRAND, "k_navy.png",  TERRA),
    (NIGHT,  CREAMTX, TERRA, BRAND, "k_light.png", TERRA),
    (DEEP,   CREAMTX, CREAMTX, (150,178,197), "k_light.png", TERRA),
]

def _font(sz):
    return ImageFont.truetype(os.path.join(ASSETS, "Jost.ttf"), sz)

def _seedvals(slug, n, lo, hi):
    """Deterministic pseudo-random ints from the slug (no RNG)."""
    out, h = [], hashlib.sha256(slug.encode()).digest()
    i = 0
    while len(out) < n:
        if i >= len(h):
            h = hashlib.sha256(h).digest(); i = 0
        out.append(lo + (h[i] % (hi - lo + 1)))
        i += 1
    return out

def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def _blend(fg, bg, a):
    return tuple(int(fg[i]*a + bg[i]*(1-a)) for i in range(3))

def _draw_motif(im, d, color, bg):
    """Subtle candlestick + trendline band across the lower third."""
    faint = _blend(color, bg, 0.16)
    line  = _blend(color, bg, 0.5)
    base_y = 520
    # faint horizontal gridlines
    for gy in range(300, 560, 46):
        d.line([(0, gy), (W, gy)], fill=_blend(color, bg, 0.07), width=1)
    slug_seed = _seedvals("motif"+str(color), 26, 0, 100)
    x = 70; prev = base_y - 40; pts = []
    for k in range(26):
        span = 26 + slug_seed[k] % 40           # candle height
        mid  = base_y - (slug_seed[(k*3) % 26] % 120)  # candle center
        top, bot = mid - span//2, mid + span//2
        col = _blend(color, bg, 0.30 if slug_seed[k] % 2 else 0.22)
        d.line([(x, top), (x, bot)], fill=line, width=1)          # wick
        d.rectangle([x-7, min(top+6,mid-4), x+7, max(bot-6,mid+4)], fill=col)  # body
        pts.append((x, mid - span))
        x += 42
    # gentle uptrend polyline
    d.line(pts, fill=_blend(color, bg, 0.55), width=3, joint="curve")

def make_cover(slug, category, title, out_path):
    v = int(hashlib.sha256(slug.encode()).hexdigest(), 16) % len(VARIANTS)
    bg, tcol, eyecol, motif, logof, accent = VARIANTS[v]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    _draw_motif(im, d, motif, bg)

    PAD = 84
    # eyebrow (category, uppercase, spaced)
    eb = category.upper()
    ef = _font(26)
    spaced = " ".join(list(eb.replace(" ", "  ")))
    # simple letter-spacing by drawing with tracking
    x = PAD; y = 92
    for ch in eb.upper():
        d.text((x, y), ch, font=ef, fill=eyecol)
        x += d.textlength(ch, font=ef) + 6
    # accent bar
    d.rectangle([PAD, 138, PAD+58, 144], fill=accent)

    # title (Jost, size adapts to length)
    size = 74 if len(title) <= 42 else (64 if len(title) <= 62 else 54)
    tf = _font(size)
    lines = _wrap(d, title, tf, W - PAD*2)
    ly = 188
    lh = int(size * 1.16)
    for ln in lines[:4]:
        d.text((PAD, ly), ln, font=tf, fill=tcol)
        ly += lh

    # footer: small logo + wordmark + url
    try:
        logo = Image.open(os.path.join(ASSETS, logof)).convert("RGBA")
        r = 46 / logo.height
        logo = logo.resize((int(logo.width*r), 46))
        im.paste(logo, (PAD, H-86), logo)
        d.text((PAD + logo.width + 16, H-84), "Karani", font=_font(34), fill=tcol)
    except Exception:
        d.text((PAD, H-84), "Karani", font=_font(34), fill=tcol)
    url = "karanimarkets.com"
    uf = _font(26)
    d.text((W - PAD - d.textlength(url, font=uf), H-78), url, font=uf, fill=_blend(tcol, bg, 0.7))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    im.save(out_path)
    return out_path

if __name__ == "__main__":
    slug, cat, title = sys.argv[1], sys.argv[2], sys.argv[3]
    outdir = sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, "..", "assets", "covers")
    p = make_cover(slug, cat, title, os.path.join(outdir, slug + ".png"))
    print("cover:", p)
