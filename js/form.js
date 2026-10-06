/**
 * Contact form: client-side validation and a status message.
 *
 * Set `data-endpoint="https://…"` on the <form> to POST the fields as JSON to your own backend or
 * form service. Without it the form only validates and shows the success message (demo mode).
 */
(function () {
  'use strict';

  var form = document.querySelector('[data-contact-form]');
  if (!form) return;

  var ok = form.querySelector('.form-msg--ok');
  var err = form.querySelector('.form-msg--err');
  var submit = form.querySelector('[type="submit"]');
  var fields = Array.prototype.slice.call(form.querySelectorAll('input, textarea, select'));

  // ?interest=Skyline%20Haven or data-interest="Skyline Haven" on the form preselects the home
  var interest = form.querySelector('[name="interest"]');
  var wanted = new URLSearchParams(window.location.search).get('interest') || form.getAttribute('data-interest');
  if (interest && wanted) {
    Array.prototype.forEach.call(interest.options, function (o) {
      if (o.text.toLowerCase().indexOf(wanted.toLowerCase()) === 0) interest.value = o.value || o.text;
    });
  }

  function validate(field) {
    var bad = !field.checkValidity();
    if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) bad = true;
    if (field.type === 'tel' && field.value && !/^[+()\d\s.-]{6,}$/.test(field.value)) bad = true;
    if (bad) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
    return !bad;
  }

  fields.forEach(function (field) {
    field.addEventListener('blur', function () { if (field.value || field.hasAttribute('aria-invalid')) validate(field); });
    field.addEventListener('input', function () { if (field.hasAttribute('aria-invalid')) validate(field); });
    field.addEventListener('change', function () { if (field.hasAttribute('aria-invalid')) validate(field); });
  });

  function show(node) {
    ok.hidden = node !== ok;
    err.hidden = node !== err;
  }

  function send() {
    var endpoint = form.getAttribute('data-endpoint');
    if (!endpoint) return new Promise(function (resolve) { setTimeout(resolve, 600); });

    var data = {};
    fields.forEach(function (f) {
      if (f.name) data[f.name] = f.type === 'checkbox' ? f.checked : f.value;
    });
    return fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data)
    }).then(function (res) { if (!res.ok) throw new Error('HTTP ' + res.status); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    show(null);

    var firstBad = null;
    fields.forEach(function (f) { if (!validate(f) && !firstBad) firstBad = f; });
    if (firstBad) { firstBad.focus(); return; }

    submit.disabled = true;
    submit.setAttribute('aria-busy', 'true');
    send().then(function () {
      form.reset();
      show(ok);
    }).catch(function () {
      show(err);
    }).then(function () {
      submit.disabled = false;
      submit.removeAttribute('aria-busy');
    });
  });
})();
