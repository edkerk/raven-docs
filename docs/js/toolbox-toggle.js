/* Global MATLAB / Python toggle injected into the Material header.
 *
 * Reads and writes Material's own localStorage key so that content.tabs.link
 * stays in sync: clicking the header toggle is equivalent to clicking a
 * MATLAB / Python content tab anywhere on the site.
 */
(function () {
  'use strict';

  var OPTS = ['MATLAB', 'Python'];
  var LS_KEY = '__tabs';

  function getPref() {
    try {
      var stored = localStorage.getItem(LS_KEY);
      var arr = stored ? JSON.parse(stored) : [];
      return arr.indexOf('Python') !== -1 ? 'Python' : 'MATLAB';
    } catch (_) {
      return 'MATLAB';
    }
  }

  function activateContentTabs(label) {
    /* Click the first matching content-tab label on the page so Material
     * handles the localStorage update and tab switching itself. */
    var labels = document.querySelectorAll('.tabbed-labels label');
    for (var i = 0; i < labels.length; i++) {
      if (labels[i].textContent.trim() === label) {
        labels[i].click();
        return;
      }
    }
    /* No content tabs on this page — write localStorage directly so the
     * preference carries through to the next page that has tabs. */
    try {
      var stored = localStorage.getItem(LS_KEY);
      var set = new Set(stored ? JSON.parse(stored) : []);
      OPTS.forEach(function (o) { set.delete(o); });
      set.add(label);
      localStorage.setItem(LS_KEY, JSON.stringify(Array.from(set)));
    } catch (_) {}
  }

  function updateToggleUI(toggle, label) {
    var btns = toggle.querySelectorAll('.raven-toggle-opt');
    for (var i = 0; i < btns.length; i++) {
      var on = btns[i].dataset.label === label;
      btns[i].classList.toggle('raven-toggle-on', on);
      btns[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
  }

  function buildToggle() {
    var wrap = document.createElement('div');
    wrap.className = 'raven-hdr-toggle';
    wrap.setAttribute('role', 'group');
    wrap.setAttribute('aria-label', 'Toolbox language');
    OPTS.forEach(function (label) {
      var btn = document.createElement('button');
      btn.className = 'raven-toggle-opt';
      btn.dataset.label = label;
      btn.textContent = label;
      btn.setAttribute('type', 'button');
      btn.addEventListener('click', function () {
        activateContentTabs(label);
        updateToggleUI(wrap, label);
      });
      wrap.appendChild(btn);
    });
    return wrap;
  }

  function syncFromContentTabs(toggle) {
    /* When a content tab is clicked, keep the header toggle in sync. */
    document.querySelectorAll('.tabbed-labels label').forEach(function (lbl) {
      lbl.addEventListener('click', function () {
        var text = lbl.textContent.trim();
        if (OPTS.indexOf(text) !== -1) updateToggleUI(toggle, text);
      }, { once: true });
    });
  }

  function init() {
    var existing = document.querySelector('.raven-hdr-toggle');
    var toggle;

    if (!existing) {
      toggle = buildToggle();
      var src = document.querySelector('.md-header__source');
      if (src) {
        src.parentNode.insertBefore(toggle, src);
      } else {
        var inner = document.querySelector('.md-header__inner');
        if (inner) inner.appendChild(toggle);
      }
    } else {
      toggle = existing;
    }

    updateToggleUI(toggle, getPref());
    syncFromContentTabs(toggle);
  }

  /* Material instant navigation: document$ fires after every page swap. */
  if (typeof document$ !== 'undefined') {
    document$.subscribe(init);
  } else {
    document.addEventListener('DOMContentLoaded', init);
  }
}());
