#!/usr/bin/env python3
"""
LUDWIG'S WEBSITE BUILDER
------------------------------------------------------------------
Builds every page from data/menu.json and data/catering.json, so the
menus are real HTML that Google can read (not just JavaScript).

Run from the repo root:   python3 build/build.py
Then commit the changed .html files.

Live things (prices, sold out, today's soups/specials/cookie/catering)
are NOT baked in here: assets/js/site.js pulls them from the Command
Center feed in the visitor's browser. This script only needs to run
when names, descriptions, page copy or the catering menu change.

When the real domain is switched on, change BASE below and rebuild.
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://bcooney2026.github.io/ludwigs-website/"   # change to https://www.ludwigsvillagemarket.com/ at domain switch

STORE = {
    "name": "Ludwig’s Village Market & Catering",
    "street": "2918 Conestoga Rd", "city": "Glenmoore", "state": "PA", "zip": "19343",
    "phone": "610-458-0700", "tel": "+16104580700",
    "email": "ludwigsmarketcatering@gmail.com",
    "fb": "https://www.facebook.com/p/Ludwigs-Village-Market-and-Catering-100063470082825/",
    "ig": "https://www.instagram.com/ludwigsvillagemarket/",
    "maps": "https://www.google.com/maps/search/?api=1&query=Ludwig%27s+Village+Market+2918+Conestoga+Rd+Glenmoore+PA+19343",
    "embed": "https://maps.google.com/maps?q=Ludwig%27s%20Village%20Market%2C%202918%20Conestoga%20Rd%2C%20Glenmoore%2C%20PA%2019343&z=14&output=embed",
}
e = lambda s: html.escape(str(s), quote=True)
MENU = json.load(open(os.path.join(ROOT, "data", "menu.json")))
CATER = json.load(open(os.path.join(ROOT, "data", "catering.json")))
VERSION = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M")

ICON = {
    "menu": '<svg viewBox="0 0 24 24"><path d="M4 5h16M4 12h16M4 19h10"/></svg>',
    "call": '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "pin": '<svg viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "cater": '<svg viewBox="0 0 24 24"><path d="M3 17h18M5 17a7 7 0 0 1 14 0M12 7V5M10 5h4"/></svg>',
    "fb": '<svg viewBox="0 0 24 24"><path d="M14 8h3V4h-3c-2.8 0-4 1.8-4 4.3V10H7v4h3v7h4v-7h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24"><path d="M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm5 3.5a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7zm0 2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM17.3 5.7a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>',
}

NAV = [("Menu", "menu/"), ("Today", "#today"), ("Catering", "catering/"), ("Holidays", "holidays/"), ("Visit", "#visit")]


def head(title, desc, path, r, body_class="", preload=""):
    canon = BASE + path
    return f'''<!doctype html>
<html lang="en" data-root="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#26382B">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ludwig’s Village Market">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="{r}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<link rel="preload" href="{r}assets/fonts/playfair-display-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}assets/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="{r}assets/css/site.css?v={VERSION}">
<link rel="preconnect" href="https://script.google.com" crossorigin>
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
'''


def header(r, active, home=False):
    def href(h):
        if h.startswith("#"):
            return (h if home else r + h)
        return r + h
    nav = "".join(f'<a href="{href(h)}"{" aria-current=\"page\"" if active == n else ""}>{n}</a>' for n, h in NAV)
    drawer = "".join(f'<a class="big" href="{href(h)}">{n}</a>' for n, h in NAV)
    return f'''<div class="announce" id="announce" role="status" data-default="Glenmoore, PA · Proudly serving Chester County since 1998">Glenmoore, PA · Proudly serving Chester County since 1998</div>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="{r if r != './' else './'}" aria-label="Ludwig’s Village Market home">
      <img src="{r}assets/img/ludwigs-logo-200.png" alt="" width="50" height="54">
      <span class="brand-txt"><b>Ludwig’s</b><span>Village Market &amp; Catering</span></span>
    </a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <a class="btn btn-brass hdr-call" href="tel:{STORE['tel']}">Call {STORE['phone']}</a>
    <button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="drawer"><span></span></button>
  </div>
</header>
<nav class="drawer" id="drawer" aria-label="Mobile">
  {drawer}
  <div class="meta">{STORE['street']}, {STORE['city']}, {STORE['state']}<br><a href="tel:{STORE['tel']}">{STORE['phone']}</a></div>
</nav>
'''


def footer(r, home=False):
    vis = "#visit" if home else r + "#visit"
    return f'''<footer class="ftr">
  <div class="wrap">
    <div class="grid">
      <div>
        <img src="{r}assets/img/ludwigs-logo-200.png" alt="Ludwig’s Village Market &amp; Catering" width="96" height="103" loading="lazy">
        <p class="tag">Good food. Great neighbors.</p>
        <p>An independent market, deli, kitchen and caterer in Glenmoore, Pennsylvania, since 1998.</p>
        <div class="social">
          <a href="{STORE['fb']}" aria-label="Ludwig’s on Facebook" rel="noopener" target="_blank">{ICON['fb']}</a>
          <a href="{STORE['ig']}" aria-label="Ludwig’s on Instagram" rel="noopener" target="_blank">{ICON['ig']}</a>
        </div>
      </div>
      <div><h4>Visit</h4><ul>
        <li>{STORE['street']}<br>{STORE['city']}, {STORE['state']} {STORE['zip']}</li>
        <li><a href="{STORE['maps']}" target="_blank" rel="noopener">Get directions</a></li>
        <li>Mon to Sat 9 am to 6:30 pm<br>Sun 10 am to 5 pm</li>
      </ul></div>
      <div><h4>Explore</h4><ul>
        <li><a href="{r}menu/">Menus</a></li>
        <li><a href="{r}menu/#pizza">Bake-at-Home Pizza</a></li>
        <li><a href="{r}menu/#dinners">Italian Dinners</a></li>
        <li><a href="{r}catering/">Catering</a></li>
        <li><a href="{r}holidays/">Holiday Meals</a></li>
        <li><a href="{vis}">Hours &amp; Directions</a></li>
      </ul></div>
      <div><h4>Contact</h4><ul>
        <li><a href="tel:{STORE['tel']}">{STORE['phone']}</a></li>
        <li><a href="mailto:{STORE['email']}">{STORE['email']}</a></li>
        <li>Gift certificates available in the store</li>
      </ul></div>
    </div>
    <div class="base"><span>© {datetime.date.today().year} Ludwig’s Village Market &amp; Catering</span><span>Prices and availability can change. Call ahead to be sure.</span></div>
  </div>
</footer>
<nav class="actionbar" aria-label="Quick actions">
  <a href="{r}menu/">{ICON['menu']}Menus</a>
  <a href="tel:{STORE['tel']}">{ICON['call']}Call</a>
  <a href="{STORE['maps']}" target="_blank" rel="noopener">{ICON['pin']}Directions</a>
  <a href="{r}catering/">{ICON['cater']}Catering</a>
</nav>
<script>window.LUDWIGS_FALLBACK = {json.dumps(MENU["fallbackPrices"])};</script>
<script src="{r}assets/js/site.js?v={VERSION}" defer></script>
</body>
</html>
'''


def img(r, name, alt, cls="", lazy=True, w=760, h=950):
    return f'<img src="{r}assets/img/{name}.webp" alt="{e(alt)}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else " fetchpriority=\"high\""}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>'


def hours_block():
    return '''<div class="openline" data-open><span class="dot"></span><span>Hours</span></div>
<table class="hours">
  <tr data-day="Mon,Tue,Wed,Thu,Fri,Sat"><td>Monday to Saturday</td><td>9:00 am to 6:30 pm</td></tr>
  <tr data-day="Sun"><td>Sunday</td><td>10:00 am to 5:00 pm</td></tr>
</table>
<p class="hours-note">Holiday hours can differ. We post them on Facebook.</p>'''


# =====================================================================
# HOME
# =====================================================================
def page_home():
    r = "./"
    S = STORE
    jsonld = {
        "@context": "https://schema.org", "@type": ["GroceryStore", "Caterer"],
        "name": "Ludwig's Village Market & Catering", "url": BASE, "telephone": "+1-610-458-0700",
        "email": S["email"], "image": BASE + "assets/img/og-image.jpg", "foundingDate": "1998",
        "address": {"@type": "PostalAddress", "streetAddress": S["street"], "addressLocality": S["city"], "addressRegion": S["state"], "postalCode": S["zip"], "addressCountry": "US"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "09:00", "closes": "18:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "10:00", "closes": "17:00"}],
        "sameAs": [S["fb"], S["ig"]], "hasMenu": BASE + "menu/", "areaServed": "Chester County, PA",
    }
    dinners = [it["n"] for it in MENU["groups"][3]["sections"][0]["items"]]
    pre = f'<link rel="preload" as="image" href="{r}assets/video/real-smores-tarts.webp" media="(max-width: 999px)">\n'
    out = head("Ludwig’s Village Market & Catering · Glenmoore, PA · Since 1998",
               "Chester County’s neighborhood gourmet market since 1998. Deli sandwiches, homemade soups every morning, bake-at-home pizza and stromboli, Italian dinners to go, and full-service catering in Glenmoore, PA.",
               "", r, "home", pre)
    out += header(r, "", home=True)
    out += f'''<script type="application/ld+json">{json.dumps(jsonld)}</script>
<main id="main">

<section class="hero" aria-label="Welcome">
  <div class="hero-media">
    <video muted loop playsinline preload="none" poster="{r}assets/video/real-smores-tarts.webp" data-src="{r}assets/video/real-smores-tarts.mp4" aria-hidden="true"></video>
  </div>
  <div class="wrap split">
    <div class="hero-copy">
      <p class="eyebrow">Chester County · Since 1998</p>
      <h1>Good food. <em>Great neighbors.</em></h1>
      <p class="sub">From a quick lunch between errands to life’s biggest celebrations, there’s always something delicious waiting at Ludwig’s.</p>
      <div class="btns">
        <a class="btn btn-brass" href="{r}menu/">Explore our menus</a>
        <a class="btn btn-ghost" href="{r}catering/">Plan your event</a>
      </div>
    </div>
    <div class="hero-frames" aria-hidden="true">
      <figure>{img(r, "bh-sandwich-08", "", "pos-low", lazy=False)}<figcaption>The Deli</figcaption></figure>
      <figure class="tall"><video muted loop playsinline preload="none" poster="{r}assets/video/real-smores-tarts.webp" data-src="{r}assets/video/real-smores-tarts.mp4"></video><figcaption>The Sweet Side</figcaption></figure>
      <figure>{img(r, "entree-spread", "", lazy=False)}<figcaption>From Our Kitchen</figcaption></figure>
    </div>
  </div>
</section>

<div class="strip"><ul><li>Est. 1998</li><li>Homemade soups daily</li><li>Bake-at-home pizza</li><li>Full-service catering</li></ul></div>

<section class="sec" id="today">
  <div class="wrap">
    <div class="sec-head row">
      <div>
        <p class="eyebrow">Today at Ludwig’s</p>
        <h2 class="big">Something delicious is <em>always happening.</em></h2>
      </div>
      <p class="today-status stale" id="today-status"><span class="dot"></span><span>Checking the counter…</span></p>
    </div>
    <div class="today-grid" id="today-grid">
      <noscript><div class="today-empty">Today’s soups and specials show here. Call <a href="tel:{S['tel']}">{S['phone']}</a>.</div></noscript>
    </div>
  </div>
</section>

<section class="sec bg-linen" id="market">
  <div class="wrap">
    <div class="sec-head row">
      <div>
        <p class="eyebrow">Explore the market</p>
        <h2 class="big">So much more than <em>sandwiches.</em></h2>
      </div>
      <a class="link-u" href="{r}menu/">See every menu</a>
    </div>
    <div class="dept-grid">
      <a class="dept reveal" href="{r}menu/#sandwiches">{img(r, "bh-sandwich-05", "Stacked deli sandwich on a white plate with kettle chips", "pos-low")}<div class="cap"><h3>The Deli</h3><p>Seventeen signature sandwiches, built to order.</p><span class="go">Sandwich menu</span></div></a>
      <a class="dept reveal" href="{r}menu/#dinners">{img(r, "entree-spread", "Trays of prepared dinners in the kitchen case")}<div class="cap"><h3>From Our Kitchen</h3><p>Dinners made by our in-house chefs.</p><span class="go">Italian dinners</span></div></a>
      <a class="dept reveal" href="#today">{img(r, "soup-chicken-noodle", "Bowl of homemade chicken noodle soup with crusty bread")}<div class="cap"><h3>Homemade Soups</h3><p>Made in house every morning. Preservative free.</p><span class="go">Today’s soups</span></div></a>
      <a class="dept reveal" href="{r}menu/#pizza">{img(r, "pizza-build", "Sauce being spread on fresh pizza dough")}<div class="cap"><h3>Pizza &amp; Stromboli</h3><p>Made fresh, baked in your oven.</p><span class="go">Bake-at-home menu</span></div></a>
      <a class="dept reveal" href="{r}catering/">{img(r, "grazing-board", "Charcuterie board with cheeses, meats and fruit")}<div class="cap"><h3>Boards &amp; Platters</h3><p>Cheese, charcuterie and fruit, ready to set out.</p><span class="go">Catering menu</span></div></a>
      <a class="dept reveal" href="#today">{img(r, "ds-strawberry-chocolate-mousse", "Strawberry chocolate mousse cup")}<div class="cap"><h3>The Sweet Side</h3><p>Mousse of the Month, dot cakes and the Cookie of the Month.</p><span class="go">This month’s treats</span></div></a>
    </div>
    <div class="also reveal">
      <h3>Also in the market</h3>
      <ul>
        <li>Fresh meats &amp; seafood</li><li>Handmade salads</li><li>Local &amp; imported cheeses</li>
        <li>Local fresh produce</li><li>Dips, sauces &amp; pastas</li><li>Gift certificates</li>
      </ul>
    </div>
  </div>
</section>

<section class="sec bg-burg on-dark" id="dinner">
  <div class="wrap split rev">
    <div class="reveal">
      <p class="eyebrow" style="color:var(--brass-lt)">Made in our kitchen. Enjoyed in yours.</p>
      <h2 class="big">Take the <em style="color:var(--brass-lt)">night off.</em></h2>
      <p class="lede">A good dinner shouldn’t mean another trip to the grocery store, another hour at the stove or another sink full of dishes. Our chefs make Italian dinners every day. Pick one up on the way home.</p>
      <ul class="dish-list">{"".join(f"<li>{e(d)}</li>" for d in dinners)}</ul>
      <p class="fine">Available daily while supplies last. Call ahead to hold yours.</p>
      <div class="btns"><a class="btn btn-brass" href="{r}menu/#dinners">See the dinner menu</a><a class="btn btn-ghost" href="tel:{S['tel']}">Call ahead</a></div>
    </div>
    <div class="frame-wrap reveal"><figure class="frame"><video muted loop playsinline preload="none" poster="{r}assets/video/real-entree-pan.webp" data-src="{r}assets/video/real-entree-pan.mp4" aria-label="Fresh trays of prepared dinners at Ludwig’s"></video></figure></div>
  </div>
</section>

<section class="sec bg-green on-dark" id="catering">
  <div class="wrap">
    <div class="split">
      <div class="reveal">
        <p class="eyebrow" style="color:var(--brass-lt)">Catering by Ludwig’s</p>
        <h2 class="big">Every occasion deserves <em style="color:var(--brass-lt)">something delicious.</em></h2>
        <p class="lede">Set menus or your own, full-service events or take-out platters. We’re happy to work with any food restrictions you have.</p>
        <div class="bars"><b>Something different?</b><br>Try our Boardwalk, Mexican or Burger Bar.</div>
        <div class="btns"><a class="btn btn-brass" href="{r}catering/">Let’s plan your event</a><a class="btn btn-ghost" href="{r}catering/#menu">Catering menu</a></div>
      </div>
      <div class="cater-photos reveal">
        <span class="a">{img(r, "event-grazing", "Grazing table set for an event")}</span>
        <span class="b">{img(r, "corporate-catering", "Sandwich trays and hot trays for an office lunch")}</span>
        <span class="c">{img(r, "fruit-platter", "Fresh fruit and cheese platter")}</span>
      </div>
    </div>
    <div class="events reveal">
      <div><h3>Weddings</h3><p>Beautiful food for your biggest day.</p></div>
      <div><h3>Corporate Events</h3><p>Office lunches to company celebrations.</p></div>
      <div><h3>Birthdays</h3><p>Enjoy the party. Leave the kitchen to us.</p></div>
      <div><h3>Bar &amp; Bat Mitzvahs</h3><p>Menus built around your family.</p></div>
      <div><h3>School Events</h3><p>Trays and boxed lunches for a crowd.</p></div>
      <div><h3>Casual Catering</h3><p>Take-out platters and small orders.</p></div>
    </div>
  </div>
</section>

<section class="sec" id="story">
  <div class="wrap split">
    <div class="frame-wrap reveal"><figure class="frame">{img(r, "storefront-flags", "The Ludwig’s Village Market storefront in Glenmoore with flags out front")}</figure></div>
    <div class="reveal">
      <p class="eyebrow">Our story</p>
      <h2 class="big">Rooted in the community. <em>Since 1998.</em></h2>
      <p class="lede">For nearly three decades, Ludwig’s has been part of everyday life in upper Chester County. A quick lunch between errands, a dinner nobody had to cook, the holiday table, the wedding reception.</p>
      <p class="lede">Our mission hasn’t changed: bring the tastiest, freshest and finest foods to the county, and serve them with a smile.</p>
      <div class="btns"><a class="link-u" href="{S['fb']}" target="_blank" rel="noopener">Follow along on Facebook</a></div>
    </div>
  </div>
</section>

<hr class="rule">

<section class="sec" id="visit">
  <div class="wrap visit">
    <div class="reveal">
      <p class="eyebrow">Visit the market</p>
      <h2 class="big">Come see <em>us.</em></h2>
      <p class="addr">{S['street']}<br>{S['city']}, {S['state']} {S['zip']}</p>
      {hours_block()}
      <div class="contact-rows">
        <a href="tel:{S['tel']}"><span>Call the market</span><span>{S['phone']}</span></a>
        <a href="mailto:{S['email']}"><span>Catering</span><span>{S['email']}</span></a>
        <a href="{S['maps']}" target="_blank" rel="noopener"><span>Directions</span><span>Open in Maps</span></a>
      </div>
    </div>
    <div class="reveal"><iframe class="map" title="Map to Ludwig’s Village Market" src="{S['embed']}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
  </div>
</section>

</main>
'''
    out += footer(r, home=True)
    return out


# =====================================================================
# MENU
# =====================================================================
def row_html(it, plus=False):
    sid = it["id"]
    search = (it["n"] + " " + it.get("d", "")).lower()
    no = f'<span class="no">#{it["no"]}</span>' if it.get("no") else ""
    price = "" if it.get("np") else f'<div class="p">{"+ " if plus else ""}<span data-price="{sid}"></span></div>'
    d = it.get("d", "")
    add = f' <span class="add">Add chicken <span data-price="{it["add"]}"></span></span>' if it.get("add") else ""
    dline = f'<div class="d">{e(d)}{add}</div>' if (d or add) else ""
    return f'<div class="mrow" data-ids="{sid}" data-search="{e(search)}"><div class="n">{no}{e(it["n"])}</div>{price}{dline}</div>'


def sec_html(sec):
    cats = "|".join(sec.get("cats", []))
    h = e(sec["h"])
    if sec.get("type") == "toppings":
        lists = "".join(f'<h4>{e(a)}</h4><div data-search="{e(b.lower())}">{e(b)}</div>' for a, b in sec["lists"])
        return f'''<div class="msec" id="{sec['id']}"><h3>{h}</h3><div class="tops"><div class="each">{e(sec['priceLabel'])}: <b data-price="{sec['priceId']}"></b></div>{lists}</div></div>'''
    if sec.get("type") == "inline":
        groups = ""
        for gname, items in sec["groups"]:
            names = "".join(f'<span data-ids="{it["id"]}" data-search="{e(it["n"].lower())}">{e(it["n"])}{"<b>+<span data-price=" + chr(34) + sec["upId"] + chr(34) + "></span></b>" if it.get("up") else ""}</span>' for it in items)
            groups += f'<h4>{e(gname)}</h4><div class="names">{names}</div>'
        return f'''<div class="msec inl" id="{sec['id']}" data-cats="{e(cats)}"><h3>{h}<span class="sizes" data-price="{sec['priceId']}"></span></h3>{groups}<p class="mnote">Flavors marked + cost a little more.</p></div>'''
    sizes = f'<span class="sizes" data-price="{sec["sizes"]}"></span>' if sec.get("sizes") else ""
    meta = f'<p class="meta">{e(sec["meta"])}</p>' if sec.get("meta") else ""
    rows = "".join(row_html(it, plus=it.get("plus", False)) for it in sec["items"])
    note = f'<p class="mnote">{e(sec["note"])}</p>' if sec.get("note") else ""
    return f'<div class="msec" id="{sec["id"]}" data-cats="{e(cats)}"><h3>{h}{sizes}</h3>{meta}<div class="mlist">{rows}</div>{note}</div>'


def page_menu():
    r = "../"
    out = head("Menus · Sandwiches, Bake-at-Home Pizza, Stromboli & Italian Dinners · Ludwig’s Glenmoore PA",
               "The full Ludwig’s Village Market menu with current prices: 17 deli sandwiches, bake-at-home pizzas, strombolis, Italian dinners and pasta specialties. Glenmoore, PA. Call 610-458-0700.",
               "menu/", r, "menu-page")
    out += header(r, "Menu")
    tabs = "".join(f'<a href="#{g["id"]}">{e(g["nav"])}</a>' for g in MENU["groups"])
    groups = ""
    for g in MENU["groups"]:
        ph = f'<img src="{r}assets/img/{g["photo"]}.webp" alt="" width="760" height="428" loading="lazy">' if g.get("photo") else ""
        bake = f'<div class="bake">{e(g["bake"])}</div>' if g.get("bake") else ""
        secs = "".join(sec_html(s) for s in g["sections"])
        groups += f'''<section class="mgroup" id="{g['id']}"><div class="wrap">
  <div class="mgroup-head{' has-ph' if ph else ''}"><div><p class="eyebrow" style="color:var(--gold)">Ludwig’s Menu</p><h2>{e(g['title'])}</h2><p class="kick">{e(g['kicker'])}</p>{bake}</div>{ph}</div>
  <div class="mcols">{secs}</div>
</div></section>'''
    out += f'''<main id="main">
<section class="phead">
  <div class="wrap">
    <p class="eyebrow" style="color:var(--gold)">Order ahead · {STORE['phone']}</p>
    <h1>Our <em>Menus</em></h1>
    <p class="lede">Every sandwich, pizza, stromboli and dinner we make, with today’s prices. Same menu as the boards in the store, updated the moment we change it.</p>
  </div>
</section>
<div class="mtools">
  <nav class="mtabs" aria-label="Menu sections">{tabs}</nav>
  <div class="msearch"><label class="sr" for="msearch">Search the menu</label><input id="msearch" type="search" placeholder="Search: turkey, pesto, meatball…" autocomplete="off"><div class="count" id="mcount" aria-live="polite"></div></div>
</div>
{groups}
<div class="wrap">
  <div class="mcta reveal"><p>Feeding a crowd?</p><a class="btn btn-brass" href="{r}catering/">See the catering menu</a></div>
  <p class="menu-foot">Prices and availability can change. Items marked <span class="tag-sold">Sold out today</span> are gone for the day. Questions about ingredients or allergies? Please ask us at the counter or call <a href="tel:{STORE['tel']}">{STORE['phone']}</a>.</p>
</div>
</main>
'''
    out += footer(r)
    return out


# =====================================================================
# CATERING
# =====================================================================
def page_catering():
    r = "../"
    S = STORE
    tabs = "".join(f'<a href="#c-{s["id"]}">{e(s["h"])}</a>' for s in CATER["sections"])
    secs = ""
    for s in CATER["sections"]:
        note = f'<p class="note">{e(s["note"])}</p>' if s.get("note") else ""
        body = ""
        for it in s.get("items", []):
            d = f'<div class="d">{e(it["d"])}</div>' if it.get("d") else ""
            p = f'<div class="p">{e(it["p"])}</div>' if it.get("p") else ""
            body += f'<div class="citem"><div class="n">{e(it["n"])}</div>{p}{d}</div>'
        for sub, rows in s.get("subs", []):
            body += f'<div class="csub"><h3>{e(sub)}</h3>' + "".join(f'<div class="citem"><div class="n">{e(n)}</div><div class="p">{e(p)}</div></div>' for n, p in rows) + "</div>"
        secs += f'<section class="csec" id="c-{s["id"]}"><h2>{e(s["h"])}</h2>{note}{body}</section>'
    pol = "".join(f"<li>{e(p)}</li>" for p in CATER["policies"])
    out = head("Catering · Weddings, Corporate & Holiday Parties · Ludwig’s Village Market, Chester County PA",
               "Full-service and take-out catering from Ludwig’s Village Market in Glenmoore, PA: sandwich trays, wrap towers, boxed lunches, carving boards, hot entrées, cheese and charcuterie, desserts. Call 610-458-0700.",
               "catering/", r, "catering-page", f'<link rel="preload" as="image" href="{r}assets/img/event-grazing.webp">\n')
    out += header(r, "Catering")
    out += f'''<main id="main">
<section class="phead photo">
  {img(r, "event-grazing", "A full grazing table of cheeses, meats and fruit set for an event", "bgimg", lazy=False)}
  <div class="wrap">
    <p class="eyebrow" style="color:var(--brass-lt)">Catering by Ludwig’s</p>
    <h1>For the moments that <em>bring us together.</em></h1>
    <p class="lede">Great food, thoughtful service and the personal attention that makes a gathering feel special. Full-service events or take-out platters.</p>
    <div class="btns"><a class="btn btn-brass" href="tel:{S['tel']}">Call {S['phone']}</a><a class="btn btn-ghost" href="mailto:{S['email']}?subject=Catering%20question">Email the catering team</a></div>
  </div>
</section>

<section class="sec bg-burg on-dark" data-show-from="2026-11-01" data-show-until="2026-12-31">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow" style="color:var(--brass-lt)">Booking now for December</p>
      <h2 class="big">Your office holiday party, <em style="color:var(--brass-lt)">catered.</em></h2>
      <p class="lede">Hot trays, cold trays, dessert trays. Sandwich trays and carving boards for the whole team, delivered or ready for pickup.</p>
      <div class="btns"><a class="btn btn-brass" href="tel:{S['tel']}">Book your party</a><a class="btn btn-ghost" href="#menu">See the menu</a></div>
    </div>
    <div class="frame-wrap reveal"><figure class="frame">{img(r, "corporate-xmas", "Holiday office party spread with sandwich trays and a carving board")}</figure></div>
  </div>
</section>

<section class="sec bg-green on-dark">
  <div class="wrap">
    <p class="eyebrow" style="color:var(--brass-lt)">What we cater</p>
    <h2 class="big">Set menus, or <em style="color:var(--brass-lt)">build your own.</em></h2>
    <div class="events reveal">
      <div><h3>Weddings</h3><p>Beautiful food for your biggest day.</p></div>
      <div><h3>Corporate Events</h3><p>Working lunches, boxed lunches, company celebrations.</p></div>
      <div><h3>Birthdays</h3><p>Be the host, not the kitchen staff.</p></div>
      <div><h3>Bar &amp; Bat Mitzvahs</h3><p>Menus built around your family.</p></div>
      <div><h3>School Events</h3><p>Trays and boxed lunches for a crowd.</p></div>
      <div><h3>Casual Catering</h3><p>Take-out platters and small orders.</p></div>
    </div>
    <div class="bars reveal"><b>Make it an experience:</b> try our Boardwalk, Mexican or Burger Bar. We’re happy to work with any food restrictions.</div>
  </div>
</section>

<div class="ctabs"><nav class="row" aria-label="Catering menu sections">{tabs}</nav></div>
<section class="sec" id="menu">
  <div class="wrap">
    <div class="sec-head row"><div><p class="eyebrow">Catering Menu 2026</p><h2 class="big">The <em>menu.</em></h2></div>
      <a class="link-u" href="{r}assets/pdf/CateringMenu_2026.pdf" target="_blank" rel="noopener">Download the PDF</a></div>
    <div class="cmenu">{secs}</div>
    <div class="policies"><p class="eyebrow">Good to know</p><ul>{pol}</ul></div>
  </div>
</section>

<section class="sec tight bg-dark on-dark">
  <div class="wrap cta-band">
    <div>
      <p class="eyebrow" style="color:var(--gold)">Let’s plan your event</p>
      <h2>Tell us the date, the headcount <em style="color:var(--gold)">and what you love.</em></h2>
      <div class="qr"><img src="{r}assets/img/qr-catering.png" alt="QR code for the Ludwig’s catering menu" width="92" height="92" loading="lazy"><span>Scan to keep the catering menu on your phone.</span></div>
    </div>
    <div class="btns" style="margin:0"><a class="btn btn-brass" href="tel:{S['tel']}">Call {S['phone']}</a><a class="btn btn-ghost" href="mailto:{S['email']}?subject=Catering%20inquiry">Email us</a></div>
  </div>
</section>
</main>
'''
    out += footer(r)
    return out


# =====================================================================
# HOLIDAYS
# =====================================================================
def hcard(r, name, photo, alt, when, text, extra="", attrs=""):
    return f'''<article class="hcard reveal"{attrs}><div class="ph">{img(r, photo, alt)}</div><div class="body"><span class="when">{e(when)}</span><h2>{name}</h2><p>{text}</p><div class="btns">{extra}<a class="btn btn-line" href="tel:{STORE['tel']}">Call to order</a></div></div></article>'''


def page_holidays():
    r = "../"
    out = head("Holiday Meals & Catering · Thanksgiving, Christmas, Easter · Ludwig’s Glenmoore PA",
               "Heat-and-serve holiday meals and holiday catering from Ludwig’s Village Market in Glenmoore, PA: Thanksgiving, Christmas, New Year’s, Easter and Mother’s Day. Call 610-458-0700.",
               "holidays/", r, "holidays-page")
    out += header(r, "Holidays")
    tg_menu = '<a class="btn btn-green" href="http://www.ludwigsvillagemarket.com/ThanksgivingMenu_2026.pdf" target="_blank" rel="noopener" data-show-until="2026-11-26">Thanksgiving 2026 menu</a>'
    cards = "".join([
        hcard(r, "Christmas", "xmas-catering", "Christmas catering spread with platters and a carving board", "December",
              "Holiday dinners to take home and heat, plus platters, carving boards and hot trays for your party. This year’s menu will be posted here.",
              attrs=' data-now-from="2026-11-27" data-now-until="2026-12-24"'),
        hcard(r, "New Year’s", "newyear-catering", "New Year’s party platters", "New Year’s Eve & Day",
              "Ring it in without the cooking. Party platters and hot trays to go.",
              attrs=' data-now-from="2026-12-26" data-now-until="2026-12-31"'),
        hcard(r, "Thanksgiving", "entree-spread", "Prepared dinners from the Ludwig’s kitchen", "November",
              "A Thanksgiving dinner worth sitting down for, ready to heat and serve. The menu posts here each fall.", tg_menu,
              attrs=' data-now-from="2026-11-01" data-now-until="2026-11-26"'),
        hcard(r, "Easter", "ds-strawberry-chocolate-mousse", "Strawberry chocolate mousse cup", "Spring",
              "Take-home Easter meals for the family. The menu posts here when it’s ready."),
        hcard(r, "Mother’s Day", "fruit-platter", "Fruit and cheese platter", "May",
              "Treat Mom to a meal nobody has to cook. Brunch packages and platters from our catering menu."),
    ])
    out += f'''<main id="main">
<section class="phead photo">
  {img(r, "xmas-catering", "Holiday catering spread", "bgimg", lazy=False)}
  <div class="wrap">
    <p class="eyebrow" style="color:var(--brass-lt)">Holiday meals</p>
    <h1>More time together. <em>Less time in the kitchen.</em></h1>
    <p class="lede">We make take-home meals for Thanksgiving, Christmas, New Year’s, Easter and Mother’s Day. Just heat and serve.</p>
  </div>
</section>
<section class="sec"><div class="wrap"><div class="hol-grid">{cards}</div>
<p class="hours-note" style="margin-top:30px">Holiday menus, prices and order deadlines are set each season. Call <a href="tel:{STORE['tel']}">{STORE['phone']}</a> for the latest.</p></div></section>
</main>
'''
    out += footer(r)
    return out


def page_404():
    r = BASE  # absolute, since 404 can be served at any depth
    out = head("Page not found · Ludwig’s Village Market", "That page isn’t on the menu.", "404.html", r)
    out += header(r, "")
    out += f'''<main id="main"><section class="phead"><div class="wrap"><p class="eyebrow" style="color:var(--brass-lt)">404</p><h1>That one’s <em>not on the menu.</em></h1>
<p class="lede">The page you wanted moved or never existed. Here’s where the good stuff is.</p>
<div class="btns"><a class="btn btn-brass" href="{r}menu/">See our menus</a><a class="btn btn-ghost" href="{r}">Home</a></div></div></section></main>
'''
    out += footer(r)
    return out


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)
    print("wrote", rel, len(text))


if __name__ == "__main__":
    write("index.html", page_home())
    write("menu/index.html", page_menu())
    write("catering/index.html", page_catering())
    write("holidays/index.html", page_holidays())
    write("404.html", page_404())
    urls = ["", "menu/", "catering/", "holidays/"]
    today = datetime.date.today().isoformat()
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
