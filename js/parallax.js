/**
 * Light parallax: <img data-parallax="0.12"> drifts vertically inside its overflow-hidden
 * wrapper while the page scrolls. The value is the share of the wrapper height it travels.
 * Uses the `translate` property so it never fights `scale` or other transforms.
 *
 * [data-drift="-24"] (Instagram gallery columns) drifts by that many px as the pinned gallery
 * is covered by the footer, so neighbouring columns slide in opposite directions.
 */
(function () {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var items = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  var drifts = Array.prototype.slice.call(document.querySelectorAll('[data-drift]'));
  var drivers = drifts.length ? document.querySelector('.social + footer') : null;
  if (!items.length && !drifts.length) return;

  var ticking = false;

  function update() {
    var vh = window.innerHeight;
    items.forEach(function (el) {
      var host = el.parentElement;
      var rect = host.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > vh) return;
      var amount = parseFloat(el.getAttribute('data-parallax')) || 0.1;
      // -1 when the wrapper enters from below, +1 when it leaves at the top
      var progress = (rect.top + rect.height / 2 - vh / 2) / (vh / 2 + rect.height / 2);
      var y = Math.max(-1, Math.min(1, progress)) * rect.height * amount * -1;
      el.style.translate = '0 ' + y.toFixed(1) + 'px';
    });
    if (drivers) {
      // 0 when the gallery enters from below, 1 once the footer has fully covered it
      var t = Math.max(0, Math.min(1, 1 - drivers.getBoundingClientRect().top / (vh * 1.95)));
      drifts.forEach(function (el) {
        var amount = parseFloat(el.getAttribute('data-drift')) || 0;
        el.style.translate = '0 ' + (amount * (t * 2 - 1)).toFixed(1) + 'px';
      });
    }
    ticking = false;
  }

  function request() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }

  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request);
  update();
})();
