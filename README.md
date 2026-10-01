# Tradies Bureau: marketing site

The public website at **tradiesbureau.com**. It's plain HTML, CSS and a little JavaScript with no build step, served by GitHub Pages.

The app itself is a separate repository (`SKHB`) running on Railway at **portal.tradiesbureau.com**. One deployment serves every business. People sign in as themselves and switch between businesses, so there are no per-client subdomains.

```
tradiesbureau.com  (GitHub Pages, this repo)          portal.tradiesbureau.com  (Railway, SKHB repo)
  "Check what applies"  ───────────────────────────▶  /check        Compliance Checker, the sign-up front door
  "Check what applies" on a trade tile  ───────────▶  /check?trade=Builder   (opens with that trade ticked)
  "Sign in"  ──────────────────────────────────────▶  /login        sign-in link sent by email
  Contact form  ───────────────────────────────────▶  /api/enquiries  saves the message; read it at /enquiries
                                                      /api/health   is the app up? (database, migrations, rules)
```

## Pages

```
index.html              Home: app beside the headline, trade picker, three feature rows, pricing, three steps
pricing.html            Pricing: free trial, then $49 a month; contact us for builders and other services
features.html           Every feature, grouped, with jump links
builders.html           Projects, work packages, tenders, client quote sharing, handover certificates
compliance.html         Victorian compliance guide for trade businesses (free, with sources)
whats-new.html          Release notes, newest first
about.html              Mission and values
contact.html            Phone, email, socials, a message form (saved in the app)
privacy.html            Privacy policy: the message form and visitor statistics
portal/index.html       Help signing in: sign in, create an account, links from tradies and builders
compliance-tracker.html Redirects to features.html (old address kept working)
services.html           Redirects to features.html (old address kept working)
css/style.css           Navy, teal and hi-vis theme (Plus Jakarta Sans headings, Inter body; the 2026 refresh is layered at the end)
js/main.js              Mobile menu, footer year, screen tabs, "you've logged out" note
js/enquiry.js           Sends the contact form to the app
js/analytics.js         Visitor statistics (Google Analytics), off until a Measurement ID is added
js/portal.js            Points app links at localhost:8080 when testing locally
scripts/check-portal-links.py   Checks every link into the app
research/                       Research briefs behind the compliance guide
assets/logo-mark.svg            Navy logo for the white header (logo-mark-white.svg for the footer)
```

## How the site links into the app

Every link into the app is written with its full live address and the path again in `data-portal`:

```html
<a href="https://portal.tradiesbureau.com/check" data-portal="/check">Check what applies to you</a>
```

That works with no JavaScript. `js/portal.js` only changes these links when the site is opened on `localhost`: it points them at the app on **port 8080**. The app listens on 8080 locally and on Railway. To test against another local port, add `?portal=http://localhost:3000` to the page address. The override only works on localhost, so a link to the live site can't redirect its sign-in buttons.

Never put a port number in a link. Visitors reach the app on normal HTTPS. Railway forwards the domain to the app's port behind the scenes. The link check fails if a port appears.

### Check the links

```bash
python3 scripts/check-portal-links.py                                    # site only
python3 scripts/check-portal-links.py --app ../SKHB                      # and each page exists in the app's code
python3 scripts/check-portal-links.py --base http://localhost:8080       # and each page loads on a running app
python3 scripts/check-portal-links.py --base https://portal.tradiesbureau.com   # and on the live app
```

Run the last one after any change to the site or a deploy of the app. It also calls `/api/health`, which reports whether the database answers, whether every migration is applied and whether the requirement rules are loaded.

## Test the site and app together locally

1. Start the app on port 8080. In the SKHB repo, with a Postgres database in `DATABASE_URL`:
   ```bash
   npm ci && npm run db:release && npm run build
   PORT=8080 npm run start          # prints "- Local: http://localhost:8080"
   ```
2. Serve this site:
   ```bash
   python3 -m http.server 8000      # then open http://localhost:8000
   ```
3. Click "Check what applies" or "Sign in". They open the local app on 8080.

## Live setup

### Marketing site: GitHub Pages

- **Settings → Pages**: Source "Deploy from a branch", branch `main`, folder `/ (root)`. The `CNAME` file sets `tradiesbureau.com`. Tick **Enforce HTTPS** once DNS verifies.
- **The live site only changes when work is merged into `main`.** Changes on other branches aren't published.

### App: Railway (SKHB repo)

Full steps are in the SKHB repo's `CONFIGURATION.md` §5. The parts that connect it to this site:

1. **Settings → Networking → Custom Domain**: `portal.tradiesbureau.com`.
2. **The domain's target port must be 8080.** Under the domain Railway shows "→ Port …". It must match the port in the Deploy Logs line `- Local: http://localhost:<port>` (usually 8080). If they differ you'll see "Application failed to respond" even though the logs end with `✓ Ready`. Don't add your own `PORT` variable.
3. **`APP_URL` = `https://portal.tradiesbureau.com`** in the app's variables. Sign-in emails, credential links and tender links are built from it. A wrong value sends people to the wrong address.
4. Check `https://portal.tradiesbureau.com/api/health` shows `"ok": true`.

### DNS (Panthur)

| Type | Host | Value | For |
|---|---|---|---|
| A | `@` | `185.199.108.153` | GitHub Pages |
| A | `@` | `185.199.109.153` | GitHub Pages |
| A | `@` | `185.199.110.153` | GitHub Pages |
| A | `@` | `185.199.111.153` | GitHub Pages |
| CNAME | `www` | `drummondnaomi007.github.io` | GitHub Pages |
| CNAME | `portal` | the target Railway shows for the custom domain (currently `0xlrojlx.up.railway.app`) | The app |

## Enquiries from the contact form

The form on `contact.html` sends each message to the app (`POST /api/enquiries`), which saves it. With JavaScript it's sent in the background and a thank-you shows in place. Without it, the form posts straight to the app, which sends the visitor back to `contact.html?sent=1`.

To read them, sign in to the app with an email listed in the app's `ADMIN_EMAILS` variable (set in Railway). An **Enquiries** link appears in the menu. Mark each one Contacted or Closed as you go. Everyone listed also gets an email per enquiry, once the app's email works.

The app only accepts enquiries from `https://tradiesbureau.com` and `www.` (and from `http://localhost:8000` when both run locally). A hidden field catches most spam bots, and one connection can send 5 an hour.

## Visitor statistics

`js/analytics.js` adds Google Analytics 4 (Measurement ID `G-GF6MK11613`). With no ID in it, nothing loads. How it was set up:

1. Go to [analytics.google.com](https://analytics.google.com) and sign in with the Google account that should own the data.
2. **Start measuring** (or **Admin → Create → Property**). Name it "Tradies Bureau", time zone Australia/Melbourne, currency AUD.
3. Choose **Web**, enter `https://tradiesbureau.com`, stream name "Website".
4. Copy the **Measurement ID** (`G-…`) into `MEASUREMENT_ID` in `js/analytics.js` and merge.
5. In **Admin → Events**, mark `generate_lead` as a key event (conversion). That's a message sent from the contact form. `contact` is a tap on the phone number.

It never runs on localhost. `privacy.html` explains it to visitors.

## Search engines and sharing

- `sitemap.xml` lists every page for Google and Bing. `robots.txt` points to it and keeps `scripts/` and `research/` out of search results.
- Every page has its own title (about 60 characters) and description (about 155) written around what Victorian tradies search for, plus a canonical address.
- Open Graph and Twitter tags give a proper preview card (`assets/screenshots/og-dashboard.jpg`, 1200×630) when the site is shared on Facebook, LinkedIn or in messages.
- Structured data (JSON-LD) on every page describes Tradies Bureau as an organisation serving Victoria. The home page adds the app, and the compliance guide is marked as an article. Add the real Facebook, Instagram and LinkedIn addresses to it once they exist.
- `404.html` is shown for any missing address, with links from the site root.

After changing pages, update `lastmod` in `sitemap.xml` and resubmit it in Google Search Console.

## Owner Builder in a Box

The Owner Builder in a Box prototype used to live in `owner-builder-in-a-box/`. It was moved out so it isn't published on tradiesbureau.com. It will get its own repository. Until then it can be recovered from this repository's history: `git checkout 99fe447 -- owner-builder-in-a-box`.

## Before launch

- Replace the placeholder social links (search for `facebook.com/tradiesbureau`, `instagram.com/tradiesbureau`, `linkedin.com/company/tradiesbureau`).
- Set `ADMIN_EMAILS` in the app's Railway variables so enquiries can be read.
- The app screenshots in `assets/screenshots/` show a made-up business (Brightwire Electrical Co.) with made-up trades, clients and addresses (postcode 3999 doesn't exist). They were taken from the real app running locally with demo data, in an Australian locale. `app-*.jpg` are desktop screens (2000px wide), `phone-*.jpg` phone screens (780px wide), `og-dashboard.jpg` the social share preview.
