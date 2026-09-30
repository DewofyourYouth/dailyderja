// Onward-reading clicks → GA4 `recommendation_click`.
// Covers every block marked with data-rec: curated "read it in context" (context),
// same-dialect related posts (related) and the learning-path pickers (path).
// One delegated listener = one event per click. Sends paths only: no query
// strings, no link text, nothing typed by the reader.
(function () {
  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest("a[href]");
    if (!link) return;
    var block = link.closest("[data-rec]");
    if (!block || typeof window.gtag !== "function") return;
    var url;
    try {
      url = new URL(link.getAttribute("href"), window.location.href);
    } catch (err) {
      return;
    }
    if (url.origin !== window.location.origin) return;
    window.gtag("event", "recommendation_click", {
      rec_type: block.dataset.rec,
      rec_location: block.dataset.recLocation || "article",
      source_path: window.location.pathname,
      destination_path: url.pathname,
      transport_type: "beacon"
    });
  });
})();
