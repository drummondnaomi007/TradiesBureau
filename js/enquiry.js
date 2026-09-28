// The contact form: sends the message to the Tradies Bureau app, which saves
// it for us to read. With JavaScript it's sent in the background and the
// thank-you shows in place. Without it, the form posts to the app directly,
// which sends the visitor back here with ?sent=1 (or ?error=1).
(function () {
  "use strict";

  var form = document.getElementById("enquiry-form");
  if (!form) return;
  var sent = document.querySelector("[data-enquiry-sent]");
  var failed = document.querySelector("[data-enquiry-error]");
  var failedText = document.querySelector("[data-enquiry-error-text]");
  var defaultError = failedText ? failedText.innerHTML : "";
  var button = form.querySelector('button[type="submit"]');

  function show(el) {
    el.hidden = false;
    el.focus();
  }

  function succeeded() {
    form.hidden = true;
    failed.hidden = true;
    show(sent);
    if (window.tbTrack) window.tbTrack("generate_lead", { form: "contact" });
  }

  function error(message) {
    if (failedText) {
      if (message) failedText.textContent = message;
      else failedText.innerHTML = defaultError;
    }
    show(failed);
  }

  // Back from a plain (no JavaScript) form post.
  var q = new URLSearchParams(location.search);
  if (q.get("sent") === "1") succeeded();
  else if (q.get("error") === "1") error();

  form.addEventListener("submit", function (e) {
    if (!window.fetch) return; // very old browser: post the form normally
    e.preventDefault();
    var data = {};
    new FormData(form).forEach(function (value, key) { data[key] = value; });
    button.disabled = true;
    button.textContent = "Sending…";
    failed.hidden = true;
    fetch((window.TB_PORTAL || "https://portal.tradiesbureau.com") + "/api/enquiries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (body) {
          if (res.ok) succeeded();
          else error(body.error);
        });
      })
      .catch(function () { error(); })
      .then(function () {
        button.disabled = false;
        button.textContent = "Send message";
      });
  });
})();
