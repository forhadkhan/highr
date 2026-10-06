/**
 * Photo loading help for the community cards and the About photo.
 *
 * Native lazy loading can leave a photo waiting on a phone, so once the page itself has loaded
 * these (small, responsive) photos are fetched in the background. A photo that fails to load is
 * hidden so the building icon placeholder behind it (css/styles.css) stays visible.
 */
(function () {
  'use strict';

  var photos = Array.prototype.slice.call(document.querySelectorAll('.project-media img, .about-media img'));
  if (!photos.length) return;

  photos.forEach(function (img) {
    img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
  });

  function fetchNow() {
    photos.forEach(function (img) {
      if (img.loading === 'lazy' && !img.complete) img.loading = 'eager';
    });
  }

  if (document.readyState === 'complete') fetchNow();
  else window.addEventListener('load', fetchNow);
})();
