# Owner Builder in a Box: offline workbook

An offline, spreadsheet version of the Owner Builder in a Box prototype, with its documents organised in Google Drive (or Dropbox or OneDrive).

The tab order, Start tab wording and the Rooms and Selections notes follow the owner's edited copy (October 2026).

The folder name starts with `_` so GitHub Pages (Jekyll) doesn't publish it on tradiesbureau.com, the same reason the prototype was moved out of this repo. Move this folder too when Owner Builder in a Box gets its own repository.

| File | What it is |
|---|---|
| `Owner-Builder-in-a-Box.xlsx` | The workbook. Opened, edited and recalculated in Excel; checked in LibreOffice; converts to Google Sheets. |
| `Code.gs` | Optional Apps Script for Google Sheets: creates the Drive folders, numbers documents, protects formula columns, clears example rows. |
| `OFFLINE-PLAYBOOK.md` | How to work offline without losing anything: choosing a master copy, device set-up, the on-site and back-online routines, backups, sharing, fixes. The workbook's read-only **Offline Playbook** tab is built from this file, and a copy is in the Drive template folder. |
| `build_workbook.py` | Rebuilds the workbook from the prototype's pages (`python3 _owner-builder-sheets/build_workbook.py`, needs `openpyxl`). |

## How the prototype maps to the workbook

| Prototype | Workbook tab | Drive folder |
|---|---|---|
| My Build: project | Project, Dashboard | 00 Project Register |
| My Build: rooms (area, paint, skirting, tiles) | Rooms (takeoffs, with Internal / Garage / External area types) | 02 Design & Engineering (drawing refs) |
| My Build: selections & specs | Selections | 05 Selections & Specs |
| My Build: plan notes & site diary | Diary | 06 Site Diary & Photos |
| My Build: plans & documents | Documents (register) | All folders, by Doc ID |
| My Build: site photos | Photos (log; files live in Drive) | 06 Site Diary & Photos |
| Compliance checklist (11 stages, 61 items) | Compliance | Per item: 01 to 08 |
| Gateways G0 to G7 | Gateways, Gate Review | Per deliverable |
| Contracts: trade packages | Packages (budget, committed, paid, forecast) | 04 Trades & Tenders/<package> |
| Contracts: pre-engagement checks, deposits | Trades (licence and insurance expiry, deposit cap) | 04 Trades & Tenders/<package> |
| Contracts: variations, paying trades | Variations, Payments | 04 Trades & Tenders/<package> |
| Tender comparison tool | Tender Setup, Tenders | 04 Trades & Tenders/<package> |
| Gateways: risk register | Risks | 00 Project Register |
| Compliance stages 8 and 9: certificates | Certificates | 07 Inspections & Certificates |
| Buying guides, Q&A, key numbers, contract types, RACI | Guides, Q&A, Reference (read-only) | n/a |
| Backup / restore (localStorage JSON) | The file itself, or Owner Builder > Back up a copy | 00 Project Register |
| Legal thresholds in the prototype's text | Settings (deposit caps, contract, warranty, consent and principal contractor thresholds, warning days) | n/a |

The tender scoring is the same as the prototype's: fail any compliance gate and the quote is excluded. The levelled price is quote + exclusions ± provisional sums + risk. Price points are the lowest levelled price ÷ this price × the price weight. Other points are each score (capped at 0 to 10) × its weight ÷ 10, and the total is scaled to 100 even if the weights don't add up. A quote more than 15% under the median (Settings) gets flagged, and ties for first are called out instead of quietly picking one. With the example quotes, Ridgeline scores 90.2 and is recommended, Summit scores 86.0, and Budget Roofs is excluded on insurance.

## Google Drive folders

```
Owner Build - <project>/
  00 Project Register             the workbook and its backups
  01 Eligibility, Land & Planning eLearning, white card, consent, title, s173, planning, LPOD
  02 Design & Engineering         drawings, engineering, energy, BAL, survey, soil
  03 Permits, Insurance & Finance RBS, building permit, asset protection, your policies, loan
  04 Trades & Tenders
     01 Surveyor ... 20 Floor coverings & landscaping
                                  quotes, contract, variations, licence/insurance/SWMS, invoices
  05 Selections & Specs
  06 Site Diary & Photos
  07 Inspections & Certificates   RBS reports, PCC, CoES, waterproofing, termite, glazing
  08 Handover, Records & Sale     occupancy permit, warranties, manuals, s137B, s32
  99 Archive                      superseded drawings, unsuccessful quotes
```

The **Google Drive Map** tab lists every folder, what goes in it, and which compliance stages and gateways use it. Its *Folder link* column feeds the **Open** links on the Compliance, Gateways, Packages, Trades and Documents tabs. Any provider works: paste a Google Drive, Dropbox, OneDrive or SharePoint folder link (Share > Copy link). Offline on a computer, paste the local folder path instead (e.g. `C:\Users\you\Dropbox\Owner Build\02 Design & Engineering`) and the link opens without internet.

Package folders are found by the package's two-digit number, so renaming `08 Roofing` to `08 Roofing & gutters` keeps its folder, costs, payments and tenders together.

### File names: `DocID_Description_Rev`

A Doc ID is the folder code, document type and number, e.g. `02-DWG-012`. Register a file on the **Documents** tab: pick the folder and type, and the tab shows the next free number (in Google Sheets the script fills it in). It then gives you the file name, e.g. `02-DWG-012_Floor-Plan_RevC`, and the folder to save it in. Trade paperwork goes in that package's subfolder of 04. Superseded files move to 99 Archive. Characters that break file names (`/ \ : * ? " < > |`) become hyphens. Document type codes are listed on the Google Drive Map tab.

## Setting it up in Google Sheets

1. Upload `Owner-Builder-in-a-Box.xlsx` to Drive, open it and choose **File > Save as Google Sheets** (or use the copy already in Drive, below).
2. **Extensions > Apps Script**, replace the contents with `Code.gs`, save, then reload the sheet. An **Owner Builder** menu appears. The first run asks for permission to manage Drive files.
3. Fill in the project name on the **Project** tab, then choose **Owner Builder > Set up Drive folders**. It creates `Owner Build - <project>` with the tree above, moves the sheet into `00 Project Register` and fills in the Google Drive Map links.
4. Choose **Owner Builder > Protect formula columns** so grey columns warn before they're typed over (the Excel sheet protection may not carry across).
5. When you've seen how each tab works, choose **Owner Builder > Remove example rows**. The pale yellow rows are examples, and the Dashboard counts how many are left.

For each new build: **File > Make a copy** of the template sheet, then run steps 3 to 5 on the copy. Drive can't copy folders, so the script creates the folders for each build.

## Working offline

- **Excel or LibreOffice**: everything except the script menu works. Paste folder links (or local paths) into the Google Drive Map tab for the Open links. Numbers hasn't been tested and probably loses the cross-tab dropdowns and the tender maths.
- **Google Sheets**: turn on offline in Drive (**Settings > Offline**), or in the Sheets app tap **⋮ > Make available offline**. Edits sync when you reconnect. The script menu needs a connection.
- **Files**: with Google Drive, Dropbox or OneDrive for desktop, the project folder is on your computer. Save files into it offline and they upload when you're back online.

## Safeguards and checks

- **Locked formulas.** Grey cells are protected in Excel (no password: Review > Unprotect sheet). Filtering, sorting entry columns, formatting and adding rows still work. Unprotect before sorting a whole table, since Excel won't sort locked cells.
- **Check columns** on Rooms, Packages, Documents, Trades and Tenders say what's wrong with a row in plain words: sizes or prices typed as text, levelled prices of $0 or less, packages that aren't on the Packages tab, scores outside 0 to 10, document numbers that aren't numbers, folder codes not on the map, duplicate Doc IDs, duplicate business names, contracts over the registered builder or home warranty thresholds.
- **Dates typed as text** on Trades show "Check date: typed as text" rather than a false "OK". Engaged trades with no expiry dates show "Missing expiry date".
- **Go is blocked** on Gate Review until every exit check is Yes, and a Go that's no longer valid (an exit check unticked later) is flagged.
- **The Dashboard** counts every check, plus entries typed below the pre-filled rows (which no total would count), earlier gates without a Go, and whether the budget needs a certificate of consent or a principal contractor.
- **Settings** holds every legal threshold. When the law changes (e.g. the proposed $10,000 to $20,000 contract threshold), change it there.

## Keeping it current

The checklist, gateway, package, guide and Q&A text comes from the prototype at commit `99fe447` (Victorian rules checked September 2026). After the content changes there, rebuild with `build_workbook.py --src <path to owner-builder-in-a-box>`. Tab layouts, Drive folders and certificates are defined at the top of the script.

General information only, not legal, financial or building advice.
