/**
 * Scroll reveal.
 *
 *   data-reveal="up|fade|left|right|scale|clip"   reveal when scrolled into view
 *   data-reveal-delay="200"                        extra delay in ms
 *   data-stagger="90"                              on a parent: stagger its [data-reveal] children
 *   data-split                                     headline revealed word by word
 *
 * Without JS (or with reduced motion) everything stays visible; see css/styles.css.
 */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Split headlines into masked words ---------- */
  function splitWords(el) {
    var index = 0;
    var label = el.textContent.replace(/\s+/g, ' ').trim();
    el.setAttribute('aria-label', label);

    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) {
              frag.appendChild(document.createTextNode(' '));
              return;
            }
            var outer = document.createElement('span');
            var inner = document.createElement('span');
            outer.className = 'split-word';
            outer.setAttribute('aria-hidden', 'true');
            inner.className = 'split-word__inner';
            inner.style.setProperty('--i', index++);
            inner.textContent = part;
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && child.nodeName !== 'BR') {
          walk(child);
        }
      });
    })(el);
  }

  /* ---------- Stagger children ---------- */
  function applyStagger() {
    document.querySelectorAll('[data-stagger]').forEach(function (parent) {
      var step = parseInt(parent.getAttribute('data-stagger'), 10) || 90;
      var base = parseInt(parent.getAttribute('data-stagger-base'), 10) || 0;
      parent.querySelectorAll(':scope > [data-reveal]').forEach(function (child, i) {
        child.style.setProperty('--reveal-delay', base + i * step + 'ms');
      });
    });
  }

  function applyDelays() {
    document.querySelectorAll('[data-reveal-delay]').forEach(function (el) {
      el.style.setProperty('--reveal-delay', el.getAttribute('data-reveal-delay') + 'ms');
    });
  }

  function init() {
    var targets = document.querySelectorAll('[data-reveal]');
    if (!targets.length) return;

    if (reduceMotion || !('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    document.querySelectorAll('[data-split]').forEach(splitWords);
    applyDelays();
    applyStagger();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });

    targets.forEach(function (el) { observer.observe(el); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
