// The trade picker on the home page, and the side rail on the long pages.
// The picker's rules come from js/trade-data.js, which is written from the
// app's own rule pack by scripts/build-from-app.mjs.
document.addEventListener("DOMContentLoaded", function () {
  var PORTAL = window.TB_PORTAL || "https://portal.tradiesbureau.com";

  // ---- Side rail: mark the section being read (trades.html, guide.html)
  var rail = document.querySelector(".rail");
  var spied = document.querySelectorAll("[data-spy]");
  if (rail && spied.length && "IntersectionObserver" in window) {
    var links = {};
    rail.querySelectorAll('a[href^="#"]').forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var current = null;
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var link = links[e.target.id];
        if (!link || link === current) return;
        if (current) current.removeAttribute("aria-current");
        link.setAttribute("aria-current", "true");
        current = link;
        // Keep the marked link in view inside the rail (it scrolls sideways on a phone).
        var list = rail.querySelector("ul");
        if (list && list.scrollWidth > list.clientWidth) {
          list.scrollLeft = link.offsetLeft - list.clientWidth / 2 + link.offsetWidth / 2;
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    spied.forEach(function (el) { seen.observe(el); });
  }

  // ---- Trade picker
  var root = document.querySelector("[data-trade-demo]");
  var data = window.TB_TRADES;
  if (!root || !data) return;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  var fallback = root.querySelector("[data-trade-fallback]");
  if (fallback) fallback.hidden = true;

  var tabs = el("div", "trade-tabs");
  tabs.setAttribute("role", "tablist");
  tabs.setAttribute("aria-label", "Trades");
  var sheet = el("div", "trade-sheet");
  sheet.setAttribute("role", "tabpanel");
  sheet.id = "trade-sheet";
  var asks = el("div", "trade-asks");
  var result = el("div", "trade-result");
  sheet.appendChild(asks);
  sheet.appendChild(result);
  root.appendChild(tabs);
  root.appendChild(sheet);

  var ticked = {}; // trade key -> { question key: true }
  var active = null;

  function tagFor(r) {
    if (r.law) return r.optional ? "By law, if it applies" : "Required by law";
    return r.optional ? "Optional" : "Usually asked for";
  }

  function codesFor(trade) {
    var codes = trade.always.slice();
    trade.questions.forEach(function (q) {
      if (!ticked[trade.key][q.key]) return;
      q.adds.forEach(function (c) { if (codes.indexOf(c) < 0) codes.push(c); });
    });
    return codes;
  }

  function drawResult(trade, fresh) {
    var codes = codesFor(trade);
    var law = codes.filter(function (c) { return data.requirements[c].law && !data.requirements[c].optional; }).length;
    result.textContent = "";
    var head = el("div", "trade-result-head");
    var count = el("p", "trade-count");
    count.setAttribute("aria-live", "polite");
    count.appendChild(el("strong", "", String(codes.length)));
    count.appendChild(document.createTextNode(" things to keep track of, " + law + " of them required by law"));
    head.appendChild(count);
    result.appendChild(head);

    var scroller = el("div", "trade-scroll");
    scroller.tabIndex = 0;
    scroller.setAttribute("role", "region");
    scroller.setAttribute("aria-label", "What applies to a " + trade.name.toLowerCase() + " business. Scrollable list.");
    var firstFresh = null;
    data.groups.forEach(function (g) {
      var items = codes.filter(function (c) { return data.requirements[c].group === g.key; });
      if (!items.length) return;
      scroller.appendChild(el("h4", "", g.label));
      var ul = el("ul", "req-list");
      items.forEach(function (c) {
        var r = data.requirements[c];
        var li = el("li", "req " + (r.law ? "req-law" : "req-asked"));
        var h = el("div", "req-head");
        h.appendChild(el("span", "req-name", r.name));
        h.appendChild(el("span", "req-tag", tagFor(r)));
        li.appendChild(h);
        if (r.why) li.appendChild(el("p", "", r.why));
        if (fresh && fresh.indexOf(c) >= 0) {
          li.classList.add("req-new");
          if (!firstFresh) firstFresh = li;
        }
        ul.appendChild(li);
      });
      scroller.appendChild(ul);
    });
    result.appendChild(scroller);
    if (firstFresh) scroller.scrollTop = Math.max(0, firstFresh.offsetTop - scroller.offsetTop - 48);

    var path = "/check?trade=" + encodeURIComponent(trade.key);
    var foot = el("div", "trade-result-foot");
    var go = el("a", "btn btn-primary", "Check your own business");
    go.href = PORTAL + path;
    var more = el("a", "text-link", "Read the full list");
    more.href = "trades.html#" + trade.key.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
    foot.appendChild(go);
    foot.appendChild(more);
    result.appendChild(foot);
  }

  function drawAsks(trade) {
    asks.textContent = "";
    asks.appendChild(el("h3", "", trade.name));
    if (!trade.questions.length) return;
    var set = el("fieldset");
    set.appendChild(el("legend", "", "Tick what you take on"));
    trade.questions.forEach(function (q, i) {
      var id = "ask-" + trade.key + "-" + i;
      var label = el("label", "trade-ask");
      label.htmlFor = id;
      var box = el("input");
      box.type = "checkbox";
      box.id = id;
      box.checked = !!ticked[trade.key][q.key];
      box.addEventListener("change", function () {
        var before = codesFor(trade);
        ticked[trade.key][q.key] = box.checked;
        var added = codesFor(trade).filter(function (c) { return before.indexOf(c) < 0; });
        drawResult(trade, added);
      });
      label.appendChild(box);
      var text = el("span", "", q.label);
      if (q.help) text.appendChild(el("small", "", q.help));
      label.appendChild(text);
      set.appendChild(label);
    });
    asks.appendChild(set);
  }

  function select(trade, focus) {
    active = trade;
    Array.prototype.forEach.call(tabs.children, function (b) {
      var on = b.dataset.trade === trade.key;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.tabIndex = on ? 0 : -1;
      if (on && focus) b.focus();
      if (on && tabs.scrollWidth > tabs.clientWidth) {
        tabs.scrollLeft = b.offsetLeft - tabs.clientWidth / 2 + b.offsetWidth / 2;
      }
    });
    sheet.setAttribute("aria-labelledby", "trade-tab-" + trade.key);
    drawAsks(trade);
    drawResult(trade, null);
  }

  data.trades.forEach(function (trade, i) {
    ticked[trade.key] = {};
    trade.questions.forEach(function (q) { if (q.on) ticked[trade.key][q.key] = true; });
    var b = el("button", "trade-tab", trade.name);
    b.type = "button";
    b.id = "trade-tab-" + trade.key;
    b.dataset.trade = trade.key;
    b.setAttribute("role", "tab");
    b.setAttribute("aria-controls", "trade-sheet");
    b.addEventListener("click", function () { select(trade, false); });
    b.addEventListener("keydown", function (e) {
      var n = data.trades.length;
      var to = e.key === "ArrowRight" ? (i + 1) % n : e.key === "ArrowLeft" ? (i - 1 + n) % n : e.key === "Home" ? 0 : e.key === "End" ? n - 1 : -1;
      if (to >= 0) { e.preventDefault(); select(data.trades[to], true); }
    });
    tabs.appendChild(b);
  });

  select(data.trades[0], false);
});
