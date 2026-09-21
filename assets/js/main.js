/* ==========================================================================
   SGS — draft site behaviour
   Deliberately minimal. Each behaviour below has a native Elementor
   equivalent so nothing here needs custom code in the WordPress build:

     mobileNav()    → Elementor Pro Nav Menu widget (built-in hamburger)
     stickyHeader() → Elementor Pro Motion Effects ▸ Sticky
     reveal()       → Elementor Motion Effects ▸ Entrance Animation
     counters()     → Elementor Counter widget
     accordions()   → Elementor Accordion widget
     tabs()         → Elementor Tabs widget
     lightbox()     → Elementor Gallery widget lightbox
     year()         → Elementor shortcode / dynamic tag
     themeSwitch()  → DRAFT ONLY — not built in WordPress
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Mobile navigation ------------------------------------------------ */
  function mobileNav() {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.nav');
    if (!toggle || !nav) return;

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    }

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 1024) setOpen(false);
    });
  }

  /* ---- Sticky header shadow --------------------------------------------- */
  function stickyHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var sentinel = document.createElement('div');
    header.parentNode.insertBefore(sentinel, header);
    new IntersectionObserver(function (entries) {
      header.classList.toggle('is-stuck', !entries[0].isIntersecting);
    }, { rootMargin: '0px' }).observe(sentinel);
  }

  /* ---- Scroll reveal ----------------------------------------------------- */
  function reveal() {
    var items = document.querySelectorAll('[data-reveal]');
    if (!items.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---- Animated counters ------------------------------------------------- */
  function counters() {
    var els = document.querySelectorAll('[data-count-to]');
    if (!els.length) return;

    function run(el) {
      var target = parseFloat(el.getAttribute('data-count-to'));
      var decimals = parseInt(el.getAttribute('data-count-decimals') || '0', 10);
      if (reduceMotion) { el.textContent = target.toFixed(decimals); return; }
      var start = performance.now();
      var dur = 1400;
      (function step(now) {
        var p = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * eased).toFixed(decimals);
        if (p < 1) requestAnimationFrame(step);
      })(start);
    }

    if (!('IntersectionObserver' in window)) { els.forEach(run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { run(entry.target); io.unobserve(entry.target); }
      });
    }, { threshold: 0.5 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---- Accordions -------------------------------------------------------- */
  function accordions() {
    document.querySelectorAll('.accordion').forEach(function (acc) {
      var single = acc.getAttribute('data-single') !== 'false';
      acc.querySelectorAll('.accordion__trigger').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var panel = document.getElementById(btn.getAttribute('aria-controls'));
          var open = btn.getAttribute('aria-expanded') === 'true';
          if (single) {
            acc.querySelectorAll('.accordion__trigger').forEach(function (other) {
              if (other === btn) return;
              other.setAttribute('aria-expanded', 'false');
              var p = document.getElementById(other.getAttribute('aria-controls'));
              if (p) p.setAttribute('data-open', 'false');
            });
          }
          btn.setAttribute('aria-expanded', String(!open));
          if (panel) panel.setAttribute('data-open', String(!open));
        });
      });
    });
  }

  /* ---- Tabs -------------------------------------------------------------- */
  function tabs() {
    document.querySelectorAll('[data-tabs]').forEach(function (root) {
      var btns = Array.prototype.slice.call(root.querySelectorAll('.tabs__btn'));

      function select(i) {
        btns.forEach(function (b, j) {
          var panel = document.getElementById(b.getAttribute('aria-controls'));
          b.setAttribute('aria-selected', String(i === j));
          b.setAttribute('tabindex', i === j ? '0' : '-1');
          if (panel) panel.hidden = i !== j;
        });
      }

      btns.forEach(function (b, i) {
        b.addEventListener('click', function () { select(i); });
        b.addEventListener('keydown', function (e) {
          var next = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : null;
          if (next === null) return;
          e.preventDefault();
          var t = (next + btns.length) % btns.length;
          select(t);
          btns[t].focus();
        });
      });
    });
  }

  /* ---- Gallery lightbox --------------------------------------------------- */
  function lightbox() {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
    if (!items.length) return;

    var box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Facility photo viewer');
    box.innerHTML =
      '<button class="lightbox__close" type="button" aria-label="Close viewer">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>' +
      '</button>' +
      '<button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Previous photo">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18 9 12l6-6"/></svg>' +
      '</button>' +
      '<img alt="">' +
      '<button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Next photo">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>' +
      '</button>' +
      '<p class="lightbox__caption"></p>';
    document.body.appendChild(box);

    var img = box.querySelector('img');
    var cap = box.querySelector('.lightbox__caption');
    var index = 0;
    var lastFocus = null;

    function show(i) {
      index = (i + items.length) % items.length;
      var source = items[index].querySelector('img');
      var caption = items[index].getAttribute('data-caption') || (source && source.alt) || '';
      img.src = source.getAttribute('data-full') || source.src;
      img.alt = caption;
      cap.textContent = caption + '  ·  ' + (index + 1) + ' / ' + items.length;
    }

    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      box.querySelector('.lightbox__close').focus();
    }

    function close() {
      box.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }

    items.forEach(function (item, i) {
      item.addEventListener('click', function () { open(i); });
      // role="button" elements do not fire click from the keyboard on their own
      item.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); }
      });
    });

    box.querySelector('.lightbox__close').addEventListener('click', close);
    box.querySelector('.lightbox__nav--prev').addEventListener('click', function () { show(index - 1); });
    box.querySelector('.lightbox__nav--next').addEventListener('click', function () { show(index + 1); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    document.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
  }

  /* ---- Demo form handling (replaced by Elementor Form in WP) ------------- */
  function demoForm() {
    var form = document.querySelector('[data-demo-form]');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.form-note');
      if (note) {
        note.hidden = false;
        note.textContent = 'Draft preview — in the live WordPress site this submits through Elementor Forms to info@satcomgs.com.';
        note.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
      }
    });
  }

  /* ---- Theme switch (draft only) ----------------------------------------
     Lets the client compare the light and dark-space directions. The chosen
     theme is remembered across pages. This is NOT part of the WordPress
     build — once a direction is picked, only that one gets built. ---------- */
  function themeSwitch() {
    var btns = document.querySelectorAll('[data-theme-set]');
    if (!btns.length) return;

    function apply(theme, persist) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      btns.forEach(function (b) {
        b.setAttribute('aria-pressed',
          String(b.getAttribute('data-theme-set') === theme));
      });
      if (persist) {
        try { localStorage.setItem('sgs-theme', theme); } catch (e) {}
      }
    }

    var stored = 'light';
    try { stored = localStorage.getItem('sgs-theme') || 'light'; } catch (e) {}
    apply(stored === 'dark' ? 'dark' : 'light', false);

    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        apply(b.getAttribute('data-theme-set'), true);
      });
    });
  }

  /* ---- Current year ------------------------------------------------------ */
  function year() {
    document.querySelectorAll('[data-year]').forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  function init() {
    themeSwitch();
    mobileNav(); stickyHeader(); reveal(); counters();
    accordions(); tabs(); lightbox(); demoForm(); year();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
