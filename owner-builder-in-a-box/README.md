# Owner Builder in a Box

A phone-first web app for Victorians who want to build their own home as an owner-builder. It's a **separate product and website** from Tradies Bureau and reuses the Tradies Bureau framework: the dark blue and teal theme in `css/base.css`, plus the same plain HTML/CSS/JS approach with no build step.

This folder is self-contained. Nothing in it links into the Tradies Bureau site, so it can be moved into its own repository as-is.

## Pages

| Page | What it does |
|---|---|
| `index.html` | Product overview, ideal customer persona, how it works, pricing concept |
| `my-build.html` | **My Build** (phone-first): project details, space-aware room schedule (areas, paint, skirting, tile quantities), selections & specs, plan notes & site diary, plan/document links, site photos, backup/restore |
| `compliance.html` | Victorian owner-builder compliance checklist in 11 stages (eligibility → selling), with progress saved on the device, key numbers table and sources |
| `gateways.html` | 8 project gateways (G0–G7) with entry criteria, deliverables, exit checks; PM principles, RACI, risk register, typical program |
| `contracts.html` | Subbing out work: trade packages, contract types, legal requirements, pre-engagement checks, must-have clauses, payments, variations, disputes |
| `tenders.html` | Tender process + **tender comparison tool**: compliance gates, quote levelling, weighted scoring, recommendation, chart, CSV export |
| `guides.html` | Stage-by-stage buying guides & specs with Australian Standards and supplier questions (searchable) |
| `faq.html` | Searchable, categorised owner-builder Q&A |

## Tech

- Static HTML/CSS/vanilla JS. Serve with `python3 -m http.server 8000`.
- `js/app.js`: shared behaviour (checklist progress, search/filter, service worker registration)
- `js/tender-tool.js`: tender comparison tool
- `js/my-build.js`: My Build
- `manifest.webmanifest` + `sw.js`: installable on a phone's home screen and works offline (service worker registers over HTTPS only)
- All user data is kept in `localStorage` on the device in this preview. A real backend (accounts, sync, file storage for plans and PDFs, sharing with trades and surveyors, expiry reminders) is the next step.

## Keeping the compliance content current

Victorian building law changed on **1 July 2026** (Building Legislation Amendment (Buyer Protections) Act 2025):

- The BPC replaced the VBA and absorbed VMIA insurance and DBDRV disputes.
- The certificate of consent threshold rose from $16,000 to $20,000.
- The First Resort Home Warranty Scheme replaced last-resort domestic building insurance.

A proposal to raise the major domestic building contract threshold from $10,000 to $20,000 went to consultation in Aug–Sep 2026. Update `compliance.html`, `contracts.html` and `faq.html` if it's adopted.

Content is general information, checked September 2026, and is not legal advice.
