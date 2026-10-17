#!/usr/bin/env python3
"""Build the offline Owner Builder in a Box workbook (Excel / Google Sheets).

The checklists, gateways, trade packages, guides and Q&A are read from the
Owner Builder in a Box prototype, so the workbook says exactly what the web app
says. By default the prototype is read from this repository's history
(commit 99fe447). Pass --src to read an unpacked copy instead.

    python3 _owner-builder-sheets/build_workbook.py
    python3 _owner-builder-sheets/build_workbook.py --src path/to/owner-builder-in-a-box
"""
import argparse
import datetime
import html
import os
import re
import subprocess

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.formula import ArrayFormula

HERE = os.path.dirname(os.path.abspath(__file__))
PROTOTYPE_COMMIT = "99fe447"

# ---------------------------------------------------------------- styling

NAVY, NAVY_700, TEAL, NAVY_100 = "1A365D", "2D5A8C", "0B6E8F", "E8F1F6"
F_HEAD = PatternFill("solid", fgColor=NAVY)
F_AUTO_HEAD = PatternFill("solid", fgColor=NAVY_700)
F_AUTO = PatternFill("solid", fgColor="F1F4F7")
F_EXAMPLE = PatternFill("solid", fgColor="FFF4D6")
F_SECTION = PatternFill("solid", fgColor=NAVY_100)
F_RED = PatternFill("solid", fgColor="F8D7DA")
F_AMBER = PatternFill("solid", fgColor="FFE8B0")
F_GREEN = PatternFill("solid", fgColor="D4EDDA")
WHITE_BOLD = Font(bold=True, color="FFFFFF")
TITLE = Font(bold=True, size=16, color=TEAL)
BOLD = Font(bold=True)
MUTED = Font(italic=True, color="5A6B7D")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Border(bottom=Side(style="thin", color="D5DDE5"))

MONEY = '"$"#,##0'
DATE = "d mmm yyyy"
EXAMPLE_NOTE = "EXAMPLE: delete this row"

HEADER_ROW = 3
FIRST = 4

# ---------------------------------------------------------------- source content


def read_source(src, name):
    if src:
        with open(os.path.join(src, name), encoding="utf-8") as f:
            return f.read()
    return subprocess.run(
        ["git", "show", f"{PROTOTYPE_COMMIT}:owner-builder-in-a-box/{name}"],
        cwd=HERE, check=True, capture_output=True, text=True,
    ).stdout


def text(fragment):
    """HTML fragment to plain text, keeping list items as bullets."""
    s = re.sub(r"<li[^>]*>", "\n• ", fragment)
    s = re.sub(r"</(p|ul|div)>", "\n", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*", "\n", s)
    return s.strip()


def parse_compliance(src):
    s = read_source(src, "compliance.html")
    items = []
    for block in re.findall(r'<div class="content-block" id="[^"]+">(.*?)</ul>', s, re.S):
        h2 = re.search(r"<h2>(.*?)</h2>", block)
        if not h2 or "check-list" not in block:
            continue
        stage = text(h2.group(1))
        for m in re.finditer(r'data-id="([^"]+)"><div><strong>(.*?)<span class="tag[^"]*">(.*?)</span></strong><small>(.*?)</small>', block, re.S):
            items.append({"id": m.group(1), "stage": stage, "item": text(m.group(2)),
                          "req": text(m.group(3)), "guide": text(m.group(4))})
    numbers = re.search(r'id="numbers".*?<tbody>(.*?)</tbody>', s, re.S)
    key_numbers = [[text(c) for c in re.findall(r"<td>(.*?)</td>", row, re.S)]
                   for row in re.findall(r"<tr>(.*?)</tr>", numbers.group(1), re.S)]
    return items, key_numbers


def parse_gateways(src):
    s = read_source(src, "gateways.html")
    gates = []
    for art in re.findall(r'<article class="gate" id="g\d">(.*?)</article>', s, re.S):
        g = {
            "code": text(re.search(r'gate-badge">(.*?)<', art).group(1)),
            "name": text(re.search(r"<h3>(.*?)</h3>", art).group(1)),
            "purpose": text(re.search(r"</h3><p>(.*?)</p>", art).group(1)),
            "sections": [],
        }
        for h4, ul in re.findall(r"<h4>(.*?)</h4><ul>(.*?)</ul>", art, re.S):
            g["sections"].append((text(h4), [text(li) for li in re.findall(r"<li>(.*?)</li>", ul, re.S)]))
        foot = re.search(r'gate-foot">(.*?)</div>', art, re.S).group(1)
        tag = re.search(r'<span class="tag">(.*?)</span>', foot)
        g["spent"] = text(tag.group(1)).replace(" of budget spent", "") if tag else ""
        g["decision"] = text(re.sub(r'<span class="tag">.*?</span>', "", foot)).replace("Decision: ", "")
        gates.append(g)
    tables = re.findall(r"<table[^>]*>(.*?)</table>", s, re.S)

    def rows(t):
        return [[text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
                for r in re.findall(r"<tr>(.*?)</tr>", t, re.S)]
    return gates, rows(tables[0]), rows(tables[1])  # gates, RACI, starter risks


def parse_contracts(src):
    s = read_source(src, "contracts.html")
    tables = re.findall(r"<table[^>]*>(.*?)</table>", s, re.S)

    def rows(t):
        return [[text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
                for r in re.findall(r"<tr>(.*?)</tr>", t, re.S) if "<td" in r]
    return rows(tables[0]), rows(tables[1])  # packages, contract types


def parse_tenders(src):
    s = read_source(src, "tenders.html")
    lists = {}
    for h3, ul in re.findall(r"<h3[^>]*>(.*?)</h3>\s*<ul[^>]*>(.*?)</ul>", s, re.S):
        lists[text(h3)] = [text(li) for li in re.findall(r"<li[^>]*>(.*?)</li>", ul, re.S)]
    return lists


def parse_qa(src, name):
    """Guides and Q&A pages share the same markup: groups of <details class="qa">."""
    s = read_source(src, name)
    out = []
    for group in re.findall(r'<div class="faq-group">(.*?)\n    </div>', s, re.S):
        heading = text(re.search(r"<h3>(.*?)</h3>", group).group(1))
        for summary, answer in re.findall(r"<summary>(.*?)</summary><div class=\"answer\">(.*?)</div></details>", group, re.S):
            out.append((heading, text(summary), answer))
    return out


# ---------------------------------------------------------------- reference data

FOLDERS = [
    ("00", "00 Project Register", "This workbook, its backups and the Apps Script notes.", "", "All", "Every tab"),
    ("01", "01 Eligibility, Land & Planning", "eLearning pass, white card, certificate of consent and application, title search, plan of subdivision, covenants, s173 agreements, Planning Property Report, planning permit, legal point of discharge, build-over-easement and siting consents.", "1, 2, 3", "G0, G1, G2", "Compliance, Gateways, Documents"),
    ("02", "02 Design & Engineering", "Design brief, concept and working drawings, specification, engineering, energy (NatHERS) report, BAL assessment, feature & level survey, soil report, asbestos report, approved amendments.", "3, 8", "G1, G2", "Documents, Rooms (drawing refs), Diary (plan notes)"),
    ("03", "03 Permits, Insurance & Finance", "RBS fee proposal and appointment, building permit, asset protection permit and bond, protection work notices, Before You Dig, your insurance policies, WorkSafe and principal contractor papers, loan, valuations, drawdowns, cost plan, tax advice.", "4, 5, 6, 11", "G0, G1, G3", "Project, Packages, Compliance"),
    ("04", "04 Trades & Tenders", "One subfolder per trade package. In each: RFQ pack and quotes, tender comparison, signed contract and variations, licence, insurance certificates of currency and SWMS, invoices and payment records.", "5, 6, 7", "G3 to G7", "Packages, Trades, Tenders, Variations, Payments"),
    ("05", "05 Selections & Specs", "Product spec sheets, brochures, colour and tile codes, quotes from suppliers, orders and delivery dockets.", "", "G5, G6", "Selections"),
    ("06", "06 Site Diary & Photos", "Site photos (especially before anything is covered), diary exports, site induction and sign-in register.", "5, 8", "G4 to G7", "Diary, Photos"),
    ("07", "07 Inspections & Certificates", "RBS inspection reports and every compliance certificate: plumbing (PCC), electrical (CoES), termite, waterproofing, glazing, insulation, smoke alarms, engineer sign-offs, commissioning sheets.", "8, 9", "G4 to G7", "Certificates, Compliance"),
    ("08", "08 Handover, Records & Sale", "Occupancy permit or certificate of final inspection, warranties, manuals, as-built service locations, paint and tile codes, s137B defects report, owner-builder insurance, section 32 papers.", "9, 10", "G7", "Compliance, Certificates"),
    ("99", "99 Archive", "Superseded drawings and documents, unsuccessful quotes. Never delete: move here.", "", "", "Documents (status Superseded)"),
]

PACKAGE_SHORT = [
    "01 Surveyor", "02 Demolition & earthworks", "03 Plumbing & drainage", "04 Concreter",
    "05 Termite management", "06 Frame & truss supply", "07 Carpenter (frame)", "08 Roofing",
    "09 Windows & external doors", "10 Bricklayer & cladding", "11 Electrician", "12 Insulation",
    "13 Plasterer", "14 Waterproofer", "15 Cabinetmaker", "16 Tiler", "17 Fixing carpenter",
    "18 Painter", "19 Heating & cooling", "20 Floor coverings & landscaping",
]
PACKAGE_GATE = ["G4", "G4", "G4", "G4", "G4", "G5", "G5", "G5", "G5", "G5", "G5", "G5",
                "G6", "G6", "G6", "G6", "G6", "G6", "G6", "G7"]

DOC_TYPES = [
    ("DWG", "Drawing"), ("SPEC", "Specification or spec sheet"), ("ENG", "Engineering"),
    ("RPT", "Report or assessment (soil, energy, BAL, asbestos, s137B)"), ("APP", "Application"),
    ("PMT", "Permit, consent or approval"), ("INSP", "Inspection report"), ("CERT", "Certificate"),
    ("RFQ", "RFQ pack or addendum"), ("QUO", "Quote or tender"), ("CON", "Contract"),
    ("VAR", "Variation"), ("INV", "Invoice"), ("REC", "Receipt or payment record"),
    ("INS", "Insurance policy or certificate of currency"), ("LIC", "Licence or registration"),
    ("SWMS", "Safe work method statement"), ("PHO", "Photo"), ("COR", "Correspondence"),
    ("FIN", "Finance (loan, valuation, drawdown)"), ("PLN", "Plan, program or cost plan"),
    ("MAN", "Manual"), ("WAR", "Warranty"), ("OTH", "Other"),
]

# Where each compliance item's evidence is filed, and the gateway it belongs to.
COMPLIANCE_MAP = {
    "el": ("01", "G0"), "co": ("01", "G2"), "bp": ("03", "G3"), "in": ("03", "G3"),
    "tr": ("04", "G3"), "fi": ("07", "G7"), "se": ("08", "G7"), "mo": ("03", "G1"),
}
COMPLIANCE_OVERRIDE = {
    "el-elearn": ("01", "G2"), "el-white": ("01", "G2"),
    "de-title": ("01", "G0"), "de-planning": ("01", "G2"), "de-survey": ("02", "G1"),
    "de-drawings": ("02", "G2"), "de-eng": ("02", "G2"), "de-energy": ("02", "G2"),
    "de-bal": ("02", "G2"), "de-lpod": ("01", "G2"), "de-easement": ("01", "G2"), "de-siting": ("01", "G2"),
    "oh-duty": ("03", "G3"), "oh-pc": ("03", "G3"), "oh-swms": ("04", "G3"), "oh-cards": ("04", "G3"),
    "oh-induct": ("06", "G4"), "oh-asbestos": ("02", "G1"), "oh-workcover": ("03", "G3"),
    "in-trade": ("04", "G3"), "bp-utilities": ("03", "G3"),
    "cn-notify": ("07", "G4"), "cn-plans": ("02", "G4"), "cn-pcc": ("07", "G4"), "cn-coes": ("07", "G5"),
    "cn-certs": ("07", "G6"), "cn-diary": ("06", "G4"), "cn-variations": ("04", "G4"),
    "fi-op": ("08", "G7"), "fi-asset": ("03", "G7"), "fi-insure": ("03", "G7"),
    "mo-loan": ("03", "G0"), "mo-fhog": ("03", "G1"), "mo-tax": ("03", "G0"),
}

# Gateway deliverables: first keyword match decides the suggested folder.
GATE_FOLDER_RULES = [
    ("occupancy|handover|warrant|lessons|final cost", "08"),
    ("consent|eligib|elearning|white card|title|zoning|planning|discharge|easement", "01"),
    ("selection", "05"),
    ("diary|photo", "06"),
    ("inspection|certificate|hold point|pcc|sign-off|waterproofing", "07"),
    ("rfq|tender|contract|trade|quote|paid|retention|defects", "04"),
    ("drawing|design|concept|engineer|energy|bal|survey|soil|spec|brief|frame|truss|window", "02"),
    ("budget|finance|cost|lender|drawdown|insurance|permit|asset|utilit", "03"),
]

CERTIFICATES = [
    # type, item, standard / law, who provides, package, gate, requirement
    ("Inspection", "Footings (before placing footings)", "Building permit", "Relevant building surveyor", "04 Concreter", "G4", "Must"),
    ("Inspection", "Pre-slab (before pouring)", "Building permit", "Relevant building surveyor", "04 Concreter", "G4", "Must"),
    ("Inspection", "Frame", "Building permit", "Relevant building surveyor", "07 Carpenter (frame)", "G5", "Must"),
    ("Inspection", "Other stage listed on your permit (e.g. pre-plaster, retaining wall)", "Building permit", "Relevant building surveyor", "", "G5", "If applies"),
    ("Inspection", "Final inspection", "Building permit", "Relevant building surveyor", "", "G7", "Must"),
    ("Certificate", "Set-out certificate", "", "Licensed land surveyor", "01 Surveyor", "G4", "Best practice"),
    ("Certificate", "Engineer pour approval / footing sign-off", "AS 2870", "Structural engineer", "04 Concreter", "G4", "If applies"),
    ("Certificate", "Plumbing compliance certificate: drainage & sewer", "Building Act 1993", "Licensed plumber", "03 Plumbing & drainage", "G4", "Must"),
    ("Certificate", "Termite management certificate & durable notice", "AS 3660.1", "Licensed pest controller", "05 Termite management", "G4", "Must"),
    ("Certificate", "Frame & truss design certificates, bracing plan", "AS 1684 / AS 4440", "Frame & truss supplier", "06 Frame & truss supply", "G5", "Must"),
    ("Certificate", "Plumbing compliance certificate: roofing", "AS/NZS 3500.3", "Licensed roof plumber", "08 Roofing", "G5", "Must"),
    ("Certificate", "Glazing certificate & energy labels (WERS)", "AS 2047 / AS 1288", "Window supplier / glazier", "09 Windows & external doors", "G5", "Must"),
    ("Certificate", "Plumbing compliance certificate: rough-in", "Building Act 1993", "Licensed plumber", "03 Plumbing & drainage", "G5", "Must"),
    ("Certificate", "Insulation certificate (R-values per energy report)", "NCC 2022", "Insulation installer", "12 Insulation", "G5", "Must"),
    ("Certificate", "Waterproofing certificate", "AS 3740", "Waterproofer", "14 Waterproofer", "G6", "Must"),
    ("Certificate", "Plumbing compliance certificate: fit-off", "Building Act 1993", "Licensed plumber", "03 Plumbing & drainage", "G6", "Must"),
    ("Certificate", "Plumbing compliance certificate: gas", "Building Act 1993", "Licensed gasfitter", "03 Plumbing & drainage", "G6", "If applies"),
    ("Certificate", "Certificate of Electrical Safety", "Electricity Safety Act 1998", "Licensed electrician", "11 Electrician", "G6", "Must"),
    ("Certificate", "Smoke alarm certificate", "AS 3786", "Licensed electrician", "11 Electrician", "G6", "Must"),
    ("Certificate", "HVAC commissioning sheet & warranty", "", "HVAC installer (ARC licence)", "19 Heating & cooling", "G6", "If applies"),
    ("Certificate", "Energy compliance (as-built matches energy report)", "NCC 2022", "Energy assessor / RBS", "", "G7", "Must"),
    ("Certificate", "Asbestos clearance certificate", "OHS Regulations 2017", "Licensed asbestos assessor", "02 Demolition & earthworks", "G4", "If applies"),
    ("Permit", "Occupancy permit or certificate of final inspection", "Building Act 1993", "Relevant building surveyor", "", "G7", "Must"),
]

LISTS = {
    "Gates": ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"],
    "YesNo": ["Yes", "No"],
    "YesNoNA": ["Yes", "No", "N/A"],
    "Status": ["Not started", "In progress", "Done", "N/A"],
    "Requirement": ["Must", "If applies", "Best practice"],
    "GateItemType": ["Entry criteria", "Deliverable", "Exit check"],
    "Decision": ["Go", "Hold", "Stop"],
    "SelectionStatus": ["To choose", "Selected", "Ordered", "Delivered", "Installed"],
    "SelectionCategory": ["Base", "Frame & roof", "Lock-up", "Services", "Fit-out", "Appliances", "External", "Other"],
    "DiaryType": ["Site diary", "Plan note", "Instruction to trade", "Defect", "Question for RBS", "Variation request"],
    "HoldPoint": ["Footings", "Pre-slab", "Frame", "Insulation", "Waterproofing", "Pre-plaster", "Final", "Other"],
    "FolderCode": [f[0] for f in FOLDERS],
    "DocType": [d[0] for d in DOC_TYPES],
    "DocStatus": ["Draft", "Current", "Superseded"],
    "TradeStatus": ["Invited", "Quoted", "Engaged", "Complete", "Not engaged"],
    "VariationStatus": ["Pending", "Approved", "Rejected"],
    "VariationReason": ["Owner change", "Site condition", "Design change", "Authority requirement", "Other"],
    "CertType": ["Inspection", "Certificate", "Permit"],
    "Result": ["Pending", "Pass", "Fail", "N/A"],
    "LowMedHigh": ["Low", "Med", "High"],
    "RiskStatus": ["Open", "Watching", "Closed"],
    "Level": ["Ground", "First", "Second", "Basement", "External"],
    "AreaType": ["Internal", "Garage", "External"],
}
LIST_REFS = {}  # name -> "Lists!$A$2:$A$9", filled when the Lists sheet is written

DRIVE_MAP = "Google Drive Map"

# Legal thresholds and rules of thumb used by the checks. They live on the Settings tab so
# they can be updated when the law changes, without touching a formula.
SETTINGS = [
    # key, label, value, number format, note
    ("dep_small", "Deposit cap: contracts under the threshold", 0.10, "0%", "Domestic Building Contracts Act 1995"),
    ("dep_threshold", "Deposit cap threshold ($)", 20000, MONEY, ""),
    ("dep_large", "Deposit cap: contracts at or over the threshold", 0.05, "0%", ""),
    ("mdbc", "Registered builder and written major domestic building contract over ($)", 10000, MONEY,
     "An increase to $20,000 has been proposed. Change it here if it's adopted."),
    ("warranty", "Home warranty cover required over ($)", 20000, MONEY, "First Resort Home Warranty Scheme, contracts signed from 1 July 2026"),
    ("consent", "Certificate of consent required over ($)", 20000, MONEY, "Was $16,000 before 1 July 2026"),
    ("pc", "Principal contractor required from ($)", 350000, MONEY, "OHS Regulations 2017"),
    ("expiry_days", "Warn about expiring licences and insurance (days ahead)", 30, "0", ""),
    ("low_price", "Flag quotes this far under the median", 0.15, "0%", "Something is probably missing from the quote"),
    ("over_budget", "Flag packages forecast over budget by more than", 0.05, "0%", ""),
    ("committed", "G3 target: share of package budgets committed", 0.80, "0%", "G3 exit check"),
    ("ceiling", "Default ceiling height (m)", 2.55, "0.00", "Used on Rooms when Ceiling is blank"),
    ("waste", "Floor covering waste allowance", 0.10, "0%", "Used on Rooms"),
]
SET = {}  # key -> "Settings!$B$5", filled when the Settings sheet is written

# ---------------------------------------------------------------- helpers


def title(ws, heading, intro):
    ws["A1"] = heading
    ws["A1"].font = TITLE
    ws["A2"] = intro
    ws["A2"].font = MUTED
    ws.row_dimensions[1].height = 24


def add_dv(ws, rng, source, prompt=None):
    dv = DataValidation(type="list", formula1=source, allow_blank=True)
    dv.error = "Pick a value from the list."
    dv.errorStyle = "warning"
    if prompt:
        dv.prompt = prompt
        dv.showInputMessage = True
    ws.add_data_validation(dv)
    dv.add(rng)


class Table:
    """A data tab: title in rows 1-2, headers in row 3, entries from row 4.

    Each column is (key, header, width, options). Options:
      f    formula template; {key} becomes that column's letter, {r} the row,
           {last} the last pre-filled row. Formula columns are shaded.
      arr  True if the formula must be an array formula
      dv   list name from LISTS, or a literal range like "=Rooms!$A$4:$A$203"
      fmt  number format;  text  True to store typed values as text
      hide True to hide the column
    """

    def __init__(self, wb, name, heading, intro, columns, rows, freeze_col=1):
        self.ws = ws = wb.create_sheet(name)
        self.name = name
        self.cols = columns
        self.last = FIRST + rows - 1
        self.letter = {c[0]: get_column_letter(i + 1) for i, c in enumerate(columns)}
        title(ws, heading, intro)
        for i, (key, header, width, opt) in enumerate(columns, start=1):
            cell = ws.cell(row=HEADER_ROW, column=i, value=header)
            cell.font = WHITE_BOLD
            cell.fill = F_AUTO_HEAD if "f" in opt else F_HEAD
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            col = get_column_letter(i)
            ws.column_dimensions[col].width = width
            if opt.get("hide"):
                ws.column_dimensions[col].hidden = True
            rng = f"{col}{FIRST}:{col}{self.last}"
            if "dv" in opt:
                src = opt["dv"] if opt["dv"].startswith("=") else LIST_REFS[opt["dv"]]
                add_dv(ws, rng, src)
            for r in range(FIRST, self.last + 1):
                c = ws.cell(row=r, column=i)
                if "fmt" in opt:
                    c.number_format = opt["fmt"]
                if opt.get("text"):
                    c.number_format = "@"
                if "f" in opt:
                    c.fill = F_AUTO
                    formula = self.formula(opt["f"], r)
                    if opt.get("arr"):
                        ws[f"{col}{r}"] = ArrayFormula(f"{col}{r}", formula)
                    else:
                        c.value = formula
                if opt.get("wrap"):
                    c.alignment = WRAP
        ws.row_dimensions[HEADER_ROW].height = 32
        ws.freeze_panes = ws.cell(row=FIRST, column=freeze_col + 1 if freeze_col else 1)
        ws.auto_filter.ref = f"A{HEADER_ROW}:{get_column_letter(len(columns))}{self.last}"

    def formula(self, template, r):
        settings = {"S_" + k: v for k, v in SET.items()}
        return template.format(r=r, last=self.last, first=FIRST, **self.letter, **settings)

    def protect(self, also_locked=()):
        """Lock formula cells (and any listed columns); leave entry cells open. No password."""
        for i, (key, _, _, opt) in enumerate(self.cols, start=1):
            if "f" in opt or key in also_locked:
                continue
            for r in range(FIRST, self.last + 1):
                self.ws.cell(row=r, column=i).protection = Protection(locked=False)
        lock_sheet(self.ws)

    def col(self, key, absolute=True):
        """Full column range for formulas on other tabs, e.g. 'Trades'!$B$4:$B$203."""
        c = self.letter[key]
        return f"'{self.name}'!${c}${FIRST}:${c}${self.last}"

    def fill(self, rows, example=False):
        """Write rows of {key: value} from row 4 down. Returns the next free row."""
        r = FIRST
        for data in rows:
            for key, value in data.items():
                self.ws[f"{self.letter[key]}{r}"] = value
            if example:
                for i in range(1, len(self.cols) + 1):
                    if "f" not in self.cols[i - 1][3]:
                        self.ws.cell(row=r, column=i).fill = F_EXAMPLE
                if "notes" in self.letter:
                    self.ws[f"{self.letter['notes']}{r}"] = EXAMPLE_NOTE
            r += 1
        return r

    def rule(self, key, rule):
        c = self.letter[key]
        self.ws.conditional_formatting.add(f"{c}{FIRST}:{c}{self.last}", rule)


def lock_sheet(ws):
    """Protect a sheet but still allow filtering, sorting, formatting and adding rows."""
    p = ws.protection
    p.sheet = True
    for allowed in ("autoFilter", "sort", "formatCells", "formatColumns", "formatRows",
                    "insertRows", "deleteRows", "insertHyperlinks"):
        setattr(p, allowed, False)


def eq_rule(value, fill):
    return CellIsRule(operator="equal", formula=[f'"{value}"'], fill=fill)


def starts_rule(cell, prefix, fill):
    return FormulaRule(formula=[f'LEFT({cell},{len(prefix)})="{prefix}"'], fill=fill)


def not_blank_rule(cell, fill):
    return FormulaRule(formula=[f'LEN({cell})>0'], fill=fill)


def bad_chars(expr):
    """Replace characters that break file names (and Drive for desktop sync) with hyphens."""
    for ch in ['/', '\\', ':', '*', '?', '""', '<', '>', '|']:
        expr = f'SUBSTITUTE({expr},"{ch}","-")'
    return expr


def gate_folder(item):
    low = item.lower()
    for pattern, code in GATE_FOLDER_RULES:
        if re.search(pattern, low):
            return code
    return "00"


def folder_name(code):
    return next(f[1] for f in FOLDERS if f[0] == code)


# ---------------------------------------------------------------- build


def build(src, out):
    compliance, key_numbers = parse_compliance(src)
    gates, raci, starter_risks = parse_gateways(src)
    package_rows, contract_types = parse_contracts(src)
    tender_lists = parse_tenders(src)
    guides = parse_qa(src, "guides.html")
    faq = parse_qa(src, "faq.html")
    LISTS["ContractType"] = [r[0] for r in contract_types]

    wb = Workbook()
    start = wb.active
    start.title = "Start"
    order = ["Start", "Dashboard", "Project"]
    for name in order[1:]:
        wb.create_sheet(name)

    # Lists first, so every other tab can point its dropdowns at it.
    lists = wb.create_sheet("Lists")
    for i, (name, values) in enumerate(LISTS.items(), start=1):
        col = get_column_letter(i)
        lists.cell(row=1, column=i, value=name).font = BOLD
        for j, v in enumerate(values, start=2):
            c = lists.cell(row=j, column=i, value=v)
            c.number_format = "@"
        LIST_REFS[name] = f"=Lists!${col}$2:${col}${len(values) + 1}"
        lists.column_dimensions[col].width = 18
    dt_col = len(LISTS) + 2
    lists.cell(row=1, column=dt_col, value="Doc type").font = BOLD
    lists.cell(row=1, column=dt_col + 1, value="Meaning").font = BOLD
    for j, (code, meaning) in enumerate(DOC_TYPES, start=2):
        lists.cell(row=j, column=dt_col, value=code)
        lists.cell(row=j, column=dt_col + 1, value=meaning)
    lists.column_dimensions[get_column_letter(dt_col + 1)].width = 48

    # Settings, so every check below can point at its threshold.
    se = wb.create_sheet("Settings")
    title(se, "Settings", "The legal thresholds and rules of thumb behind the checks. Update a figure here when the law changes and every tab follows.")
    for i, (h, w) in enumerate(zip(["Setting", "Value", "Notes"], [58, 14, 70]), start=1):
        c = se.cell(row=HEADER_ROW, column=i, value=h)
        c.font, c.fill = WHITE_BOLD, F_HEAD
        se.column_dimensions[get_column_letter(i)].width = w
    for r, (key, label, value, fmt, note) in enumerate(SETTINGS, start=FIRST):
        se.cell(row=r, column=1, value=label)
        v = se.cell(row=r, column=2, value=value)
        v.number_format, v.fill, v.border = fmt, PatternFill("solid", fgColor="FFFBE6"), THIN
        se.cell(row=r, column=3, value=note).font = MUTED
        SET[key] = f"Settings!$B${r}"
    se.cell(row=FIRST + len(SETTINGS) + 1, column=1,
            value="Victorian rules checked September 2026. General information, not legal advice.").font = MUTED

    # Drive Map rows are fixed (folders + package subfolders), so links can be wired up before it's written.
    dm_last = FIRST + len(FOLDERS) + len(PACKAGE_SHORT) - 1
    dm_code = f"'{DRIVE_MAP}'!$A${FIRST}:$A${dm_last}"
    dm_path = f"'{DRIVE_MAP}'!$B${FIRST}:$B${dm_last}"
    dm_link = f"'{DRIVE_MAP}'!$G${FIRST}:$G${dm_last}"

    def package_folder(pkg_expr):
        """Folder for a package, found by its two-digit number so renaming a package can't break it."""
        return f'IFERROR(INDEX({dm_path},MATCH("04/"&LEFT({pkg_expr},2),{dm_code},0)),"04 Trades & Tenders/"&{pkg_expr})'

    def open_link(folder_key):
        lookup = f"INDEX({dm_link},MATCH({{{folder_key}}}{{r}},{dm_path},0))"
        return {"f": f'=IF({{{folder_key}}}{{r}}="","",IF(IFERROR({lookup}&"","")="","",HYPERLINK({lookup},"Open")))'}

    # ---------------- Gateways
    gw = Table(wb, "Gateways", "Gateways G0 to G7",
               "Tick each entry criterion, deliverable and exit check as it's met. A gate is ready to pass when every exit check is Yes (see Gate Review).",
               [("gate", "Gate", 7, {"dv": "Gates"}), ("gname", "Gate name", 24, {}),
                ("type", "Type", 14, {"dv": "GateItemType"}), ("item", "Item", 52, {"wrap": True}),
                ("done", "Done?", 9, {"dv": "YesNo"}), ("date", "Date", 12, {"fmt": DATE}),
                ("doc", "Evidence Doc ID", 16, {}), ("folder", "Drive folder (suggested)", 30, {}),
                ("open", "Folder", 8, open_link("folder")), ("notes", "Notes", 36, {"wrap": True})],
               rows=sum(len(items) for g in gates for _, items in g["sections"]) + 20, freeze_col=4)
    rows = []
    for g in gates:
        for section, items in g["sections"]:
            kind = {"Entry criteria": "Entry criteria", "Deliverables": "Deliverable", "Exit checks": "Exit check"}[section]
            for item in items:
                rows.append({"gate": g["code"], "gname": g["name"], "type": kind, "item": item,
                             "folder": folder_name(gate_folder(item)) if kind == "Deliverable" else ""})
    gw.fill(rows)
    gw.rule("done", eq_rule("Yes", F_GREEN))

    # ---------------- Compliance
    cp = Table(wb, "Compliance", "Victorian owner-builder compliance",
               "Every item from the 11-stage checklist. Set Status as you go; use N/A only where the item genuinely doesn't apply to your build.",
               [("id", "ID", 12, {}), ("stage", "Stage", 22, {}), ("item", "Item", 44, {"wrap": True}),
                ("req", "Requirement", 13, {"dv": "Requirement"}), ("guide", "What it means", 60, {"wrap": True}),
                ("gate", "Gateway", 9, {"dv": "Gates"}), ("status", "Status", 13, {"dv": "Status"}),
                ("date", "Date done", 12, {"fmt": DATE}), ("ref", "Reference / permit no.", 18, {}),
                ("doc", "Evidence Doc ID", 16, {}), ("folder", "Drive folder", 30, {}),
                ("open", "Folder", 8, open_link("folder")), ("notes", "Notes", 36, {"wrap": True})],
               rows=len(compliance) + 15, freeze_col=3)
    rows = []
    for c in compliance:
        code, gate = COMPLIANCE_OVERRIDE.get(c["id"]) or COMPLIANCE_MAP[c["id"].split("-")[0]]
        rows.append({"id": c["id"], "stage": c["stage"], "item": c["item"], "req": c["req"],
                     "guide": c["guide"], "gate": gate, "status": "Not started", "folder": folder_name(code)})
    cp.fill(rows)
    cp.rule("status", eq_rule("Done", F_GREEN))
    cp.rule("status", eq_rule("In progress", F_AMBER))
    stages = list(dict.fromkeys(c["stage"] for c in compliance))

    # ---------------- Rooms
    rm = Table(wb, "Rooms", "Rooms & spaces",
               "Enter each room or area once. Internal rooms get every quantity; garages skip skirting; external areas (driveways, paving, decks) get floor area only. Blank area type counts as internal.",
               [("name", "Room / area", 22, {}), ("level", "Level", 11, {"dv": "Level"}),
                ("atype", "Area type", 11, {"dv": "AreaType"}),
                ("l", "Length (m)", 11, {"fmt": "0.00"}), ("w", "Width (m)", 11, {"fmt": "0.00"}),
                ("h", "Ceiling (m)", 11, {"fmt": "0.00"}),
                ("area", "Floor area (m²)", 13, {"fmt": "0.0", "f": '=IF(AND(ISNUMBER({l}{r}),ISNUMBER({w}{r})),{l}{r}*{w}{r},"")'}),
                ("perim", "Skirting (m)", 12, {"fmt": "0.0", "f": '=IF(OR({area}{r}="",{atype}{r}="Garage",{atype}{r}="External"),"",2*({l}{r}+{w}{r}))'}),
                ("wall", "Wall paint (m²)", 13, {"fmt": "0.0", "f": '=IF(OR({area}{r}="",{atype}{r}="External"),"",2*({l}{r}+{w}{r})*IF(ISNUMBER({h}{r}),{h}{r},{S_ceiling}))'}),
                ("tiles", "Floor covering + waste (m²)", 14, {"fmt": "0.0", "f": '=IF({area}{r}="","",{area}{r}*(1+{S_waste}))'}),
                ("squares", "Squares", 10, {"fmt": "0.0", "f": '=IF(OR({area}{r}="",{atype}{r}="External"),"",{area}{r}/9.29)'}),
                ("issues", "Check", 22, {"f": '=IF(OR(AND({l}{r}<>"",NOT(ISNUMBER({l}{r}))),AND({w}{r}<>"",NOT(ISNUMBER({w}{r}))),AND({h}{r}<>"",NOT(ISNUMBER({h}{r})))),"Type sizes as numbers in metres, e.g. 3.2","")'}),
                ("dwg", "Drawing ref", 14, {}), ("notes", "Notes", 36, {"wrap": True})],
               rows=60)
    rm.fill([{"name": "Kitchen / living", "level": "Ground", "atype": "Internal", "l": 7.2, "w": 5.4},
             {"name": "Driveway", "level": "External", "atype": "External", "l": 12, "w": 3.5}], example=True)
    rm.ws["B1"] = "Takeoffs"
    rm.ws["B2"] = "NOTE: Include Garages and Outdoor areas where pricing and quoting is required (i.e driveways, paving etc) "
    rm.rule("issues", not_blank_rule(f"{rm.letter['issues']}{FIRST}", F_RED))

    # ---------------- Selections
    sel = Table(wb, "Selections", "Selections & specs",
                "Every product decision in one list. Lock them all in before G6 (fit-out). File spec sheets in 05 Selections & Specs.",
                [("item", "Item", 26, {}), ("cat", "Category", 14, {"dv": "SelectionCategory"}),
                 ("room", "Room", 18, {"dv": f"='Rooms'!$A${FIRST}:$A${rm.last}"}),
                 ("spec", "Spec / model / colour", 34, {"wrap": True}), ("supplier", "Supplier", 18, {}),
                 ("qty", "Qty", 7, {}), ("unit", "Unit", 7, {}), ("price", "Unit price ($)", 12, {"fmt": MONEY}),
                 ("total", "Total ($)", 12, {"fmt": MONEY, "f": '=IF({price}{r}="","",{price}{r}*IF({qty}{r}="",1,{qty}{r}))'}),
                 ("status", "Status", 12, {"dv": "SelectionStatus"}), ("gate", "Needed by", 10, {"dv": "Gates"}),
                 ("ordered", "Order date", 12, {"fmt": DATE}), ("delivered", "Delivery date", 12, {"fmt": DATE}),
                 ("doc", "Spec Doc ID", 15, {}), ("notes", "Notes", 32, {"wrap": True})],
                rows=150)
    sel.fill([{"item": "Kitchen mixer tap", "cat": "Fit-out", "room": "Kitchen / living",
               "spec": "Gooseneck, brushed nickel, WELS 5-star", "supplier": "Plumbing supplier", "qty": 1,
               "unit": "ea", "price": 420, "status": "Selected", "gate": "G6"}], example=True)
    sel.ws["B2"] = "Note: You may have a separate spec sheet from your contract but keep this here to track"
    sel.rule("status", eq_rule("To choose", F_RED))
    sel.rule("status", eq_rule("Installed", F_GREEN))

    # ---------------- Diary
    di = Table(wb, "Diary", "Plan notes & site diary",
               "Who was on site, weather, deliveries, instructions, defects and questions for the building surveyor. Link notes to a drawing sheet.",
               [("date", "Date", 12, {"fmt": DATE}), ("type", "Type", 18, {"dv": "DiaryType"}),
                ("ref", "Drawing / sheet ref", 15, {}), ("note", "Note", 50, {"wrap": True}),
                ("people", "On site", 22, {"wrap": True}), ("weather", "Weather", 12, {}),
                ("trade", "Trade / package", 20, {"dv": f"='Packages'!$B${FIRST}:$B${FIRST + 29}"}),
                ("action", "Action by", 14, {}), ("due", "Due", 12, {"fmt": DATE}),
                ("closed", "Closed?", 9, {"dv": "YesNo"}), ("photos", "Photo Doc IDs", 18, {}),
                ("notes", "Notes", 30, {"wrap": True})],
               rows=300)
    di.fill([{"type": "Instruction to trade", "ref": "A102", "note": "Move kitchen power point 300 mm left of window as marked on site.",
              "trade": "11 Electrician", "action": "Electrician", "closed": "No"}], example=True)
    di.rule("closed", eq_rule("No", F_AMBER))

    # ---------------- Photos
    ph = Table(wb, "Photos", "Site photo log",
               "Photograph everything before it's covered: slab mesh, frame, plumbing, insulation, waterproofing. Save the files in 06 Site Diary & Photos and log them here.",
               [("date", "Date", 12, {"fmt": DATE}), ("gate", "Stage", 8, {"dv": "Gates"}),
                ("location", "Location / element", 26, {}), ("hold", "Hold point", 14, {"dv": "HoldPoint"}),
                ("cover", "Before covering?", 11, {"dv": "YesNo"}), ("desc", "Description", 40, {"wrap": True}),
                ("doc", "Doc ID / file name", 26, {}), ("link", "Google Drive link", 30, {}),
                ("notes", "Notes", 28, {"wrap": True})],
               rows=300)
    ph.fill([{"gate": "G4", "location": "Slab, north side", "hold": "Pre-slab", "cover": "Yes",
              "desc": "Mesh, bar chairs and edge beam before pour", "doc": "06-PHO-001_Slab-mesh-north"}], example=True)

    # ---------------- Drive Map (needed by Documents)
    dm = wb.create_sheet(DRIVE_MAP)
    title(dm, "Folder map",
          "The folder tree for one build, in Google Drive, Dropbox or OneDrive. Paste each folder's link, or a local folder path, into Folder link; the Open links on other tabs use it. In Google Sheets the Apps Script can create the folders and fill in the links.")
    heads = ["Code", "Folder path", "What goes here", "Compliance stages", "Gateways", "Tabs that point here", "Folder link (paste)"]
    widths = [8, 44, 70, 12, 12, 30, 40]
    for i, (h, w) in enumerate(zip(heads, widths), start=1):
        c = dm.cell(row=HEADER_ROW, column=i, value=h)
        c.font, c.fill = WHITE_BOLD, F_HEAD
        dm.column_dimensions[get_column_letter(i)].width = w
    r = FIRST
    for code, path, what, stages_, gateways_, tabs in FOLDERS:
        for i, v in enumerate([code, path, what, stages_, gateways_, tabs], start=1):
            c = dm.cell(row=r, column=i, value=v)
            c.alignment = WRAP
            if i == 1:
                c.number_format = "@"
        r += 1
        if code == "04":
            for short in PACKAGE_SHORT:
                dm.cell(row=r, column=1, value="04/" + short[:2]).number_format = "@"
                dm.cell(row=r, column=2, value=f"{path}/{short}")
                dm.cell(row=r, column=3, value="RFQ & quotes, contract & variations, licence / insurance / SWMS, invoices.").font = MUTED
                r += 1
    assert r - 1 == dm_last
    dm.freeze_panes = "A4"
    r += 1
    guide = [
        ("File naming: DocID_Description_Rev", True),
        ("Doc ID = folder code - document type - number, e.g. 02-DWG-012 is drawing number 12 in 02 Design & Engineering.", False),
        ("File name = Doc ID, then a short description with hyphens, then the revision: 02-DWG-012_Floor-Plan_RevC.pdf", False),
        ("Register every file in the Documents tab first. It builds the Doc ID and file name for you and tells you which folder to save it in.", False),
        ("Trade paperwork goes in that package's subfolder of 04, e.g. 04 Trades & Tenders/08 Roofing/04-CON-003_Roofing-Contract.pdf", False),
        ("When a drawing is replaced, set the old one to Superseded in Documents and move the file to 99 Archive. Never delete.", False),
        ("Folder links: any provider", True),
        ("Google Drive, Dropbox, OneDrive or SharePoint: open the folder in your browser, choose Share > Copy link, and paste it into Folder link.", False),
        ("Working offline on a computer? Paste the local folder path instead, e.g. C:\\Users\\you\\Dropbox\\Owner Build\\02 Design & Engineering or /Users/you/Library/CloudStorage/... It opens without internet.", False),
        ("Google Sheets: Owner Builder > Set up Drive folders creates the folders and fills in every link for you.", False),
        ("Document types", True),
    ] + [(f"{code}  {meaning}", False) for code, meaning in DOC_TYPES]
    for line, bold in guide:
        c = dm.cell(row=r, column=2, value=line)
        if bold:
            c.font = BOLD
            c.fill = F_SECTION
        r += 1
    # ---------------- Packages (needed by Trades, Tenders, Payments)
    pk = Table(wb, "Packages", "Trade packages & cost control",
               "Budget, committed (signed contracts + approved variations), paid and forecast for each package. Other tabs find a package by its two-digit No., so you can rename it safely. Type your own forecast in Forecast override if you have one.",
               [("no", "No.", 6, {"text": True}), ("pkg", "Package", 26, {}),
                ("scope", "Scope", 36, {"wrap": True}), ("basis", "Usual basis", 20, {"wrap": True}),
                ("licence", "Licence / registration", 22, {"wrap": True}), ("paper", "Paperwork to collect", 28, {"wrap": True}),
                ("gate", "On site from", 9, {"dv": "Gates"}), ("budget", "Budget ($)", 12, {"fmt": MONEY}),
                ("contracted", "Contracted ($)", 13, {"fmt": MONEY}), ("variations", "Approved variations ($)", 13, {"fmt": MONEY}),
                ("committed", "Committed ($)", 13, {"fmt": MONEY, "f": '=IF({pkg}{r}="","",N({contracted}{r})+N({variations}{r}))'}),
                ("paid", "Paid ($)", 12, {"fmt": MONEY}),
                ("override", "Forecast override ($)", 13, {"fmt": MONEY}),
                ("forecast", "Forecast final ($)", 14, {"fmt": MONEY, "f": '=IF({pkg}{r}="","",IF(ISNUMBER({override}{r}),{override}{r},IF(N({committed}{r})>0,{committed}{r},N({budget}{r}))))'}),
                ("variance", "Under / (over) budget ($)", 14, {"fmt": '"$"#,##0;[Red]("$"#,##0)', "f": '=IF(OR({pkg}{r}="",N({budget}{r})=0),"",{budget}{r}-{forecast}{r})'}),
                ("flag", "Flag", 12, {"f": '=IF(OR({pkg}{r}="",N({budget}{r})=0),"",IF({forecast}{r}>{budget}{r}*(1+{S_over_budget}),"Over budget",""))'}),
                ("issues", "Check", 24, {"f": '=IF({pkg}{r}="","",TRIM(IF(OR({no}{r}="",LEFT({pkg}{r},LEN({no}{r})+1)<>{no}{r}&" "),"Start the name with its No. and a space, e.g. 21 Pool. ","")&IF(AND({no}{r}<>"",COUNTIF({no}${first}:{no}${last},{no}{r})>1),"Duplicate No. ","")))'}),
                ("folder", "Drive folder", 36, {"f": '=IF({pkg}{r}="","",' + package_folder("{pkg}{r}") + ')'}),
                ("open", "Folder", 8, open_link("folder")), ("notes", "Notes", 30, {"wrap": True})],
               rows=30, freeze_col=2)
    pk.fill([{"no": short[:2], "pkg": short, "scope": row[1], "basis": row[2], "licence": row[3],
              "paper": row[4], "gate": gate} for short, row, gate in zip(PACKAGE_SHORT, package_rows, PACKAGE_GATE)])
    pk.rule("flag", eq_rule("Over budget", F_RED))
    pk.rule("issues", not_blank_rule(f"{pk.letter['issues']}{FIRST}", F_RED))
    pk_names = f"='Packages'!$B${FIRST}:$B${pk.last}"

    # ---------------- Documents
    dc = Table(wb, "Documents", "Document register",
               "Register every plan, permit, quote, contract, certificate and photo set. Pick the folder and type, type the number shown under 'Next free no.', and save the file with the name in column N.",
               [("folder", "Folder", 8, {"dv": "FolderCode", "text": True}), ("type", "Type", 8, {"dv": "DocType"}),
                ("no", "No.", 6, {}),
                ("fcode", "Folder code", 6, {"hide": True, "f": '=IF({folder}{r}="","",IF(ISNUMBER({folder}{r}),TEXT({folder}{r},"00"),TRIM({folder}{r})))'}),
                ("next", "Next free no.", 9, {"arr": True, "f": '=IF(OR({fcode}{r}="",{type}{r}=""),"",MAX(IF(({fcode}${first}:{fcode}${last}={fcode}{r})*({type}${first}:{type}${last}={type}{r})*ISNUMBER({no}${first}:{no}${last}),{no}${first}:{no}${last},0))+1)'}),
                ("docid", "Doc ID", 14, {"f": '=IF(OR({fcode}{r}="",{type}{r}="",NOT(ISNUMBER({no}{r}))),"",{fcode}{r}&"-"&{type}{r}&"-"&TEXT({no}{r},"000"))'}),
                ("desc", "Description", 34, {"wrap": True}), ("rev", "Rev", 6, {}),
                ("date", "Date", 12, {"fmt": DATE}), ("from", "From / issued by", 18, {}),
                ("pkg", "Trade package", 22, {"dv": pk_names}), ("status", "Status", 11, {"dv": "DocStatus"}),
                ("gate", "Gateway", 8, {"dv": "Gates"}), ("comp", "Compliance ID", 12, {}),
                ("file", "File name to use", 40, {"f": '=IF({docid}{r}="","",{docid}{r}&"_"&' + bad_chars('SUBSTITUTE(TRIM({desc}{r})," ","-")') + '&IF({rev}{r}="","","_Rev"&{rev}{r}))'}),
                ("where", "Save in Drive folder", 38, {"f": '=IF({fcode}{r}="","",IF({status}{r}="Superseded","99 Archive",IF(AND({fcode}{r}="04",{pkg}{r}<>""),' + package_folder("{pkg}{r}") + ',IFERROR(INDEX(' + dm_path + ',MATCH({fcode}{r},' + dm_code + ',0)),""))))'}),
                ("open", "Folder", 8, open_link("where")),
                ("issues", "Check", 26, {"f": '=IF(AND({folder}{r}="",{type}{r}="",{no}{r}=""),"",TRIM(IF(AND({fcode}{r}<>"",ISNA(MATCH({fcode}{r},' + dm_code + ',0))),"Folder code isn\'t on the folder map. ","")&IF(AND({no}{r}<>"",NOT(ISNUMBER({no}{r}))),"No. must be a whole number. ","")&IF(AND({fcode}{r}<>"",{type}{r}<>"",{no}{r}=""),"Type the next free no. ","")&IF(AND({docid}{r}<>"",COUNTIF({docid}${first}:{docid}${last},{docid}{r})>1),"Duplicate Doc ID. ","")))'}),
                ("link", "File link", 30, {}), ("notes", "Notes", 28, {"wrap": True})],
               rows=300, freeze_col=6)
    dc.fill([{"folder": "02", "type": "DWG", "no": 1, "desc": "Floor plan", "rev": "C", "from": "Draftsperson",
              "status": "Current", "gate": "G2", "comp": "de-drawings"}], example=True)
    dc.rule("docid", FormulaRule(formula=[f'AND({dc.letter["docid"]}{FIRST}<>"",COUNTIF(${dc.letter["docid"]}${FIRST}:${dc.letter["docid"]}${dc.last},{dc.letter["docid"]}{FIRST})>1)'], fill=F_RED))
    dc.rule("status", eq_rule("Superseded", F_AMBER))
    dc.rule("issues", not_blank_rule(f"{dc.letter['issues']}{FIRST}", F_RED))

    # ---------------- Trades
    tr = Table(wb, "Trades", "Trade register",
               "Every trade you invite or engage. Licence and insurance dates turn amber before they expire (days set on Settings) and red once expired. Type dates as dates, e.g. 30/06/2027.",
               [("pkg", "Package", 22, {"dv": pk_names}), ("business", "Business name", 24, {}),
                ("contact", "Contact", 16, {}), ("phone", "Phone", 13, {"text": True}), ("email", "Email", 22, {}),
                ("abn", "ABN", 14, {"text": True}), ("gst", "GST registered?", 10, {"dv": "YesNo"}),
                ("lictype", "Licence / registration", 20, {}), ("licno", "Licence no.", 13, {"text": True}),
                ("licexp", "Licence expiry", 12, {"fmt": DATE}), ("insurer", "Public liability insurer", 18, {}),
                ("plexp", "PL expiry", 12, {"fmt": DATE}), ("workcover", "WorkCover", 10, {"dv": "YesNoNA"}),
                ("warranty", "Home warranty cover (> $20k)", 13, {"dv": "YesNoNA"}),
                ("swms", "SWMS received", 10, {"dv": "YesNoNA"}), ("cards", "White cards checked", 10, {"dv": "YesNo"}),
                ("status", "Status", 12, {"dv": "TradeStatus"}), ("ctype", "Contract type", 18, {"dv": "ContractType"}),
                ("signed", "Contract signed?", 10, {"dv": "YesNo"}), ("value", "Contract value inc GST ($)", 14, {"fmt": MONEY}),
                ("deposit", "Deposit ($)", 11, {"fmt": MONEY}),
                ("depcheck", "Deposit check", 16, {"f": '=IF(OR(N({value}{r})=0,N({deposit}{r})=0),"",IF({deposit}{r}>{value}{r}*IF({value}{r}<{S_dep_threshold},{S_dep_small},{S_dep_large}),"Over statutory cap","OK"))'}),
                ("alert", "Paperwork", 20, {"f": '=IF({business}{r}="","",IF(OR(AND({licexp}{r}<>"",NOT(ISNUMBER({licexp}{r}))),AND({plexp}{r}<>"",NOT(ISNUMBER({plexp}{r})))),"Check date: typed as text",IF(OR(AND(ISNUMBER({licexp}{r}),{licexp}{r}<TODAY()),AND(ISNUMBER({plexp}{r}),{plexp}{r}<TODAY())),"Expired",IF(OR(AND(ISNUMBER({licexp}{r}),{licexp}{r}-TODAY()<={S_expiry_days}),AND(ISNUMBER({plexp}{r}),{plexp}{r}-TODAY()<={S_expiry_days})),"Expires within "&{S_expiry_days}&" days",IF(AND(OR({status}{r}="Engaged",{signed}{r}="Yes"),OR({licexp}{r}="",{plexp}{r}="")),"Missing expiry date","OK")))))'}),
                ("checks", "Contract checks", 30, {"wrap": True, "f": '=IF({business}{r}="","",TRIM(IF(COUNTIF({business}${first}:{business}${last},{business}{r})>1,"Duplicate business name. ","")&IF(AND(N({value}{r})>{S_mdbc},{lictype}{r}=""),"Over "&TEXT({S_mdbc},"$#,##0")&": record the builder registration (or exemption) and use a written major domestic building contract. ","")&IF(AND(N({value}{r})>{S_warranty},{warranty}{r}<>"Yes"),"Home warranty cover needed over "&TEXT({S_warranty},"$#,##0")&". ","")))'}),
                ("folder", "Drive folder", 32, {"f": '=IF({pkg}{r}="","",' + package_folder("{pkg}{r}") + ')'}),
                ("open", "Folder", 8, open_link("folder")), ("notes", "Notes", 28, {"wrap": True})],
               rows=100, freeze_col=2)
    tr.fill([{"pkg": "08 Roofing", "business": "Ridgeline Metal Roofs", "gst": "Yes", "lictype": "Roof plumbing licence",
              "workcover": "Yes", "warranty": "Yes", "swms": "Yes", "cards": "Yes", "status": "Engaged",
              "ctype": "Supply & install", "signed": "Yes", "value": 36900, "deposit": 1845,
              "licexp": datetime.date(2027, 6, 30), "plexp": datetime.date(2027, 3, 31)}], example=True)
    a1 = f"{tr.letter['alert']}{FIRST}"
    tr.rule("alert", eq_rule("Expired", F_RED))
    tr.rule("alert", starts_rule(a1, "Expires", F_AMBER))
    tr.rule("alert", starts_rule(a1, "Check date", F_RED))
    tr.rule("alert", starts_rule(a1, "Missing", F_AMBER))
    tr.rule("depcheck", eq_rule("Over statutory cap", F_RED))
    tr.rule("checks", not_blank_rule(f"{tr.letter['checks']}{FIRST}", F_AMBER))

    # ---------------- Tender Setup + Tenders
    ts = Table(wb, "Tender Setup", "Tender weights & recommendations",
               "Set the scoring weights for each package (they must add to 100). The recommendation updates as you enter quotes on the Tenders tab.",
               [("pkg", "Package", 26, {"f": "=IF('Packages'!B{r}=\"\",\"\",'Packages'!B{r})"}),
                ("budget", "Budget ($)", 12, {"fmt": MONEY, "f": "=IF('Packages'!H{r}=\"\",\"\",'Packages'!H{r})"}),
                ("wprice", "Price %", 8, {}), ("wexp", "Experience %", 10, {}), ("wprog", "Program %", 9, {}),
                ("wqual", "Quality %", 9, {}), ("wcomm", "Comms %", 9, {}), ("wwarr", "Warranty %", 9, {}),
                ("wsum", "Total %", 8, {"f": '=IF({pkg}{r}="","",SUM({wprice}{r}:{wwarr}{r}))'}),
                ("count", "Compliant tenders", 10, {}), ("rec", "Recommended", 24, {}),
                ("score", "Score /100", 9, {"fmt": "0.0"}), ("levelled", "Levelled price ($)", 14, {"fmt": MONEY}),
                ("vsbudget", "Over / (under) budget ($)", 14, {"fmt": '"$"#,##0;[Red]("$"#,##0)', "f": '=IF(OR({levelled}{r}="",N({budget}{r})=0),"",{levelled}{r}-{budget}{r})'}),
                ("margin", "Lead over #2 (points)", 11, {"fmt": "0.0"}),
                ("notes", "Notes", 30, {"wrap": True})],
               rows=30, freeze_col=1)
    for r in range(FIRST, ts.last + 1):
        for key, w in zip(["wprice", "wexp", "wprog", "wqual", "wcomm", "wwarr"], [50, 15, 15, 10, 5, 5]):
            ts.ws[f"{ts.letter[key]}{r}"] = w

    tn = Table(wb, "Tenders", "Tender comparison",
               "One row per quote. Fail any gate and the quote is excluded. Levelling adds exclusions, provisional-sum adjustments and a risk allowance so prices are like-for-like. Scores are 0 to 10. The Check column says why a quote is excluded or needs a look.",
               [("pkg", "Package", 22, {"dv": pk_names}), ("name", "Tenderer", 22, {}),
                ("recv", "Received", 11, {"fmt": DATE}),
                ("g_reg", "Registered / licensed", 10, {"dv": "YesNo"}), ("g_ins", "Insurance current", 10, {"dv": "YesNo"}),
                ("g_abn", "ABN verified", 9, {"dv": "YesNo"}), ("g_swms", "SWMS provided", 9, {"dv": "YesNo"}),
                ("g_scope", "Scope conforms", 9, {"dv": "YesNo"}),
                ("compliant", "Compliant?", 10, {"f": '=IF({name}{r}="","",IF(AND(COUNTIF({g_reg}{r}:{g_scope}{r},"Yes")=5,SUMPRODUCT(--ISTEXT({price}{r}:{risk}{r}))=0,N({price}{r})>0,N({levelled}{r})>0,{m}{r}>0),"Yes","No"))'}),
                ("price", "Quoted price inc GST ($)", 13, {"fmt": MONEY}), ("excl", "+ Cost of exclusions ($)", 12, {"fmt": MONEY}),
                ("ps", "± Provisional sum adj. ($)", 12, {"fmt": MONEY}), ("risk", "+ Risk allowance ($)", 12, {"fmt": MONEY}),
                ("levelled", "Levelled price ($)", 13, {"fmt": MONEY, "f": '=IF({name}{r}="","",N({price}{r})+N({excl}{r})+N({ps}{r})+N({risk}{r}))'}),
                ("s_exp", "Experience & references", 10, {}), ("s_prog", "Program / availability", 10, {}),
                ("s_qual", "Quality of past work", 10, {}), ("s_comm", "Communication", 10, {}),
                ("s_warr", "Warranty & defects terms", 10, {}),
                ("pkey", "Package no.", 6, {"hide": True, "f": '=IF({pkg}{r}="","",LEFT({pkg}{r},2))'}),
                ("m", "Weights row", 6, {"hide": True, "f": "=IF({pkg}{r}=\"\",0,IFERROR(MATCH(LEFT({pkg}{r},3)&\"*\",'Tender Setup'!$A$4:$A$33,0),0))"}),
                ("lowest", "Lowest compliant in package ($)", 13, {"fmt": MONEY, "arr": True,
                 "f": '=IF({compliant}{r}<>"Yes","",MIN(IF(({pkey}${first}:{pkey}${last}={pkey}{r})*({compliant}${first}:{compliant}${last}="Yes"),{levelled}${first}:{levelled}${last})))'}),
                ("median", "Median compliant in package ($)", 13, {"fmt": MONEY, "arr": True,
                 "f": '=IF({compliant}{r}<>"Yes","",MEDIAN(IF(({pkey}${first}:{pkey}${last}={pkey}{r})*({compliant}${first}:{compliant}${last}="Yes"),{levelled}${first}:{levelled}${last})))'}),
                ("pricepts", "Price points", 9, {"fmt": "0.0", "f": "=IF({compliant}{r}<>\"Yes\",0,{lowest}{r}/{levelled}{r}*INDEX('Tender Setup'!$C$4:$C$33,{m}{r}))"}),
                ("critpts", "Other points", 9, {"fmt": "0.0", "f": "=IF({compliant}{r}<>\"Yes\",0,(MIN(10,MAX(0,N({s_exp}{r})))*INDEX('Tender Setup'!$D$4:$D$33,{m}{r})+MIN(10,MAX(0,N({s_prog}{r})))*INDEX('Tender Setup'!$E$4:$E$33,{m}{r})+MIN(10,MAX(0,N({s_qual}{r})))*INDEX('Tender Setup'!$F$4:$F$33,{m}{r})+MIN(10,MAX(0,N({s_comm}{r})))*INDEX('Tender Setup'!$G$4:$G$33,{m}{r})+MIN(10,MAX(0,N({s_warr}{r})))*INDEX('Tender Setup'!$H$4:$H$33,{m}{r}))/10)"}),
                ("total", "Total /100", 9, {"fmt": "0.0", "f": "=IF({name}{r}=\"\",\"\",IF({compliant}{r}<>\"Yes\",0,IF(N(INDEX('Tender Setup'!$I$4:$I$33,{m}{r}))=0,0,({pricepts}{r}+{critpts}{r})*100/INDEX('Tender Setup'!$I$4:$I$33,{m}{r}))))"}),
                ("rank", "Rank", 9, {"f": '=IF({name}{r}="","",IF({compliant}{r}<>"Yes","Excluded",COUNTIFS({pkey}${first}:{pkey}${last},{pkey}{r},{compliant}${first}:{compliant}${last},"Yes",{total}${first}:{total}${last},">"&{total}{r})+1))'}),
                ("lowflag", "Price check", 18, {"f": '=IF({compliant}{r}<>"Yes","",IF(AND(COUNTIFS({pkey}${first}:{pkey}${last},{pkey}{r},{compliant}${first}:{compliant}${last},"Yes")>=2,{levelled}{r}<{median}{r}*(1-{S_low_price})),"Well under median: check scope",""))'}),
                ("issues", "Check", 30, {"wrap": True, "f": '=IF({name}{r}="","",TRIM(IF(COUNTIF({g_reg}{r}:{g_scope}{r},"Yes")<5,"Compliance gates not all Yes. ","")&IF(SUMPRODUCT(--ISTEXT({price}{r}:{risk}{r}))>0,"A price cell holds text, not a number. ","")&IF(N({price}{r})<=0,"No quoted price. ",IF(N({levelled}{r})<=0,"Levelled price is $0 or less. ",""))&IF({m}{r}=0,"Package isn\'t on the Packages tab. ","")&IF(SUMPRODUCT(ISTEXT({s_exp}{r}:{s_warr}{r})+({s_exp}{r}:{s_warr}{r}<0)+({s_exp}{r}:{s_warr}{r}>10))>0,"Scores must be 0 to 10 (capped). ","")&IF(AND({rank}{r}=1,COUNTIFS({pkey}${first}:{pkey}${last},{pkey}{r},{rank}${first}:{rank}${last},1)>1),"Tied for 1st: ask both for clarifications. ","")))'}),
                ("key", "Key", 6, {"hide": True, "f": '={pkey}{r}&"|"&{rank}{r}'}),
                ("doc", "Quote Doc ID", 15, {}), ("notes", "Notes", 28, {"wrap": True})],
               rows=100, freeze_col=2)
    for key in ["s_exp", "s_prog", "s_qual", "s_comm", "s_warr"]:
        dv = DataValidation(type="whole", operator="between", formula1="0", formula2="10", allow_blank=True)
        dv.error, dv.errorStyle = "Score from 0 to 10.", "warning"
        tn.ws.add_data_validation(dv)
        dv.add(f"{tn.letter[key]}{FIRST}:{tn.letter[key]}{tn.last}")
    yes = {k: "Yes" for k in ["g_reg", "g_ins", "g_abn", "g_swms", "g_scope"]}
    tn.fill([
        dict(yes, pkg="08 Roofing", name="Summit Roofing", price=32500, excl=1800, ps=0, risk=500, s_exp=8, s_prog=6, s_qual=8, s_comm=7, s_warr=7),
        dict(yes, pkg="08 Roofing", name="Ridgeline Metal Roofs", price=36900, excl=0, ps=0, risk=0, s_exp=9, s_prog=8, s_qual=9, s_comm=9, s_warr=8),
        dict(yes, pkg="08 Roofing", name="Budget Roofs Co", g_ins="No", price=27900, excl=3500, ps=1200, risk=2000, s_exp=5, s_prog=9, s_qual=5, s_comm=4, s_warr=5),
    ], example=True)
    tn.rule("compliant", eq_rule("No", F_RED))
    tn.rule("rank", CellIsRule(operator="equal", formula=["1"], fill=F_GREEN))
    tn.rule("lowflag", not_blank_rule(f"{tn.letter['lowflag']}{FIRST}", F_AMBER))
    tn.rule("issues", not_blank_rule(f"{tn.letter['issues']}{FIRST}", F_AMBER))
    tn.rule("g_reg", eq_rule("No", F_RED))
    for k in ["g_ins", "g_abn", "g_swms", "g_scope"]:
        tn.rule(k, eq_rule("No", F_RED))

    # Tender Setup summary columns now that Tenders exists
    for r in range(FIRST, ts.last + 1):
        a = f"$A{r}"
        k = f"LEFT({a},2)"
        first = f'MATCH({k}&"|1",{tn.col("key")},0)'
        ties = f'COUNTIF({tn.col("key")},{k}&"|1")'
        ts.ws[f"{ts.letter['count']}{r}"] = f'=IF({a}="","",COUNTIFS({tn.col("pkey")},{k},{tn.col("compliant")},"Yes"))'
        ts.ws[f"{ts.letter['rec']}{r}"] = f'=IF({a}="","",IF({ties}>1,"Tie: "&{ties}&" quotes share 1st",IFERROR(INDEX({tn.col("name")},{first}),"")))'
        ts.ws[f"{ts.letter['score']}{r}"] = f'=IF({a}="","",IFERROR(INDEX({tn.col("total")},{first}),""))'
        ts.ws[f"{ts.letter['levelled']}{r}"] = f'=IF(OR({a}="",{ties}>1),"",IFERROR(INDEX({tn.col("levelled")},{first}),""))'
        ts.ws[f"{ts.letter['margin']}{r}"] = f'=IF(OR({a}="",{ties}>1),"",IFERROR({ts.letter["score"]}{r}-INDEX({tn.col("total")},MATCH({k}&"|2",{tn.col("key")},0)),""))'
        for key in ["count", "rec", "score", "levelled", "margin"]:
            ts.ws[f"{ts.letter[key]}{r}"].fill = F_AUTO
    for key in ["count", "rec", "score", "levelled", "margin"]:
        ts.ws[f"{ts.letter[key]}{HEADER_ROW}"].fill = F_AUTO_HEAD
    ts.ws.conditional_formatting.add(
        f"{ts.letter['wsum']}{FIRST}:{ts.letter['wsum']}{ts.last}",
        FormulaRule(formula=[f'AND({ts.letter["wsum"]}{FIRST}<>"",{ts.letter["wsum"]}{FIRST}<>100)'], fill=F_RED))
    ts.rule("rec", starts_rule(f"{ts.letter['rec']}{FIRST}", "Tie", F_AMBER))

    # ---------------- Variations
    va = Table(wb, "Variations", "Variations",
               "Agree the price and time impact in writing before any extra work. Approved variations add to the package's committed cost.",
               [("no", "Var. no.", 8, {}), ("date", "Date", 12, {"fmt": DATE}),
                ("pkg", "Package", 22, {"dv": pk_names}), ("trade", "Trade", 20, {}),
                ("desc", "Description", 40, {"wrap": True}), ("reason", "Reason", 16, {"dv": "VariationReason"}),
                ("price", "Price impact ($)", 12, {"fmt": '"$"#,##0;[Red]-"$"#,##0'}), ("days", "Time impact (days)", 10, {}),
                ("approved", "Approval", 11, {"dv": "VariationStatus"}), ("apdate", "Approved date", 12, {"fmt": DATE}),
                ("doc", "Signed Doc ID", 15, {}), ("notes", "Notes", 28, {"wrap": True})],
               rows=150, freeze_col=1)
    va.rule("approved", eq_rule("Pending", F_AMBER))

    # ---------------- Payments
    pay = Table(wb, "Payments", "Invoices & payments",
                "Every invoice and claim. Only rows marked Paid count towards spent to date. Don't release final payment until you have that trade's certificates.",
                [("date", "Invoice date", 12, {"fmt": DATE}), ("pkg", "Package", 22, {"dv": pk_names}),
                 ("trade", "Trade", 22, {"dv": f"='Trades'!$B${FIRST}:$B${tr.last}"}), ("inv", "Invoice no.", 12, {"text": True}),
                 ("stage", "Stage / claim", 16, {}), ("amount", "Amount inc GST ($)", 13, {"fmt": MONEY}),
                 ("gstcharged", "GST charged?", 9, {"dv": "YesNo"}),
                 ("tradegst", "Trade GST registered", 10, {"f": "=IF({trade}{r}=\"\",\"\",IFERROR(INDEX(" + tr.col("gst") + ",MATCH({trade}{r}," + tr.col("business") + ",0))&\"\",\"\"))"}),
                 ("gstflag", "GST check", 16, {"f": '=IF(AND({gstcharged}{r}="Yes",{tradegst}{r}="No"),"GST charged, not registered","")'}),
                 ("due", "Due", 12, {"fmt": DATE}), ("paid", "Paid?", 8, {"dv": "YesNo"}),
                 ("paiddate", "Paid date", 12, {"fmt": DATE}), ("retention", "Retention held ($)", 12, {"fmt": MONEY}),
                 ("doc", "Invoice Doc ID", 15, {}), ("notes", "Notes", 28, {"wrap": True})],
                rows=300, freeze_col=2)
    pay.fill([{"pkg": "08 Roofing", "trade": "Ridgeline Metal Roofs", "inv": "1042", "stage": "Deposit",
               "amount": 1845, "gstcharged": "Yes", "paid": "Yes"}], example=True)
    pay.rule("gstflag", eq_rule("GST charged, not registered", F_RED))
    pay.rule("paid", eq_rule("No", F_AMBER))

    # Packages: contracted, variations and paid come from the tabs above
    # Matched on the two-digit No. ("08 *"), so renaming "08 Roofing" doesn't orphan its rows.
    for r in range(FIRST, pk.last + 1):
        b, key = f"$B{r}", f'$A{r}&" *"'
        pk.ws[f"{pk.letter['contracted']}{r}"] = f'=IF(OR({b}="",$A{r}=""),"",SUMIFS({tr.col("value")},{tr.col("pkg")},{key},{tr.col("signed")},"Yes"))'
        pk.ws[f"{pk.letter['variations']}{r}"] = f'=IF(OR({b}="",$A{r}=""),"",SUMIFS({va.col("price")},{va.col("pkg")},{key},{va.col("approved")},"Approved"))'
        pk.ws[f"{pk.letter['paid']}{r}"] = f'=IF(OR({b}="",$A{r}=""),"",SUMIFS({pay.col("amount")},{pay.col("pkg")},{key},{pay.col("paid")},"Yes"))'
        for key in ["contracted", "variations", "paid"]:
            pk.ws[f"{pk.letter[key]}{r}"].fill = F_AUTO
    for key in ["contracted", "variations", "paid"]:
        pk.ws[f"{pk.letter[key]}{HEADER_ROW}"].fill = F_AUTO_HEAD

    # ---------------- Certificates
    ce = Table(wb, "Certificates", "Inspections & certificates",
               "Mandatory inspections and the certificates the building surveyor needs at final. A missing certificate is the most common reason a final is delayed.",
               [("type", "Type", 11, {"dv": "CertType"}), ("item", "Inspection / certificate", 40, {"wrap": True}),
                ("std", "Standard / law", 18, {}), ("who", "Who provides it", 22, {}),
                ("pkg", "Package", 22, {"dv": pk_names}), ("gate", "Gateway", 8, {"dv": "Gates"}),
                ("req", "Requirement", 12, {"dv": "Requirement"}), ("requested", "Booked / requested", 12, {"fmt": DATE}),
                ("received", "Passed / received", 12, {"fmt": DATE}), ("result", "Result", 10, {"dv": "Result"}),
                ("ref", "Reference no.", 14, {}), ("doc", "Doc ID", 14, {}),
                ("notes", "Notes", 30, {"wrap": True})],
               rows=len(CERTIFICATES) + 25, freeze_col=2)
    ce.fill([{"type": c[0], "item": c[1], "std": c[2], "who": c[3], "pkg": c[4], "gate": c[5], "req": c[6], "result": "Pending"}
             for c in CERTIFICATES])
    ce.rule("result", eq_rule("Pass", F_GREEN))
    ce.rule("result", eq_rule("Fail", F_RED))

    # ---------------- Risks
    rk = Table(wb, "Risks", "Risk register",
               "Likelihood × impact gives the rating. Review it weekly. Contingency is money set aside for these risks, not for upgrades.",
               [("id", "ID", 6, {}), ("risk", "Risk", 40, {"wrap": True}),
                ("like", "Likelihood", 10, {"dv": "LowMedHigh"}), ("impact", "Impact", 9, {"dv": "LowMedHigh"}),
                ("score", "Score", 7, {"f": '=IF(OR({like}{r}="",{impact}{r}=""),"",MATCH({like}{r},{{"Low","Med","High"}},0)*MATCH({impact}{r},{{"Low","Med","High"}},0))'}),
                ("rating", "Rating", 9, {"f": '=IF({score}{r}="","",IF({score}{r}>=6,"High",IF({score}{r}>=3,"Medium","Low")))'}),
                ("response", "Response", 50, {"wrap": True}), ("owner", "Owner", 12, {}),
                ("status", "Status", 10, {"dv": "RiskStatus"}), ("review", "Next review", 12, {"fmt": DATE}),
                ("notes", "Notes", 28, {"wrap": True})],
               rows=60, freeze_col=2)
    rk.fill([{"id": f"R{i:02d}", "risk": row[0], "like": row[1], "impact": row[2], "response": row[3],
              "owner": "Owner-builder", "status": "Open"} for i, row in enumerate(starter_risks[1:], start=1)])
    rk.rule("rating", eq_rule("High", F_RED))
    rk.rule("rating", eq_rule("Medium", F_AMBER))

    # ---------------- Gate Review
    gr = Table(wb, "Gate Review", "Gate review",
               "At each gate decide Go, Hold or Stop. A gate is ready when every exit check on the Gateways tab is Yes.",
               [("gate", "Gate", 7, {}), ("name", "Name", 24, {}), ("purpose", "Purpose", 36, {"wrap": True}),
                ("entry", "Entry criteria met", 11, {"f": f'=COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Entry criteria",{gw.col("done")},"Yes")&" of "&COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Entry criteria")'}),
                ("deliv", "Deliverables done", 11, {"f": f'=COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Deliverable",{gw.col("done")},"Yes")&" of "&COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Deliverable")'}),
                ("exitn", "Exit checks", 8, {"f": f'=COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Exit check")'}),
                ("exitd", "Exit checks done", 9, {"f": f'=COUNTIFS({gw.col("gate")},{{gate}}{{r}},{gw.col("type")},"Exit check",{gw.col("done")},"Yes")'}),
                ("pct", "Exit %", 8, {"fmt": "0%", "f": '=IF({exitn}{r}=0,"",{exitd}{r}/{exitn}{r})'}),
                ("ready", "Ready to pass?", 11, {"f": '=IF({exitn}{r}=0,"",IF({exitd}{r}={exitn}{r},"Ready","Not yet"))'}),
                ("decision", "Decision", 9, {}),
                ("dcheck", "Decision check", 22, {"f": '=IF(AND({decision}{r}="Go",{ready}{r}<>"Ready"),"Go recorded, exit checks open","")'}),
                ("ddate", "Decision date", 12, {"fmt": DATE}),
                ("guide", "Decision guide", 44, {"wrap": True}), ("spent", "Typical budget spent", 12, {}),
                ("duration", "Typical duration", 14, {}), ("notes", "Notes", 30, {"wrap": True})],
               rows=len(gates), freeze_col=2)
    durations = ["1–3 months (with G1)", "1–3 months (with G0)", "2–6 months", "1–2 months", "4–8 weeks", "8–12 weeks", "12–20 weeks", "2–6 weeks"]
    gr.fill([{"gate": g["code"], "name": g["name"], "purpose": g["purpose"], "guide": g["decision"],
              "spent": g["spent"], "duration": d} for g, d in zip(gates, durations)])
    gr.rule("ready", eq_rule("Ready", F_GREEN))
    gr.rule("decision", eq_rule("Go", F_GREEN))
    gr.rule("decision", eq_rule("Hold", F_AMBER))
    gr.rule("decision", eq_rule("Stop", F_RED))
    gr.rule("dcheck", not_blank_rule(f"{gr.letter['dcheck']}{FIRST}", F_RED))
    # Go is only accepted once every exit check is Yes. (A custom rule replaces the dropdown.)
    d, rd = f"{gr.letter['decision']}{FIRST}", f"{gr.letter['ready']}{FIRST}"
    dv = DataValidation(type="custom", allow_blank=True,
                        formula1=f'OR({d}="Hold",{d}="Stop",AND({d}="Go",{rd}="Ready"))')
    dv.errorStyle, dv.errorTitle = "stop", "Not ready for Go"
    dv.error = "Type Go, Hold or Stop. Go is only allowed once every exit check for this gate is Yes on the Gateways tab."
    dv.prompt, dv.showInputMessage = "Type Go, Hold or Stop. Go needs every exit check done.", True
    gr.ws.add_data_validation(dv)
    dv.add(f"{d}:{gr.letter['decision']}{gr.last}")

    # ---------------- Project
    pj = wb["Project"]
    title(pj, "Project", "The basics, always at hand. Yellow cells are yours to fill in.")
    fields = [
        ("Project", None), ("Project name", ""), ("Site address", ""), ("Lot / plan of subdivision", ""),
        ("Title volume / folio", ""), ("Owner-builder(s)", ""), ("Phone", ""), ("Email", ""),
        ("Current gateway", "G0"), ("Target start", "date"), ("Target finish", "date"),
        ("Money", None), ("Total budget inc GST ($)", "money"), ("Contingency (%)", "pct"), ("Lender", ""),
        ("Approvals", None), ("Certificate of consent no.", ""), ("Relevant building surveyor", ""),
        ("Building permit no.", ""), ("Planning permit no. (if any)", ""),
        ("Site & design", None), ("Soil classification (AS 2870)", ""), ("Wind classification", ""),
        ("BAL rating (if bushfire prone)", ""), ("Energy rating (stars)", ""),
        ("Google Drive", None), ("Project folder link", ""),
    ]
    pj.column_dimensions["A"].width = 32
    pj.column_dimensions["B"].width = 46
    pj.column_dimensions["C"].width = 50
    pj["C4"] = "Notes"
    cell_of = {}
    r = HEADER_ROW + 1
    F_INPUT = PatternFill("solid", fgColor="FFFBE6")
    for label, kind in fields:
        a = pj.cell(row=r, column=1, value=label)
        if kind is None:
            a.font, a.fill = BOLD, F_SECTION
            pj.cell(row=r, column=2).fill = F_SECTION
        else:
            b = pj.cell(row=r, column=2)
            b.fill, b.border = F_INPUT, THIN
            cell_of[label] = f"Project!$B${r}"
            if kind == "date":
                b.number_format = DATE
            elif kind == "money":
                b.number_format = MONEY
            elif kind == "pct":
                b.value, b.number_format = 0.12, "0%"
            elif kind == "G0":
                b.value = "G0"
                add_dv(pj, f"B{r}", LIST_REFS["Gates"])
        r += 1
    pj.cell(row=int(cell_of["Contingency (%)"].split("$")[-1]), column=3,
            value="10–15% is typical. Owner-builders often underestimate site works, services and finishes.").font = MUTED
    pj.cell(row=int(cell_of["Project folder link"].split("$")[-1]), column=3,
            value="Paste your project folder link (any provider), or let Owner Builder > Set up Drive folders fill it in Google Sheets.").font = MUTED

    # ---------------- Dashboard
    db = wb["Dashboard"]
    title(db, "Dashboard", "Where the build is up to. Everything here is calculated; change the other tabs, not this one.")
    for col, w in zip("ABCDEF", [34, 16, 12, 12, 12, 40]):
        db.column_dimensions[col].width = w
    r = HEADER_ROW + 1

    def section(label, heads=()):
        nonlocal r
        db.cell(row=r, column=1, value=label).font = WHITE_BOLD
        for i in range(1, 7):
            db.cell(row=r, column=i).fill = F_HEAD
        for i, h in enumerate(heads, start=2):
            c = db.cell(row=r, column=i, value=h)
            c.font = WHITE_BOLD
        r += 1

    def line(label, formula, fmt=None, note=None):
        nonlocal r
        db.cell(row=r, column=1, value=label)
        c = db.cell(row=r, column=2, value=formula)
        c.fill = F_AUTO
        if fmt:
            c.number_format = fmt
        if note:
            db.cell(row=r, column=6, value=note).font = MUTED
        r += 1
        return f"B{r - 1}"

    gate_cell = cell_of["Current gateway"]
    gr_gate = f"'Gate Review'!$A${FIRST}:$A${gr.last}"
    section("Project")
    line("Project", f'=IF({cell_of["Project name"]}="","(name it on the Project tab)",{cell_of["Project name"]})')
    line("Current gateway", f'={gate_cell}&" "&IFERROR(INDEX(\'Gate Review\'!$B${FIRST}:$B${gr.last},MATCH({gate_cell},{gr_gate},0)),"")')
    line("Exit checks done at this gate", f"=IFERROR(INDEX('Gate Review'!$H${FIRST}:$H${gr.last},MATCH({gate_cell},{gr_gate},0)),\"\")", "0%")
    line("Ready to pass?", f"=IFERROR(INDEX('Gate Review'!$I${FIRST}:$I${gr.last},MATCH({gate_cell},{gr_gate},0)),\"\")")
    r += 1

    section("Money")
    budget = line("Total budget", f"=N({cell_of['Total budget inc GST ($)']})", MONEY)
    cont = line("Contingency in the budget", f"={budget}*N({cell_of['Contingency (%)']})", MONEY)
    pkb = line("Allocated to packages", f"=SUM({pk.col('budget')})", MONEY, "Sum of Packages budgets. Should be about the total budget less contingency.")
    com = line("Committed (contracts + approved variations)", f"=SUM({pk.col('committed')})", MONEY)
    line("Committed as % of package budgets", f'=IF({pkb}=0,"",{com}/{pkb})', "0%", "G3 exit check: compare with the target on Settings before going to site.")
    line("G3 target", f"={SET['committed']}", "0%")
    paid = line("Spent to date (paid)", f'=SUMIFS({pay.col("amount")},{pay.col("paid")},"Yes")', MONEY)
    line("Budget used", f'=IF({budget}=0,"",{paid}/{budget})', "0%")
    fc = line("Forecast final cost", f"=SUM({pk.col('forecast')})", MONEY)
    line("Forecast under / (over) total budget", f"={budget}-{fc}", '"$"#,##0;[Red]("$"#,##0)')
    line("Selections total", f"=SUM({sel.col('total')})", MONEY)
    r += 1

    section("Takeoffs (Rooms tab)")
    a_, t_ = rm.col("area"), rm.col("atype")
    line("Internal floor area (m²)", f'=SUMIFS({a_},{t_},"<>Garage",{t_},"<>External")', "0.0", "Blank area type counts as internal.")
    line("Garage floor area (m²)", f'=SUMIFS({a_},{t_},"Garage")', "0.0")
    line("External areas (m²)", f'=SUMIFS({a_},{t_},"External")', "0.0", "Driveways, paving, decks.")
    line("Wall paint, one coat (m²)", f"=SUM({rm.col('wall')})", "0.0")
    line("Skirting (m)", f"=SUM({rm.col('perim')})", "0.0")
    line("Floor covering incl. waste (m²)", f"=SUM({rm.col('tiles')})", "0.0")
    r += 1

    section("Compliance by stage", ["Items", "N/A", "Done", "% done"])
    first_stage_row = r
    for stage in stages:
        db.cell(row=r, column=1, value=stage)
        db.cell(row=r, column=2, value=f'=COUNTIFS({cp.col("stage")},$A{r})')
        db.cell(row=r, column=3, value=f'=COUNTIFS({cp.col("stage")},$A{r},{cp.col("status")},"N/A")')
        db.cell(row=r, column=4, value=f'=COUNTIFS({cp.col("stage")},$A{r},{cp.col("status")},"Done")')
        db.cell(row=r, column=5, value=f'=IF(B{r}-C{r}=0,"",D{r}/(B{r}-C{r}))').number_format = "0%"
        for i in range(2, 6):
            db.cell(row=r, column=i).fill = F_AUTO
        r += 1
    db.cell(row=r, column=1, value="All stages").font = BOLD
    for i, col in zip(range(2, 5), "BCD"):
        db.cell(row=r, column=i, value=f"=SUM({col}{first_stage_row}:{col}{r - 1})").font = BOLD
    db.cell(row=r, column=5, value=f'=IF(B{r}-C{r}=0,"",D{r}/(B{r}-C{r}))').number_format = "0%"
    db.conditional_formatting.add(f"E{first_stage_row}:E{r}", CellIsRule(operator="equal", formula=["1"], fill=F_GREEN))
    r += 2

    section("Needs attention", ["Count"])
    alerts_first = r
    def past_rows(t):
        """Anything typed below a tab's pre-filled rows, which no total counts."""
        end = get_column_letter(len(t.cols))
        return f"COUNTA('{t.name}'!$A${t.last + 1}:${end}${t.last + 1000})"

    budget_ref = cell_of["Total budget inc GST ($)"]
    alerts = [
        ("Entries past the pre-filled rows (not counted!)", "=" + "+".join(past_rows(t) for t in (gw, cp, rm, sel, di, ph, dc, pk, tr, tn, va, pay, ce, rk)),
         "Something was typed below the last formula row. Unprotect the sheet and copy the last row down to extend it."),
        ("Go decisions with exit checks open", f'=COUNTIF({gr.col("dcheck")},"?*")', "Gate Review tab"),
        ("Earlier gates without a Go decision", f'=SUMPRODUCT(({gr.col("gate")}<{gate_cell})*({gr.col("decision")}<>"Go"))', "Gates before the current gateway on the Project tab."),
        ("Certificate of consent needed, no number recorded", f'=IF(AND(N({budget_ref})>{SET["consent"]},{cell_of["Certificate of consent no."]}=""),1,0)', "Budget is over the consent threshold on Settings."),
        ("Principal contractor needed, not done", f'=IF(AND(N({budget_ref})>={SET["pc"]},COUNTIFS({cp.col("id")},"oh-pc",{cp.col("status")},"Done")=0),1,0)', "Budget is at or over the principal contractor threshold (Compliance oh-pc)."),
        ("Trade paperwork expired", f'=COUNTIF({tr.col("alert")},"Expired")', "Trades tab: licence or insurance past its expiry date."),
        ("Trade paperwork expiring soon", f'=COUNTIF({tr.col("alert")},"Expires*")', "Ask for new certificates of currency now."),
        ("Trade dates typed as text or missing", f'=COUNTIF({tr.col("alert")},"Check date*")+COUNTIF({tr.col("alert")},"Missing*")', "A date typed as text can't be checked for expiry."),
        ("Trade contract checks to look at", f'=COUNTIF({tr.col("checks")},"?*")', "Trades tab: duplicates, registration and home warranty."),
        ("Deposits over the statutory cap", f'=COUNTIF({tr.col("depcheck")},"Over statutory cap")', "Caps and threshold are on Settings."),
        ("Quotes needing a look", f'=COUNTIF({tn.col("issues")},"?*")', "Tenders tab: Check column."),
        ("Tender packages tied for 1st", f'=COUNTIF({ts.col("rec")},"Tie*")', "Tender Setup tab"),
        ("Documents with problems", f'=COUNTIF({dc.col("issues")},"?*")', "Documents tab: Check column."),
        ("Packages with naming problems", f'=COUNTIF({pk.col("issues")},"?*")', "Packages tab: names must start with their No."),
        ("Rooms with sizes typed as text", f'=COUNTIF({rm.col("issues")},"?*")', ""),
        ("Invoices charging GST from unregistered trades", f'=COUNTIF({pay.col("gstflag")},"GST charged, not registered")', ""),
        ("Unpaid invoices", f'=COUNTIFS({pay.col("amount")},">0",{pay.col("paid")},"<>Yes")', ""),
        ("Open defects", f'=COUNTIFS({di.col("type")},"Defect",{di.col("closed")},"<>Yes")', "Diary tab"),
        ("Open questions for the building surveyor", f'=COUNTIFS({di.col("type")},"Question for RBS",{di.col("closed")},"<>Yes")', "Diary tab"),
        ("Pending variations", f'=COUNTIF({va.col("approved")},"Pending")', "Don't let work start before the price is agreed."),
        ("Selections still to choose", f'=COUNTIF({sel.col("status")},"To choose")', "All selections must be locked before G6."),
        ("Packages forecast over budget", f'=COUNTIF({pk.col("flag")},"Over budget")', "By more than the margin on Settings."),
        ("Tender weights that don't add to 100", f'=SUMPRODUCT(({ts.col("pkg")}<>"")*({ts.col("wsum")}<>100))', "Tender Setup tab"),
        ("Must-have certificates not yet passed", f'=COUNTIFS({ce.col("req")},"Must",{ce.col("result")},"<>Pass")', "Certificates tab. Needed before the final inspection."),
        ("High risks still open", f'=COUNTIFS({rk.col("rating")},"High",{rk.col("status")},"<>Closed")', ""),
        ("Duplicate Doc IDs", f'=SUMPRODUCT(({dc.col("docid")}<>"")*(COUNTIF({dc.col("docid")},{dc.col("docid")})>1))', "Documents tab: rows sharing a Doc ID. Should be 0."),
        ("Example rows still in the workbook", f'=COUNTIF({rm.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({sel.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({di.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({ph.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({dc.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({tr.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({tn.col("notes")},"{EXAMPLE_NOTE}")+COUNTIF({pay.col("notes")},"{EXAMPLE_NOTE}")', "Delete them once you've seen how each tab works."),
    ]
    for label, formula, note in alerts:
        line(label, formula, None, note)
    db.conditional_formatting.add(f"B{alerts_first}:B{r - 1}", CellIsRule(operator="notEqual", formula=["0"], fill=F_AMBER))
    lock_sheet(db)

    # ---------------- Guides, Q&A, Reference (read-only)
    gd = wb.create_sheet("Guides")
    title(gd, "Buying guides & specs", "Stage-by-stage: the standards that apply, the spec to confirm and what to ask suppliers. Read-only. Content checked September 2026.")
    for i, (h, w) in enumerate(zip(["Stage", "Topic", "Standards", "Spec to confirm", "Ask the supplier / trade"], [16, 26, 30, 70, 50]), start=1):
        c = gd.cell(row=HEADER_ROW, column=i, value=h)
        c.font, c.fill = WHITE_BOLD, F_HEAD
        gd.column_dimensions[get_column_letter(i)].width = w
    r = FIRST
    for stage, topic, answer in guides:
        std = re.search(r"<p><b>Standards:</b>(.*?)</p>", answer, re.S)
        ask = re.search(r"<p><b>Ask[^<]*</b>(.*?)</p>", answer, re.S)
        rest = re.sub(r"<p><b>(Standards:|Ask[^<]*)</b>.*?</p>", "", answer, flags=re.S)
        for i, v in enumerate([stage, topic, text(std.group(1)) if std else "", text(rest), text(ask.group(1)) if ask else ""], start=1):
            gd.cell(row=r, column=i, value=v).alignment = WRAP
        r += 1
    gd.freeze_panes = "C4"
    gd.auto_filter.ref = f"A{HEADER_ROW}:E{r - 1}"

    qa = wb.create_sheet("Q&A")
    title(qa, "Owner-builder Q&A (Victoria)", "Plain-English answers, grouped by topic. Read-only. General information, checked September 2026, not legal advice.")
    for i, (h, w) in enumerate(zip(["Topic", "Question", "Answer"], [24, 44, 100]), start=1):
        c = qa.cell(row=HEADER_ROW, column=i, value=h)
        c.font, c.fill = WHITE_BOLD, F_HEAD
        qa.column_dimensions[get_column_letter(i)].width = w
    r = FIRST
    for topic, question, answer in faq:
        for i, v in enumerate([topic, question, text(answer)], start=1):
            qa.cell(row=r, column=i, value=v).alignment = WRAP
        r += 1
    qa.freeze_panes = "C4"
    qa.auto_filter.ref = f"A{HEADER_ROW}:C{r - 1}"

    rf = wb.create_sheet("Reference")
    title(rf, "Reference", "Key numbers, contract types, tendering and who does what. Read-only.")
    for col, w in zip("ABCDEF", [36, 30, 30, 30, 30, 22]):
        rf.column_dimensions[col].width = w
    r = HEADER_ROW

    def ref_table(heading, heads, rows_):
        nonlocal r
        rf.cell(row=r, column=1, value=heading).font = TITLE
        r += 1
        for i, h in enumerate(heads, start=1):
            c = rf.cell(row=r, column=i, value=h)
            c.font, c.fill = WHITE_BOLD, F_HEAD
        r += 1
        for row in rows_:
            for i, v in enumerate(row, start=1):
                rf.cell(row=r, column=i, value=v).alignment = WRAP
            r += 1
        r += 1

    ref_table("Key numbers", ["Rule", "Figure", "Where it comes from"], key_numbers)
    ref_table("Contract types", ["Type", "How it's priced", "Best for", "Watch out for"], contract_types)
    for heading, items in tender_lists.items():
        ref_table(heading, [heading], [[i] for i in items])
    ref_table("Who does what (RACI)", raci[0], raci[1:])

    for ws in (gd, qa, rf):
        ws.protection.sheet = True
        ws.protection.autoFilter = False
        ws.sheet_properties.tabColor = "8A9BAE"

    # ---------------- Start
    st = start
    title(st, "Owner Builder in a Box: Owner Workbook",
          "Your whole owner-build in one spreadsheet. Works offline in Excel, Numbers, LibreOffice or Google Sheets (offline mode).")
    st["A3"] = "Includes Guides and common Q&A for tracking your project efficiently"
    st.column_dimensions["A"].width = 22
    st.column_dimensions["B"].width = 100
    r = HEADER_ROW + 1
    guide = [
        ("How it works", None),
        ("Colours", "White cells are for you. Grey cells are calculated and locked so they can't be typed over by accident (Review > Unprotect sheet if you need to; there's no password). Pale yellow rows are examples: delete them when you're ready (the Dashboard counts what's left)."),
        ("Start here", "1. Fill in the Project tab.  2. Set your budgets on Packages.  3. Work through Compliance and Gateways from G0.  4. Log everything else as it happens."),
        ("Files", "Documents live in Google Drive, not in the workbook. Register each one on the Documents tab: it builds a Doc ID (e.g. 02-DWG-012), the file name to use, and the Drive folder to save it in. Paste the Drive link once it's uploaded.\n"
                  "Share documents, photos and tender documents with trades and others as needed. (recommend to use suggested naming conventions for files)"),
        ("Offline", "Excel / Numbers / LibreOffice: open this file and work. With Google Drive / Dropbox / Onedrive for desktop the project folder is on your computer too, so you can save files offline and they sync later. Google Sheets: turn on Drive > Settings > Offline, or in the Sheets app tap ⋮ > Make available offline. The Apps Script menu needs a connection."),
        ("Folder links", "The Open links work with Google Drive, Dropbox, OneDrive or SharePoint: paste each folder's link (Share > Copy link) into the Google Drive Map tab. Working offline on a computer, paste the local folder path instead and it opens without internet."),
        ("Google Sheets fast set-up", "Upload this file to Drive, open it, then File > Save as Google Sheets. Then Extensions > Apps Script, paste in Code.gs, save and reload. A new Owner Builder menu appears: Set up Drive folders creates the folder tree for this build and links every folder path in the workbook."),
        ("Need more rows?", "Each tab has room for hundreds of entries. If you run out, unprotect the sheet and copy the last row down so the formulas come too. The Dashboard warns if anything is typed below the last formula row."),
        ("Tabs", None),
        ("Dashboard", "Current gateway, money, compliance progress and everything that needs attention."),
        ("Project", "Address, title, owners, budget, permits, site classification."),
        ("Guides / Q&A / Reference", "Buying guides, plain-English answers and key numbers from Owner Builder in a Box. Read-only."),
        ("Gate Review", "G0 to G7: progress against entry, deliverables and exit checks, with your Go / Hold / Stop decision."),
        ("Gateways", "Every entry criterion, deliverable and exit check for each gate."),
        ("Compliance", "The 11-stage Victorian owner-builder checklist, with the folder to file the evidence in."),
        ("Risks", "Starter risk register with likelihood × impact ratings."),
        ("Google Drive Map", "The folder tree, what goes in each folder, the file naming rules, and the folder links."),
        ("Rooms", "Room sizes give floor area, paint area, skirting length and tile quantities. Area type keeps garages and outdoor areas out of the paint and skirting figures."),
        ("Selections", "Every product decision: spec, supplier, price, status."),
        ("Diary", "Site diary, plan notes, instructions to trades, defects, questions for the building surveyor."),
        ("Photos", "Log of site photos, especially before anything is covered."),
        ("Documents", "The register of every file in Google Drive, with Doc IDs and file names."),
        ("Tender Setup / Tenders", "Quote comparison: compliance gates, price levelling, weighted scoring and a recommendation per package."),
        ("Packages", "20 trade packages: budget, committed, paid and forecast."),
        ("Trades", "Contacts, licences, insurance, SWMS, contracts, deposit checks, expiry alerts."),
        ("Variations / Payments", "Written variations and every invoice. They feed the Packages costs."),
        ("Certificates", "Mandatory inspections and the certificates needed for the final inspection."),
        ("Settings", "The legal thresholds and rules behind the checks (deposit caps, contract, warranty and consent thresholds, warning days). Update them here when the law changes."),
        ("Important", None),
        ("Not advice", "General information only. It is not legal, financial or building advice. Always confirm current requirements with the Building and Plumbing Commission (BPC), your relevant building surveyor, your council and WorkSafe Victoria. Victorian rules checked September 2026."),
    ]
    for label, body in guide:
        a = st.cell(row=r, column=1, value=label)
        if body is None:
            a.font, a.fill = WHITE_BOLD, F_HEAD
            st.cell(row=r, column=2).fill = F_HEAD
        else:
            a.font = BOLD
            a.alignment = WRAP
            st.cell(row=r, column=2, value=body).alignment = WRAP
        r += 1

    lock_sheet(st)

    # Lock formula cells everywhere. Summary columns filled in after the fact are listed explicitly.
    for t in (gw, cp, rm, sel, di, ph, dc, tr, va, pay, ce, rk, gr):
        t.protect()
    pk.protect(also_locked=("contracted", "variations", "paid"))
    ts.protect(also_locked=("count", "rec", "score", "levelled", "margin"))
    tn.protect()

    # Tab order (as arranged in the owner's copy) and colours
    final_order = ["Start", "Dashboard", "Project", "Q&A", "Guides", "Reference", "Gate Review", "Gateways",
                   "Compliance", "Risks", DRIVE_MAP, "Rooms", "Selections", "Diary", "Photos", "Documents",
                   "Tender Setup", "Tenders", "Packages", "Trades", "Payments", "Variations", "Certificates",
                   "Settings", "Lists"]
    wb._sheets = [wb[n] for n in final_order]
    for n in ["Start", "Dashboard", "Project"]:
        wb[n].sheet_properties.tabColor = TEAL
    lists.sheet_state = "hidden"
    wb.active = 0
    wb.save(out)
    print(f"Wrote {out}: {len(compliance)} compliance items, {sum(len(i) for g in gates for _, i in g['sections'])} gateway items, "
          f"{len(guides)} guides, {len(faq)} Q&A")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--src", help="Unpacked owner-builder-in-a-box folder (default: read it from git history)")
    p.add_argument("--out", default=os.path.join(HERE, "Owner-Builder-in-a-Box.xlsx"))
    args = p.parse_args()
    build(args.src, args.out)
