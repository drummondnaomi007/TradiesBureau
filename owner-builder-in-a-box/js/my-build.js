// My Build: project, rooms, selections, notes, documents and photos, saved to this device.
(function () {
  "use strict";

  var KEY = "ob-mybuild";
  var blank = { project: { gate: "G0" }, rooms: [], selections: [], notes: [], docs: [], photos: [] };
  var state = window.OBStore(KEY) || JSON.parse(JSON.stringify(blank));

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
      return true;
    } catch (e) {
      alert("This device is out of storage for My Build. Remove some photos, or back up and clear.");
      return false;
    }
  }
  function $(id) { return document.getElementById(id); }
  function num(v) { var n = parseFloat(v); return isNaN(n) ? 0 : n; }
  function fmt(n, d) { return n.toLocaleString("en-AU", { maximumFractionDigits: d === undefined ? 1 : d }); }
  function money(n) { return "$" + Math.round(n).toLocaleString("en-AU"); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function today() { return new Date().toLocaleDateString("en-AU", { day: "numeric", month: "short", year: "numeric" }); }
  function del(list, i) {
    return '<button class="btn-sm ghost" data-del="' + list + '" data-i="' + i + '" aria-label="Delete" style="padding:2px 8px;">&times;</button>';
  }

  // Project
  function renderProject() {
    var p = state.project;
    document.querySelectorAll("[data-p]").forEach(function (el) {
      if (document.activeElement !== el) el.value = p[el.dataset.p] == null ? "" : p[el.dataset.p];
    });
    $("projTitle").textContent = p.name || "My owner-build";
    var pct = p.budget ? Math.round((num(p.spent) / num(p.budget)) * 100) : 0;
    $("budgetBar").style.width = Math.min(pct, 100) + "%";
    $("budgetBar").style.background = pct > 100 ? "var(--ob-red)" : "";
    $("budgetText").textContent = "Budget used: " + pct + "%" + (p.budget ? " (" + money(num(p.budget) - num(p.spent)) + " left)" : "");
  }
  document.querySelectorAll("[data-p]").forEach(function (el) {
    el.addEventListener("input", function () {
      state.project[el.dataset.p] = el.type === "number" ? num(el.value) : el.value;
      save();
      renderProject();
    });
  });

  // Rooms
  function renderRooms() {
    var list = $("roomList");
    if (!state.rooms.length) {
      list.innerHTML = '<li class="empty">No rooms yet. Add your first one above.</li>';
      $("roomPlan").innerHTML = "";
      $("roomTotals").textContent = "";
      return;
    }
    var tot = { area: 0, wall: 0, skirt: 0 };
    list.innerHTML = state.rooms.map(function (r, i) {
      var area = r.l * r.w;
      var perim = 2 * (r.l + r.w);
      var wall = perim * r.h;
      var tiles = area * 1.1;
      tot.area += area; tot.wall += wall; tot.skirt += perim;
      return "<li><div><strong>" + esc(r.name) + "</strong><div class=\"meta\">" + fmt(r.l, 2) + " × " + fmt(r.w, 2) + " m · ceiling " + fmt(r.h, 2) + " m</div></div>" +
        '<div class="figs"><b>' + fmt(area) + " m²</b><br><span class=\"meta\">walls " + fmt(wall) + " m² · skirting " + fmt(perim) + " m<br>floor tiles +10%: " + fmt(tiles) + " m²</span></div>" +
        del("rooms", i) + "</li>";
    }).join("");

    var max = Math.max.apply(null, state.rooms.map(function (r) { return Math.max(r.l, r.w); })) || 1;
    var scale = 90 / max;
    $("roomPlan").innerHTML = state.rooms.map(function (r) {
      return '<div style="width:' + Math.max(r.l * scale, 26) + "px;height:" + Math.max(r.w * scale, 22) + 'px" title="' + esc(r.name) + '">' + esc(r.name) + "</div>";
    }).join("");
    $("roomTotals").innerHTML = "<b>Total: " + fmt(tot.area) + " m²</b> floor (" + fmt(tot.area / 9.29, 1) + " squares) · " +
      fmt(tot.wall) + " m² walls to paint (one coat, before openings) · " + fmt(tot.skirt) + " m skirting";
  }
  $("roomForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var f = e.target;
    state.rooms.push({ name: f.rname.value.trim(), l: num(f.l.value), w: num(f.w.value), h: num(f.h.value) || 2.55 });
    save();
    f.rname.value = ""; f.l.value = ""; f.w.value = "";
    f.rname.focus();
    renderRooms();
  });

  // Selections
  var STATUS_PILL = { "To choose": "pill-red", "Selected": "pill-amber", "Ordered": "pill-amber", "Delivered": "pill-green", "Installed": "pill-green" };
  function renderSelections() {
    var list = $("selList");
    if (!state.selections.length) { list.innerHTML = '<li class="empty">Nothing selected yet.</li>'; return; }
    var total = 0;
    list.innerHTML = state.selections.map(function (s, i) {
      total += num(s.price);
      return "<li><div><strong>" + esc(s.item) + "</strong> <span class=\"meta\">" + esc(s.room) + "</span><div class=\"meta\">" + esc(s.spec) +
        (s.supplier ? " · " + esc(s.supplier) : "") + "</div></div>" +
        '<div class="figs">' + (s.price ? money(s.price) + "<br>" : "") +
        '<select data-status="' + i + '" aria-label="Status" style="width:auto;padding:4px;font-size:0.8rem;">' +
        Object.keys(STATUS_PILL).map(function (k) { return "<option" + (k === s.status ? " selected" : "") + ">" + k + "</option>"; }).join("") +
        '</select> <span class="pill ' + STATUS_PILL[s.status] + '" style="font-size:0.7rem;">&#9679;</span></div>' + del("selections", i) + "</li>";
    }).join("") + '<li><span class="meta">Total selections</span><b>' + money(total) + "</b></li>";
  }
  $("selForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var f = e.target;
    state.selections.push({
      item: f.item.value.trim(), room: f.room.value.trim(), spec: f.spec.value.trim(),
      supplier: f.supplier.value.trim(), price: num(f.price.value), status: f.status.value
    });
    save();
    f.reset();
    renderSelections();
  });
  $("selList").addEventListener("change", function (e) {
    var i = e.target.dataset.status;
    if (i === undefined) return;
    state.selections[+i].status = e.target.value;
    save();
    renderSelections();
  });

  // Notes
  function renderNotes() {
    var list = $("noteList");
    if (!state.notes.length) { list.innerHTML = '<li class="empty">No notes yet.</li>'; return; }
    list.innerHTML = state.notes.map(function (n, i) {
      return "<li><div>" + (n.ref ? '<span class="tag">' + esc(n.ref) + "</span> " : "") + '<span class="meta">' + esc(n.type) + " · " + esc(n.date) +
        "</span><div>" + esc(n.text) + "</div></div>" + del("notes", i) + "</li>";
    }).join("");
  }
  $("noteForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var f = e.target;
    state.notes.unshift({ ref: f.ref.value.trim(), type: f.type.value, text: f.text.value.trim(), date: today() });
    save();
    f.text.value = "";
    renderNotes();
  });

  // Documents
  function renderDocs() {
    var list = $("docList");
    if (!state.docs.length) { list.innerHTML = '<li class="empty">No documents linked yet.</li>'; return; }
    list.innerHTML = state.docs.map(function (d, i) {
      var safe = /^https?:\/\//i.test(d.url) ? d.url : "";
      return "<li><div><strong>" + (safe ? '<a href="' + esc(safe) + '" target="_blank" rel="noopener">' + esc(d.title) + "</a>" : esc(d.title)) + "</strong>" +
        (d.rev ? ' <span class="tag">Rev ' + esc(d.rev) + "</span>" : "") + '<div class="meta">Added ' + esc(d.date) + "</div></div>" + del("docs", i) + "</li>";
    }).join("");
  }
  $("docForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var f = e.target;
    state.docs.push({ title: f.dtitle.value.trim(), rev: f.rev.value.trim(), url: f.url.value.trim(), date: today() });
    save();
    f.reset();
    renderDocs();
  });

  // Photos: downscaled so they fit in browser storage
  function renderPhotos() {
    $("photoGrid").innerHTML = state.photos.map(function (p, i) {
      return '<figure><img src="' + p.src + '" alt="' + esc(p.label) + '"><figcaption>' + esc(p.label) + "</figcaption>" +
        '<button class="btn-sm ghost" data-del="photos" data-i="' + i + '" aria-label="Delete photo" style="position:absolute;top:2px;right:2px;padding:0 6px;background:#fff;">&times;</button></figure>';
    }).join("") || '<p class="empty">No photos yet.</p>';
  }
  $("photoInput").addEventListener("change", function (e) {
    var file = e.target.files[0];
    if (!file) return;
    var label = prompt("What is this photo of? (e.g. Slab mesh, north side)", "") || file.name;
    var img = new Image();
    var reader = new FileReader();
    reader.onload = function () { img.src = reader.result; };
    img.onload = function () {
      var scale = Math.min(1, 640 / Math.max(img.width, img.height));
      var c = document.createElement("canvas");
      c.width = Math.round(img.width * scale);
      c.height = Math.round(img.height * scale);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      state.photos.unshift({ src: c.toDataURL("image/jpeg", 0.65), label: label + " · " + today() });
      if (!save()) state.photos.shift();
      renderPhotos();
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  });

  // Delete buttons (shared)
  document.addEventListener("click", function (e) {
    var list = e.target.dataset && e.target.dataset.del;
    if (!list) return;
    if (!confirm("Delete this item?")) return;
    state[list].splice(+e.target.dataset.i, 1);
    save();
    renderAll();
  });

  // Backup / restore / clear
  $("exportJson").addEventListener("click", function () {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(state, null, 2)], { type: "application/json" }));
    a.download = (state.project.name || "my-build").replace(/[^a-z0-9]+/gi, "-").toLowerCase() + "-backup.json";
    a.click();
  });
  $("importJson").addEventListener("change", function (e) {
    var file = e.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var data = JSON.parse(reader.result);
        Object.keys(blank).forEach(function (k) { if (!(k in data)) data[k] = blank[k]; });
        state = data;
        save();
        renderAll();
      } catch (err) {
        alert("That file isn't a My Build backup.");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  });
  $("clearAll").addEventListener("click", function () {
    if (!confirm("Clear everything in My Build on this device? Download a backup first if you need one.")) return;
    state = JSON.parse(JSON.stringify(blank));
    save();
    renderAll();
  });

  function renderAll() {
    renderProject();
    renderRooms();
    renderSelections();
    renderNotes();
    renderDocs();
    renderPhotos();
  }
  renderAll();
})();
