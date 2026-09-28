# Tradies Bureau: marketing site

The public website at **tradiesbureau.com**. It's plain HTML, CSS and a little JavaScript with no build step, served by GitHub Pages.

The app itself is a separate repository (`SKHB`) running on Railway at **portal.tradiesbureau.com**. One deployment serves every business. People sign in as themselves and switch between businesses, so there are no per-client subdomains.

```
tradiesbureau.com  (GitHub Pages, this repo)          portal.tradiesbureau.com  (Railway, SKHB repo)
  "Check what applies"  ───────────────────────────▶  /check        Compliance Checker, the sign-up front door
  "Check what applies" on a trade tile  ───────────▶  /check?trade=Builder   (opens with that trade ticked)
  "Sign in"  ──────────────────────────────────────▶  /login        sign-in link sent by email
  "User guide"  ───────────────────────────────────▶  /docs
                                                      /api/health   is the app up? (database, migrations, rules)
```

## Pages

```
index.html              Home: trade picker into the Checker, what the app does, three steps
features.html           Every feature, grouped, with jump links
builders.html           Projects, work packages, tenders, client quote sharing, handover certificates
compliance.html         Victorian compliance guide for trade businesses (free, with sources)
whats-new.html          Release notes, newest first
about.html              Mission and values
contact.html            Email, socials, a message form (opens the visitor's email app)
portal/index.html       Help signing in: sign in, create an account, links from tradies and builders
compliance-tracker.html Redirects to features.html (old address kept working)
services.html           Redirects to features.html (old address kept working)
css/style.css           Dark blue and teal theme
js/main.js              Mobile menu, footer year
js/portal.js            Points app links at localhost:8080 when testing locally
scripts/check-portal-links.py   Checks every link into the app
research/                       Research briefs behind the compliance guide
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

## Owner Builder in a Box

The Owner Builder in a Box prototype used to live in `owner-builder-in-a-box/`. It was moved out so it isn't published on tradiesbureau.com. It will get its own repository. Until then it can be recovered from this repository's history: `git checkout 99fe447 -- owner-builder-in-a-box`.

## Before launch

- Replace the placeholder social links (search for `facebook.com/tradiesbureau`, `instagram.com/tradiesbureau`, `linkedin.com/company/tradiesbureau`).
- Add a real phone number in `contact.html`.
- The dashboard screenshots show a made-up business (Brightwire Electrical Co.).
