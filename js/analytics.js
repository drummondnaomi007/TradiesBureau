// Visitor statistics (Google Analytics 4).
//
// Paste the Measurement ID from Google Analytics (Admin → Data streams →
// your web stream, it looks like G-XXXXXXXXXX) between the quotes below.
// Until then nothing loads and nothing is counted. It never runs on
// localhost, so testing doesn't count as visits.
//
// Counted as well as page views:
//   generate_lead   a message sent from the contact form (js/enquiry.js)
//   contact         a tap on the phone number (links with data-track="phone")
(function () {
  "use strict";

  var MEASUREMENT_ID = "G-GF6MK11613";

  window.tbTrack = function () {};
  var host = location.hostname;
  if (!/^G-[A-Z0-9]+$/.test(MEASUREMENT_ID) || host === "localhost" || host === "127.0.0.1" || location.protocol === "file:") return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag("js", new Date());
  gtag("config", MEASUREMENT_ID);
  window.tbTrack = function (name, params) { gtag("event", name, params || {}); };

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + MEASUREMENT_ID;
  document.head.appendChild(s);

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[data-track="phone"]');
    if (a) window.tbTrack("contact", { method: "phone" });
  });
})();
