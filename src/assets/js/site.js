// EAC De Sperwers — kleine scripts zonder libraries
(function () {
  // Mobiel menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('hoofdmenu');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.closest('li');
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Verlopen agenda-items verbergen, ook als de site nog niet opnieuw gebouwd is
  var today = new Date(); today.setHours(0, 0, 0, 0);
  document.querySelectorAll('[data-date]').forEach(function (el) {
    var d = new Date(el.getAttribute('data-date') + 'T23:59:59');
    if (d < today) el.remove();
  });

  // Carousel knoppen
  var car = document.querySelector('.carousel');
  if (car) {
    var btns = document.querySelectorAll('.car-btn');
    var update = function () {
      var max = car.scrollWidth - car.clientWidth - 2;
      btns.forEach(function (b) {
        b.disabled = b.dataset.dir === '-1' ? car.scrollLeft <= 2 : car.scrollLeft >= max;
      });
      if (!car.children.length) car.closest('section').remove();
    };
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var card = car.querySelector('li');
        var step = card ? card.getBoundingClientRect().width + 20 : 300;
        car.scrollBy({ left: step * Number(b.dataset.dir), behavior: 'smooth' });
      });
    });
    car.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  // Formulieren: via endpoint versturen, of anders een e-mail openen
  document.querySelectorAll('form.club-form').forEach(function (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      if (form.dataset.fallback === 'mailto') {
        var lines = [];
        form.querySelectorAll('.field').forEach(function (f) {
          var label = (f.querySelector('label,legend') || {}).textContent || '';
          var input = f.querySelector('input,select,textarea');
          if (!input) return;
          var val = input.type === 'radio' ? (form.querySelector('[name="' + input.name + '"]:checked') || {}).value
                  : input.type === 'checkbox' ? (input.checked ? 'Ja' : 'Nee') : input.value;
          lines.push(label.replace('*', '').trim().slice(0, 60) + ': ' + (val || ''));
        });
        window.location.href = 'mailto:' + form.dataset.mailto + '?subject=' + encodeURIComponent(form.dataset.subject) + '&body=' + encodeURIComponent(lines.join('\n'));
        status.textContent = 'Je e-mailprogramma wordt geopend. Verstuur daar het bericht.';
        return;
      }
      status.textContent = 'Bezig met versturen…';
      fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          status.textContent = 'Bedankt! We hebben je bericht ontvangen.';
        })
        .catch(function () {
          status.textContent = 'Er ging iets mis. Mail ons via ' + form.dataset.mailto + '.';
        });
    });
  });
})();
