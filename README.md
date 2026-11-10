# PDIR General Trading LLC — website

Static website of PDIR General Trading LLC, Dubai: European food supplements (the Visanto range) distributed across the MENA region.

- `site/` — the website (plain HTML/CSS, no build step). Published to GitHub Pages by `.github/workflows/pages.yml`.
- `site/products.html` and the product counts on the home page are **generated**: run `python3 scripts/build_products.py` to refresh them from visanto.com. `.github/workflows/update-catalogue.yml` does this automatically every Monday and redeploys if anything changed.
- Contact details live in `site/index.html` (search for `EDIT`).
