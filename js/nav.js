/**
 * Header behaviour: mobile menu, hide on scroll down / show on scroll up,
 * shadow once scrolled, and highlighting the link of the section in view.
 */
(function () {
  'use strict';

  var header = document.getElementById('site-header');
  if (!header) return;

  var toggle = header.querySelector('[data-menu-toggle]');
  var panel = document.getElementById('site-nav');
  var links = Array.prototype.slice.call(header.querySelectorAll('[data-nav-link]'));
  var desktop = window.matchMedia('(min-width: 1024px)');

  /* ---------- Mobile menu ---------- */
  function setMenu(open) {
    if (!toggle || !panel) return;
    panel.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    if (open) header.classList.remove('is-hidden');
  }

  function isOpen() {
    return !!panel && panel.classList.contains('is-open');
  }

  if (toggle) {
    toggle.addEventListener('click', function () { setMenu(!isOpen()); });
  }

  links.forEach(function (link) {
    link.addEventListener('click', function () { setMenu(false); });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) {
      setMenu(false);
      if (toggle) toggle.focus();
    }
  });

  document.addEventListener('click', function (e) {
    if (isOpen() && !header.contains(e.target)) setMenu(false);
  });

  function onBreakpoint() { if (desktop.matches) setMenu(false); }
  if (desktop.addEventListener) desktop.addEventListener('change', onBreakpoint);
  else desktop.addListener(onBreakpoint);

  /* ---------- Hide on scroll down, show on scroll up ---------- */
  var lastY = window.scrollY;
  var ticking = false;

  function onScroll() {
    var y = Math.max(window.scrollY, 0);
    var delta = y - lastY;

    header.classList.toggle('is-scrolled', y > 8);

    if (isOpen() || y < 120) {
      header.classList.remove('is-hidden');
    } else if (delta > 6) {
      header.classList.add('is-hidden');
    } else if (delta < -6) {
      header.classList.remove('is-hidden');
    }

    if (Math.abs(delta) > 6) lastY = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(onScroll);
    }
  }, { passive: true });

  header.addEventListener('focusin', function () { header.classList.remove('is-hidden'); });
  onScroll();

  /* ---------- Active section link ---------- */
  var targets = links
    .map(function (link) {
      var id = (link.getAttribute('href') || '').replace('#', '');
      return { link: link, section: id ? document.getElementById(id) : null };
    })
    .filter(function (item) { return item.section; });

  if (targets.length && 'IntersectionObserver' in window) {
    var current = null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) current = entry.target;
        else if (current === entry.target) current = null;
      });
      targets.forEach(function (item) {
        if (item.section === current) item.link.setAttribute('aria-current', 'true');
        else item.link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    targets.forEach(function (item) { observer.observe(item.section); });
  }
})();
