# Plan: Council & approvals coverage

Source: owner-builder research item "Council approvals for a Victorian single-family home" (received Sept 2026).
Goal: make sure every point in the research is answered in the content or handled by a feature in Owner Builder in a Box.

---

## 1. Evaluation of the research

**Overall: accurate and useful.** The core message is right and is the most valuable thing we can teach: *council ≠ building surveyor*. Council handles planning, local laws and council assets. The relevant building surveyor (RBS) handles the building permit, mandatory inspections and the occupancy permit. Keep two separate lists and cross-reference them.

### Corrections and nuances to build in

| # | Research says | Refinement |
|---|---|---|
| 1 | A planning permit may be required for "construction of a new dwelling" | In most residential zones a single dwelling needs a planning permit **only** on a small lot (under 300 m², or 500 m² where the zone schedule says so) or when an overlay triggers one. Otherwise siting is assessed by the RBS under **Part 5 of the Building Regulations 2018**. |
| 2 | Planning permit for "front setbacks, site coverage, overlooking…" | Where no planning permit is needed and the design varies the Part 5 siting rules, the RBS needs a **council report and consent** (Building Regulations). The research leaves this out, and it's a common owner-builder delay. |
| 3 | Demolition may need a planning permit | Demolition always needs a **building permit**. For significant demolition the RBS must also get **council report & consent under s29A of the Building Act**. A planning permit is needed only where an overlay (e.g. heritage) applies. |
| 4 | "For a $400,000 owner-built home…" | The research is written for one project. We'll generalise it: consent applies over **$20,000**. At **$350,000 or more**, WorkSafe **principal contractor** duties also apply, and the research doesn't mention them. |
| 5 | Tree controls "from a planning overlay, local law or both" | Correct. Add: native vegetation removal can also be controlled by **Clause 52.17** of the planning scheme, not just overlays. |
| 6 | Stormwater / legal point of discharge | Correct. Add: on flood-prone land, the RBS needs a council report & consent and the **flood level from the floodplain authority** (e.g. Melbourne Water or the local catchment management authority), which sets the finished floor level. |

### Gaps: authorities the research doesn't cover (in scope for us)

- **Water authority:** build-over-easement consent, sewer connection, property service plan, water meter.
- **Unsewered lots (important for regional owner-builders):** council **septic tank permit** and a land capability assessment.
- **Power, gas and NBN:** new connection applications, often with long lead times.
- **Before You Dig Australia** and **protection work notices** to neighbours.
- **Title:** covenants and **s173 agreements**. A planning permit can't override a covenant.
- **Bushfire:** the difference between the Bushfire Management Overlay (a planning control) and a Bushfire Prone Area (a building control via BAL / AS 3959).
- **Council property information** request to the RBS/council (Building Regulations reg 51). This is a cheap first step that surfaces flood, termite and designated land.

### Current coverage in the app

| Research topic | Where it is today | Status |
|---|---|---|
| Council vs building surveyor roles | FAQ, Gateways RACI | 🟡 Partial: not stated clearly anywhere |
| Planning permit triggers | Compliance §3 (one item) | 🟡 Partial |
| Building permit documents | Compliance §3–4 | 🟢 Covered |
| Certificate of consent | Compliance §2 | 🟢 Covered |
| Asset protection permit + pre-condition photos | Compliance §4 (one item) | 🟡 Partial: no guided photo report |
| Vehicle crossing permit | none | 🔴 Gap |
| Road / footpath occupation permit | none | 🔴 Gap |
| Tree protection | Overlays mention only | 🔴 Gap |
| Stormwater / legal point of discharge | Compliance §3, Guides | 🟡 Partial |
| Site & construction controls (hours, sediment, waste) | Compliance §4 site set-up | 🟡 Partial |
| Council completion items | Compliance §9 asset bond | 🟡 Partial |
| "Occupancy permit ≠ all council conditions discharged" | none | 🔴 Gap |
| **Council register with owner, due date and evidence per condition** | none | 🔴 Gap: the key control in the research |
| "What council does not replace" | implicit | 🟡 Partial |

---

## 2. Plan

### Phase 1: Content (1–2 days, no new code)

1. **New page `approvals.html`: "Who approves what"**
   - A two-column visual: **Council / planning** vs **Building surveyor / building**, plus a third lane for **other authorities** (water, power, NBN, floodplain authority, WorkSafe, BPC).
   - Every approval gets a card: *what it is · when it's triggered · who issues it · what you submit · typical conditions · evidence to keep.* This covers the planning permit, report & consent (siting, demolition s29A, flood), asset protection, vehicle crossing, road/footpath occupation, tree permits, legal point of discharge / stormwater, septic, build-over-easement and connections.
   - A callout box: **"What council does not replace"**, using the research list.
2. **Restructure `compliance.html` §3–4** into three sections: *Planning & council*, *Building permit (surveyor)* and *Other authorities*. Add checklist items for the crossover, road occupation, tree protection, report & consent, s29A demolition, flood level, septic and property information request.
3. **Update `gateways.html`:**
   - G0: property information request and council planning enquiry.
   - G2: planning permit **and** council checklist obtained; RBS inspection schedule obtained; both cross-referenced.
   - G7 exit check: "All council conditions discharged in writing (the occupancy permit does not prove this)."
4. **Add about 10 questions to `faq.html`**, for example: Does council certify my house? Do I need a planning permit for a single house? What is report & consent? Do I need a permit for a skip or crane on the road? Can I remove a tree on my block? What is the legal point of discharge? Who signs off my crossover? Does my occupancy permit mean council is happy?
5. **Fix the facts** from the evaluation table in section 1 across all pages.

### Phase 2: "Do I need it?" wizard (2–3 days)

An **Approvals finder** on `approvals.html` that asks 10–12 plain questions:

- **Zone and lot size** (from the Planning Property Report, with a VicPlan link and a how-to)
- **Overlays**, ticked from a list: HO, BMO, LSIO/SBO, VPO, ESO, SLO, NCO, DDO
- Is there an existing house to demolish?
- Any trees within X m of the works?
- New or changed crossover?
- Sewer or septic?
- Easements, covenants or s173 agreements on the title?
- Will skips, cranes or pumps sit on the road?
- Bushfire prone area?
- Estimated project value: triggers consent ($20k) and principal contractor ($350k)

**Output:** a personalised list of *likely* approvals, each tagged *Likely*, *Check with council* or *Not likely*, with the authority and a link. It saves straight into the Council register (Phase 3). The output is always labelled "confirm with council and your building surveyor".

### Phase 3: Council & approvals register in My Build (3–4 days)

This is the key control in the research. It turns "assign every condition to a person, due date and evidence" into a feature.

- **Approvals list:** type, issuing authority, reference number, date issued, expiry, and a link to the document.
- **Conditions under each approval:** condition text, **responsible person** (owner-builder, designer, trade…), **due gateway or date**, **evidence required**, evidence attached (photo, document link), status (Open → Evidence collected → Confirmed in writing).
- **Two registers, cross-referenced:** *Council / planning register* and *Building permit & inspection schedule*. A condition can link to an inspection. Example: "Tree protection fencing installed" links to "Pre-start" and "Footings inspection".
- **Dashboard:** open conditions by gateway, overdue items, and a "ready for occupancy?" check that lists anything still open.
- **Export:** a PDF/CSV council register for the lender, a buyer, or a refinance.

### Phase 4: Pre-condition & close-out reports (2 days)

- **Guided pre-condition photo report** for asset protection. A shot list covers kerb and channel, footpath, nature strip, street trees, pits, crossover, road pavement, laneway and neighbours' fences. Each photo is date-stamped with GPS where available, and the report exports as a PDF to lodge with council.
- **Completion photo report** with the same shot list at the end, compared side-by-side with the pre-condition photos.
- **Site controls checklist** for display on site: construction hours, sediment control, waste, public safety. Add a **road occupation prompt** in the program: when a crane, pump or skip is booked, the app asks whether a road occupation permit is in place.

### Phase 5: Council directory (ongoing data work)

- A per-council page for the **79 Victorian councils**, linking to the asset protection, vehicle crossing, tree local law, construction hours, road occupation and stormwater pages.
- Start with the 10–15 councils where early customers are building (growth corridors plus the regional councils with the most owner-builder permits). Add the rest over time.
- This is also a partnership and SEO opportunity.

---

## 3. Verification before publishing

Have these confirmed by a building surveyor or planning lawyer:

- Single-dwelling planning permit lot-size triggers per zone (GRZ / NRZ / RGZ / LDRZ / rural zones)
- Report & consent regulation numbers and when each applies (siting, demolition s29A, flood, over easements)
- Septic permit process under the current EPA and council arrangements
- Whether the BPC certificate of consent template or process changed after 1 July 2026

## 4. Suggested order

| Priority | Item | Why |
|---|---|---|
| 1 | Phase 1 content + fact fixes | Cheap, closes most gaps, improves trust |
| 2 | Phase 3 register | The key control in the research, and a strong reason to pay for a subscription |
| 3 | Phase 2 wizard | Great for onboarding and free-tier conversion |
| 4 | Phase 4 photo reports | Solves a real pain point (bond refunds, disputes) |
| 5 | Phase 5 directory | Ongoing, scales with customers |
