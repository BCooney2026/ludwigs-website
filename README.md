# Ludwig's Village Market & Catering: website

Public site for Ludwig's Village Market & Catering, 2918 Conestoga Rd, Glenmoore, PA.
Hosted free on GitHub Pages: https://bcooney2026.github.io/ludwigs-website/

The TV menu boards live in a different repo (`ludwigs-assets`) on purpose. Nothing here
can break the TVs, and nothing in that repo can take this site down.

## What updates by itself (no code)

Everything set on the Command Center tablet shows here within a few minutes, same as the TVs:

- Menu prices, items taken off the menu, items added (L100 and up join their category)
- Sold out today (red tag, clears at midnight)
- Today at Ludwig's: soups of the day, sandwich/chef's/dessert specials (with photos),
  Cookie of the Month, catering message, sold out list
- Announcement line at the very top (the tablet's Announcement screen)

If the feed is ever down, the site still shows the full menu with the last good prices
(kept in the visitor's browser) or the built-in fallback prices.

## What needs a rebuild

Names, descriptions, page copy and the catering menu live in:

- `data/menu.json`: menu names and descriptions (same L IDs as the TVs)
- `data/catering.json`: every catering item and price from CateringMenu_2026.pdf
- `build/build.py`: page copy, store info (hours, phone, address), page layout

After editing: `python3 build/build.py`, then commit everything.

## Files

- `index.html`, `menu/`, `catering/`, `holidays/`, `404.html`: built pages (do not hand-edit)
- `assets/css/site.css`: the whole design system
- `assets/js/site.js`: live feed, prices, Today, hours, menu search. FEED_URL is the same
  Command Center /exec?feed=1 the TVs use. Photo rules (SOUP_RULES, SPECIAL_RULES,
  COOKIE_PHOTOS) are copies of the TV board's; keep them in step.
- `assets/img/*.webp`: photos (from ludwigs-assets/boards/img, resized to 760 wide)
- `assets/video/`: Ludwig's own footage, re-encoded light for phones
- `assets/pdf/CateringMenu_2026.pdf`: hosted here so it opens over HTTPS

## Switching on ludwigsvillagemarket.com (when we have the DNS login)

1. In this repo: Settings > Pages > Custom domain: `www.ludwigsvillagemarket.com`, Enforce HTTPS.
2. At the registrar: CNAME `www` -> `bcooney2026.github.io`, and A records for the bare
   domain -> 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
3. Change `BASE` in build/build.py, rebuild, commit.
4. Repoint the QR Tiger catering code to the new catering page if wanted.

Cost: $0 for hosting. Only the domain's yearly renewal, which whoever owns it already pays.
