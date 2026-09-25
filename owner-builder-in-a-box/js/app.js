// Owner Builder in a Box — shared page behaviour
(function () {
  "use strict";

  function store(key, value) {
    try {
      if (value === undefined) return JSON.parse(localStorage.getItem(key) || "null");
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      return null;
    }
  }
  window.OBStore = store;

  document.addEventListener("DOMContentLoaded", function () {
    var yearEl = document.querySelector("[data-year]");
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    var activeTab = document.querySelector(".hub-nav a.active");
    if (activeTab && activeTab.parentNode.parentNode.scrollWidth > window.innerWidth) {
      activeTab.parentNode.parentNode.scrollLeft = activeTab.offsetLeft - 16;
    }

    // Persistent checklists: <ul class="check-list" data-list="key"> with checkbox inputs
    var boxes = document.querySelectorAll(".check-list input[type=checkbox][data-id]");
    if (boxes.length) {
      var saved = store("ob-checklist") || {};
      var bar = document.querySelector(".progress-bar span");
      var text = document.querySelector(".progress-text");
      var update = function () {
        var done = 0;
        boxes.forEach(function (b) { if (b.checked) done++; });
        var pct = Math.round((done / boxes.length) * 100);
        if (bar) bar.style.width = pct + "%";
        if (text) text.textContent = done + " of " + boxes.length + " done (" + pct + "%)";
      };
      boxes.forEach(function (b) {
        b.checked = !!saved[b.dataset.id];
        b.addEventListener("change", function () {
          saved[b.dataset.id] = b.checked;
          store("ob-checklist", saved);
          update();
        });
      });
      var reset = document.querySelector("[data-reset-checklist]");
      if (reset) reset.addEventListener("click", function () {
        if (!confirm("Clear all ticks on this checklist?")) return;
        saved = {};
        store("ob-checklist", saved);
        boxes.forEach(function (b) { b.checked = false; });
        update();
      });
      update();
    }

    // FAQ search + category filter
    var search = document.querySelector(".faq-search");
    var chips = document.querySelectorAll(".chip[data-cat]");
    var items = document.querySelectorAll("details.qa");
    if (search || chips.length) {
      var cat = "all";
      var none = document.querySelector(".no-results");
      var apply = function () {
        var q = (search ? search.value : "").trim().toLowerCase();
        var shown = 0;
        items.forEach(function (d) {
          var okCat = cat === "all" || d.dataset.cat === cat;
          var okQ = !q || d.textContent.toLowerCase().indexOf(q) !== -1;
          d.style.display = okCat && okQ ? "" : "none";
          if (okCat && okQ) shown++;
          if (q && okCat && okQ) d.open = true;
        });
        document.querySelectorAll(".faq-group").forEach(function (g) {
          var any = Array.prototype.some.call(g.querySelectorAll("details.qa"), function (d) { return d.style.display !== "none"; });
          g.style.display = any ? "" : "none";
        });
        if (none) none.style.display = shown ? "none" : "block";
      };
      if (search) search.addEventListener("input", apply);
      chips.forEach(function (c) {
        c.addEventListener("click", function () {
          chips.forEach(function (x) { x.classList.remove("active"); });
          c.classList.add("active");
          cat = c.dataset.cat;
          apply();
        });
      });
      var expand = document.querySelector("[data-expand-all]");
      if (expand) expand.addEventListener("click", function () {
        var open = expand.dataset.state !== "open";
        items.forEach(function (d) { if (d.style.display !== "none") d.open = open; });
        expand.dataset.state = open ? "open" : "closed";
        expand.textContent = open ? "Collapse all" : "Expand all";
      });
    }

    if ("serviceWorker" in navigator && location.protocol === "https:") {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    }
  });
})();
