// Tender comparison tool: compliance gates, quote levelling and weighted scoring.
(function () {
  "use strict";

  var KEY = "ob-tenders";

  var GATES = [
    { id: "reg", label: "Registered / licensed" },
    { id: "ins", label: "Insurance current" },
    { id: "abn", label: "ABN verified" },
    { id: "swms", label: "SWMS provided" },
    { id: "scope", label: "Scope conforms" }
  ];

  var PRICE_ROWS = [
    { id: "price", label: "Quoted price (inc. GST)" },
    { id: "excl", label: "+ Cost of exclusions" },
    { id: "ps", label: "± Provisional sum adj." },
    { id: "risk", label: "+ Risk allowance" }
  ];

  var CRITERIA = [
    { id: "exp", label: "Experience & references" },
    { id: "prog", label: "Program / availability" },
    { id: "qual", label: "Quality of past work" },
    { id: "comm", label: "Communication" },
    { id: "warr", label: "Warranty & defects terms" }
  ];

  var COLORS = {
    price: "#0B6E8F", exp: "#1B8FA8", prog: "#2D5A8C", qual: "#1f7a4d", comm: "#e0a020", warr: "#8a6bbf"
  };

  function tenderer(name, price, excl, ps, risk, scores, gates) {
    return {
      name: name, price: price, excl: excl, ps: ps, risk: risk,
      scores: scores,
      gates: gates || { reg: true, ins: true, abn: true, swms: true, scope: true }
    };
  }

  function example() {
    return {
      current: "roof",
      packages: {
        roof: {
          name: "Roofing: supply & install Colorbond, gutters & downpipes",
          budget: 38000,
          weights: { price: 50, exp: 15, prog: 15, qual: 10, comm: 5, warr: 5 },
          tenderers: [
            tenderer("Summit Roofing", 32500, 1800, 0, 500, { exp: 8, prog: 6, qual: 8, comm: 7, warr: 7 }),
            tenderer("Ridgeline Metal Roofs", 36900, 0, 0, 0, { exp: 9, prog: 8, qual: 9, comm: 9, warr: 8 }),
            tenderer("Budget Roofs Co", 27900, 3500, 1200, 2000, { exp: 5, prog: 9, qual: 5, comm: 4, warr: 5 },
              { reg: true, ins: false, abn: true, swms: true, scope: true })
          ]
        }
      }
    };
  }

  var state = window.OBStore(KEY) || example();

  function save() { window.OBStore(KEY, state); }
  function pkg() { return state.packages[state.current]; }
  function num(v) { var n = parseFloat(v); return isNaN(n) ? 0 : n; }
  function money(n) { return "$" + Math.round(n).toLocaleString("en-AU"); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function evaluate(p) {
    var rows = p.tenderers.map(function (t, i) {
      var levelled = num(t.price) + num(t.excl) + num(t.ps) + num(t.risk);
      var compliant = GATES.every(function (g) { return t.gates[g.id]; });
      return { t: t, i: i, levelled: levelled, compliant: compliant && num(t.price) > 0 };
    });
    var ok = rows.filter(function (r) { return r.compliant; });
    var lowest = ok.length ? Math.min.apply(null, ok.map(function (r) { return r.levelled; })) : 0;
    var sorted = ok.map(function (r) { return r.levelled; }).sort(function (a, b) { return a - b; });
    var median = sorted.length ? (sorted.length % 2 ? sorted[(sorted.length - 1) / 2]
      : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2) : 0;

    rows.forEach(function (r) {
      r.parts = {};
      r.parts.price = r.compliant && r.levelled > 0 ? (lowest / r.levelled) * 10 * p.weights.price / 10 : 0;
      CRITERIA.forEach(function (c) {
        r.parts[c.id] = r.compliant ? num(r.t.scores[c.id]) * p.weights[c.id] / 10 : 0;
      });
      r.total = 0;
      Object.keys(r.parts).forEach(function (k) { r.total += r.parts[k]; });
      r.low = r.compliant && sorted.length >= 2 && r.levelled < median * 0.85;
    });
    rows.sort(function (a, b) {
      if (a.compliant !== b.compliant) return a.compliant ? -1 : 1;
      return b.total - a.total;
    });
    return { rows: rows, lowest: lowest, median: median };
  }

  // ---------- Rendering ----------

  var table = document.getElementById("tenderTable");

  function renderPackages() {
    var sel = document.getElementById("pkgSelect");
    sel.innerHTML = Object.keys(state.packages).map(function (id) {
      return '<option value="' + id + '"' + (id === state.current ? " selected" : "") + ">" + esc(state.packages[id].name) + "</option>";
    }).join("");
    document.getElementById("pkgBudget").value = pkg().budget || "";
  }

  function renderTable() {
    var p = pkg();
    var ts = p.tenderers;
    var h = "<thead><tr><th></th>";
    ts.forEach(function (t, i) {
      h += '<th><input type="text" data-i="' + i + '" data-f="name" value="' + esc(t.name) + '" aria-label="Tenderer name">' +
        ' <button class="btn-sm ghost no-print" data-remove="' + i + '" title="Remove tenderer" style="padding:2px 6px;">&times;</button></th>';
    });
    h += "</tr></thead><tbody>";

    h += '<tr><th class="group" colspan="' + (ts.length + 1) + '">Compliance gates (pass / fail)</th></tr>';
    GATES.forEach(function (g) {
      h += '<tr><td class="rowhead">' + g.label + "</td>";
      ts.forEach(function (t, i) {
        h += '<td style="text-align:center"><input type="checkbox" data-i="' + i + '" data-gate="' + g.id + '"' + (t.gates[g.id] ? " checked" : "") + ' aria-label="' + g.label + '"></td>';
      });
      h += "</tr>";
    });

    h += '<tr><th class="group" colspan="' + (ts.length + 1) + '">Price levelling ($)</th></tr>';
    PRICE_ROWS.forEach(function (r) {
      h += '<tr><td class="rowhead">' + r.label + "</td>";
      ts.forEach(function (t, i) {
        h += '<td><input type="number" step="100" data-i="' + i + '" data-f="' + r.id + '" value="' + (t[r.id] || 0) + '" aria-label="' + r.label + '"></td>';
      });
      h += "</tr>";
    });
    h += '<tr><td class="rowhead">= Levelled price</td>';
    ts.forEach(function (t, i) { h += '<td class="num" data-levelled="' + i + '"></td>'; });
    h += "</tr>";

    h += '<tr><th class="group" colspan="' + (ts.length + 1) + '">Non-price scores (0–10)</th></tr>';
    CRITERIA.forEach(function (c) {
      h += '<tr><td class="rowhead">' + c.label + "</td>";
      ts.forEach(function (t, i) {
        h += '<td><input type="number" min="0" max="10" step="1" data-i="' + i + '" data-score="' + c.id + '" value="' + (t.scores[c.id] || 0) + '" aria-label="' + c.label + '"></td>';
      });
      h += "</tr>";
    });
    h += "</tbody>";
    table.innerHTML = h;
  }

  function renderWeights() {
    var p = pkg();
    var all = [{ id: "price", label: "Price (levelled)" }].concat(CRITERIA);
    document.getElementById("weights").innerHTML = all.map(function (c) {
      return '<label><span style="font-size:0.82rem;font-weight:600;"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:' + COLORS[c.id] + ';margin-right:6px;"></i>' +
        c.label + ': <b data-wlabel="' + c.id + '">' + p.weights[c.id] + "%</b></span>" +
        '<input type="range" min="0" max="100" step="5" data-w="' + c.id + '" value="' + p.weights[c.id] + '"></label>';
    }).join("");
  }

  function renderResults() {
    var p = pkg();
    var ev = evaluate(p);
    var wsum = 0;
    Object.keys(p.weights).forEach(function (k) { wsum += p.weights[k]; });
    var wt = document.getElementById("weightTotal");
    wt.textContent = "Total weight: " + wsum + "%" + (wsum === 100 ? " ✓" : ". Adjust the sliders so the total is 100%.");
    wt.className = "weight-total" + (wsum === 100 ? "" : " bad");

    ev.rows.forEach(function (r) {
      var cell = table.querySelector('[data-levelled="' + r.i + '"]');
      if (cell) cell.innerHTML = "<b>" + money(r.levelled) + "</b>";
    });

    var rank = 0;
    document.getElementById("results").innerHTML = ev.rows.map(function (r) {
      var cls = "result-card";
      var badge;
      if (!r.compliant) { cls += " fail"; badge = "Excluded"; }
      else { rank++; badge = "#" + rank; if (rank === 1) cls += " winner"; }
      var failed = GATES.filter(function (g) { return !r.t.gates[g.id]; }).map(function (g) { return g.label; });
      var budgetLine = p.budget ? '<dt>vs budget</dt><dd style="color:' + (r.levelled > p.budget ? "var(--ob-red)" : "var(--ob-green)") + '">' +
        (r.levelled > p.budget ? "+" : "−") + money(Math.abs(r.levelled - p.budget)) + "</dd>" : "";
      return '<div class="' + cls + '"><span class="rank">' + badge + "</span>" +
        "<h4>" + esc(r.t.name || "Unnamed") + "</h4>" +
        (r.compliant ? '<div class="score">' + r.total.toFixed(1) + '<span style="font-size:1rem;color:var(--muted);font-weight:600;"> / 100</span></div>'
          : '<p style="margin:8px 0;color:var(--ob-red);font-weight:600;">Failed: ' + esc(failed.join(", ") || "no price") + "</p>") +
        (r.low ? '<span class="pill pill-amber">Check scope: well under median</span>' : "") +
        "<dl><dt>Quoted</dt><dd>" + money(num(r.t.price)) + "</dd>" +
        "<dt>Levelled</dt><dd>" + money(r.levelled) + "</dd>" + budgetLine +
        "<dt>Price score</dt><dd>" + (r.compliant && p.weights.price ? (r.parts.price * 10 / p.weights.price).toFixed(1) + " / 10" : "–") + "</dd></dl></div>";
    }).join("");

    var ok = ev.rows.filter(function (r) { return r.compliant; });
    var rec = document.getElementById("recommendation");
    if (!ok.length) {
      rec.className = "callout danger";
      rec.innerHTML = "<strong>No compliant tenders.</strong><p>Every tenderer failed at least one gate. Chase the missing paperwork or invite more trades.</p>";
    } else {
      var w = ok[0];
      var cheapest = ok.slice().sort(function (a, b) { return a.levelled - b.levelled; })[0];
      var msg = "<strong>Recommended: " + esc(w.t.name) + "</strong><p>Highest weighted score (" + w.total.toFixed(1) + "/100) with a levelled price of " + money(w.levelled) + ".";
      if (cheapest !== w) msg += " That's " + money(w.levelled - cheapest.levelled) + " more than the cheapest compliant quote (" + esc(cheapest.t.name) + "), but it scores better on the non-price criteria.";
      if (ok.length > 1) msg += " Margin over #2: " + (w.total - ok[1].total).toFixed(1) + " points" + (w.total - ok[1].total < 3 ? ". That's close, so ask both for clarifications before deciding." : ".");
      var excluded = ev.rows.length - ok.length;
      if (excluded) msg += " " + excluded + " tender" + (excluded > 1 ? "s" : "") + " excluded on compliance.";
      if (wsum !== 100) msg += " <b>Weights don't add to 100%.</b>";
      msg += "</p>";
      rec.className = "callout " + (wsum === 100 ? "ok" : "warn");
      rec.innerHTML = msg;
    }

    // Stacked contribution chart
    var keys = ["price"].concat(CRITERIA.map(function (c) { return c.id; }));
    var html = '<h4 style="margin:0 0 10px;color:var(--navy-900);">Where each score comes from</h4>';
    ok.forEach(function (r) {
      html += '<div class="bar-row"><span>' + esc(r.t.name) + '</span><div class="bar-track">';
      keys.forEach(function (k) {
        html += '<span title="' + k + ": " + r.parts[k].toFixed(1) + '" style="width:' + r.parts[k] + "%;background:" + COLORS[k] + '"></span>';
      });
      html += "</div><b>" + r.total.toFixed(1) + "</b></div>";
    });
    html += '<div class="legend">' + keys.map(function (k) {
      var label = k === "price" ? "Price" : CRITERIA.filter(function (c) { return c.id === k; })[0].label;
      return '<span><i style="background:' + COLORS[k] + '"></i>' + label + "</span>";
    }).join("") + "</div>";
    document.getElementById("chart").innerHTML = ok.length ? html : "";
  }

  function renderAll() {
    renderPackages();
    renderTable();
    renderWeights();
    renderResults();
  }

  // ---------- Events ----------

  table.addEventListener("input", function (e) {
    var el = e.target;
    var t = pkg().tenderers[+el.dataset.i];
    if (!t) return;
    if (el.dataset.gate) t.gates[el.dataset.gate] = el.checked;
    else if (el.dataset.score) t.scores[el.dataset.score] = Math.max(0, Math.min(10, num(el.value)));
    else if (el.dataset.f === "name") t.name = el.value;
    else if (el.dataset.f) t[el.dataset.f] = num(el.value);
    save();
    renderResults();
  });

  table.addEventListener("click", function (e) {
    var i = e.target.dataset.remove;
    if (i === undefined) return;
    if (!confirm("Remove " + (pkg().tenderers[+i].name || "this tenderer") + "?")) return;
    pkg().tenderers.splice(+i, 1);
    save();
    renderTable();
    renderResults();
  });

  document.getElementById("weights").addEventListener("input", function (e) {
    var k = e.target.dataset.w;
    if (!k) return;
    pkg().weights[k] = num(e.target.value);
    document.querySelector('[data-wlabel="' + k + '"]').textContent = e.target.value + "%";
    save();
    renderResults();
  });

  document.getElementById("addTenderer").addEventListener("click", function () {
    if (pkg().tenderers.length >= 8) { alert("Eight tenderers is plenty for one package."); return; }
    pkg().tenderers.push(tenderer("Tenderer " + (pkg().tenderers.length + 1), 0, 0, 0, 0,
      { exp: 5, prog: 5, qual: 5, comm: 5, warr: 5 }, { reg: false, ins: false, abn: false, swms: false, scope: false }));
    save();
    renderTable();
    renderResults();
  });

  document.getElementById("pkgSelect").addEventListener("change", function (e) {
    state.current = e.target.value;
    save();
    renderAll();
  });

  document.getElementById("pkgBudget").addEventListener("input", function (e) {
    pkg().budget = num(e.target.value);
    save();
    renderResults();
  });

  document.getElementById("pkgNew").addEventListener("click", function () {
    var name = prompt("Trade package name (e.g. Electrical: rough-in & fit-off)");
    if (!name) return;
    var id = "p" + Date.now();
    state.packages[id] = {
      name: name, budget: 0,
      weights: { price: 50, exp: 15, prog: 15, qual: 10, comm: 5, warr: 5 },
      tenderers: [1, 2, 3].map(function (n) {
        return tenderer("Tenderer " + n, 0, 0, 0, 0, { exp: 5, prog: 5, qual: 5, comm: 5, warr: 5 },
          { reg: false, ins: false, abn: false, swms: false, scope: false });
      })
    };
    state.current = id;
    save();
    renderAll();
  });

  document.getElementById("pkgRename").addEventListener("click", function () {
    var name = prompt("Rename package", pkg().name);
    if (!name) return;
    pkg().name = name;
    save();
    renderPackages();
  });

  document.getElementById("pkgDelete").addEventListener("click", function () {
    if (Object.keys(state.packages).length === 1) { alert("You need at least one package. Use Reset to start over."); return; }
    if (!confirm("Delete package \"" + pkg().name + "\"?")) return;
    delete state.packages[state.current];
    state.current = Object.keys(state.packages)[0];
    save();
    renderAll();
  });

  document.getElementById("resetExample").addEventListener("click", function () {
    if (!confirm("Replace all your packages with the example?")) return;
    state = example();
    save();
    renderAll();
  });

  document.getElementById("exportCsv").addEventListener("click", function () {
    var p = pkg();
    var ev = evaluate(p);
    var head = ["Tenderer", "Compliant"].concat(GATES.map(function (g) { return g.label; }))
      .concat(PRICE_ROWS.map(function (r) { return r.label; }))
      .concat(["Levelled price"]).concat(CRITERIA.map(function (c) { return c.label; })).concat(["Weighted score"]);
    var lines = [head];
    ev.rows.forEach(function (r) {
      lines.push([r.t.name, r.compliant ? "Yes" : "No"]
        .concat(GATES.map(function (g) { return r.t.gates[g.id] ? "Pass" : "Fail"; }))
        .concat(PRICE_ROWS.map(function (x) { return num(r.t[x.id]); }))
        .concat([Math.round(r.levelled)])
        .concat(CRITERIA.map(function (c) { return num(r.t.scores[c.id]); }))
        .concat([r.compliant ? r.total.toFixed(1) : "Excluded"]));
    });
    var csv = lines.map(function (l) {
      return l.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(",");
    }).join("\n");
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = p.name.replace(/[^a-z0-9]+/gi, "-").toLowerCase() + "-tender-comparison.csv";
    a.click();
  });

  renderAll();
})();
