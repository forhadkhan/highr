/**
 * Count-up numbers: <p data-count="15" data-prefix="" data-suffix="k+" data-decimals="0">15k+</p>
 * The final value is already in the markup, so it reads correctly without JS or with reduced motion.
 */
(function () {
  'use strict';

  var els = document.querySelectorAll('[data-count]');
  if (!els.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;

  var DURATION = 1800;
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 4); };

  function format(el, value) {
    var decimals = parseInt(el.getAttribute('data-decimals'), 10) || 0;
    return (el.getAttribute('data-prefix') || '') + value.toFixed(decimals) + (el.getAttribute('data-suffix') || '');
  }

  function run(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var start = null;
    function frame(now) {
      if (start === null) start = now;
      var t = Math.min((now - start) / DURATION, 1);
      el.textContent = format(el, target * easeOut(t));
      if (t < 1) window.requestAnimationFrame(frame);
    }
    window.requestAnimationFrame(frame);
  }

  els.forEach(function (el) {
    // Keep the box from jumping while the number grows
    el.style.fontVariantNumeric = 'tabular-nums';
  });

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      run(entry.target);
    });
  }, { threshold: 0.6 });

  els.forEach(function (el) { observer.observe(el); });
})();
