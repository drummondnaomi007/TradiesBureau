# Tradies Bureau

Tradies Bureau — for tradies who want freedom and to step back from their business with ease.

This is the marketing site and front end for Tradies Bureau's offerings, starting with the MVP Compliance Tracker. It's a simple, static, green-themed site — no build step required.

## Structure

```
index.html                Home
compliance-tracker.html   MVP Compliance Tracker feature page
services.html             Services / offerings overview
about.html                About / mission
contact.html               Contact + social links
portal/index.html          Client portal landing (per-client subdomain placeholder)
css/style.css               Green theme styles
js/main.js                  Mobile nav + small interactions
assets/                     Favicon / logo mark
```

## Running locally

No build tools needed — it's plain HTML/CSS/JS. Either open `index.html` directly in a browser, or serve it locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploying — GitHub Pages

This repo is set up for GitHub Pages with a custom domain (`CNAME` file already added, pointing at `tradiesbureau.com`).

**One-time setup on GitHub:**
1. Go to the repo's **Settings → Pages**.
2. Under "Build and deployment", set **Source** to "Deploy from a branch".
3. Set **Branch** to `main`, folder `/ (root)`, and save.
4. GitHub will show the custom domain from the `CNAME` file — leave it as `tradiesbureau.com` and once DNS (below) is verified, tick **Enforce HTTPS**.

**DNS records to add at your DNS provider (Panthur):**

| Type | Host/Name | Value |
|---|---|---|
| A | `@` (apex, i.e. `tradiesbureau.com`) | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `drummondnaomi007.github.io` |

These four A records are GitHub Pages' standard IPs. DNS changes can take anywhere from a few minutes to a few hours to propagate; GitHub auto-provisions an HTTPS certificate once it verifies the domain, which can take a little while after that.

## Client subdomains

The site is designed around per-client portals living on subdomains, e.g. `yourbusiness.tradiesbureau.com`. `portal/index.html` is the current placeholder for that experience (linked from the "Client Portal" nav button).

The actual Compliance Tracker backend (separate build from this marketing site) deploys **one full instance per client business** — not a single shared multi-tenant app. That means subdomains don't need wildcard/tenant-routing infrastructure: each client's subdomain is just its own DNS record at Panthur, added when that client is onboarded:

| Type | Host/Name | Value |
|---|---|---|
| CNAME | `yourbusiness` | wherever that client's backend instance is deployed (e.g. `yourbusiness-tb.up.railway.app`) |

GitHub Pages only serves the root marketing site (`tradiesbureau.com` / `www`) — it has no role in the client subdomains, they point straight at each client's own deployment.

## Things to update before launch

- Replace placeholder social links in `contact.html`, `index.html`, `compliance-tracker.html`, `services.html`, `about.html`, and `portal/index.html` (search for `facebook.com/tradiesbureau`, `instagram.com/tradiesbureau`, `linkedin.com/company/tradiesbureau`) with your real profile URLs.
- Replace the placeholder email `hello@tradiesbureau.com` and add a real phone number in `contact.html`.
- Swap `assets/favicon.svg` for your real logo/mark.
- The compliance dashboard example on the home page and `compliance-tracker.html` uses sample data for illustration only.
