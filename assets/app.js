/* ═══════════════════════════════════════════════════════════════════════════
   Lecturas del Dia / Egunaren Irakurgaiak — Client-side interactions
   Vanilla JS, no framework, no build step.
   Bilingual (ES + EU): all language-specific strings come from the
   <script id="i18n-data"> JSON block injected by base.html.
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── i18n + lang root ───────────────────────────────────────────────────

  var I18N = {};
  try {
    var rawI18n = document.getElementById('i18n-data');
    if (rawI18n) I18N = JSON.parse(rawI18n.textContent);
  } catch (_) {
    I18N = {};
  }

  // /eu/... → '/eu' prefix; ES → '' (apex).
  var LANG_ROOT = window.location.pathname.indexOf('/eu/') === 0 ? '/eu' : '';

  function t(key, fallback) {
    return (I18N && typeof I18N[key] === 'string') ? I18N[key] : (fallback || '');
  }

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
      var count = 0;
      for (var i = 0; i < headers.length; i++) {
        if (headers[i].closest('.aclamacion-section')) continue;
        count++;
        if (headers[i].getAttribute('aria-expanded') !== 'true') return false;
      }
      return count > 0;
    }

    function updateExpandAllLabel() {
      if (!expandAllBtn) return;
      var label = areAllExpanded()
        ? t('expand_all_collapse', 'Contraer todas')
        : t('expand_all_open', 'Expandir todas');
      expandAllBtn.innerHTML = '&#128214; ' + escapeHtml(label);
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
      lines.push(t('download_footer', 'Fuente: lecturasdeldia.org — Textos CEE'));

      var text = lines.join('\n');
      var blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      var url = URL.createObjectURL(blob);

      var suffix = t('download_filename_suffix', '_lecturas');
      var a = document.createElement('a');
      a.href = url;
      a.download = dateIso + suffix + '.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ── 3. Search (dedicated /buscar/ or /eu/bilatu/ page) ──────────────────
  //
  // Fully accent-insensitive substring search with bilingual book-name aliases.
  // Pipeline: lowercase → strip diacritics → expand full book names to the
  // language's CEE/Basque abbreviation. Applied to BOTH query and indexed
  // haystack so e.g. "Génesis 1", "genesis 1", and "Gen 1" all match the
  // entry stored as "Gen 1, 1".

  function stripAccents(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  // Spanish full names → CEE abbreviation. Keys are post-strip-accents/lowercase.
  var BOOK_ALIASES_ES = {
    "genesis":"gen","exodo":"ex","levitico":"lev","numeros":"num",
    "deuteronomio":"dt","josue":"jos","jueces":"jue",
    "1 samuel":"1 sam","2 samuel":"2 sam",
    "1 reyes":"1 re","2 reyes":"2 re",
    "1 cronicas":"1 cron","2 cronicas":"2 cron",
    "esdras":"esd","nehemias":"neh","tobias":"tob","judit":"jdt","ester":"est",
    "1 macabeos":"1 mac","2 macabeos":"2 mac",
    "salmos":"sal","salmo":"sal","proverbios":"prov","eclesiastes":"ecl",
    "cantar":"cant","cantares":"cant","sabiduria":"sab","eclesiastico":"eclo",
    "isaias":"is","jeremias":"jer","lamentaciones":"lam","baruc":"bar",
    "ezequiel":"ez","daniel":"dan","oseas":"os","joel":"jl","amos":"am",
    "abdias":"abd","jonas":"jon","miqueas":"miq","nahum":"nah","habacuc":"hab",
    "sofonias":"sof","ageo":"ag","zacarias":"zac","malaquias":"mal",
    "mateo":"mt","marcos":"mc","lucas":"lc","juan":"jn","hechos":"hch",
    "romanos":"rom",
    "1 corintios":"1 cor","2 corintios":"2 cor",
    "galatas":"gal","efesios":"ef","filipenses":"flp","colosenses":"col",
    "1 tesalonicenses":"1 tes","2 tesalonicenses":"2 tes",
    "1 timoteo":"1 tim","2 timoteo":"2 tim",
    "tito":"tit","filemon":"flm","hebreos":"heb","santiago":"sant",
    "1 pedro":"1 pe","2 pedro":"2 pe",
    "1 juan":"1 jn","2 juan":"2 jn","3 juan":"3 jn",
    "judas":"jds","apocalipsis":"ap"
  };

  // Basque full names → Basque abbreviation. Includes Spanish full names so a
  // user typing "Génesis" on the EU site still finds "Has 1, 1".
  var BOOK_ALIASES_EU = {
    "hasiera":"has","irteera":"ir","lebitarrak":"lb","zenbakiak":"zen",
    "deuteronomioa":"dt","epaileak":"ep",
    "1 samuel":"1 sm","2 samuel":"2 sm",
    "1 erregeak":"1 erg","2 erregeak":"2 erg",
    "1 kronikak":"1 kro","2 kronikak":"2 kro",
    "ezra":"esd","tobit":"tb",
    "1 makabearrak":"1 mak","2 makabearrak":"2 mak",
    "salmoa":"sal","salmoak":"sal","salmoz":"sal","salmo":"sal",
    "esaera zaharrak":"es","kohelet":"koh",
    "kantarik ederrena":"ka","kantar":"ka",
    "jakinduria":"jkd","sirakida":"si",
    "auhenak":"aud","baruk":"ba","ezekiel":"ez",
    "mikeas":"mi","habakuk":"hab","zakarias":"za","malakias":"ml",
    "matiu":"mt","markos":"mk","lukas":"lk","joan":"jn","eginak":"eg",
    "erromatarrei":"erm","romatarrei":"erm",
    "1 korintoarrei":"1 kor","2 korintoarrei":"2 kor",
    "galatarrei":"gal","efesoarrei":"ef","filipenseei":"flp","kolosarrei":"kol",
    "1 tesalonikarrei":"1 tes","2 tesalonikarrei":"2 tes",
    "1 timoteo":"1 tim","2 timoteo":"2 tim",
    "filemon":"flm","hebrearrei":"heb",
    "1 pedro":"1 p","2 pedro":"2 p",
    "1 joan":"1 jn","2 joan":"2 jn","3 joan":"3 jn",
    "apokalipsia":"ap",
    // Spanish full names mapped to Basque abbreviations (cross-language search)
    "genesis":"has","exodo":"ir","numeros":"zen","deuteronomio":"dt",
    "1 samuel":"1 sm","2 samuel":"2 sm",
    "1 reyes":"1 erg","2 reyes":"2 erg",
    "1 cronicas":"1 kro","2 cronicas":"2 kro",
    "esdras":"esd","tobias":"tb","ester":"est",
    "1 macabeos":"1 mak","2 macabeos":"2 mak",
    "salmos":"sal","proverbios":"es","eclesiastes":"koh",
    "cantar":"ka","cantares":"ka","sabiduria":"jkd","eclesiastico":"si",
    "isaias":"is","jeremias":"jr","lamentaciones":"aud","baruc":"ba",
    "ezequiel":"ez","daniel":"dn","oseas":"os","joel":"jl","amos":"am",
    "abdias":"ab","jonas":"jon","miqueas":"mi","nahum":"nah","habacuc":"hab",
    "sofonias":"sof","ageo":"ag","zacarias":"za","malaquias":"ml",
    "mateo":"mt","marcos":"mk","lucas":"lk","juan":"jn","hechos":"eg",
    "romanos":"erm","galatas":"gal","efesios":"ef","filipenses":"flp",
    "colosenses":"kol",
    "1 corintios":"1 kor","2 corintios":"2 kor",
    "1 tesalonicenses":"1 tes","2 tesalonicenses":"2 tes",
    "tito":"tit","hebreos":"heb","santiago":"sant",
    "1 juan":"1 jn","2 juan":"2 jn","3 juan":"3 jn",
    "judas":"jud","apocalipsis":"ap"
  };

  var BOOK_ALIASES = LANG_ROOT === '/eu' ? BOOK_ALIASES_EU : BOOK_ALIASES_ES;
  var ALIAS_KEYS = Object.keys(BOOK_ALIASES).sort(function (a, b) {
    return b.length - a.length;
  });
  var ALIAS_RE = ALIAS_KEYS.length
    ? new RegExp(
        '\\b(?:' +
          ALIAS_KEYS.map(function (k) { return k.replace(/\s+/g, '\\s+'); })
                    .join('|') +
          ')\\b',
        'g'
      )
    : null;

  function normalizeForSearch(s) {
    var out = stripAccents(String(s || '').toLowerCase());
    if (ALIAS_RE) {
      out = out.replace(ALIAS_RE, function (m) {
        return BOOK_ALIASES[m.replace(/\s+/g, ' ')] || m;
      });
    }
    return out;
  }

  function initSearch() {
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    if (!input || !results) return;

    var searchIndex = null;
    var normalizedHaystacks = null;  // parallel to searchIndex; built once at load
    var debounceTimer = null;

    fetch(LANG_ROOT + '/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        searchIndex = data;
        normalizedHaystacks = data.map(function (e) {
          return normalizeForSearch([
            e.fecha, e.nombre, e.citas, e.santos, e.titulos
          ].join(' '));
        });
        if (input.value.trim().length >= 2) {
          doSearch(input.value.trim());
        }
      })
      .catch(function () {
        searchIndex = [];
        normalizedHaystacks = [];
      });

    input.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        doSearch(input.value.trim());
      }, 200);
    });

    function doSearch(query) {
      if (!searchIndex || !normalizedHaystacks) {
        results.innerHTML = '';
        return;
      }
      if (query.length < 2) {
        results.innerHTML = '';
        return;
      }

      var q = normalizeForSearch(query);
      var matches = [];

      for (var i = 0; i < normalizedHaystacks.length && matches.length < 15; i++) {
        if (normalizedHaystacks[i].indexOf(q) !== -1) {
          matches.push(searchIndex[i]);
        }
      }

      if (matches.length === 0) {
        var msg = t('search_no_results', 'La búsqueda no ha dado resultados');
        results.innerHTML = '<p class="search-empty">' + escapeHtml(msg) + '</p>';
        return;
      }

      var html = '';
      matches.forEach(function (m) {
        html += '<a class="search-result" href="' + m.url + '">';
        html += '<span class="search-fecha">' + escapeHtml(m.fecha) + '</span><br>';
        html += '<span class="search-nombre">' + escapeHtml(m.nombre) + '</span><br>';
        html += '<span class="search-citas">' + escapeHtml(m.citas.replace(/\|/g, ' · ')) + '</span>';
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

    var MONTH_NAMES = (I18N && I18N.calendar_month_names) || [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    var DAY_HEADERS = (I18N && I18N.calendar_day_headers) || ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'];
    var LEGEND = (I18N && I18N.calendar_legend) || {
      purple: 'Morado', green: 'Verde', red: 'Rojo', white: 'Blanco', pink: 'Rosa'
    };

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
        if (!calData) {
          fetch(LANG_ROOT + '/calendario/data.json')
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
      var month = calCurrentMonth.month;

      var today = new Date();
      var todayIso = today.getFullYear() + '-' +
        String(today.getMonth() + 1).padStart(2, '0') + '-' +
        String(today.getDate()).padStart(2, '0');

      var html = '<div class="calendar-header">';
      html += '<button id="cal-prev-month">&larr;</button>';
      html += '<h3>' + escapeHtml(MONTH_NAMES[month]) + ' ' + year + '</h3>';
      html += '<button id="cal-next-month">&rarr;</button>';
      html += '</div>';

      html += '<div class="calendar-grid">';
      DAY_HEADERS.forEach(function (d) {
        html += '<div class="cal-weekday">' + escapeHtml(d) + '</div>';
      });

      var firstDay = new Date(year, month, 1);
      var startDow = (firstDay.getDay() + 6) % 7;
      var daysInMonth = new Date(year, month + 1, 0).getDate();

      for (var i = 0; i < startDow; i++) {
        html += '<span></span>';
      }

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
      html += '<span><span class="dot" style="background:var(--color-purple)"></span> ' + escapeHtml(LEGEND.purple || '') + '</span>';
      html += '<span><span class="dot" style="background:var(--color-green)"></span> ' + escapeHtml(LEGEND.green || '') + '</span>';
      html += '<span><span class="dot" style="background:var(--color-red)"></span> ' + escapeHtml(LEGEND.red || '') + '</span>';
      html += '<span><span class="dot" style="background:#fff;border:1.5px solid var(--color-brand)"></span> ' + escapeHtml(LEGEND.white || '') + '</span>';
      html += '<span><span class="dot" style="background:var(--color-pink)"></span> ' + escapeHtml(LEGEND.pink || '') + '</span>';
      html += '</div>';

      panel.innerHTML = html;

      var prevBtn = document.getElementById('cal-prev-month');
      var nextBtn = document.getElementById('cal-next-month');
      if (prevBtn) prevBtn.addEventListener('click', function () { changeMonth(-1); });
      if (nextBtn) nextBtn.addEventListener('click', function () { changeMonth(1); });
    }
  }

  // ── Utility ────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str == null ? '' : String(str)));
    return div.innerHTML;
  }

  // ── 5. Alternative saint readings toggle ────────────────────────────────

  function initSaintReadings() {
    var toggle = document.getElementById('alt-readings-toggle');
    if (!toggle) return;
    var ferial = document.querySelector('section.readings:not(#saint-readings)');
    var saint = document.getElementById('saint-readings');
    if (!ferial || !saint) return;

    var showingSaint = false;

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      showingSaint = !showingSaint;
      ferial.hidden = showingSaint;
      saint.hidden = !showingSaint;
      toggle.textContent = showingSaint
        ? t('alt_readings_back', 'Lecturas del día')
        : t('alt_readings_link', 'Lecturas alternativas');
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    initReadingToggles();
    initDownload();
    initSearch();
    initCalendar();
    initSaintReadings();
  });

})();
