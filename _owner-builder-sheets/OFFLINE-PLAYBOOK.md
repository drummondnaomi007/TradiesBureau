# Offline playbook

How to keep your Owner Builder in a Box workbook and your project files working when you're on site with no signal, without losing anything or ending up with two different versions.

## 1. Pick one master copy, and only ever edit that one

The biggest offline risk isn't losing signal. It's ending up with two copies that both have changes and can't be merged. Decide once:

| Your situation | Master copy |
|---|---|
| You use your phone on site, or two people edit (you and a partner) | **The Google Sheet** |
| One person, one computer, and you prefer Excel | **The Excel file**, kept in a synced folder (Google Drive, Dropbox or OneDrive for desktop) |

Then:

- Write which one is the master in the Project tab's Notes column.
- If you move from Excel to Google Sheets, rename the old file `NOT MASTER - Owner-Builder-in-a-Box.xlsx` and move it to `99 Archive`.
- An Excel master is edited on **one computer at a time**. If two computers open it while offline, the sync app keeps both as "conflicted copies" and you'll have to copy changes across by hand.
- In Google Sheets, two people editing offline is fine for different cells. If you both change the same cell, the last one to sync wins.

## 2. Set up each device once, with signal

Do this at home before you need it. Offline mode can't be switched on without a connection.

**Google Sheet on a computer**
1. Use Chrome or Edge, signed in to your Google account.
2. Install the **Google Docs Offline** extension.
3. In Google Drive, open **Settings** and tick **Offline**.
4. In Drive, right-click the workbook and choose **Available offline**.

**Google Sheet on a phone or tablet**
1. Install the **Google Sheets** and **Google Drive** apps.
2. Open the workbook once, tap **⋮**, and turn on **Available offline**.
3. Do the same in the Drive app for any drawings or PDFs you'll need on site.

**Excel master**
- With Google Drive for desktop, choose **Mirror files**, or right-click the project folder and choose **Available offline**.
- With Dropbox, right-click the project folder and choose **Make available offline**.
- With OneDrive, right-click the project folder and choose **Always keep on this device**.

**Dates and money on every device**
- Google Sheet: **File > Settings**, then set Locale to **Australia** and Time zone to **Melbourne**.
- Excel: your computer's region must be **English (Australia)**.

Get this wrong and 1/2/2027 is read as 2 January, which throws off every expiry date check.

## 3. What works offline

| Works | Doesn't work until you're back online |
|---|---|
| Typing and editing on every tab | The **Owner Builder** menu (it needs a connection) |
| All calculations, the Dashboard and the Check columns | Automatic Doc ID numbers: type the **Next free no.** yourself |
| Dropdowns, area takeoffs, tender scoring, the Go block | Automatic dates on new Diary notes: type the date yourself |
| Guides, Q&A and Reference tabs | **Open** links to web folders (local folder paths work in Excel) |
| Files you've marked available offline | Uploading photos and documents to Drive |

## 4. On site with no signal

- **Diary:** log who's on site, the weather, deliveries, instructions to trades, defects and questions for the building surveyor. Type the date.
- **Photos:** take them with your phone's camera. In the Photos tab, record the date, the stage, what it shows, and the phone's file name (e.g. `IMG_4821`). Photograph anything before it's covered.
- **Documents and quotes:** if a trade hands you paperwork, photograph it and add a Documents row with the folder and type. Fill in the number and link later.
- **Don't make decisions on stale information.** The Dashboard only knows what's been entered. Check it once you're back online before paying anyone or recording a Go at a gate.

## 5. Back online: the 10-minute routine

1. Let everything sync. In Google Sheets, wait until it no longer says it's offline. In Excel, wait for the sync icon to go green.
2. Upload the day's photos to `06 Site Diary & Photos`. Rename each one with its Doc ID, e.g. `06-PHO-014_Slab-mesh-north`, and paste its link into the Photos tab.
3. Upload any paperwork to the folder the Documents tab shows. Fill in the number and paste the link.
4. Look at **Needs attention** on the Dashboard. Fix anything new, especially **Entries past the pre-filled rows**, which means something typed below the last formula row isn't being counted.
5. Once a week: **Owner Builder > Check trade paperwork**, then **Owner Builder > Back up a copy**.

Only delete photos from your phone after you've checked they're in Drive.

## 6. Backups

- **Google Sheet:** Google keeps a version history (**File > Version history**). Run **Back up a copy** weekly, and always before big changes such as removing example rows or adding columns.
- **Excel:** use **File > Save a Copy** weekly into `00 Project Register`, named `Backup YYYY-MM-DD`. Sync apps keep some history, but don't rely on it.
- **One copy off the cloud:** each month, download the workbook (**File > Download > Microsoft Excel** in Google Sheets) and copy it, with the project folder, to a USB drive or external disk. That protects you if your account is locked or a sync goes wrong.

## 7. Sharing and privacy

- Share **folders**, not the workbook. A trade or surveyor needs the drawings and certificates, not your budget, payments or other trades' quotes. In Drive, share the folder **view only**.
- The workbook holds ABNs, contract values and personal details, and offline copies sit on your devices. Use a passcode on your phone and laptop.
- If a device is lost, sign it out from your Google, Dropbox or Microsoft account's security settings straight away.

## 8. If something goes wrong

| Problem | What to do |
|---|---|
| Two versions with different changes | Keep the master. Open the other copy, copy the rows that are missing into the master, then move the other copy to `99 Archive`. |
| A grey cell won't let you type | It's a formula. Type in the white cells next to it. If you really need to change it, use **Review > Unprotect sheet** (there's no password). |
| A date shows "Check date: typed as text" | Retype it as a date, e.g. 30/06/2027. Check your locale (section 2). |
| An **Open** link does nothing | You're offline, or there's no link on the Google Drive Map tab yet. In Excel you can paste a local folder path there instead. |
| A Check column flags a row | Read the message. It says what's wrong in plain words. |
| You've run out of rows | Unprotect the sheet and copy the last row down, so the formulas come too. |

General information only. It is not legal, financial or building advice.
