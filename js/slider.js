/**
 * Testimonial slider: infinite loop, autoplay, prev/next buttons, drag/swipe, arrow keys.
 *
 * The slides are cloned before and after the real ones; once a move ends on a clone the track
 * jumps (without animation) to the identical real slide, so the loop never shows a seam.
 * Autoplay (data-autoplay="5000" ms) pauses on hover, focus, drag, a hidden tab and when the
 * slider is off screen, and is off with prefers-reduced-motion.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-slider]');
  if (!root) return;

  var viewport = root.querySelector('.slider__viewport');
  var track = root.querySelector('.slider__track');
  var originals = Array.prototype.slice.call(track.children);
  var count = originals.length;
  var prev = root.querySelector('[data-slider-prev]');
  var next = root.querySelector('[data-slider-next]');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var drag = null;

  /* ---------- Clones: [before][real][after]; `pos` indexes the whole list ---------- */
  function clones() {
    return originals.map(function (slide) {
      var copy = slide.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      copy.setAttribute('inert', '');
      copy.removeAttribute('role');
      copy.removeAttribute('aria-roledescription');
      copy.removeAttribute('aria-label');
      return copy;
    });
  }
  clones().forEach(function (copy) { track.insertBefore(copy, originals[0]); });
  clones().forEach(function (copy) { track.appendChild(copy); });

  var slides = Array.prototype.slice.call(track.children);
  var pos = count; // first real slide

  function offsetFor(i) { return slides[i].offsetLeft; }

  function render() {
    track.style.transform = 'translate3d(' + -offsetFor(pos) + 'px,0,0)';
    slides.forEach(function (slide, i) { slide.classList.toggle('is-active', i === pos); });
  }

  /* Jump from a clone to its real twin, with no animation. */
  function normalize() {
    if (pos >= count && pos < count * 2) return;
    pos = ((pos % count) + count) % count + count;
    track.classList.add('is-dragging');
    render();
    void track.offsetWidth;
    track.classList.remove('is-dragging');
  }

  function go(i) {
    pos = Math.max(0, Math.min(slides.length - 1, i));
    render();
    if (reduceMotion) normalize();
    restart();
  }

  track.addEventListener('transitionend', function (e) {
    if (e.target === track && e.propertyName === 'transform') normalize();
  });

  prev.addEventListener('click', function () { go(pos - 1); });
  next.addEventListener('click', function () { go(pos + 1); });

  root.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(pos - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); go(pos + 1); }
  });

  /* ---------- Autoplay ---------- */
  var delay = parseInt(root.getAttribute('data-autoplay'), 10) || 0;
  var timer = null;
  var onScreen = false;
  var held = false; // hover, focus or drag

  function stop() {
    window.clearInterval(timer);
    timer = null;
  }

  function restart() {
    stop();
    if (!delay || reduceMotion || held || !onScreen || document.hidden) return;
    timer = window.setInterval(function () { go(pos + 1); }, delay);
  }

  function hold(value) {
    held = value;
    restart();
  }

  root.addEventListener('mouseenter', function () { hold(true); });
  root.addEventListener('mouseleave', function () { hold(false); });
  root.addEventListener('focusin', function () { hold(true); });
  root.addEventListener('focusout', function () { hold(false); });
  document.addEventListener('visibilitychange', restart);

  if (delay && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      onScreen = entries[0].isIntersecting;
      restart();
    }, { threshold: 0.3 }).observe(root);
  }

  /* ---------- Drag / swipe ---------- */
  viewport.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    normalize(); // a swipe may start while the previous move is still on a clone
    held = true;
    stop();
    drag = { x: e.clientX, y: e.clientY, dx: 0, base: -offsetFor(pos), time: Date.now(), locked: false };
  });

  viewport.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x;
    var dy = e.clientY - drag.y;
    if (!drag.locked) {
      if (Math.abs(dx) < 6) return;
      if (Math.abs(dy) > Math.abs(dx)) { drag = null; return; }
      drag.locked = true;
      viewport.setPointerCapture(e.pointerId);
      track.classList.add('is-dragging');
      viewport.classList.add('is-dragging');
    }
    drag.dx = dx;
    track.style.transform = 'translate3d(' + (drag.base + dx) + 'px,0,0)';
  });

  function endDrag() {
    if (!drag) return;
    var moved = drag.locked;
    var dx = drag.dx;
    var fast = Date.now() - drag.time < 300;
    drag = null;
    held = root.matches(':hover') || root.contains(document.activeElement);
    if (!moved) { restart(); return; }
    track.classList.remove('is-dragging');
    viewport.classList.remove('is-dragging');
    var threshold = fast ? 30 : slides[pos].offsetWidth / 4;
    if (dx < -threshold) go(pos + 1);
    else if (dx > threshold) go(pos - 1);
    else { render(); restart(); }
  }

  viewport.addEventListener('pointerup', endDrag);
  viewport.addEventListener('pointercancel', endDrag);

  window.addEventListener('resize', function () {
    track.classList.add('is-dragging'); // no animation while re-measuring
    render();
    window.requestAnimationFrame(function () { track.classList.remove('is-dragging'); });
  });

  if (reduceMotion) track.style.transition = 'none';
  render();
})();
