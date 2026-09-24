// Track clicks on the "join the community" WhatsApp/Telegram/Discord buttons
// rendered by the join-channels shortcode (layouts/shortcodes/join-channels.html).
(function () {
  function trackEvent(name, params) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, params || {});
  }

  function platformFromClass(el) {
    if (el.classList.contains("jc-btn--whatsapp")) return "whatsapp";
    if (el.classList.contains("jc-btn--telegram")) return "telegram";
    if (el.classList.contains("jc-btn--discord")) return "discord";
    return "unknown";
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest(".jc-btn");
    if (!link) return;
    trackEvent("community_click", {
      platform: platformFromClass(link),
      link_url: link.getAttribute("href") || "",
      page_path: window.location.pathname,
    });
  });
})();
