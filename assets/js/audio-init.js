document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('audio.js-player').forEach(el => {
    if (!el.dataset.plyr) {
      const player = new Plyr(el, {
        controls: ['play', 'progress', 'current-time', 'volume', 'download'],
        seekTime: 5
      });
      player.on('play', () => {
        if (typeof window.gtag !== 'function') return;
        const src = el.currentSrc || el.querySelector('source')?.src || '';
        const file = src.split('/').pop();
        window.gtag('event', 'audio_play', {
          audio_file: file,
          page_path: window.location.pathname
        });
      });
    }
  });
});
