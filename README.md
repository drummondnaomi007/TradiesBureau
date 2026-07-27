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

## Deploying

Any static host works (Netlify, Vercel, GitHub Pages, Cloudflare Pages). Point the host at the repo root — there's no build command, the output directory is the repo root itself.

## Client subdomains

The site is designed around per-client portals living on subdomains, e.g. `yourbusiness.tradiesbureau.com`. `portal/index.html` is the current placeholder for that experience (linked from the "Client Portal" nav button).

To turn this into real per-client subdomains later, the general approach is:
1. Set a wildcard DNS record (`*.tradiesbureau.com`) pointing at your hosting provider.
2. Use your host's wildcard/multi-tenant subdomain support (Vercel and Netlify both support this) to route `*.tradiesbureau.com` requests into an app that reads the subdomain and loads that client's data.
3. The Compliance Tracker itself (the actual tracking app behind the portal) is a separate build from this marketing site — this repo is the public-facing front end only.

## Things to update before launch

- Replace placeholder social links in `contact.html`, `index.html`, `compliance-tracker.html`, `services.html`, `about.html`, and `portal/index.html` (search for `facebook.com/tradiesbureau`, `instagram.com/tradiesbureau`, `linkedin.com/company/tradiesbureau`) with your real profile URLs.
- Replace the placeholder email `hello@tradiesbureau.com` and add a real phone number in `contact.html`.
- Swap `assets/favicon.svg` for your real logo/mark.
- The compliance dashboard example on the home page and `compliance-tracker.html` uses sample data for illustration only.
