# -*- coding: utf-8 -*-
"""
Karani language checker — the anti-AI-slop / anti-cheese gate for the blog engine.

Adapted from the Dr. Leaf master language rules, but TUNED for a trading site:
we keep the transferable rules (AI puffery lexicon, the "not X, it's Y" contrast
cadence, em-dashes, LLM leaks, marketing hype, structural tells) and DROP the
therapy-specific word bans that collide with legitimate trading vocabulary
(system, leverage, position, volatility, drawdown, execute, edge are all fine).

Usage:
    python rules_check.py <file.html|file.txt>      -> prints hits, exit 1 if HARD
    from rules_check import scan; hits = scan(text)  -> list of (category, match)
"""
import re, sys, html

# ---- HARD categories (fail the build) ----------------------------------

# Never-legitimate AI puffery. These do not appear in real trading writing.
AI_LEXICON = [
    "delve","delves","delved","delving","tapestry","tapestries","testament",
    "underscore","underscores","underscored","underscoring","boast","boasts",
    "boasting","boasted","vibrant","captivating","majestic","nestled",
    "seamless","seamlessly","showcase","showcases","showcased","showcasing",
    "myriad","plethora","bustling","treasure trove","realm of possibilit",
]

# AI scaffolding + promotional phrases (substring, case-insensitive).
AI_PHRASES = [
    "stands as a testament","a testament to","rich tapestry","it's worth noting",
    "it is worth noting","in conclusion","in summary","to summarize","a myriad of",
    "in today's fast-paced world","in today's digital age","fast-paced world",
    "in the realm of","navigating the complexities","navigate the complexities",
    "serves as a reminder","a powerful reminder","plays a pivotal role",
    "plays a crucial role","plays a vital role","plays a significant role",
    "it's important to note","it is important to note","important to note",
    "in a world where","when it comes to","at the end of the day",
    "the bottom line is","needless to say","first and foremost","last but not least",
    "the world of","ever-evolving","ever-changing landscape","the key takeaway",
]

# Marketing hype + trading-compliance red flags (HARD — both slop and risky).
HYPE = [
    "transformative","groundbreaking","game-changing","game changing",
    "revolutionary","cutting-edge","cutting edge","unlock","unlocking","unlocked",
    "unleash","unleashing","supercharge","supercharged","next level",
    "the secret to","the secret of","holy grail","get rich","getting rich",
    "risk-free","risk free","guaranteed profit","guaranteed return","guaranteed returns",
    "guaranteed win","can't lose","cant lose","sure thing","double your money",
    "quick money","easy money","foolproof","effortless","10x your","skyrocket",
    "mind-blowing","mind blowing","jaw-dropping","jaw dropping","must-have",
    "life-changing","life changing",
]

# Leftover assistant chatter.
LLM_LEAK = [
    "as an ai language model","as a language model","as an ai model","as an ai,",
    "i'm an ai","i am an ai","as of my last knowledge update","knowledge cutoff",
    "i hope this helps","hope this helps","i cannot fulfill","i can't fulfill",
    "let me know if you'd like","feel free to let me know",
    "is there anything else you'd like","certainly! here","sure, here's",
    "sure here's","of course! here","here's a draft","here is a draft",
    "[insert","[your name","[topic]","fill in the blank","as requested",
]

# Structural regexes (HARD).
AI_REGEX = [
    (r"\bnot only\b[^.?!]{0,60}\bbut also\b", "not-only-but-also"),
    (r"(?im)^\s*overall[,:]", "overall-opener"),
    (r"(?im)^\s*in conclusion", "in-conclusion-opener"),
]

# The #1 AI tell: the "not X, it's Y" / "isn't just X, it's Y" antithesis.
# Catches comma / dash / colon / semicolon / period variants.
CONTRAST_PATTERNS = [
    r"\bit'?s not (?:about |just |only |a |an |the )?[^.?!,;:]{2,60}[.,;:—-] it'?s\b",
    r"\bthis is'?nt (?:about |just |a |an )?[^.?!,;:]{2,60}[.,;:—-] (?:it'?s|this is)\b",
    r"\bisn'?t just [^.?!,;:]{2,60}[.,;:—-] it'?s\b",
    r"\byou'?re not [^.?!,;:]{2,60}[.,;:—-] you'?re\b",
    r"\bnot because\b",
    r"\bis not the same as\b|\bisn'?t the same as\b",
    r"\bnot (?:a|an|the) [^.?!,;:]{2,50}[,;:—-] (?:a|an|but) \w",
]

EM_DASH = "—"  # —

def _strip_html(t):
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S|re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S|re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)

def _wb(words):
    return re.compile(r"(?<!\w)(?:%s)(?!\w)" % "|".join(re.escape(w) for w in words), re.I)

def scan(text, is_html=True):
    """Return list of (category, matched_text). Empty list = clean."""
    t = _strip_html(text) if is_html else text
    low = t.lower()
    hits = []
    for m in _wb(AI_LEXICON).finditer(t):
        hits.append(("ai-lexicon", m.group(0)))
    for m in _wb(HYPE).finditer(t):
        hits.append(("hype/compliance", m.group(0)))
    for p in AI_PHRASES:
        if p in low:
            hits.append(("ai-phrase", p))
    for p in LLM_LEAK:
        if p in low:
            hits.append(("llm-leak", p))
    for rx, name in AI_REGEX:
        for m in re.finditer(rx, t):
            hits.append((name, m.group(0)[:70]))
    for rx in CONTRAST_PATTERNS:
        for m in re.finditer(rx, t, re.I):
            hits.append(("contrast-cadence", m.group(0)[:70]))
    if EM_DASH in t:
        hits.append(("em-dash", EM_DASH))
    return hits

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: rules_check.py <file>"); sys.exit(2)
    raw = open(sys.argv[1], encoding="utf-8").read()
    hits = scan(raw, is_html=sys.argv[1].lower().endswith((".html",".htm")))
    if not hits:
        print("CLEAN"); sys.exit(0)
    seen=set()
    for cat, m in hits:
        k=(cat,m.lower())
        if k in seen: continue
        seen.add(k)
        print(f"  [{cat}] {m!r}")
    print(f"{len(seen)} unique HARD hit(s)")
    sys.exit(1)
