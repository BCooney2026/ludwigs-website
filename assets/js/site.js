/*
  LUDWIG'S WEBSITE: live data + page behavior
  ------------------------------------------------------------------
  - FEED_URL is the same Command Center feed the TVs read. Change a
    price, 86 an item, or set today's soups/specials/cookie/catering on
    the tablet and the TVs AND this site follow.
  - The site never depends on the feed to show a menu: every page ships
    with the full menu in its HTML (built by build/build.py), and the last
    good feed is kept in this browser. If the feed is down, visitors still
    see the menu with the last known prices.
  - PHOTO RULES below are a copy of the ones in the TV board
    (boards/v1/menu.html) and the tablet (Index.html). Keep all three in
    step when a rule is added.
*/
(function () {
  "use strict";

  var FEED_URL = "https://script.google.com/macros/s/AKfycbxti1E8FtIh0mmDJVuVwIBCS2jgfZCdJSIJ6Po85z2Ci_YpRxkKGE2DLT1AA-i61VNTvw/exec?feed=1";
  var STORE_KEY = "ludwigs_site_feed_v1";
  var TZ = "America/New_York";
  var ROOT = document.documentElement.getAttribute("data-root") || "./";
  var IMG = ROOT + "assets/img/";

  /* ---------------- small helpers ---------------- */
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function today() { return new Date().toLocaleDateString("en-CA", { timeZone: TZ }); }
  function nowParts() {
    var p = {};
    new Intl.DateTimeFormat("en-US", { timeZone: TZ, weekday: "short", hour: "numeric", minute: "numeric", hour12: false })
      .formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    return { day: p.weekday, mins: (Number(p.hour) % 24) * 60 + Number(p.minute) };
  }
  /** Always show cents: "$12" -> "$12.00", "$12.5" -> "$12.50". */
  function cents(str) {
    return String(str || "").replace(/\$(\d+)(?:\.(\d{1,2}))?(?!\d)/g, function (m, d, c) { return "$" + d + "." + ((c || "") + "00").slice(0, 2); });
  }
  /** One size out of "Small $13.00 / Large $21.95". */
  function sizePart(str, label) {
    var part = String(str || "").split("/").map(function (s) { return s.trim(); })
      .filter(function (s) { return s.toLowerCase().indexOf(label.toLowerCase()) === 0; })[0];
    return part ? part.replace(/^[A-Za-z]+\s+/, "") : "";
  }
  /** "Small $13.00 / Large $21.95" -> labelled HTML. */
  function sizesHtml(str, labels) {
    labels = labels || {};
    return String(str).split("/").map(function (part) {
      var m = part.trim().match(/^([A-Za-z]+)\s+(.*)$/);
      return m ? "<small>" + esc(labels[m[1]] || m[1]) + "</small>" + esc(m[2]) : esc(part.trim());
    }).join("");
  }

  /* ---------------- feed ---------------- */
  var FEED = null;
  try { FEED = JSON.parse(localStorage.getItem(STORE_KEY) || "null"); } catch (e) {}
  var feedFresh = false;

  function priceOf(id) {
    if (FEED && Array.isArray(FEED.items)) {
      for (var i = 0; i < FEED.items.length; i++) if (FEED.items[i].id === id && FEED.items[i].price) return String(FEED.items[i].price).trim();
    }
    return (window.LUDWIGS_FALLBACK || {})[id] || "";
  }
  function isRemoved(id) { return !!(FEED && Array.isArray(FEED.removed) && FEED.removed.indexOf(id) >= 0); }
  function isSoldOut(id) { return !!(FEED && FEED.soldOutDate === today() && Array.isArray(FEED.soldOut) && FEED.soldOut.indexOf(id) >= 0); }
  function itemName(id) {
    var it = FEED && Array.isArray(FEED.items) ? FEED.items.filter(function (x) { return x.id === id; })[0] : null;
    return it ? String(it.item || "").replace(/^#\d+\s*/, "") : "";
  }

  function loadFeed() {
    var ctl = "AbortController" in window ? new AbortController() : null;
    var t = setTimeout(function () { if (ctl) ctl.abort(); }, 9000);
    fetch(FEED_URL, { cache: "no-store", signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.json(); })
      .then(function (f) {
        clearTimeout(t);
        if (!f || !Array.isArray(f.items)) throw new Error("bad feed");
        FEED = f; feedFresh = true;
        try { localStorage.setItem(STORE_KEY, JSON.stringify(f)); } catch (e) {}
        renderAll();
      })
      .catch(function () { clearTimeout(t); renderAll(); });
  }

  /* ---------------- menu: prices, sold out, removed, new items ---------------- */
  var SIZE_LABEL = { Small: "Small 10″", Large: "Large 16″" };
  function renderMenu() {
    // Prices
    $$("[data-price]").forEach(function (el) {
      var id = el.getAttribute("data-price"), size = el.getAttribute("data-size");
      var p = priceOf(id);
      if (size) p = sizePart(p, size);
      if (!p) { el.textContent = ""; return; }
      el.innerHTML = /\//.test(p) ? sizesHtml(cents(p), SIZE_LABEL) : esc(cents(p));
      var pc = el.closest(".p"); if (pc && pc.parentNode.classList.contains("mrow")) pc.classList.toggle("multi", /\//.test(p));
    });
    // Rows: removed = hidden, sold out = tag
    $$("[data-ids]").forEach(function (row) {
      var ids = row.getAttribute("data-ids").split(",");
      var gone = ids.every(isRemoved), out = ids.every(isSoldOut);
      row.hidden = gone;
      row.classList.toggle("out", out);
      var tag = $(".tag-sold", row);
      if (out && !tag) { var target = $(".n", row) || row; target.insertAdjacentHTML("beforeend", ' <span class="tag-sold">Sold out today</span>'); }
      if (!out && tag) tag.remove();
    });
    // Items added on the tablet (L100 and up) join the section for their category.
    if (FEED && Array.isArray(FEED.items)) {
      FEED.items.forEach(function (it) {
        var m = /^L(\d+)$/.exec(it.id || "");
        if (!m || Number(m[1]) < 100 || !it.item || isRemoved(it.id)) return;
        if ($('[data-ids="' + it.id + '"]')) return;
        var sec = $$("[data-cats]").filter(function (s) { return s.getAttribute("data-cats").split("|").indexOf(String(it.category || "")) >= 0; })[0];
        if (!sec) return;
        var list = $(".mlist", sec) || $(".names", sec);
        if (!list) return;
        if (list.classList.contains("names")) {
          list.insertAdjacentHTML("beforeend", '<span data-ids="' + esc(it.id) + '" data-search="' + esc(String(it.item).toLowerCase()) + '">' + esc(it.item) + "</span>");
        } else {
          list.insertAdjacentHTML("beforeend", '<div class="mrow" data-ids="' + esc(it.id) + '" data-search="' + esc(String(it.item).toLowerCase()) + '"><div class="n">' + esc(it.item) + '</div><div class="p" data-price="' + esc(it.id) + '">' + esc(cents(it.price || "")) + "</div></div>");
        }
      });
    }
  }

  /* ---------------- photo rules (copy of the TV board's) ---------------- */
  var SOUP_PHOTOS = {
    chickennoodle: "soup-chicken-noodle", italianwedding: "soup-italian-wedding",
    kennettsquaremushroom: "soup-mushroom", mushroom: "soup-mushroom", creamofmushroom: "soup-mushroom",
    beefchili: "soup-beef-chili", chili: "soup-beef-chili",
    lasagna: "soup-lasagna", seafoodbisque: "soup-seafood-bisque",
    vegetable: "soup-vegetable", hamsplitpea: "soup-split-pea", splitpea: "soup-split-pea", hamandsplitpea: "soup-split-pea",
    beefymac: "soup-beefy-mac", loadedbakedpotato: "soup-loaded-potato", snapper: "soup-snapper"
  };
  var SOUP_RULES = [
    [/blackbean/, "soup-black-bean-chili"], [/whitechicken|chickenchili|mangochicken|chipotlechicken/, "soup-white-chicken-chili"],
    [/turkeychili/, "soup-turkey-chili"], [/chili/, "soup-beef-chili"], [/squash|pumpkin|parsnip|sweetpotato/, "soup-squash-bisque"],
    [/frenchonion/, "soup-french-onion"], [/clam/, "soup-clam-chowder"], [/cornnoodle/, "soup-chicken-corn-noodle"],
    [/corn/, "soup-corn-chowder"], [/lobster|crab|shrimp|seafood/, "soup-seafood-bisque"], [/snapper/, "soup-snapper"],
    [/tomato/, "soup-creamy-tomato"], [/stuffedpepper|stuffedcabbage|cabbageandbeef/, "soup-stuffed-pepper"],
    [/cabbage/, "soup-ham-cabbage"], [/stew/, "soup-beef-stew"], [/orzo/, "soup-lemon-chicken-orzo"],
    [/tortellini/, "soup-tortellini"], [/minestrone|pasta|penne/, "soup-minestrone"], [/ramen|miso/, "soup-miso-ramen"],
    [/coconut|lemongrass|thai|curry/, "soup-coconut-curry"], [/potpie/, "soup-chicken-pot-pie"],
    [/broccoli|cauliflower/, "soup-broccoli-cheddar"], [/loaded/, "soup-loaded-potato"], [/potato/, "soup-creamy-potato"],
    [/florentine/, "soup-creamy-florentine"], [/whitebean|spinach|tuscan/, "soup-spinach-white-bean"],
    [/barley/, "soup-beef-barley"], [/splitpea|lentil/, "soup-split-pea"], [/mushroom/, "soup-mushroom"],
    [/wedding|meatball/, "soup-italian-wedding"], [/rice/, "soup-chicken-rice"], [/lasagna/, "soup-lasagna"],
    [/mac/, "soup-beefy-mac"], [/(chicken|turkey|beef|sausage|hearty)\w*(veg)/, "soup-chicken-vegetable"],
    [/veg/, "soup-vegetable"], [/noodle/, "soup-chicken-noodle"]
  ];
  var SPECIAL_RULES = [
    [/elvis|peanutbutter/, "sp-elvis"], [/tuna/, "sp-tuna-melt"], [/pulledpork/, "sp-bbq-pulled-pork"],
    [/manchego/, "sp-ham-manchego"], [/meatball/, "sp-meatball-hoagie"], [/fig|sweetspicy|sweetandspicy/, "sp-sweet-spicy-prosciutto"],
    [/hothoney/, "sp-hot-honey-cutlet"], [/spicyitalian|sassy/, "sp-spicy-italian"], [/rosemary/, "sp-rosemary-chicken"],
    [/cordon/, "sp-cordon-bleu"], [/blt|chickenclub|grilledchicken\w*bacon/, "sp-chicken-blt"],
    [/stuffing|hotturkey/, "sp-hot-turkey-hoagie"], [/cutlet\w*gravy|gravy\w*cutlet/, "sp-cutlet-gravy-cranberry"],
    [/turkey\w*bacon\w*wrap|turkeybaconcheddar/, "sp-turkey-bacon-wrap"], [/potroast/, "sp-pot-roast-grinder"],
    [/sausage\w*pepper|pepper\w*sausage/, "sp-sausage-peppers"], [/pastrami/, "sp-tender-pastrami-hoagie"],
    [/parm/, "sp-chicken-parm"], [/tender\w*wrap|toasterwrap/, "wrap-special"],
    [/cutlet\w*prosciutto|prosciutto\w*cutlet|balsamic/, "sp-cutlet-prosciutto"],
    [/strawberry\w*mousse|strawberrychocolate/, "ds-strawberry-chocolate-mousse"],
    [/caramel\w*cheesecake|cheesecakemousse/, "ds-caramel-cheesecake-mousse"],
    [/smore\w*mousse|mousse\w*smore/, "ds-smores-mousse"], [/spicedapple|applesandcream|applescream/, "ds-spiced-apples-cream"],
    [/mint\w*mousse|mintchocolate/, "ds-mint-mousse"]
  ];
  var COOKIE_PHOTOS = [
    [/smore/, "cookie-smores"], [/applepie/, "cookie-apple-pie-oatmeal"], [/bacon/, "cookie-bacon-chocolate-chip"],
    [/cran/, "cookie-oatmeal-cran-raisin"], [/sprinkle/, "sprinkle-cookies"]
  ];
  function key(s) { return String(s || "").toLowerCase().replace(/[^a-z]/g, ""); }
  function rule(rules, text) { var k = key(text); for (var i = 0; i < rules.length; i++) if (rules[i][0].test(k)) return rules[i][1]; return ""; }
  function soupFile(name) { var k = key(name).replace(/soup$/, ""); return SOUP_PHOTOS[k] || rule(SOUP_RULES, k); }

  // Photos made on the tablet live in the Command Center's Drive (?img=<id>).
  var photoCache = {};
  function tabletPhoto(id, done) {
    if (!id || id === "none") return;
    if (photoCache[id]) { done(photoCache[id]); return; }
    fetch(FEED_URL.replace(/\?.*$/, "") + "?img=" + encodeURIComponent(id), { cache: "force-cache" })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (j && /^data:image\//.test(j.data || "")) { photoCache[id] = j.data; done(j.data); } })
      .catch(function () {});
  }

  /* ---------------- Today at Ludwig's ---------------- */
  function liveToday() {
    var s = (FEED && FEED.settings) || {};
    var t = today();
    var soups = s.soupsDate === t && Array.isArray(s.soups) ? s.soups.filter(function (x) { return x && x.name; }) : [];
    var specials = (Array.isArray(s.specials) ? s.specials : []).filter(function (sp) { return sp && sp.name && (!sp.ends || sp.ends >= t); });
    var cookie = s.cookie && s.cookieMonth === t.slice(0, 7) ? String(s.cookie) : "";
    var c = s.catering, cat = null;
    if (c && Array.isArray(c.tvs) && c.tvs.length) {
      cat = (c.byTv && (c.byTv["2"] || c.byTv["1"])) || c;
      if (!cat || !cat.headline) cat = null;
    }
    var out = (FEED && FEED.soldOutDate === t && Array.isArray(FEED.soldOut) ? FEED.soldOut : []).map(itemName).filter(Boolean);
    return { soups: soups, specials: specials, cookie: cookie, cookiePhoto: s.cookiePhoto, catering: cat, out: out, banner: s.banner || "" };
  }

  function renderToday() {
    var box = $("#today-grid");
    if (!box) return;
    var d = liveToday();
    var html = [];
    // Soups
    if (d.soups.length) {
      var first = d.soups.map(function (x) { return soupFile(x.name); }).filter(Boolean)[0];
      html.push('<article class="tcard soups' + (d.soups.length > 2 ? " wide" : "") + ' reveal in">' +
        (first ? '<div class="ph"><img src="' + IMG + first + '.webp" alt="A bowl of ' + esc(d.soups[0].name) + ' soup" loading="lazy"></div>' : "") +
        '<div class="body"><span class="k">Homemade Soups Today</span><h3>Soup of the Day</h3><ul class="soup-list">' +
        d.soups.map(function (x) { return "<li><span>" + esc(x.name) + "</span>" + (x.tags && x.tags.length ? '<span class="tags">' + esc(x.tags.join(" · ")) + "</span>" : "") + "</li>"; }).join("") +
        '</ul><p class="note">Made in house, preservative free. Cold quarts to go, too.</p></div></article>');
    }
    // Specials
    d.specials.forEach(function (sp, i) {
      var f = sp.photo && sp.photo !== "none" ? "" : (sp.photo === "none" ? "" : rule(SPECIAL_RULES, sp.name + " " + (sp.desc || "")));
      var ph = sp.photo && sp.photo !== "none" ? '<div class="ph"><img data-tablet-photo="' + esc(sp.photo) + '" alt="' + esc(sp.name) + '" src="' + IMG + 'cutlet-special.webp"></div>'
        : (f ? '<div class="ph"><img src="' + IMG + f + '.webp" alt="' + esc(sp.name) + '" loading="lazy"></div>' : "");
      html.push('<article class="tcard reveal in' + (ph ? "" : " nophoto") + '">' + ph + '<div class="body"><span class="k">' + esc(sp.kind || "Special") + "</span><h3>" + esc(sp.name) + "</h3>" +
        (sp.desc ? "<p>" + esc(sp.desc) + "</p>" : "") + (sp.price ? '<div class="price">' + esc(cents(sp.price)) + "</div>" : "") +
        (sp.ends === today() ? '<p style="font-size:13px;margin-top:6px">Today only</p>' : "") + "</div></article>");
    });
    // Cookie of the Month
    if (d.cookie) {
      var cf = rule(COOKIE_PHOTOS, d.cookie);
      html.push('<article class="tcard reveal in">' + (cf ? '<div class="ph"><img src="' + IMG + cf + '.webp" alt="' + esc(d.cookie) + ' cookies" loading="lazy"></div>' :
        (d.cookiePhoto ? '<div class="ph"><img data-tablet-photo="' + esc(d.cookiePhoto) + '" alt="' + esc(d.cookie) + '" src="' + IMG + 'sprinkle-cookies.webp"></div>' : "")) +
        '<div class="body"><span class="k">Cookie of the Month</span><h3>' + esc(d.cookie) + "</h3><p>This month’s flavor.</p></div></article>");
    }
    // Catering message
    if (d.catering) {
      html.push('<article class="tcard cater reveal in"><div class="body"><span class="k">Now Booking</span><h3>' + esc(d.catering.headline) + "</h3>" +
        (d.catering.message ? "<p>" + esc(d.catering.message) + "</p>" : "") +
        '<a class="btn btn-brass" href="' + ROOT + 'catering/">See the catering menu</a></div></article>');
    }
    // Sold out today
    if (d.out.length) {
      html.push('<article class="tcard out reveal in"><div class="body"><span class="k">Sold Out Today</span><h3>Gone for the day</h3><ul>' +
        d.out.map(function (n) { return "<li>" + esc(n) + "</li>"; }).join("") + "</ul><p>Back tomorrow. Call ahead to save one.</p></div></article>");
    }
    if (!html.length) {
      html.push('<div class="today-empty tcard full"><p style="font-family:var(--serif);font-size:24px;color:var(--char);margin:0 0 6px">The kitchen is just getting started.</p>' +
        "<p>Today’s soups and specials go up here as soon as the counter posts them. Call ahead at <a href=\"tel:+16104580700\">610-458-0700</a>.</p></div>");
    }
    box.innerHTML = html.join("");
    // Full-width last card on the 12-column grid when the row would leave a hole.
    $$("[data-tablet-photo]", box).forEach(function (img) {
      tabletPhoto(img.getAttribute("data-tablet-photo"), function (src) { img.src = src; });
    });
    var st = $("#today-status");
    if (st) {
      var upd = FEED && FEED.updated ? new Date(FEED.updated) : null;
      var mins = upd && !isNaN(upd) ? Math.max(0, Math.round((Date.now() - upd) / 60000)) : null;
      st.classList.toggle("stale", !feedFresh);
      st.querySelector("span:last-child").textContent = feedFresh ? ("Live from the counter" + (mins !== null && mins < 600 ? " · updated " + (mins < 1 ? "just now" : mins + " min ago") : "")) : "Showing the last update we have";
    }
  }

  /* ---------------- announcement bar ---------------- */
  function renderBanner() {
    var bar = $("#announce");
    if (!bar) return;
    var b = FEED && FEED.settings && FEED.settings.banner;
    var bd = FEED && FEED.settings && FEED.settings.bannerDate;
    var live = b && (!bd || bd >= today());
    bar.textContent = live ? b : bar.getAttribute("data-default");
    bar.classList.toggle("live", !!live);
  }

  /* ---------------- hours / open now ---------------- */
  // Mon-Sat 9:00 am to 6:30 pm, Sun 10:00 am to 5:00 pm (CateringMenu_2026.pdf + current site).
  var HOURS = { Mon: [540, 1110], Tue: [540, 1110], Wed: [540, 1110], Thu: [540, 1110], Fri: [540, 1110], Sat: [540, 1110], Sun: [600, 1020] };
  // Big holidays: hours are not published, so never claim "open".
  var HOLIDAYS = ["2026-11-26", "2026-12-25", "2027-01-01", "2027-03-28", "2027-11-25", "2027-12-25", "2028-01-01"];
  function fmt(m) { var h = Math.floor(m / 60), mm = m % 60; return ((h + 11) % 12 + 1) + (mm ? ":" + String(mm).padStart(2, "0") : "") + (h < 12 ? " am" : " pm"); }
  function renderHours() {
    var n = nowParts(), h = HOURS[n.day];
    $$("[data-open]").forEach(function (el) {
      var txt, cls;
      if (HOLIDAYS.indexOf(today()) >= 0) { txt = "Holiday today. Call ahead for hours"; cls = ""; }
      else if (n.mins >= h[0] && n.mins < h[1]) { txt = "Open now · until " + fmt(h[1]); cls = "open"; }
      else if (n.mins < h[0]) { txt = "Closed · opens today at " + fmt(h[0]); cls = "closed"; }
      else { var days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]; var nx = days[(days.indexOf(n.day) + 1) % 7]; txt = "Closed · opens " + (nx === "Sun" ? "Sunday" : "tomorrow") + " at " + fmt(HOURS[nx][0]); cls = "closed"; }
      el.className = "openline " + cls;
      el.innerHTML = '<span class="dot"></span><span>' + txt + "</span>";
    });
    $$(".hours tr").forEach(function (tr) { tr.classList.toggle("now", tr.getAttribute("data-day") && tr.getAttribute("data-day").split(",").indexOf(n.day) >= 0); });
  }

  /* ---------------- seasonal (holiday cards) ---------------- */
  function renderSeasonal() {
    var t = today();
    $$("[data-show-until]").forEach(function (el) { if (t > el.getAttribute("data-show-until")) el.remove(); });
    $$("[data-show-from]").forEach(function (el) { if (t < el.getAttribute("data-show-from")) el.remove(); });
    $$("[data-now-from]").forEach(function (el) { el.classList.toggle("now", t >= el.getAttribute("data-now-from") && t <= el.getAttribute("data-now-until")); });
  }

  function renderAll() { renderMenu(); renderToday(); renderBanner(); filterMenu(); }

  /* ---------------- header, drawer, reveals ---------------- */
  var hdr = $(".hdr");
  function onScroll() { if (hdr) hdr.classList.toggle("scrolled", window.scrollY > 10); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  var burger = $(".burger");
  if (burger) burger.addEventListener("click", function () {
    var open = document.body.classList.toggle("menu-open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });
  $$(".drawer a").forEach(function (a) { a.addEventListener("click", function () { document.body.classList.remove("menu-open"); if (burger) burger.setAttribute("aria-expanded", "false"); }); });

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }); }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else { $$(".reveal").forEach(function (el) { el.classList.add("in"); }); }

  /* Videos: only play when on screen, never for reduced motion or data saver. */
  var calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches || (navigator.connection && navigator.connection.saveData);
  $$("video[data-src]").forEach(function (v) {
    if (calm) return;
    var start = function () { if (!v.src) { v.src = v.getAttribute("data-src"); } var p = v.play(); if (p && p.catch) p.catch(function () {}); };
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(); else if (v.src) v.pause(); }); }, { threshold: .2 }).observe(v);
    } else start();
  });

  /* ---------------- menu page: tabs + search ---------------- */
  var tabs = $$(".mtabs a, .ctabs a");
  if (tabs.length && "IntersectionObserver" in window) {
    var secs = tabs.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); }).filter(Boolean);
    var spy = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        tabs.forEach(function (a) {
          var on = a.getAttribute("href") === "#" + e.target.id;
          a.classList.toggle("on", on);
          if (on && a.parentNode.scrollTo) a.parentNode.scrollTo({ left: a.offsetLeft - 24, behavior: "smooth" });
        });
      });
    }, { rootMargin: "-30% 0px -65% 0px" });
    secs.forEach(function (s) { spy.observe(s); });
  }
  var q = $("#msearch");
  function filterMenu() {
    if (!q) return;
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    $$("[data-search]").forEach(function (el) {
      if (el.hidden && el.getAttribute("data-ids") && el.getAttribute("data-ids").split(",").every(isRemoved)) return;
      var hit = !term || el.getAttribute("data-search").indexOf(term) >= 0;
      el.style.display = hit ? "" : "none";
      if (hit && term) shown++;
    });
    $$(".msec, .mgroup").forEach(function (s) {
      var any = !term || $$("[data-search]", s).some(function (el) { return el.style.display !== "none"; });
      s.style.display = any ? "" : "none";
    });
    var c = $("#mcount");
    if (c) c.textContent = term ? (shown ? shown + " match" + (shown === 1 ? "" : "es") : "Nothing matches. Try another word, or call 610-458-0700.") : "";
  }
  if (q) q.addEventListener("input", filterMenu);

  /* ---------------- go ---------------- */
  renderSeasonal();
  renderHours();
  setInterval(renderHours, 60 * 1000);
  renderAll();          // last good feed (or the built-in prices) right away
  loadFeed();           // then the live one
  setInterval(loadFeed, 3 * 60 * 1000);
})();
