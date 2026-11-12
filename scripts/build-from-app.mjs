#!/usr/bin/env node
// Rebuilds the parts of the site that come straight from the app (SKHB repo),
// so the site never says something different from the app:
//
//   js/trade-data.js   what applies to each trade, for the picker on the home page
//   trades.html        the same, written out trade by trade (between the markers)
//   guide.html         the app's how-to articles (between the markers)
//
//   node --experimental-strip-types scripts/build-from-app.mjs ../SKHB
//
// It reads packs/vic-core.json (the requirement rules), and uses the app's own
// src/lib/requirements/conditions.ts to decide what applies, and
// src/lib/docsContent.ts for the articles. Run it after the rules or the guide
// change in the app, then commit what it writes.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const APP = path.resolve(process.argv[2] || "../SKHB");
const LIVE = "https://portal.tradiesbureau.com";

if (!fs.existsSync(path.join(APP, "packs/vic-core.json"))) {
  console.error(`Can't find the app at ${APP}. Pass the path to the SKHB repo.`);
  process.exit(1);
}

const pack = JSON.parse(fs.readFileSync(path.join(APP, "packs/vic-core.json"), "utf8"));
const { conditionHolds } = await import(pathToFileURL(path.join(APP, "src/lib/requirements/conditions.ts")));
const { DOCS } = await import(pathToFileURL(path.join(APP, "src/lib/docsContent.ts")));

// ---------------------------------------------------------------- trades

// The order and the short names the site uses. Keys are the app's.
const TRADE_ORDER = ["Electrician", "Plumber", "Builder", "Carpenter", "Roofer", "Waterproofer", "Refrigeration", "Solar", "Plasterer", "Painter", "Landscaper", "BuildingDesigner"];
const TRADE_NAMES = { Refrigeration: "Refrigeration and air conditioning", Solar: "Solar installer", BuildingDesigner: "Building designer" };
const REGISTERS = {
  ESV: "Energy Safe Victoria",
  BPC: "Building and Plumbing Commission",
  ARC: "Australian Refrigeration Council",
  SAA: "Solar Accreditation Australia",
};
// How the site groups the app's categories.
const GROUPS = [
  ["licence", "Licences and registrations", ["licence", "registration"]],
  ["insurance", "Insurance", ["insurance"]],
  ["tickets", "Tickets and training", ["training", "check"]],
  ["job", "On each job", []], // anything whose subject is a job
  ["paperwork", "Dates and paperwork", ["deadline", "financial", "safety", "statement", "certificate"]],
];
// Questions about one person rather than the business. The picker is about
// the business, so these stay in the full Checker.
const PERSON_ONLY = new Set(["non-citizen", "drives-work-vehicle", "works-with-children"]);
const EMPLOYS = "employs-staff";
// The app words these about one person; the picker asks about the business.
const QUESTION_LABELS = { "high-risk-plant": "We operate boom lifts over 11m, forklifts, scaffolding, rigging or dogging" };

function groupOf(req) {
  if (req.subjectTypes.includes("job")) return "job";
  return GROUPS.find(([, , cats]) => cats.includes(req.category))[0];
}

/** Every requirement code that applies to a business in this trade with these answers. */
function applies(trade, ticked) {
  const capabilities = pack.capabilities.map((c) => c.key).filter((k) => ticked.has(k));
  const workTypes = pack.workTypes.map((w) => w.key).filter((k) => ticked.has(k));
  const hasEmployees = ticked.has(EMPLOYS);
  const base = { trades: [trade], capabilities, workTypes };
  const contexts = [
    { subjectType: "business", subject: { ...base, hasEmployees } },
    { subjectType: "person", subject: { ...base, isOwner: true } },
    { subjectType: "job", subject: { workTypes } },
  ];
  if (hasEmployees) contexts.push({ subjectType: "person", subject: { ...base, isOwner: false } });
  const out = new Set();
  for (const req of pack.requirements) {
    for (const ctx of contexts) {
      if (req.subjectTypes.includes(ctx.subjectType) && conditionHolds(req.conditions, ctx)) out.add(req.code);
    }
  }
  return out;
}

const reqByCode = new Map(pack.requirements.map((r) => [r.code, r]));
const usedCodes = new Set();
const trades = TRADE_ORDER.map((key) => {
  const t = pack.trades.find((x) => x.key === key);
  if (!t) throw new Error(`Trade ${key} isn't in the pack`);
  const always = applies(key, new Set());
  const questions = [
    ...pack.workTypes.filter((w) => w.trades.includes(key)).map((w) => ({ key: w.key, label: w.label, help: w.helpText, kind: "work" })),
    ...pack.capabilities
      .filter((c) => !PERSON_ONLY.has(c.key) && (c.trades.length === 0 || c.trades.includes(key)))
      .map((c) => ({ key: c.key, label: QUESTION_LABELS[c.key] || c.question.replace(/^I /, "We ").replace(/\bmy\b/g, "our"), kind: "does" })),
    { key: EMPLOYS, label: "We employ staff or apprentices", kind: "does" },
  ]
    .map((q) => ({ ...q, adds: [...applies(key, new Set([q.key]))].filter((c) => !always.has(c)) }))
    .filter((q) => q.adds.length > 0);
  const on = new Set([...(t.suggestedCapabilities || []), ...(t.suggestedWorkTypes || [])]);
  for (const q of questions) q.on = on.has(q.key);
  [...always, ...questions.flatMap((q) => q.adds)].forEach((c) => usedCodes.add(c));
  return { key, name: TRADE_NAMES[key] || t.label, always: [...always], questions };
});

function firstSentenceRegulator(req) {
  const reg = req.evidence?.registerCheck;
  return reg ? REGISTERS[reg] || reg : null;
}

const requirements = {};
for (const code of usedCodes) {
  const r = reqByCode.get(code);
  requirements[code] = {
    name: r.name,
    group: groupOf(r),
    law: !!r.legal,
    optional: !!r.optional,
    why: r.whyText || "",
    register: firstSentenceRegulator(r),
  };
}

const data = { groups: GROUPS.map(([key, label]) => ({ key, label })), requirements, trades };
fs.writeFileSync(
  path.join(ROOT, "js/trade-data.js"),
  "// Written by scripts/build-from-app.mjs from the app's rules (packs/vic-core.json). Don't edit by hand.\n" +
    "window.TB_TRADES = " + JSON.stringify(data) + ";\n"
);

// ---------------------------------------------------------------- html helpers

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const slug = (s) => s.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();

function inject(file, name, html) {
  const p = path.join(ROOT, file);
  const src = fs.readFileSync(p, "utf8");
  const re = new RegExp(`(<!-- ${name}:start -->)[\\s\\S]*?(<!-- ${name}:end -->)`);
  if (!re.test(src)) throw new Error(`${file} has no ${name} markers`);
  fs.writeFileSync(p, src.replace(re, (_, a, b) => `${a}\n${html}\n${b}`));
}

function reqItem(code) {
  const r = requirements[code];
  const tag = r.law ? (r.optional ? "By law, if it applies to you" : "Required by law") : r.optional ? "Optional" : "Usually asked for";
  const cls = r.law ? "req-law" : "req-asked";
  return (
    `<li class="req ${cls}"><div class="req-head"><span class="req-name">${esc(r.name)}</span><span class="req-tag">${tag}</span></div>` +
    (r.why ? `<p>${esc(r.why)}</p>` : "") +
    (r.register ? `<p class="req-register">Checked against the ${esc(r.register)} register.</p>` : "") +
    `</li>`
  );
}

function grouped(codes) {
  return data.groups
    .map((g) => {
      const items = codes.filter((c) => requirements[c].group === g.key);
      if (!items.length) return "";
      return `<h4>${esc(g.label)}</h4>\n<ul class="req-list">\n${items.map(reqItem).join("\n")}\n</ul>`;
    })
    .filter(Boolean)
    .join("\n");
}

// ---------------------------------------------------------------- trades.html

const tradeNav = trades.map((t) => `<li><a href="#${slug(t.key)}">${esc(t.name)}</a></li>`).join("\n");
const tradeSections = trades
  .map((t) => {
    const check = `/check?trade=${t.key}`;
    const qs = t.questions
      .map(
        (q) =>
          `<details class="trade-if"><summary>${esc(q.kind === "work" ? "If your work includes: " + q.label : "If " + q.label.replace(/^We /, "you ").replace(/\bour\b/g, "your"))}</summary>\n` +
          `<ul class="req-list">\n${q.adds.map(reqItem).join("\n")}\n</ul>\n</details>`
      )
      .join("\n");
    return (
      `<section class="trade-doc" id="${slug(t.key)}" data-spy>\n` +
      `<h2>${esc(t.name)}</h2>\n` +
      `<p class="trade-doc-count">${t.always.length} things apply to every Victorian business in this trade. More depend on the work you take on.</p>\n` +
      `<h3>Every business in this trade</h3>\n${grouped(t.always)}\n` +
      (qs ? `<h3>Depending on your work</h3>\n${qs}\n` : "") +
      `<p class="trade-doc-cta"><a class="btn btn-primary" href="${LIVE}${check}" data-portal="${check}">Check your own business</a> <a class="text-link" href="index.html#trades">Try it here first</a></p>\n` +
      `</section>`
    );
  })
  .join("\n\n");
inject("trades.html", "trade-nav", tradeNav);
inject("trades.html", "trades", tradeSections);

// ---------------------------------------------------------------- guide.html

// Left out of the public site: it's about how the app's storage is wired up.
const SKIP_DOCS = new Set(["document-storage"]);
const SECTION_NAMES = { "Admin Guide": "Running the business", "User Guide": "For you and your crew" };
const docs = DOCS.filter((d) => !SKIP_DOCS.has(d.slug));

// Paths the articles mention (/check, /compliance/map) become links into the app.
function prose(s) {
  return esc(s).replace(/(^|\s)(\/[a-z][a-z/-]*[a-z])(?=[\s.,)]|$)/g, (_, pre, p) => `${pre}<a href="${LIVE}${p}" data-portal="${p}">${p.slice(1)}</a>`);
}

function block(b) {
  if (typeof b === "string") return `<p>${prose(b)}</p>`;
  if ("heading" in b) return `<h3>${esc(b.heading)}</h3>`;
  if ("steps" in b) return `<ol class="doc-steps">\n${b.steps.map((s) => `<li>${prose(s)}</li>`).join("\n")}\n</ol>`;
  if ("list" in b) return `<ul>\n${b.list.map((s) => `<li>${prose(s)}</li>`).join("\n")}\n</ul>`;
  if ("tip" in b) return `<p class="doc-tip">${prose(b.tip)}</p>`;
  return `<details class="doc-qa"><summary>${esc(b.qa[0])}</summary><p>${prose(b.qa[1])}</p></details>`;
}

const sections = [...new Set(docs.map((d) => d.section))];
const guideNav = sections
  .map(
    (s) =>
      `<li class="rail-group">${esc(SECTION_NAMES[s] || s)}</li>\n` +
      docs.filter((d) => d.section === s).map((d) => `<li><a href="#${d.slug}">${esc(d.title)}</a></li>`).join("\n")
  )
  .join("\n");
const guideBody = docs
  .map(
    (d) =>
      `<article class="doc" id="${d.slug}" data-spy>\n<h2>${esc(d.title)}</h2>\n<p class="doc-summary">${esc(d.summary)}</p>\n${d.body.map(block).join("\n")}\n</article>`
  )
  .join("\n\n");
inject("guide.html", "guide-nav", guideNav);
inject("guide.html", "guide", guideBody);

console.log(`Wrote js/trade-data.js (${trades.length} trades, ${usedCodes.size} requirements), trades.html and guide.html (${docs.length} articles).`);
