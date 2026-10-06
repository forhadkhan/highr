/**
 * Project filter tabs (ARIA tabs pattern, one panel, items filtered by data-status).
 * Arrow keys / Home / End move between tabs.
 */
(function () {
  'use strict';

  var list = document.querySelector('[data-tabs]');
  var panel = document.getElementById('project-panel');
  if (!list || !panel) return;

  var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
  var items = Array.prototype.slice.call(panel.querySelectorAll('.project-item'));

  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
    });
    panel.setAttribute('aria-labelledby', tab.id);
    if (focus) tab.focus();

    var filter = tab.getAttribute('data-filter');
    var shown = 0;
    items.forEach(function (item) {
      var match = filter === 'all' || item.getAttribute('data-status') === filter;
      item.hidden = !match;
      item.classList.remove('filter-in');
      if (match) {
        // Replay a short entrance for items that were already revealed
        if (item.classList.contains('is-visible')) {
          item.style.setProperty('--i', shown);
          void item.offsetWidth;
          item.classList.add('filter-in');
        }
        shown++;
      }
    });
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () { select(tab, false); });
    tab.addEventListener('keydown', function (e) {
      var next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') next = tabs[0];
      else if (e.key === 'End') next = tabs[tabs.length - 1];
      if (next) {
        e.preventDefault();
        select(next, true);
      }
    });
  });
})();
