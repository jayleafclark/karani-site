# -*- coding: utf-8 -*-
"""
Generate profile.html as the responsive "Client login" page:
  - Desktop (>560px): a login form -> /dashboard.html#app (boots into the app view)
  - Mobile (<=560px): a "download the app" message with App Store / Google Play badges
Client login links already point at /profile.html, so no nav rewiring is needed.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import template as T
SITE = "https://karanimarkets.com"

APPLE = ('<svg width="22" height="22" viewBox="0 0 384 512" fill="currentColor"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>')
PLAY = ('<svg width="20" height="20" viewBox="0 0 512 512"><path fill="#00d1ff" d="M47 32 300 256 47 480c-9-5-15-15-15-27V59c0-12 6-22 15-27z"/><path fill="#00e676" d="M47 32c4-2 9-3 14-2l253 145-63 63z"/><path fill="#ffea00" d="M363 205l55 32c17 10 17 28 0 38l-55 32-70-70z"/><path fill="#ff3d47" d="M314 337 61 482c-5 1-10 0-14-2l204-204z"/></svg>')

STYLE = """<style>
.loginwrap{max-width:430px;margin:0 auto}
.login-mobile{display:none}
.lcard{background:#fff;border:1px solid var(--line);border-radius:22px;padding:30px 28px;box-shadow:var(--shadow-card)}
.lcard label{display:block;font-size:13px;font-weight:600;color:var(--ink2);margin:14px 0 6px}
.lcard input{width:100%;border:1px solid var(--line);border-radius:12px;padding:13px 14px;font:inherit;font-size:15px;background:var(--cream);color:var(--ink)}
.lcard input:focus{outline:none;border-color:var(--brand-deep);background:#fff}
.lcard .fp{text-align:right;margin-top:8px}
.lcard .fp a{color:var(--brand-deep);font-size:13px;text-decoration:none}
.lcard .lbtn{width:100%;justify-content:center;margin-top:20px}
.ldiv{display:flex;align-items:center;gap:12px;color:var(--ink3);font-size:13px;margin:18px 0}
.ldiv:before,.ldiv:after{content:"";flex:1;height:1px;background:var(--line)}
.lgoog{width:100%;justify-content:center;gap:10px}
.lnote{text-align:center;color:var(--ink2);font-size:14px;margin-top:20px}
.lnote a{color:var(--brand-deep);font-weight:600;cursor:pointer}
.appbadge{display:inline-flex;align-items:center;gap:11px;border-radius:13px;padding:12px 20px;text-decoration:none}
@media(max-width:560px){.login-desktop{display:none}.login-mobile{display:block}}
</style>"""

def main():
    s = T.load_site()
    # On desktop we send clients to the real animated dashboard login (dashboard.html).
    # This block is only a graceful fallback if the head redirect script did not run.
    desktop = ('<div class="login-desktop" style="text-align:center;padding-top:44px">'
      '<div class="eyebrow" style="margin-bottom:10px">Client login</div>'
      '<h1 style="font-family:var(--display);font-weight:600;font-size:32px;letter-spacing:-.01em;margin-bottom:10px">Opening your dashboard</h1>'
      '<p style="color:var(--ink2);font-size:15px;margin-bottom:22px">Taking you to the Karani dashboard login.</p>'
      '<a href="/dashboard.html" class="btn btn-brand" style="justify-content:center;display:inline-flex">Continue to dashboard ' + T.ARROW + '</a>'
      '</div>')

    mobile = ('<div class="login-mobile">'
      '<div style="width:58px;height:58px;border-radius:17px;background:linear-gradient(150deg,var(--brand),var(--brand-deep));display:grid;place-items:center;margin:0 auto 18px">'
      '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/></svg></div>'
      '<h1 style="font-family:var(--display);font-weight:600;font-size:28px;text-align:center;letter-spacing:-.01em;margin-bottom:10px">Sign in from the Karani app</h1>'
      '<p style="text-align:center;color:var(--ink2);font-size:15.5px;line-height:1.6;max-width:340px;margin:0 auto 24px">Your live balance, every trade, and the one-tap kill switch live in the Karani iOS app. Download it to sign in and watch your system work.</p>'
      '<div style="display:flex;flex-direction:column;gap:12px;max-width:300px;margin:0 auto">'
      '<a class="appbadge" href="#" onclick="return false" style="background:var(--brand-night);color:#fff;justify-content:center">' + APPLE + '<span style="display:flex;flex-direction:column;line-height:1.15;font-weight:600;font-size:16px"><small style="font-size:10px;font-weight:500;opacity:.7">Download on the</small>App Store</span></a>'
      '<a class="appbadge" href="#" onclick="return false" style="background:#fff;border:1px solid var(--line);color:var(--ink);justify-content:center">' + PLAY + '<span style="display:flex;flex-direction:column;line-height:1.15;font-weight:600;font-size:16px"><small style="font-size:10px;font-weight:500;opacity:.55">Get it on</small>Google Play</span></a>'
      '</div>'
      '<p class="lnote">Not a client yet? Access is invitation only. <a data-modal="signup">Request access</a></p>'
      '</div>')

    head = (T.DOCTOP
      + '<script>if(window.matchMedia("(min-width:561px)").matches){location.replace("/dashboard.html")}</script>'
      + '<title>Client login</title>'
      '<meta name="description" content="Sign in to your Karani dashboard.">'
      '<meta name="robots" content="noindex">'
      '<link rel="canonical" href="' + SITE + '/profile.html">'
      + T.COMMONMETA + s["style"] + T.BLOGCSS + STYLE + '</head><body>')
    doc = (head + T.nav(s["navy"])
      + '<section class="sec" style="padding-top:56px;min-height:68vh"><div class="wrap"><div class="loginwrap">'
      + desktop + mobile + '</div></div></section>'
      + T.footer(s["cream"]) + s["mroot"] + s["script"] + '</body></html>')
    open(os.path.join(ROOT, "profile.html"), "w", encoding="utf-8").write(doc)
    print("profile.html (responsive login) written", round(len(doc)/1024), "KB")

if __name__ == "__main__":
    main()
