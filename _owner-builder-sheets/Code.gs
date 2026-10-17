/**
 * Owner Builder in a Box: Google Sheets helper.
 *
 * Paste into Extensions > Apps Script in the converted workbook, save, reload.
 * Adds an "Owner Builder" menu. Everything in the workbook still works without
 * this script (and offline); the script only does what a formula can't:
 * create the Drive folders, number documents, and tidy up.
 */

var HEADER_ROW = 3;
var FIRST_ROW = 4;
var EXAMPLE_NOTE = 'EXAMPLE: delete this row';
var REGISTER_FOLDER = '00 Project Register';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Owner Builder')
    .addItem('Set up Drive folders', 'setUpDriveFolders')
    .addItem('Check trade paperwork', 'checkTradePaperwork')
    .addSeparator()
    .addItem('Remove example rows', 'removeExampleRows')
    .addItem('Back up a copy', 'backUpCopy')
    .addToUi();
}

// Documents: fill in the next free number once folder and type are picked.
// Diary: date a new entry if the date is blank.
function onEdit(e) {
  var sheet = e.range.getSheet();
  var row = e.range.getRow();
  if (row < FIRST_ROW) return;
  var cols = headers_(sheet);
  if (sheet.getName() === 'Documents') {
    var folder = sheet.getRange(row, cols['Folder']).getDisplayValue();
    var type = sheet.getRange(row, cols['Type']).getDisplayValue();
    var noCell = sheet.getRange(row, cols['No.']);
    if (folder && type && noCell.isBlank()) {
      var last = sheet.getLastRow();
      var data = sheet.getRange(FIRST_ROW, 1, last - FIRST_ROW + 1, sheet.getLastColumn()).getDisplayValues();
      var max = 0;
      data.forEach(function (r) {
        if (r[cols['Folder'] - 1] === folder && r[cols['Type'] - 1] === type) {
          max = Math.max(max, parseInt(r[cols['No.'] - 1], 10) || 0);
        }
      });
      noCell.setValue(max + 1);
    }
  } else if (sheet.getName() === 'Diary' && e.range.getColumn() === cols['Note']) {
    var dateCell = sheet.getRange(row, cols['Date']);
    if (dateCell.isBlank() && e.value) dateCell.setValue(new Date());
  }
}

// Create (or find) this build's folder tree and write each folder's link into
// the Drive Map. Every "Open" link in the workbook reads from there.
function setUpDriveFolders() {
  var ui = SpreadsheetApp.getUi();
  var ss = SpreadsheetApp.getActive();
  var file = DriveApp.getFileById(ss.getId());
  var parents = file.getParents();
  var parent = parents.hasNext() ? parents.next() : DriveApp.getRootFolder();

  var root;
  if (parent.getName() === REGISTER_FOLDER && parent.getParents().hasNext()) {
    var existing = parent.getParents().next();
    var answer = ui.alert('Set up Drive folders',
      'This sheet is already in "' + existing.getName() + '". Use that folder for this build?\n\n' +
      'Yes: use it.  No: create a new folder for this build instead.', ui.ButtonSet.YES_NO_CANCEL);
    if (answer === ui.Button.CANCEL || answer === ui.Button.CLOSE) return;
    if (answer === ui.Button.YES) root = existing;
    else parent = existing.getParents().hasNext() ? existing.getParents().next() : DriveApp.getRootFolder();
  }
  if (!root) {
    var name = projectValue_('Project name');
    if (!name) {
      var reply = ui.prompt('Set up Drive folders', 'What is this build called? (e.g. 12 Example St)', ui.ButtonSet.OK_CANCEL);
      if (reply.getSelectedButton() !== ui.Button.OK || !reply.getResponseText().trim()) return;
      name = reply.getResponseText().trim();
      setProjectValue_('Project name', name);
    }
    var answer2 = ui.alert('Set up Drive folders',
      'Create "Owner Build - ' + name + '" in "' + parent.getName() + '" and move this sheet into its ' +
      REGISTER_FOLDER + ' folder?', ui.ButtonSet.OK_CANCEL);
    if (answer2 !== ui.Button.OK) return;
    root = childFolder_(parent, 'Owner Build - ' + name);
  }

  var map = ss.getSheetByName('Drive Map');
  var cols = headers_(map);
  var rows = map.getRange(FIRST_ROW, 1, map.getLastRow() - FIRST_ROW + 1, map.getLastColumn()).getDisplayValues();
  var made = 0;
  for (var i = 0; i < rows.length; i++) {
    var path = rows[i][cols['Folder path'] - 1];
    if (!rows[i][cols['Code'] - 1] || !path) break; // the naming guide below the table
    var folder = root;
    path.split('/').forEach(function (part) { folder = childFolder_(folder, part); });
    map.getRange(FIRST_ROW + i, cols['Folder link']).setValue(folder.getUrl());
    made++;
  }

  var register = childFolder_(root, REGISTER_FOLDER);
  if (parent.getId() !== register.getId()) file.moveTo(register);
  setProjectValue_('Project folder link', root.getUrl());
  ui.alert('Done', made + ' folders are ready in "' + root.getName() + '". The Open links on each tab now go straight to them.', ui.ButtonSet.OK);
}

function checkTradePaperwork() {
  var sheet = SpreadsheetApp.getActive().getSheetByName('Trades');
  var cols = headers_(sheet);
  var rows = sheet.getRange(FIRST_ROW, 1, sheet.getLastRow() - FIRST_ROW + 1, sheet.getLastColumn()).getDisplayValues();
  var lines = [];
  rows.forEach(function (r) {
    var status = r[cols['Paperwork'] - 1];
    if (status === 'Expired' || status === 'Expires within 30 days') {
      lines.push(r[cols['Business name'] - 1] + ' (' + r[cols['Package'] - 1] + '): ' + status +
        '. Licence ' + (r[cols['Licence expiry'] - 1] || 'n/a') + ', insurance ' + (r[cols['PL expiry'] - 1] || 'n/a'));
    }
  });
  SpreadsheetApp.getUi().alert('Trade paperwork',
    lines.length ? lines.join('\n') : 'Nothing expired or expiring in the next 30 days.', SpreadsheetApp.getUi().ButtonSet.OK);
}

// Clears what you typed in example rows. Formulas stay, so every tab keeps working.
function removeExampleRows() {
  var ui = SpreadsheetApp.getUi();
  if (ui.alert('Remove example rows', 'Clear every row marked "' + EXAMPLE_NOTE + '"?', ui.ButtonSet.OK_CANCEL) !== ui.Button.OK) return;
  var cleared = 0;
  SpreadsheetApp.getActive().getSheets().forEach(function (sheet) {
    if (sheet.getLastRow() < FIRST_ROW) return;
    var notesCol = headers_(sheet)['Notes'];
    if (!notesCol) return;
    var width = sheet.getLastColumn();
    var notes = sheet.getRange(FIRST_ROW, notesCol, sheet.getLastRow() - FIRST_ROW + 1, 1).getValues();
    notes.forEach(function (n, i) {
      if (n[0] !== EXAMPLE_NOTE) return;
      var row = FIRST_ROW + i;
      var formulas = sheet.getRange(row, 1, 1, width).getFormulas()[0];
      formulas.forEach(function (f, c) {
        if (!f) sheet.getRange(row, c + 1).clearContent().setBackground(null);
      });
      cleared++;
    });
  });
  ui.alert('Done', cleared + ' example rows cleared.', ui.ButtonSet.OK);
}

function backUpCopy() {
  var ss = SpreadsheetApp.getActive();
  var file = DriveApp.getFileById(ss.getId());
  var parents = file.getParents();
  var stamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var copy = file.makeCopy('Backup ' + stamp + ' - ' + ss.getName(), parents.hasNext() ? parents.next() : DriveApp.getRootFolder());
  SpreadsheetApp.getUi().alert('Backed up', 'Saved "' + copy.getName() + '" next to this sheet.', SpreadsheetApp.getUi().ButtonSet.OK);
}

// ---------- helpers

function headers_(sheet) {
  var values = sheet.getRange(HEADER_ROW, 1, 1, sheet.getLastColumn()).getDisplayValues()[0];
  var cols = {};
  values.forEach(function (h, i) { if (h && !cols[h]) cols[h] = i + 1; });
  return cols;
}

function childFolder_(parent, name) {
  var found = parent.getFoldersByName(name);
  return found.hasNext() ? found.next() : parent.createFolder(name);
}

function projectRow_(label) {
  var sheet = SpreadsheetApp.getActive().getSheetByName('Project');
  var labels = sheet.getRange(1, 1, sheet.getLastRow(), 1).getDisplayValues();
  for (var i = 0; i < labels.length; i++) if (labels[i][0] === label) return sheet.getRange(i + 1, 2);
  return null;
}

function projectValue_(label) {
  var cell = projectRow_(label);
  return cell ? cell.getDisplayValue().trim() : '';
}

function setProjectValue_(label, value) {
  var cell = projectRow_(label);
  if (cell) cell.setValue(value);
}
