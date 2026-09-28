// Links from the marketing site into the Tradies Bureau app (the portal).
//
// Every portal link is written in the HTML with its full live address, so it
// works with no JavaScript:
//   <a href="https://portal.tradiesbureau.com/check" data-portal="/check">
// This script only changes the address when you're testing locally: on
// localhost it points the links at the app running on port 8080 (the port the
// app listens on, locally and on Railway). Add ?portal=http://localhost:3000
// to the page address to test against a different local port.
//
// The override only works on localhost, so nobody can send a link to the live
// site that points its sign-in buttons somewhere else.
(function () {
  "use strict";

  // Lets the CSS know scripts run (screen tabs show only then).
  document.documentElement.classList.add("js");

  var LIVE = "https://portal.tradiesbureau.com";
  var LOCAL = "http://localhost:8080";

  var host = location.hostname;
  var isLocal = host === "localhost" || host === "127.0.0.1" || location.protocol === "file:";
  var base = LIVE;

  if (isLocal) {
    base = LOCAL;
    try {
      var asked = new URLSearchParams(location.search).get("portal");
      if (asked && /^http:\/\/(localhost|127\.0\.0\.1)(:\d{2,5})?$/.test(asked.replace(/\/$/, ""))) {
        sessionStorage.setItem("tb-portal", asked.replace(/\/$/, ""));
      }
      base = sessionStorage.getItem("tb-portal") || LOCAL;
    } catch (e) {
      base = LOCAL;
    }
  }

  window.TB_PORTAL = base;
  if (base === LIVE) return;

  function rewrite() {
    document.querySelectorAll("a[data-portal]").forEach(function (a) {
      a.href = base + a.getAttribute("data-portal");
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", rewrite);
  else rewrite();
})();
