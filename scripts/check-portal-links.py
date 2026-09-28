#!/usr/bin/env python3
"""Checks the marketing site is hooked into the Tradies Bureau app correctly.

  python3 scripts/check-portal-links.py
      Checks every page: links into the app use the live address
      https://portal.tradiesbureau.com, carry a matching data-portal path
      (so js/portal.js can point them at localhost:8080 when testing), and
      every link between pages goes to a file that exists.

  python3 scripts/check-portal-links.py --app ../SKHB
      Also checks each linked path is a real page in the app's code.

  python3 scripts/check-portal-links.py --base http://localhost:8080
  python3 scripts/check-portal-links.py --base https://portal.tradiesbureau.com
      Also opens each linked path on a running app and expects it to load,
      plus /api/health, which reports the database, migrations and rules.

Exits non-zero if anything is wrong. Standard library only.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = "https://portal.tradiesbureau.com"
SKIP_DIRS = {"owner-builder-in-a-box", "node_modules", ".git"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "link", "script", "img"):
            a = dict(attrs)
            url = a.get("href") or a.get("src")
            if url:
                self.links.append((tag, url, a.get("data-portal"), self.getpos()[0]))


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def app_has_route(app, path):
    """True if the Next.js app under `app` serves `path` (no query string)."""
    segs = [s for s in path.split("?")[0].split("/") if s]
    d = app / "src" / "app"
    for s in segs:
        if (d / s).is_dir():
            d = d / s
            continue
        dyn = [c for c in d.iterdir() if c.is_dir() and c.name.startswith("[")]
        if not dyn:
            return False
        d = dyn[0]
    return any((d / f).exists() for f in ("page.tsx", "page.ts", "route.ts", "route.tsx"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tb-link-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(200000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # network, DNS, TLS
        return None, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", help="path to the app's repository (SKHB)")
    ap.add_argument("--base", help="address of a running app, e.g. http://localhost:8080")
    args = ap.parse_args()

    problems = []
    portal_paths = set()
    count = 0

    for page in pages():
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8"))
        rel = page.relative_to(ROOT)
        for tag, url, data_portal, line in parser.links:
            where = f"{rel}:{line}"
            if url.startswith(LIVE) or data_portal is not None:
                count += 1
                path = url[len(LIVE):] if url.startswith(LIVE) else None
                if path is None:
                    problems.append(f"{where}: data-portal link doesn't use the live address: {url}")
                elif not path.startswith("/"):
                    problems.append(f"{where}: portal link has no path: {url}")
                elif data_portal != path:
                    problems.append(f"{where}: data-portal {data_portal!r} doesn't match href path {path!r}")
                else:
                    portal_paths.add(path)
                if re.search(r":\d+", url.split("//", 1)[-1].split("/")[0]):
                    problems.append(f"{where}: portal link includes a port number: {url}")
                continue
            if re.match(r"^(https?:|mailto:|tel:|#|data:)", url) or url.startswith("//"):
                continue
            target = (page.parent / url.split("#")[0].split("?")[0]).resolve()
            if url.split("#")[0] and not target.exists():
                problems.append(f"{where}: broken link to {url}")

    print(f"Checked {count} links into the app across the site: {len(portal_paths)} different addresses.")
    for p in sorted(portal_paths):
        print(f"  {LIVE}{p}")

    if args.app:
        app = pathlib.Path(args.app).resolve()
        for p in sorted(portal_paths):
            if not app_has_route(app, p):
                problems.append(f"The app has no page for {p} (looked in {app / 'src' / 'app'})")
        print(f"Checked each address against the app's code in {app}.")

    if args.base:
        base = args.base.rstrip("/")
        for p in sorted(portal_paths | {"/api/health"}):
            status, body = fetch(base + p)
            ok = status == 200
            print(f"  {'ok  ' if ok else 'FAIL'} {status} {base}{p}")
            if not ok:
                problems.append(f"{base}{p} returned {status} {body[:120] if status is None else ''}".strip())
            elif p == "/api/health":
                try:
                    h = json.loads(body)
                    if not h.get("ok"):
                        problems.append(f"/api/health says the app isn't healthy: {body[:300]}")
                except ValueError:
                    problems.append("/api/health didn't return JSON")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("\nAll good.")


if __name__ == "__main__":
    main()
