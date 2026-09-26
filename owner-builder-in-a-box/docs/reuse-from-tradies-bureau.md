# Reusing the Tradies Bureau Compliance Tracker (SKHB) in Owner Builder in a Box

Checked against `drummondnaomi007/SKHB` @ `5b7779f` (Sept 2026). The TradiesBureau repo is only the marketing site; the working app is SKHB: Next.js 14, Prisma/SQLite, magic-link sign-in, Resend email, WhatsApp (Meta Cloud API), Google Drive storage, tesseract OCR and 58 test files.

Most of SKHB's domain logic lives in pure modules marked "No prisma here", written to be unit-tested. That makes them easy to lift into another app.

## Paid owner-builder features → what SKHB already has

| Owner-builder feature | Reusable SKHB parts | Reuse |
|---|---|---|
| **Reminders & alerts** (the engine behind everything) | `rag.ts` (expired/0–6 days red, 7–29 amber, 30+ green), `cache.ts` + `nightly.ts` (nightly status job), `notifications/*` (weekly digest email, critical WhatsApp alerts, quiet hours, two-way "check" reply), `NotificationConfig`/`NotificationLog`, `cronAuth.ts` + the 4 cron routes | ~90%: add owner-builder item types |
| **Trade register + expiry alerts** | `Subcontractor`, `SubcontractorDocument` + onboarding, **token links so trades upload their own certificates** (`api/subcontractors/[token]/*`), `trades.ts` (certificates per trade), `subbieRequirements.ts`, `insuranceRequirements.ts`, `ocr.ts` (reads expiry dates off certificate photos), `abn.ts`, `chase/policy.ts` (automatic chasing of missing documents) | ~85% |
| **Mandatory inspections** | `capm/inspectionStages.ts` (Building Regs r167 stages, "notify without delay" logic), `MandatoryInspection` model | ~95%: the owner-builder is the builder here |
| **Trade contracts, variations, defects** | `subcontractorAgreement.ts`, per-trade agreement templates, e-signing (`signing/*`, `SignatureRequest`), `Variation` with sign/approve/PDF, `Defect`, `RFI`, `DelayEvent`/clock stops | ~70%: reword from the builder's side to the owner-builder's side |
| **Payment rules & budget** | `capm/domesticPayments.ts` (DBC Act s11 deposit caps, s40 stage caps, s42 final payment), `PaymentClaim` | ~40%: rules reuse. Budget → committed → paid → forecast and the bank's progress-payment schedule are new |
| **Council & approvals register** (conditions with owner, due date, evidence) | `ComplianceRule` / `RuleInstance` / `RuleEvidence` + `capm/due-date-calculator.ts` (chained triggers, business days, clock stops), `holidays/vic.ts` | ~70%: add council, planning and authority rule types |
| **Handover / sale-ready pack** | `capm/handover.ts` (occupancy permit, plumbing certificate ≥ $750, Certificate of Electrical Safety, suggested surveyor certificates), `zip.ts`, `csv.ts` (safe from spreadsheet-formula injection), `auditReports.ts` | ~75% |
| **Owner-builder insurance & thresholds** | `capm/homeWarranty.ts` (First Resort Scheme, $20k trigger incl. variations), `capm/thresholds.ts` (major-contract threshold switch-over) | ~90% |
| **Gateway review by a mentor** | Client-portal pattern: `capm/clientPortal.ts` + `invite-client` magic-link token gives read-only outside access | ~60% |
| **Document storage** | `storage/drive.ts` + `googleOAuth.ts`. Each customer connects **their own** Google Drive, so we pay nothing for storage | ~90% |
| Sign-in | `auth.ts` magic links (no passwords) | 100% |

**Not needed for owner-builders:** employees, apprenticeships, awards, super, Fair Work statements, vehicles, subscriptions, and security-of-payment claim handling (which doesn't apply to an owner-occupier's domestic work).

**Not in SKHB (owner-builder only):** tender comparison (already built in OBiaB), rooms/specs/My Build, owner-builder eligibility and consent tracking, council register content, billing (Stripe), and multi-customer support (see below).

## Things to decide before reusing

1. **One deployment per customer won't work for owner-builders.** SKHB deploys one instance per business. That's fine for tradies paying monthly, but impossible for hundreds of $500 Build Passes. Every table already carries `businessId`, and the README says multi-tenant is "a config change, not a rewrite". Realistically that means Postgres instead of SQLite, a tenant check on every query, and per-tenant cron runs.
2. **How to share code.** Options:
   - (a) Copy the pure modules and their tests into a new Next.js app for OBiaB. Fastest.
   - (b) Pull them into a shared `@tradies-bureau/core` package used by both apps. Best long-term.
   - (c) Run OBiaB as a "mode" inside SKHB. Least new code, but it mixes two products.

   Recommendation: (a) now, moving to (b) once both products are live.
3. **Point of view.** SKHB is written for a builder managing subcontractors and billing a client. An owner-builder is *both* the builder and the client, so labels and some rules flip. For example, deposit caps become a check on what a trade asks the owner-builder to pay.

## Fact to fix in OBiaB

SKHB's `thresholds.ts` records that the major domestic building contract threshold rise to $20,000 is **legislated** by the *Building and Plumbing Administration and Enforcement Act 2026* (assent 19 May 2026). The start date isn't proclaimed yet but must be no later than 1 December 2027. OBiaB currently calls it "proposed / under consultation" in `compliance.html`, `contracts.html` and `faq.html`. That wording should be updated after a quick check against the Act.
