/**
 * Testimonial slider: prev/next buttons, drag/swipe, arrow keys.
 * Not infinite; buttons disable at either end.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-slider]');
  if (!root) return;

  var viewport = root.querySelector('.slider__viewport');
  var track = root.querySelector('.slider__track');
  var slides = Array.prototype.slice.call(track.children);
  var prev = root.querySelector('[data-slider-prev]');
  var next = root.querySelector('[data-slider-next]');
  var index = 0;
  var drag = null;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function maxIndex() { return slides.length - 1; }

  function offsetFor(i) { return slides[i].offsetLeft; }

  function render() {
    track.style.transform = 'translate3d(' + -offsetFor(index) + 'px,0,0)';
    slides.forEach(function (slide, i) { slide.classList.toggle('is-active', i === index); });
    prev.disabled = index === 0;
    next.disabled = index === maxIndex();
  }

  function go(i) {
    index = Math.max(0, Math.min(maxIndex(), i));
    render();
  }

  prev.addEventListener('click', function () { go(index - 1); });
  next.addEventListener('click', function () { go(index + 1); });

  root.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
  });

  /* ---------- Drag / swipe ---------- */
  viewport.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    drag = { x: e.clientX, y: e.clientY, dx: 0, base: -offsetFor(index), time: Date.now(), locked: false };
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
    var min = -offsetFor(maxIndex());
    var pos = drag.base + dx;
    // resist pulling past either end
    if (pos > 0) pos *= 0.35;
    else if (pos < min) pos = min + (pos - min) * 0.35;
    track.style.transform = 'translate3d(' + pos + 'px,0,0)';
  });

  function endDrag() {
    if (!drag) return;
    var moved = drag.locked;
    var dx = drag.dx;
    var fast = Date.now() - drag.time < 300;
    drag = null;
    if (!moved) return;
    track.classList.remove('is-dragging');
    viewport.classList.remove('is-dragging');
    var threshold = fast ? 30 : slides[index].offsetWidth / 4;
    if (dx < -threshold) go(index + 1);
    else if (dx > threshold) go(index - 1);
    else render();
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
