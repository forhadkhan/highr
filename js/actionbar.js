/**
 * Mobile action bar (Call / WhatsApp / Book a tour): slides up once the hero has scrolled away
 * and slides down again while the footer contact form is on screen.
 */
(function () {
  'use strict';

  var bar = document.querySelector('[data-actionbar]');
  var hero = document.getElementById('top');
  var footer = document.getElementById('contact');
  if (!bar || !hero || !footer || !('IntersectionObserver' in window)) return;

  var heroVisible = true;
  var footerVisible = false;

  function update() {
    bar.classList.toggle('is-visible', !heroVisible && !footerVisible);
  }

  new IntersectionObserver(function (entries) {
    heroVisible = entries[0].isIntersecting;
    update();
  }).observe(hero);

  new IntersectionObserver(function (entries) {
    footerVisible = entries[0].isIntersecting;
    update();
  }, { threshold: 0.1 }).observe(footer);
})();
