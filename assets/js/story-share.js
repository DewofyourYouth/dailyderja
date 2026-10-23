// Instagram story share (layouts/partials/story-share.html) → GA4 `story_share`.
// The link downloads the story card by default. On touch devices that can share
// files it opens the share sheet with the card instead and copies the post link
// for a link sticker. The card is fetched as the button nears the viewport,
// because iOS Safari refuses navigator.share() if the tap waits on a download.
// Desktop browsers can share files too, but their share sheets have no
// Instagram, so share mode is for touch devices only.
(function () {
  var btn = document.querySelector(".dd-story-btn");
  if (!btn) return;

  var track = function (method) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", "story_share", {
      share_method: method,
      page_path: window.location.pathname,
    });
  };

  var canShare = false;
  try {
    canShare =
      !!navigator.canShare &&
      window.matchMedia("(pointer: coarse)").matches &&
      navigator.canShare({ files: [new File([""], "probe.jpg", { type: "image/jpeg" })] });
  } catch (err) {}

  if (!canShare) {
    btn.addEventListener("click", function () { track("download"); });
    return;
  }

  var label = btn.querySelector(".dd-story-label");
  var status = btn.parentElement.querySelector(".dd-story-status");
  label.textContent = "Share to Instagram story";
  var file = null;
  var timer;

  var say = function (text) {
    if (!status) return;
    status.textContent = text;
    clearTimeout(timer);
    timer = setTimeout(function () { status.textContent = ""; }, 6000);
  };

  new IntersectionObserver(function (entries, io) {
    if (!entries.some(function (e) { return e.isIntersecting; })) return;
    io.disconnect();
    fetch(btn.href)
      .then(function (r) { return r.blob(); })
      .then(function (b) {
        file = new File([b], btn.getAttribute("download"), { type: "image/jpeg" });
      })
      .catch(function () {});
  }, { rootMargin: "600px" }).observe(btn);

  btn.addEventListener("click", function (e) {
    if (!file) { track("download"); return; } // not fetched yet: fall back to the download
    e.preventDefault();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(btn.dataset.storyUrl)
        .then(function () { say("Link copied. Paste it into a link sticker."); })
        .catch(function () {});
    }
    navigator.share({ files: [file] })
      .then(function () { track("share"); })
      .catch(function (err) {
        if (err.name !== "AbortError") window.location.href = btn.href;
      });
  });
})();
