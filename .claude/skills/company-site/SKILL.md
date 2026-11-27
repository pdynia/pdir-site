---
name: company-site
description: Build and publish a small static company website (home page, optional catalogue page, enquiry form, analytics, custom domain) in the style worked out for pdir.ae. Use when the user asks for a website for one of their companies, wants "a site like PDIR", or wants to reuse the PDIR design, hero line animation, markets map, Formspree form or GitHub Pages deployment in a new project.
---

# Company site

A repeatable way to take one of the owner's companies from "we need a website" to a live site on its own domain. It encodes the decisions made while building pdir.ae (PDIR General Trading LLC, Dubai), so the next site starts where that one ended instead of from zero.

The owner writes in Polish and sometimes English. Reply in the language they write in. Site copy is English unless they say otherwise.

## What is in this skill

- `reference/index.html`, `reference/styles.css` — the finished PDIR home page. A working example of every section, not a file to copy wholesale: `styles.css` grew by layering overrides, so for a new site write one clean stylesheet from the tokens below and lift only the rules you need.
- `reference/build_products.py` — generates a catalogue page from a Shopify store's public JSON and keeps counts on the home page in sync. Only relevant when the new company also resells a catalogue.
- `reference/workflows/` — GitHub Pages deploy and weekly catalogue refresh.
- `snippets/hero-lines.js`, `snippets/map-routes.js`, `snippets/enquiry-form.js` — the three scripts worth reusing as they are.

Form endpoint and analytics token in the reference are placeholders (`YOUR_FORM_ID`, `YOUR_CLOUDFLARE_TOKEN`). Never reuse another company's IDs.

## How to run a new site

### 1. Intake

Ask only for what you cannot invent. Everything else gets a clearly marked placeholder so work can start.

- Legal company name, and what it does in one or two sentences
- Logo files (SVG preferred) and brand colours; derive colours from the logo if none are given
- Domain, email, phone, address, trade licence number
- Who the site is for (buyers, partners, both) and the one action they should take
- Whether there is a product range to show, and where its data lives

Placeholders are marked with `<!-- EDIT: ... -->` comments in the HTML and listed for the owner at the end of every reply until they are filled.

### 2. Build

Plain HTML and CSS in a `site/` folder, no framework and no build step. The owner hosts on GitHub Pages and edits rarely; a static folder is what survives that.

Page skeleton that worked, in order: sticky header → hero with facts row → about → how it works (numbered steps, because it is a real sequence) → range or services → markets or coverage → who we work with → contact with enquiry form → footer with logo and link columns. Drop sections the business does not need rather than filling them with filler.

### 3. Show before shipping

The owner reviews visually and reacts to what they see. So:

- Work on a `claude/...` branch and publish each iteration as a private preview (Artifact) the owner can open on their phone.
- Never push to `main` (which deploys) until they say "wdrażaj" / "deploy" for that specific version. Approval for one version does not carry to the next.
- After a deploy, check the Actions run and report its result. Say plainly when you could not open the live site yourself.
- Take screenshots at 1440, ~900 and 390 px before showing anything, and check for horizontal overflow and console errors. Scroll slowly in the capture script or reveal animations will photograph as blank sections.

### 4. Publish

Covered in "Deployment" below. A site that shares a repository with another project cannot have its own domain, so give each company site its own repository from the start.

## Design system

These are the owner's settled preferences. Follow them unless they ask for something else.

**Type.** Newsreader (light, tight tracking) for headings and running text; Hanken Grotesk for navigation, buttons, labels, forms and small UI. Small labels are uppercase with wide tracking ("micro" text, as on the owner's NSPanel and posters) at about 11 px; the line beside the logo may go down to 10 px but no smaller.

**Colour.** Two brand colours carry the page: a dark brand colour for bands and buttons, and an off-white background. PDIR's are `#243918` and `#F5F3EE`. One muted accent for labels, darkened until it passes 4.5:1 on the background. A gold (`#c8a96a`) is used sparingly on dark bands. Product categories may each take a colour drawn from their packaging.

**Shape.** Rounded pill buttons, 14 px card radius, 24 px for large media. Hairline borders. Soft, low-contrast shadows.

**Logo.** A full logo with small text turns jagged when squeezed into a header. Use a compact mark in the header with the secondary line set as live micro text beside it, and the full logo larger in the contact band or footer.

**Menu.** Thin vertical bars before each item; the contact link is a filled pill. On phones, a Menu button opening a full-width panel with every section. Never hide sections on mobile.

**Hero.** Dark brand band. Thin wavy lines fan out from a point off-screen (`snippets/hero-lines.js`): they wave slightly all the time and the whole fan rotates with the scroll position. Text sits on a blurred, feathered patch of the band colour so lines never cross letters sharply; the facts row below gets the same treatment as a full-width band. Never show the centre of the fan.

**Motion.** Subtle, and tied to what the visitor does. Scroll-driven beats always-on. Everything stops under `prefers-reduced-motion`, and the page must be complete without JavaScript.

**Feedback on tiles.** A gentle lift with a soft shadow on hover or focus. No dark outline or frame on click; keep a thin light outline for keyboard focus only.

**Section dividers.** Whitespace or a faint fading shadow. Rows of vertical tick marks were tried and rejected as too heavy.

**Things the owner rejected — do not reintroduce.**
- Decorative star or geometric patterns. An eight-point star built from two squares read as a hexagram, a serious problem for a Gulf audience. Avoid religious or national symbols in decoration altogether.
- Stretched or heavily cropped images. Give every `<img>` with fixed dimensions `height: auto`, and show square studio images whole.
- Stock photos that pretend to be the company's own (someone else's warehouse or port). A real photo of the city is fine; label nothing as "our warehouse" unless it is.
- A raw, text-only page. Each long text section needs an image, map or graphic.

## Reusable pieces

**Hero lines** — `snippets/hero-lines.js`. Add `<canvas class="hero-art" aria-hidden="true">` as the first child of the hero; position it absolutely over the section. Change the stroke colour to a light tint of the new brand colour.

**Markets map** — `snippets/map-routes.js` with the `.mena-map` SVG from the reference. Routes are drawn as SVG paths starting at the hub. They draw one at a time as the map scrolls into view, in the order of the country list; hovering a country (in the list or on the map) highlights it in the list and loops its route from hub to country. Draw a new schematic map for a new region by hand: place labelled dots at rough positions and keep labels from colliding, rather than projecting real coordinates, which crowds small neighbouring countries.

**Enquiry form** — `snippets/enquiry-form.js`. Posts to Formspree in the background, with a `_subject` naming the company, a hidden `_gotcha` honeypot, a disabled button while sending, and a `?product=` parameter that pre-fills the message. Without JavaScript the form still posts directly via `action`.

**Catalogue** — `reference/build_products.py`. Reads `/products.json` and collection JSON from a Shopify store, groups products, downloads thumbnails into the site, writes the catalogue page, and rewrites every `<span data-count="...">` on the home page. The banner shows the newest product. Run it from a weekly workflow so the owner never edits counts by hand.

## Content rules

- Describe the business; make no health or performance claims about products. Supplements and similar goods are regulated in the UAE and Saudi Arabia.
- State only facts that are known. No certification badges (GMP, halal, registrations) until the owner confirms them.
- When showing another brand's products or photos, tell the owner to confirm they have permission, once, and move on.

## Deployment

1. **Repository.** One public repository per company site. Creating a repository is not possible from a cloud session; ask the owner to create an empty public one, then attach it.
2. **Workflow.** `reference/workflows/pages.yml` deploys `site/` on every push to `main`. Add `site/.nojekyll` and `site/CNAME` containing the domain.
3. **Enable Pages.** The workflow cannot turn Pages on by itself in a new repository. The owner must open Settings → Pages and set Source to "GitHub Actions" once. Until then every push fails and emails them; warn them first and avoid pushing.
4. **Domain.** In the same settings page they enter the custom domain. At the DNS host they add four A records for the apex (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and a CNAME `www` → `<user>.github.io`. On Cloudflare the records stay "DNS only". Leave MX and TXT records alone: they carry the company's email. Once GitHub issues the certificate they tick "Enforce HTTPS".
5. **Form.** The owner creates a Formspree form and sends the endpoint. "Restrict to Domain" lives in the Formspree *project* settings, not the form's.
6. **Analytics.** Cloudflare Web Analytics: the owner adds the site (manual / JS snippet setup) and pastes the snippet; put it before `</body>` on every page and in any page template a script generates.

Commit author email should be the owner's GitHub noreply address, not their personal email, since the repository is public.

## Working in a cloud session

- The session cannot see the owner's browser or logged-in accounts. Ask for screenshots instead of saying you will look.
- Outbound network is limited to an allowlist. When a site the task needs is blocked, propose adding exactly that host to the environment and explain why in one sentence.
- Some sites (Unsplash) block automated downloads. Give the owner links and let them send the files.
- Images pasted while a turn is running may not reach the disk; ask the owner to resend them in a new message.
- Write test screenshots to the scratchpad, never into the repository.
