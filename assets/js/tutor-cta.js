// Append a "Tutor Recommendations" CTA after likely vocabulary tables,
// and track clicks to the tutor page + platform links on the tutor page.
(function () {
  function trackEvent(name, params) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, params || {});
  }

  function normalize(text) {
    return (text || "").trim().toLowerCase();
  }

  function hasArabicScript(text) {
    // Arabic Unicode block.
    return /[\u0600-\u06FF]/.test(text || "");
  }

  function getHeaderCells(table) {
    const theadHeaders = Array.from(table.querySelectorAll("thead th"));
    if (theadHeaders.length > 0) {
      return theadHeaders;
    }
    const firstRowHeaders = Array.from(
      table.querySelectorAll("tr:first-child th, tr:first-child td"),
    );
    return firstRowHeaders;
  }

  function isVocabTable(table) {
    const headers = getHeaderCells(table).map((cell) =>
      normalize(cell.textContent),
    );
    if (headers.length === 0) return false;

    const hasIPA = headers.some(
      (h) => h.includes("ipa") || h.includes("pronunciation") || h.includes("phonetic"),
    );
    const hasMeaning = headers.some(
      (h) =>
        h.includes("meaning") ||
        h.includes("english") ||
        h.includes("translation") ||
        h.includes("gloss"),
    );
    const hasArabicLike = headers.some(
      (h) => h.includes("arabic") || h.includes("derja") || hasArabicScript(h),
    );

    // Most of your vocab tables have IPA plus meaning/arabic columns.
    return hasIPA && (hasMeaning || hasArabicLike);
  }

  function hasExistingCTA(table) {
    const next = table.nextElementSibling;
    return !!(next && next.classList.contains("tutor-cta"));
  }

  function buildCTA() {
    const wrapper = document.createElement("div");
    wrapper.className = "tutor-cta";

    const link = document.createElement("a");
    link.className = "tutor-cta__link";
    link.href = "/tutors/";
    link.dataset.ctaSource = "vocab_table";
    link.textContent = "Need a tutor? See my recommended tutors →";

    wrapper.appendChild(link);
    return wrapper;
  }

  function addCTAs() {
    const tables = Array.from(
      document.querySelectorAll(".article-content table"),
    );
    tables.forEach((table) => {
      if (!isVocabTable(table)) return;
      if (hasExistingCTA(table)) return;
      table.insertAdjacentElement("afterend", buildCTA());
    });
  }

  function trackTutorPageClicks() {
    const links = Array.from(document.querySelectorAll('a[href^="/tutors/"]'));
    links.forEach((link) => {
      link.addEventListener("click", () => {
        trackEvent("tutor_page_click", {
          cta_source: link.dataset.ctaSource || "unknown",
          link_text: (link.textContent || "").trim().slice(0, 80),
          link_url: link.getAttribute("href") || "/tutors/",
        });
      });
    });
  }

  function platformFromHost(host) {
    const h = (host || "").toLowerCase();
    if (h.includes("preply")) return "preply";
    if (h.includes("italki")) return "italki";
    if (h.includes("verbling")) return "verbling";
    if (h.includes("amazingtalker")) return "amazingtalker";
    if (h.includes("superprof")) return "superprof";
    return "";
  }

  function trackTutorPlatformClicks() {
    const onTutorPage =
      window.location.pathname === "/tutors/" ||
      window.location.pathname.startsWith("/tutors/");
    if (!onTutorPage) return;

    const links = Array.from(
      document.querySelectorAll(".article-content a[href]"),
    );
    links.forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (!href.startsWith("http://") && !href.startsWith("https://")) return;

      let platform = "";
      try {
        platform = platformFromHost(new URL(href).host);
      } catch (e) {
        platform = "";
      }
      if (!platform) return;

      link.addEventListener("click", () => {
        trackEvent("tutor_platform_click", {
          platform,
          link_text: (link.textContent || "").trim().slice(0, 80),
          link_url: href,
        });
      });
    });
  }

  function init() {
    addCTAs();
    trackTutorPageClicks();
    trackTutorPlatformClicks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
