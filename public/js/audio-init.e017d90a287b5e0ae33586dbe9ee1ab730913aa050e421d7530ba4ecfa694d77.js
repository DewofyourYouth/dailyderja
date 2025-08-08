document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('audio.js-player').forEach(el => {
    if (!el.dataset.plyr) new Plyr(el, {
      controls: ['play','progress','current-time', 'download', "volume"],
      seekTime: 5
    });
  });
});
