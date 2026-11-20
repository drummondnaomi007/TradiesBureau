# Problems Tradies Bureau solves (as at 20 November 2026)

An internal brief. It lists the problems small Victorian trade businesses have with compliance, onboarding and audits, says what the app does about each, and marks what it doesn't do yet. The public version is `problems.html`, which only includes what the app does today.

**How this was checked:** against this site's own pages (`features.html`, `builders.html`, and `trades.html` and `guide.html`, which are built from the app's rule pack and guide). The app's code (SKHB) wasn't read for this brief, so check the "Not yet" and "Ideas" items against SKHB before building or promising them. Compliance facts come from `victoria-trade-compliance-2026.md`.

Status key: **Solved**: the app does this today. **Partly**: it helps, but some of the problem is left to the owner. **Not yet**: no sign of it on the site; it may or may not be in the app.

---

## Who has these problems

| Who | What their week looks like | What hurts most |
|---|---|---|
| Owner-operator electrician or plumber (1 to 10 staff) | On the tools all day, quotes and paperwork at night | Renewals and certificate deadlines kept in their head; proving cover to builders |
| Small employer taking on apprentices | Hiring, supervising, paying under an award | Fair Work paperwork, award rates, apprentice supervision ratios, WorkCover dates |
| Trade business that uses subbies | Chasing certificates by text | Lapsed cover mid-job, sham contracting, super owed to "contractors" |
| Builder or head contractor | Running several trades per job | Awarding work to unlicensed or uninsured trades; Domestic Building Contracts Act rules |
| Contract administrator (new audience, see below) | Moving claims, variations, delays and certificates between builder, trades and client | Statutory deadlines across several jobs and businesses |
| Owner in their mid-50s and beyond | Thinking about stepping back | A business that only runs on their memory isn't worth much to a buyer |

---

## 1. Running the business: juggling it all

| Problem | What the app does | Status |
|---|---|---|
| Licences, registrations, insurance and tickets all renew on different dates (REC up to 5 years, A-grade licence 5 years with CPD, policies yearly) | Compliance map built from the trade and work ticked in the Checker; met, due within 30 days, or missing | Solved |
| Finding out about a lapse when a builder or customer asks | Sunday digest; WhatsApp alerts for anything critical outside quiet hours; text "check" for a live summary | Solved |
| Certificate deadlines missed at the end of a job (COES to customer within 1 month; prescribed work inspected within 8 business days; plumbing compliance certificate within 5 days, for work of $750 or more) | Jobs carry their certificate deadlines | Solved |
| Yearly and quarterly dates sneak up (LeavePlus quarterly, TPAR 28 August, WorkCover declaration and 1 October discount) | Recurring deadlines come round each year automatically | Solved |
| Security of Payment claims chased from memory (schedule within 10 business days; payment within 20 business days at most) | Claims logged with schedule and payment due dates, reminders before they pass | Solved |
| Paperwork scattered across email, the ute and a shoebox | Photo upload with the expiry read off the certificate; Google Drive folder | Solved |
| The business can't run without the owner | Admin role with the same access as an owner; one map anyone authorised can read | Partly: the records are shared, but the doing still depends on people |
| Plumbers' warranty cover must be $50,000 *per compliance certificate*, not a $50,000 total cap | Warranty cover is a requirement for plumbers on domestic work | Partly: check whether the app warns about a policy with a total cap |

## 2. Onboarding employees

| Problem | What the app does | Status |
|---|---|---|
| Not knowing which Fair Work statements to give | Fair Work statements sent and signed off, including the Fixed Term Contract Information Statement; reminder when a contract ends | Solved |
| Paying the wrong award or classification | Award and classification recorded; digest flags pay not checked since the last 1 July wage review | Solved |
| Not knowing who holds which tickets | Per-person right to work, driver licence, Working with Children, White Card, high-risk work licences | Solved |
| Apprentice supervision (ESV ratios mandatory since 1 September 2025: 1:1 direct for first-years, up to 5 under broad supervision) | Supervision ratios at a glance | Solved |
| Staff seeing more than they should | Employee role; everyone signs in as themselves | Solved |
| Registering for WorkCover in time (pay over $7,500 a year, or any apprentice or trainee, within 60 days) | Declaration and premium dates are tracked | Not yet: check SKHB for a registration prompt when the first employee or apprentice is added |
| Tax file number declaration, super choice form, bank details | None seen | Not yet |
| Payday Super from 1 July 2026: super must reach the fund within 7 business days of each payday | None seen | Not yet: a reminder or check would suit the digest |
| Site induction, PPE issued, emergency contacts, a starter checklist | None seen | Not yet: an onboarding checklist per new starter is the natural next step |
| Payroll tax threshold ($1m a year) as the business grows | None seen | Not yet: low priority for most small trades |

## 3. Onboarding subcontractors

| Problem | What the app does | Status |
|---|---|---|
| Chasing certificates by text | Invite link; subbie uploads their own paperwork; agreements signed online | Solved |
| Accepting a wrong or expired certificate | Uploads wait for review; accept, or reject with a reason and a resend link | Solved |
| Not knowing what to require of them | Your own requirements (for example WorkCover and PI) on top of what the trade legally needs | Solved |
| Sham contracting and super owed to contractors paid mainly for their labour | Contractor-or-employee check on the Fair Work Ombudsman's indicators, saved with a date; possible super liability flagged | Solved |
| Cover lapsing mid-job | Nightly recheck; certificates running out during a job flagged in the digest | Solved |
| ABN cancelled or GST status wrong | ABN and GST on file, rechecked every night | Solved |
| End-of-job certificates not handed over | Subbies send COES or plumbing compliance certificates to the handover checklist | Solved |
| TPAR: payments to contractors reported by 28 August | Deadline reminder | Partly: the app reminds, but doesn't total payments |
| Some contractors are deemed workers for WorkCover, so their pay counts as remuneration | Contractor check | Partly: check whether the result feeds into the WorkCover estimate |

## 4. Audits and proof

| Problem | What the app does | Status |
|---|---|---|
| "Send me your licence and insurance" | Live credentials link, register links, masked policy numbers, QR code, open and download tracking, expiry and withdrawal | Solved |
| Is the record genuine? | Each record shows how it was checked, up to the official register | Solved |
| Who changed what, and when? | Audit trail with CSV exports | Solved |
| Auditor needs to look without touching | Read-only Auditor role | Solved |
| Gaps that look like neglect | "Doesn't apply" with the reason kept | Solved |
| WorkSafe incidents and safety paperwork | 48-hour written notice tracked; incidents and site safety audits; SWMS deadlines on jobs | Solved |
| One pack of everything for an audit or prequalification | CSV exports and the credentials link | Partly: a single "audit pack" PDF or zip per date range would make audit day one click |

## 5. Builders and head contractors

Covered on `builders.html`: tenders on compliant trades, a reason required to award to a non-compliant bidder, client quote sharing, Domestic Building Contracts Act deposit and progress caps, home warranty over $20,000, inspection stages, handover certificates, and mid-project flags. All solved.

---

## 6. Contract administrators (new audience)

**The idea:** a contract administrator manages the paperwork of a job on behalf of a builder or owner. Their work is mostly statutory deadlines and records, and most of it already exists in the app as features for builders. They often work for several builders, which the multi-business sign-in already handles.

**What already fits:**

- Security of Payment claims with schedule and payment due dates
- Variations signed online, sent to the client with a PDF
- Delays and extension of time register
- Mandatory inspection stages and waterproofing records
- Deposit and progress claim checks under the Domestic Building Contracts Act
- Handover certificates collected from trades and passed to the client
- Switching between businesses; read-only Auditor role
- Audit trail and CSV exports

**What a contract administrator would likely need next** (ideas, to test with real contract administrators before building):

1. **One view across every job and business**: every claim, schedule and notice due this week, whichever builder it belongs to.
2. **Adjudication deadlines**: after a payment schedule, the 10-business-day windows for an adjudication application and the decision.
3. **Notices register**: show cause, suspension and other contract notices, with their response periods.
4. **Practical completion and the defects liability period**, with the dates for releasing retention.
5. **Variation register with cost and time effect**, rolled up into the contract sum and completion date.
6. **Time bars on extension of time claims**, warned before a claim is out of time.
7. **A contract administrator role**: able to issue and record documents on a job without owner or admin rights to the whole business.
8. **Domestic contract reforms**: the Domestic Building Contracts Amendment Act 2025 was due to start by 1 December 2026, but a delay was legislated. Track the new date and update the contract checks.

**Next step:** talk to three to five contract administrators. Ask what they track in spreadsheets today, and which of the items above they would pay for. The contact link in the contract administrators section of `problems.html` collects interest in the meantime.

---

## One-liners for marketing

- Every licence, policy and ticket for your trade, with a heads-up before anything lapses.
- New starter? The Fair Work statements, award check and tickets in one place.
- Subbies send their own paperwork, and nothing counts until you've checked it.
- Proof for a builder, insurer or auditor in one link, always current.
- Award work only to trades who hold what the job needs.
- The paper trail on every job (claims, variations, delays, certificates) in one place.
