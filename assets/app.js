/* ═══════════════════════════════════════════════════════════════════════════
   Lecturas del Dia — Client-side interactions
   Vanilla JS, no framework, no build step.
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── 1. Expand / Collapse Readings ──────────────────────────────────────

  function initReadingToggles() {
    var headers = document.querySelectorAll('.reading-header');
    var expandAllBtn = document.getElementById('expand-all');

    headers.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var expanded = btn.getAttribute('aria-expanded') === 'true';
        var targetId = btn.getAttribute('aria-controls');
        var target = document.getElementById(targetId);
        if (!target) return;

        if (expanded) {
          btn.setAttribute('aria-expanded', 'false');
          target.hidden = true;
        } else {
          btn.setAttribute('aria-expanded', 'true');
          target.hidden = false;
        }
        updateExpandAllLabel();
      });
    });

    if (expandAllBtn) {
      expandAllBtn.addEventListener('click', function () {
        var allExpanded = areAllExpanded();
        headers.forEach(function (btn) {
          var targetId = btn.getAttribute('aria-controls');
          var target = document.getElementById(targetId);
          if (!target) return;

          if (allExpanded) {
            btn.setAttribute('aria-expanded', 'false');
            target.hidden = true;
          } else {
            btn.setAttribute('aria-expanded', 'true');
            target.hidden = false;
          }
        });
        updateExpandAllLabel();
      });

      // Set initial label based on template state (default: expanded)
      updateExpandAllLabel();
    }

    function areAllExpanded() {
      if (headers.length === 0) return false;
      for (var i = 0; i < headers.length; i++) {
        if (headers[i].getAttribute('aria-expanded') !== 'true') return false;
      }
      return true;
    }

    function updateExpandAllLabel() {
      if (!expandAllBtn) return;
      if (areAllExpanded()) {
        expandAllBtn.innerHTML = '&#128214; Colapsar todas';
      } else {
        expandAllBtn.innerHTML = '&#128214; Expandir todas';
      }
    }
  }

  // ── 2. Download .txt ───────────────────────────────────────────────────

  function initDownload() {
    var btn = document.getElementById('download-txt');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var article = document.querySelector('article[data-date]');
      if (!article) return;

      var dateIso = article.getAttribute('data-date');
      var lines = [];

      // Day name
      var dayHeader = article.querySelector('.day-header h1');
      if (dayHeader) {
        lines.push(dayHeader.textContent.trim().toUpperCase());
      }

      // Date + color
      var dateEl = article.querySelector('.day-header .date');
      var colorEl = article.querySelector('.color-badge');
      var dateLine = '';
      if (dateEl) dateLine += dateEl.textContent.trim();
      if (colorEl) dateLine += ' — ' + colorEl.textContent.trim();
      if (dateLine) lines.push(dateLine);

      lines.push('');
      lines.push('─'.repeat(50));
      lines.push('');

      // Each reading
      var readings = article.querySelectorAll('.reading');
      readings.forEach(function (reading) {
        var labelEl = reading.querySelector('.reading-label');
        var citaEl = reading.querySelector('.reading-cita');
        var tituloEl = reading.querySelector('.titulo');
        var textDiv = reading.querySelector('.reading-text');

        if (labelEl) lines.push(labelEl.textContent.trim().toUpperCase());
        if (citaEl) lines.push(citaEl.textContent.trim());
        if (tituloEl) lines.push(tituloEl.textContent.trim());
        lines.push('');

        if (textDiv) {
          var paragraphs = textDiv.querySelectorAll('p:not(.titulo):not(.antifona)');
          paragraphs.forEach(function (p) {
            lines.push(p.textContent.trim());
            lines.push('');
          });

          // Include antifona if present
          var antifona = textDiv.querySelector('.antifona');
          if (antifona) {
            lines.push(antifona.textContent.trim());
            lines.push('');
          }
        }

        lines.push('─'.repeat(50));
        lines.push('');
      });

      // Footer
      lines.push('Fuente: lecturasdeldia.org \u2014 Textos CEE');

      var text = lines.join('\n');
      var blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      var url = URL.createObjectURL(blob);

      var a = document.createElement('a');
      a.href = url;
      a.download = dateIso + '_lecturas.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ── 3. Search ──────────────────────────────────────────────────────────

  function initSearch() {
    var toggle = document.getElementById('search-toggle');
    var panel = document.getElementById('search-panel');
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    if (!toggle || !panel) return;

    var searchIndex = null;
    var debounceTimer = null;

    toggle.addEventListener('click', function () {
      var isHidden = panel.hidden;
      panel.hidden = !isHidden;
      if (!panel.hidden) {
        // Lazy load search index on first open
        if (!searchIndex) {
          fetch('/search-index.json')
            .then(function (r) { return r.json(); })
            .then(function (data) {
              searchIndex = data;
            })
            .catch(function () {
              searchIndex = [];
            });
        }
        if (input) input.focus();
      }
    });

    if (input) {
      input.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
          doSearch(input.value.trim());
        }, 200);
      });
    }

    function doSearch(query) {
      if (!results) return;
      if (!searchIndex) {
        results.innerHTML = '';
        return;
      }
      if (query.length < 2) {
        results.innerHTML = '';
        return;
      }

      var q = query.toLowerCase();
      var matches = [];

      for (var i = 0; i < searchIndex.length && matches.length < 15; i++) {
        var entry = searchIndex[i];
        var haystack = [
          entry.fecha || '',
          entry.nombre || '',
          entry.citas || '',
          entry.santos || '',
          entry.titulos || ''
        ].join(' ').toLowerCase();

        if (haystack.indexOf(q) !== -1) {
          matches.push(entry);
        }
      }

      if (matches.length === 0) {
        results.innerHTML = '<p style="padding:0.5rem;color:var(--color-text-muted);font-size:0.9rem;">Sin resultados</p>';
        return;
      }

      var html = '';
      matches.forEach(function (m) {
        html += '<a class="search-result" href="' + m.url + '">';
        html += '<span class="search-fecha">' + escapeHtml(m.fecha) + '</span><br>';
        html += '<span class="search-nombre">' + escapeHtml(m.nombre) + '</span><br>';
        html += '<span class="search-citas">' + escapeHtml(m.citas.replace(/\|/g, ' \u00b7 ')) + '</span>';
        html += '</a>';
      });
      results.innerHTML = html;
    }
  }

  // ── 4. Calendar ────────────────────────────────────────────────────────

  function initCalendar() {
    var toggle = document.getElementById('calendar-toggle');
    var panel = document.getElementById('calendar-panel');
    if (!toggle || !panel) return;

    var calData = null;
    var calCurrentMonth = null; // { year, month } (month is 0-based)

    var MONTH_NAMES = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    var DAY_HEADERS = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'S\u00e1', 'Do'];

    // Get initial month from page date
    var article = document.querySelector('article[data-date]');
    if (article) {
      var dateStr = article.getAttribute('data-date');
      var parts = dateStr.split('-');
      calCurrentMonth = { year: parseInt(parts[0], 10), month: parseInt(parts[1], 10) - 1 };
    } else {
      var now = new Date();
      calCurrentMonth = { year: now.getFullYear(), month: now.getMonth() };
    }

    toggle.addEventListener('click', function () {
      var isHidden = panel.hidden;
      panel.hidden = !isHidden;
      if (!panel.hidden) {
        // Lazy load calendar data on first open
        if (!calData) {
          fetch('/calendario/data.json')
            .then(function (r) { return r.json(); })
            .then(function (data) {
              calData = data;
              renderCalendar();
            })
            .catch(function () {
              calData = {};
              renderCalendar();
            });
        } else {
          renderCalendar();
        }
      }
    });

    function changeMonth(delta) {
      calCurrentMonth.month += delta;
      if (calCurrentMonth.month > 11) {
        calCurrentMonth.month = 0;
        calCurrentMonth.year += 1;
      } else if (calCurrentMonth.month < 0) {
        calCurrentMonth.month = 11;
        calCurrentMonth.year -= 1;
      }
      renderCalendar();
    }

    function renderCalendar() {
      if (!calData) return;

      var year = calCurrentMonth.year;
      var month = calCurrentMonth.month; // 0-based

      var today = new Date();
      var todayIso = today.getFullYear() + '-' +
        String(today.getMonth() + 1).padStart(2, '0') + '-' +
        String(today.getDate()).padStart(2, '0');

      // Header
      var html = '<div class="calendar-header">';
      html += '<button id="cal-prev-month">&larr;</button>';
      html += '<h3>' + MONTH_NAMES[month] + ' ' + year + '</h3>';
      html += '<button id="cal-next-month">&rarr;</button>';
      html += '</div>';

      // Grid
      html += '<div class="calendar-grid">';

      // Day headers (Mon-first)
      DAY_HEADERS.forEach(function (d) {
        html += '<div class="cal-weekday">' + d + '</div>';
      });

      // First day of month — convert to Monday-based (0=Mon, 6=Sun)
      var firstDay = new Date(year, month, 1);
      var startDow = (firstDay.getDay() + 6) % 7; // 0=Mon

      // Days in month
      var daysInMonth = new Date(year, month + 1, 0).getDate();

      // Empty cells before first day
      for (var i = 0; i < startDow; i++) {
        html += '<span></span>';
      }

      // Day cells
      for (var d = 1; d <= daysInMonth; d++) {
        var iso = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
        var entry = calData[iso];

        if (entry) {
          var isToday = iso === todayIso;
          var cls = 'cal-day' + (isToday ? ' today' : '');
          var dotStyle;
          if (entry.color === 'white') {
            dotStyle = 'background:#fff;border:1.5px solid var(--color-brand)';
          } else {
            dotStyle = 'background:var(--color-' + entry.color + ')';
          }

          html += '<a class="' + cls + '" href="' + entry.url + '" title="' + escapeHtml(entry.nombre) + '">';
          html += d;
          html += '<span class="dot" style="' + dotStyle + '"></span>';
          html += '</a>';
        } else {
          html += '<span class="cal-day muted">' + d + '</span>';
        }
      }

      html += '</div>';

      // Legend
      html += '<div class="calendar-legend">';
      html += '<span><span class="dot" style="background:var(--color-purple)"></span> Morado</span>';
      html += '<span><span class="dot" style="background:var(--color-green)"></span> Verde</span>';
      html += '<span><span class="dot" style="background:var(--color-red)"></span> Rojo</span>';
      html += '<span><span class="dot" style="background:#fff;border:1.5px solid var(--color-brand)"></span> Blanco</span>';
      html += '<span><span class="dot" style="background:var(--color-pink)"></span> Rosa</span>';
      html += '</div>';

      panel.innerHTML = html;

      // Bind prev/next buttons
      var prevBtn = document.getElementById('cal-prev-month');
      var nextBtn = document.getElementById('cal-next-month');
      if (prevBtn) prevBtn.addEventListener('click', function () { changeMonth(-1); });
      if (nextBtn) nextBtn.addEventListener('click', function () { changeMonth(1); });
    }
  }

  // ── Utility ────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // ── Init ───────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    initReadingToggles();
    initDownload();
    initSearch();
    initCalendar();
  });

})();
