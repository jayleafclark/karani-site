# -*- coding: utf-8 -*-
"""
Generate profile.html: a fast, on-brand bounce page that immediately redirects
to the real client dashboard at https://app.karanimarkets.com/sign-in.

This page is a fallback only. Every real "Client login" link on the site (nav,
mobile menu, footer) points DIRECTLY at https://app.karanimarkets.com/sign-in
now, so this URL is reached only via old bookmarks/backlinks or direct visits
to /profile.html. It exists purely to avoid a dead link for those. robots
"noindex" keeps it out of search results.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
APP_SIGNIN = "https://app.karanimarkets.com/sign-in"

DOC = ("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>Karani — Client Access</title>
<meta http-equiv="refresh" content="0; url=""" + APP_SIGNIN + """" />
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@500;700&family=Space+Mono&display=swap" rel="stylesheet" />
<style>
  :root{--cream:#FBF7EF;--base:#EFE7D8;--ink:#132630;--blue:#557790;}
  *{box-sizing:border-box;margin:0}html,body{height:100%}
  body{background:var(--base);color:var(--ink);font-family:'Jost',system-ui,sans-serif;display:flex;align-items:center;justify-content:center;overflow:hidden}
  .wash{position:fixed;border-radius:50%;filter:blur(90px);z-index:0}
  .s{width:60vmax;height:60vmax;left:-20vmax;top:-24vmax;background:radial-gradient(circle,rgba(150,170,158,.85),transparent)}
  .p{width:56vmax;height:56vmax;right:-18vmax;bottom:-22vmax;background:radial-gradient(circle,rgba(224,176,146,.8),transparent)}
  .card{position:relative;z-index:1;text-align:center}
  .word{font-weight:700;font-size:2.4rem;letter-spacing:-.02em}.word span{color:#CE8168}
  .eyebrow{margin-top:.6rem;font-family:'Space Mono',monospace;font-size:.72rem;letter-spacing:.24em;text-transform:uppercase;color:rgba(19,38,48,.55)}
  .spin{margin:1.6rem auto 0;width:26px;height:26px;border:2px solid rgba(19,38,48,.15);border-top-color:var(--blue);border-radius:50%;animation:sp .8s linear infinite}
  .fb{margin-top:1.2rem;font-family:'Space Mono',monospace;font-size:.72rem;color:rgba(19,38,48,.5)}.fb a{color:var(--blue)}
  @keyframes sp{to{transform:rotate(360deg)}}
  @media(prefers-reduced-motion:reduce){.spin{animation:none}}
</style>
</head>
<body>
  <div class="wash s"></div><div class="wash p"></div>
  <div class="card">
    <div class="word">Karani<span>.</span></div>
    <div class="eyebrow">Client Access</div>
    <div class="spin" role="status" aria-label="Opening secure sign in"></div>
    <div class="fb">Opening secure sign in… <a href=\"""" + APP_SIGNIN + """\">continue&nbsp;&rarr;</a></div>
  </div>
  <script>location.replace(\"""" + APP_SIGNIN + """\");</script>
</body>
</html>
""")

def main():
    path = os.path.join(ROOT, "profile.html")
    open(path, "w", encoding="utf-8").write(DOC)
    print("profile.html (bounce -> app.karanimarkets.com/sign-in) written", round(len(DOC)/1024), "KB")

if __name__ == "__main__":
    main()
