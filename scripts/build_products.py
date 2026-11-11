#!/usr/bin/env python3
"""Build site/products.html from the Visanto online catalogue (visanto.com, a Shopify store).

Usage:
    python3 scripts/build_products.py              # fetch the live catalogue
    python3 scripts/build_products.py --source DIR # use products.json + col_<handle>.json saved in DIR

Re-run it whenever Visanto changes its range, then commit the regenerated page.
"""
import argparse
import datetime
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

STORE = "https://visanto.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "products.html")
INDEX = os.path.join(ROOT, "site", "index.html")
IMG_DIR = os.path.join(ROOT, "site", "assets", "products")

# Supplement sub-categories, in display order: (title, store collections that map to it).
SUPPLEMENT_GROUPS = [
    ("Vitamins", ["vitamin-a", "vitamin-b", "vitamin-c", "vitamin-d", "vitamin-k", "adek"]),
    ("Minerals", ["magnesium"]),
    ("Amino acids & collagen", ["amino-acids", "collagen"]),
    ("Omega-3 fatty acids", ["omega-acids"]),
    ("Liposomal formulas & coenzyme Q10", ["liposomes", "coenzyme-q10"]),
    ("Medicinal mushrooms", ["mushrooms"]),
    ("Plant extracts & freeze-dried products", ["extracts", "lyophilisates"]),
    ("Other supplements", []),
]
# Products the store files under no specific collection.
SUPPLEMENT_OVERRIDES = {
    "jodolit-en-visanto": "Minerals",
    "carnosine-forte": "Amino acids & collagen",
    "natural-curcumin-visanto": "Plant extracts & freeze-dried products",
    "natural-curcumin-visanto-120-capsules": "Plant extracts & freeze-dried products",
    "mumio-visanto": "Plant extracts & freeze-dried products",
}
OTHER_GROUPS = [
    ("Grounding", ["grounding"]),
    ("Hydrogen inhalation", ["hydrogen-browns-gas-inhalation-system-and-accessories"]),
    ("Water filtration", ["water-filter"]),
    ("Kitchen appliances", ["home-appliance"]),
    ("Food & other", []),
]
BOOK_LANGUAGES = [
    ("english", "English"), ("polish", "Polish"), ("german", "German"),
    ("czech", "Czech"), ("italian", "Italian"), ("spanish", "Spanish"),
]
COLLECTIONS = sorted({c for _, cs in SUPPLEMENT_GROUPS + OTHER_GROUPS for c in cs}
                     | {h for h, _ in BOOK_LANGUAGES} | {"books"})

# Retail promotions (multi-packs, gift sets, gift cards) are not part of the trade range.
PROMO = re.compile(r"bundle|\bset of\b|\bdetox set\b|2\+1|10 packs|\+ ?shaker|\+ ?pillbox|"
                   r"day & night|valentine|gift card", re.I)
# Store titles that carry marketing claims after the product name.
NAME_OVERRIDES = {
    "alkavis-visanto-support-for-acid-base-balance-30-sachets": "AlkaVis",
    "acidepro-digestive-support": "AcidePro",
}


def fetch_json(source, name, url_path):
    if source:
        with open(os.path.join(source, name)) as f:
            return json.load(f)
    req = urllib.request.Request(STORE + url_path, headers={"User-Agent": "pdir-site-builder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def load(source):
    products = fetch_json(source, "products.json", "/products.json?limit=250")["products"]
    membership = {}
    for handle in COLLECTIONS:
        data = fetch_json(source, f"col_{handle}.json", f"/collections/{handle}/products.json?limit=250")
        for p in data["products"]:
            membership.setdefault(p["handle"], set()).add(handle)
    return products, membership


# Groups checked first when a product sits in several collections: the more specific
# form (liposomal) beats the ingredient group (e.g. liposomal vitamin C is listed under
# both vitamin-c and liposomes).
GROUP_PRIORITY = ["Liposomal formulas & coenzyme Q10"]


def group_for(groups, cols, override=None):
    if override:
        return override
    ordered = sorted(groups, key=lambda g: (g[0] not in GROUP_PRIORITY, GROUP_PRIORITY.index(g[0]) if g[0] in GROUP_PRIORITY else 0))
    for title, handles in ordered:
        if cols & set(handles):
            return title
    return groups[-1][0]


def classify(products, membership):
    sections = {
        "supplements": {t: [] for t, _ in SUPPLEMENT_GROUPS},
        "books": {lang: [] for _, lang in BOOK_LANGUAGES},
        "other": {t: [] for t, _ in OTHER_GROUPS},
    }
    seen = set()
    for p in products:
        title = p["title"].strip()
        if PROMO.search(title) or title.lower() in seen:
            continue
        seen.add(title.lower())
        cols = membership.get(p["handle"], set())
        item = {
            "name": NAME_OVERRIDES.get(p["handle"], title),
            "url": f"{STORE}/products/{p['handle']}",
            "img": p["images"][0]["src"] if p["images"] else "",
        }
        if p["product_type"] == "Book" or "books" in cols:
            # Untagged books are the publisher's Polish titles, apart from English editions.
            fallback = "English" if title.startswith("The ") else "Polish"
            lang = next((l for h, l in BOOK_LANGUAGES if h in cols), fallback)
            sections["books"].setdefault(lang, []).append(item)
        elif p["product_type"] == "Supplement":
            g = group_for(SUPPLEMENT_GROUPS, cols, SUPPLEMENT_OVERRIDES.get(p["handle"]))
            sections["supplements"][g].append(item)
        else:
            sections["other"][group_for(OTHER_GROUPS, cols)].append(item)
    for groups in sections.values():
        for items in groups.values():
            items.sort(key=lambda i: i["name"].lower())
    return sections


def local_image(item, width=400):
    """Download the product image once into site/assets/products/ and return its site path."""
    if not item["img"]:
        return ""
    filename = item["img"].split("?")[0].rsplit("/", 1)[-1]
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    name = item["url"].rsplit("/", 1)[-1] + ext
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        os.makedirs(IMG_DIR, exist_ok=True)
        # The store serves its Shopify files from its own domain as well as cdn.shopify.com.
        url = f"{STORE}/cdn/shop/files/{urllib.parse.quote(filename)}?width={width}"
        req = urllib.request.Request(url, headers={"User-Agent": "pdir-site-builder"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
        except urllib.error.HTTPError as err:
            print(f"  image not downloaded ({err.code}), linking to the store's copy: {item['name']}")
            return item["img"].split("?")[0] + f"?width={width}"
        with open(path, "wb") as f:
            f.write(data)
    return f"assets/products/{name}"


def card(item):
    e = html.escape
    img = (f'<img src="{e(local_image(item))}" alt="{e(item["name"])}" loading="lazy" '
           f'width="400" height="400">' if item["img"] else '<span class="product-noimg" aria-hidden="true"></span>')
    quote = "index.html?product=" + urllib.parse.quote(item["name"]) + "#contact"
    # The quote link is stretched over the whole card; the spec-sheet link sits above it.
    return (f'<li class="product">\n'
            f'  <div class="product-img">{img}</div>\n'
            f'  <h4>{e(item["name"])}</h4>\n'
            f'  <a class="product-quote" href="{quote}">Request a quote</a>\n'
            f'  <a class="product-ext" href="{e(item["url"])}" target="_blank" rel="noopener">Spec sheet on visanto.com <span aria-hidden="true">&#8599;</span></a>\n'
            f'</li>')


SECTION_META = [
    ("supplements", "Food supplements", "Vitamins, minerals, amino acids, omega-3 and more, produced in the EU."),
    ("books", "Books", "Titles published and distributed by Visanto, in several languages."),
    ("other", "Other products", "Grounding products, hydrogen inhalation, water filtration and kitchen appliances."),
]


def render(sections):
    counts = {k: sum(len(v) for v in g.values()) for k, g in sections.items()}
    total = sum(counts.values())
    chips = "\n".join(f'          <a class="chip" href="#{k}">{t} <span>{counts[k]}</span></a>'
                      for k, t, _ in SECTION_META)
    body = []
    for key, title, intro in SECTION_META:
        body.append(f'    <section id="{key}" class="section catalogue-section">\n      <div class="wrap">\n'
                    f'        <h2>{title}</h2>\n        <p class="muted">{intro}</p>')
        for sub, items in sections[key].items():
            if not items:
                continue
            cards = "\n".join(card(i) for i in items)
            body.append(f'        <h3 class="group-title" id="{slug(sub)}">{html.escape(sub)} <span>{len(items)}</span></h3>\n'
                        f'        <ul class="product-grid">\n{cards}\n        </ul>')
        body.append('      </div>\n    </section>')
    today = datetime.date.today().strftime("%B %Y")
    return TEMPLATE.format(total=total, chips=chips, sections="\n".join(body), updated=today)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Products — PDIR General Trading LLC</title>
  <meta name="description" content="The Visanto range distributed by PDIR General Trading LLC from Dubai: food supplements, books and other products from Europe.">
  <meta name="theme-color" content="#243918">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip" href="#top">Skip to content</a>
  <!-- Generated by scripts/build_products.py from visanto.com. Do not edit by hand. -->
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="logo" href="index.html" aria-label="PDIR General Trading LLC home">
        <img src="assets/pdir-mark.svg" alt="PDIR" width="149" height="36">
        <span class="logo-micro"><span>General Trading LLC</span><span>Dubai &middot; UAE</span></span>
      </a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">
        <span class="menu-bars" aria-hidden="true"></span>Menu
      </button>
      <nav class="nav" id="site-nav" aria-label="Main">
        <a href="index.html#about">About</a>
        <a href="index.html#services">What we do</a>
        <a href="products.html" aria-current="page">Products</a>
        <a href="index.html#markets">Markets</a>
        <a class="nav-cta" href="index.html#contact">Contact</a>
      </nav>
    </div>
  </header>

  <main id="top">
    <section class="page-hero">
      <div class="wrap page-hero-grid">
        <div>
          <p class="eyebrow">Our range &middot; Visanto</p>
          <h1>Products</h1>
          <p class="lead">We distribute the full Visanto range across the MENA region from our warehouse in Dubai: {total} products in three groups. For trade prices, availability and registration documents, please contact us.</p>
        </div>
        <img class="page-hero-photo" src="assets/studio/tranol-sachets.webp" alt="Tranol sachets on a blue studio set" width="800" height="800">
      </div>
    </section>
    <nav class="chips-bar" aria-label="Product groups">
      <div class="wrap chips">
{chips}
      </div>
    </nav>

{sections}

    <section class="section contact cta-band">
      <div class="wrap cta-inner">
        <div>
          <h2>Interested in these products?</h2>
          <p class="muted">Ask us for the trade price list, minimum order quantities and product documentation.</p>
        </div>
        <a class="btn btn-primary" href="index.html#contact">Contact us</a>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <nav class="footer-nav" aria-label="Footer">
        <a href="index.html#about">About</a>
        <a href="index.html#services">What we do</a>
        <a href="products.html">Products</a>
        <a href="index.html#markets">Markets</a>
        <a href="index.html#contact">Contact</a>
      </nav>
      <div class="footer-inner">
        <p>&copy; 2026 PDIR General Trading LLC &middot; Dubai, UAE</p>
        <p class="muted">Product range and images: visanto.com, updated {updated}.</p>
      </div>
    </div>
  </footer>
  <script>
    (function () {{
      var btn = document.querySelector('.menu-btn'), header = document.querySelector('.site-header');
      function set(open) {{ header.classList.toggle('nav-open', open); btn.setAttribute('aria-expanded', open); btn.lastChild.textContent = open ? 'Close' : 'Menu'; }}
      btn.addEventListener('click', function () {{ set(!header.classList.contains('nav-open')); }});
      document.addEventListener('keydown', function (e) {{ if (e.key === 'Escape') set(false); }});
    }})();
  </script>
</body>
</html>
"""


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def update_counts(sections):
    """Refresh every <span data-count="key"> on the home page so its numbers follow the catalogue."""
    counts = {key: sum(len(v) for v in groups.values()) for key, groups in sections.items()}
    counts["total"] = sum(counts.values())
    for groups in sections.values():
        for title, items in groups.items():
            counts[slug(title)] = len(items)
    with open(INDEX) as f:
        page = f.read()
    missing = set()

    def swap(m):
        key = m.group(2)
        if key not in counts:
            missing.add(key)
            return m.group(0)
        return f"{m.group(1)}{counts[key]}{m.group(3)}"

    page, n = re.subn(r'(<span data-count="([^"]+)">)[^<]*(</span>)', swap, page)
    with open(INDEX, "w") as f:
        f.write(page)
    print(f"updated {n} counts in {os.path.relpath(INDEX, ROOT)}" + (f"; unknown keys: {sorted(missing)}" if missing else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="directory with saved products.json and col_<handle>.json files")
    args = ap.parse_args()
    sections = classify(*load(args.source))
    with open(OUT, "w") as f:
        f.write(render(sections))
    update_counts(sections)
    for key, groups in sections.items():
        print(key, {k: len(v) for k, v in groups.items() if v})
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
