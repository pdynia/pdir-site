// Requires form#enquiry with data-endpoint (Formspree URL) and fields f-company, f-email, f-country, f-role, f-message, f-product, f-subject.
// Enquiry form: posts to data-endpoint when one is configured, otherwise opens a pre-filled email.
(function () {
  var form = document.getElementById('enquiry');
  if (!form) return;
  var product = new URLSearchParams(location.search).get('product');
  if (product) {
    document.getElementById('f-product').value = product;
    document.getElementById('f-message').value = 'Please send me a trade price and availability for: ' + product;
    var inv = document.getElementById('f-role'); inv.value = 'Pharmacy or retailer';
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var err = document.getElementById('f-error'), ok = document.getElementById('f-ok');
    var required = ['f-company', 'f-email', 'f-country', 'f-role'].map(function (id) { return document.getElementById(id); });
    var bad = required.filter(function (el) { return !el.value || (el.type === 'email' && !el.checkValidity()); });
    required.forEach(function (el) { el.classList.toggle('invalid', bad.indexOf(el) !== -1); });
    err.hidden = bad.length === 0;
    if (bad.length) { bad[0].focus(); return; }
    var data = new FormData(form);
    var endpoint = form.getAttribute('data-endpoint');
    if (endpoint) {
      var btn = form.querySelector('button[type="submit"]');
      document.getElementById('f-subject').value = 'Website enquiry from ' + data.get('company');
      data = new FormData(form);
      btn.disabled = true; btn.textContent = 'Sending…'; ok.hidden = true;
      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(); ok.textContent = 'Thank you. We have received your enquiry and will reply within one business day.'; ok.hidden = false; form.reset(); })
        .catch(function () { err.textContent = 'Sending failed. Please email us at info@pdir.ae.'; err.hidden = false; })
        .then(function () { btn.disabled = false; btn.textContent = 'Send enquiry'; });
      return;
    }
    var lines = ['Company: ' + data.get('company'), 'Email: ' + data.get('email'), 'Country: ' + data.get('country'), 'Role: ' + data.get('role')];
    if (data.get('product')) lines.push('Product: ' + data.get('product'));
    lines.push('', data.get('message') || '');
    location.href = 'mailto:info@pdir.ae?subject=' + encodeURIComponent('Enquiry from ' + data.get('company')) + '&body=' + encodeURIComponent(lines.join('\n'));
    ok.hidden = false;
  });
})();
