/**
 * Lightbox: <a href="full.jpg" data-lightbox="group" data-caption="…"><img …></a> opens the image
 * full size in a modal <dialog>. Links with the same data-lightbox value form a gallery
 * (chevrons, arrow keys). Esc, the close button or a click outside the image closes it.
 * Without JavaScript the link just opens the image.
 */
(function () {
  'use strict';

  var triggers = Array.prototype.slice.call(document.querySelectorAll('a[data-lightbox]'));
  if (!triggers.length || typeof HTMLDialogElement === 'undefined') return;

  var dialog, img, caption, prev, next, group = [], index = 0;

  function icon(name) { return '<i class="icon icon-' + name + '" aria-hidden="true"></i>'; }

  function build() {
    dialog = document.createElement('dialog');
    dialog.className = 'lightbox';
    dialog.setAttribute('aria-label', 'Image viewer');
    dialog.innerHTML =
      '<figure class="lightbox__figure"><img class="lightbox__img" alt=""><figcaption class="lightbox__caption"></figcaption></figure>' +
      '<button type="button" class="lightbox__btn lightbox__close" aria-label="Close">' + icon('close') + '</button>' +
      '<button type="button" class="lightbox__btn lightbox__prev" aria-label="Previous image">' + icon('chevron-left') + '</button>' +
      '<button type="button" class="lightbox__btn lightbox__next" aria-label="Next image">' + icon('chevron-right') + '</button>';
    document.body.appendChild(dialog);

    img = dialog.querySelector('.lightbox__img');
    caption = dialog.querySelector('.lightbox__caption');
    prev = dialog.querySelector('.lightbox__prev');
    next = dialog.querySelector('.lightbox__next');

    dialog.querySelector('.lightbox__close').addEventListener('click', function () { dialog.close(); });
    prev.addEventListener('click', function () { show(index - 1); });
    next.addEventListener('click', function () { show(index + 1); });
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog || e.target === img.parentNode) dialog.close();
    });
    dialog.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
    });
    dialog.addEventListener('close', function () { document.documentElement.classList.remove('lightbox-open'); });
    img.addEventListener('load', fit);
  }

  /* Size the image to the free space; vectors scale up, photos never past their own pixels. */
  function fit() {
    var w = img.naturalWidth || 4, h = img.naturalHeight || 3;
    img.style.setProperty('--ar', w / h);
    img.style.maxWidth = /\.svg(\?|$)/i.test(img.currentSrc) ? 'none' : w + 'px';
  }

  function show(i) {
    index = (i + group.length) % group.length;
    var a = group[index];
    var thumb = a.querySelector('img');
    img.alt = thumb ? thumb.alt : '';
    img.src = a.getAttribute('href');
    caption.textContent = a.getAttribute('data-caption') || '';
    caption.hidden = !caption.textContent;
    prev.hidden = next.hidden = group.length < 2;
  }

  function open(a) {
    if (!dialog) build();
    var name = a.getAttribute('data-lightbox');
    group = triggers.filter(function (t) { return t.getAttribute('data-lightbox') === name; });
    document.documentElement.classList.add('lightbox-open');
    dialog.showModal();
    show(group.indexOf(a));
  }

  triggers.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      open(a);
    });
  });
})();
