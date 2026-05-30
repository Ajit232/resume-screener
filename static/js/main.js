'use strict';

document.addEventListener('DOMContentLoaded', function () {

  // -----------------------------------------------------------------------
  // 1. File upload drag-and-drop
  // -----------------------------------------------------------------------
  document.querySelectorAll('.upload-zone').forEach(function (zone) {
    const input = zone.querySelector('input[type="file"]');
    const label = zone.querySelector('.upload-filename');
    if (!input) return;

    zone.addEventListener('click', function (e) {
      if (e.target !== input) input.click();
    });

    input.addEventListener('change', function () {
      if (label && input.files.length > 0) {
        label.textContent = input.files[0].name;
        label.style.color = '#4361ee';
        label.style.fontWeight = '600';
      }
    });

    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', function () {
      zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        input.files = e.dataTransfer.files;
        if (label) {
          label.textContent = e.dataTransfer.files[0].name;
          label.style.color = '#4361ee';
          label.style.fontWeight = '600';
        }
      }
    });
  });

  // -----------------------------------------------------------------------
  // 2. Progress bar animation (score bars)
  // -----------------------------------------------------------------------
  function animateProgressBars() {
    document.querySelectorAll('.progress-bar[data-value]').forEach(function (bar) {
      const target = parseFloat(bar.getAttribute('data-value')) || 0;
      bar.style.width = '0%';
      setTimeout(function () {
        bar.style.transition = 'width 0.9s cubic-bezier(.4,0,.2,1)';
        bar.style.width = Math.min(target, 100) + '%';
      }, 150);
    });
  }
  animateProgressBars();

  // -----------------------------------------------------------------------
  // 3. Auto-dismiss success/info alerts after 5 seconds
  // -----------------------------------------------------------------------
  document.querySelectorAll('.alert-success, .alert-info').forEach(function (el) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // -----------------------------------------------------------------------
  // 4. Confirm delete dialogs
  // -----------------------------------------------------------------------
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var msg = el.getAttribute('data-confirm') || 'Are you sure?';
      if (!window.confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  // -----------------------------------------------------------------------
  // 5. Score circle entrance animation
  // -----------------------------------------------------------------------
  var scoreCircles = document.querySelectorAll('.score-circle');
  if (scoreCircles.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'scale(1)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });

    scoreCircles.forEach(function (circle) {
      circle.style.opacity = '0';
      circle.style.transform = 'scale(0.85)';
      circle.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      observer.observe(circle);
    });
  }

  // -----------------------------------------------------------------------
  // 6. Navbar active link highlight
  // -----------------------------------------------------------------------
  var currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(function (link) {
    if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href')) &&
        link.getAttribute('href') !== '/') {
      link.classList.add('active');
    }
  });

  // -----------------------------------------------------------------------
  // 7. Export toast helper (called by export buttons if needed)
  // -----------------------------------------------------------------------
  window.showExportToast = function (message, type) {
    type = type || 'success';
    var container = document.getElementById('exportToastContainer');
    if (!container) return;

    var colors = {
      success: { bg: '#d1fae5', color: '#065f46', icon: 'bi-check-circle-fill' },
      error:   { bg: '#fee2e2', color: '#991b1b', icon: 'bi-exclamation-circle-fill' },
      info:    { bg: '#dbeafe', color: '#1e40af', icon: 'bi-info-circle-fill' },
    };
    var c = colors[type] || colors.success;

    var toast = document.createElement('div');
    toast.style.cssText = [
      'display:flex;align-items:center;gap:10px;',
      'padding:12px 18px;border-radius:10px;',
      'background:' + c.bg + ';color:' + c.color + ';',
      'font-size:0.875rem;font-weight:500;',
      'box-shadow:0 4px 16px rgba(0,0,0,.12);',
      'margin-top:8px;',
      'animation:fadeSlideIn .25s ease;',
      'font-family:Inter,system-ui,sans-serif;',
    ].join('');

    toast.innerHTML = '<i class="bi ' + c.icon + '"></i><span>' + message + '</span>';
    container.appendChild(toast);

    setTimeout(function () {
      toast.style.transition = 'opacity .3s ease';
      toast.style.opacity = '0';
      setTimeout(function () { toast.remove(); }, 350);
    }, 3500);
  };

  // -----------------------------------------------------------------------
  // 8. Character counter for textareas with data-maxlength
  // -----------------------------------------------------------------------
  document.querySelectorAll('textarea[data-maxlength]').forEach(function (ta) {
    var max = parseInt(ta.getAttribute('data-maxlength'));
    var counterId = ta.getAttribute('data-counter');
    var counter = counterId ? document.getElementById(counterId) : null;
    if (!counter) return;
    ta.addEventListener('input', function () {
      var remaining = max - ta.value.length;
      counter.textContent = remaining + ' characters remaining';
      counter.className = remaining < 50 ? 'text-danger small' : 'text-muted small';
    });
  });

  // -----------------------------------------------------------------------
  // 9. Smooth card hover shadow transition (already in CSS, JS fallback)
  // -----------------------------------------------------------------------
  document.querySelectorAll('.card').forEach(function (card) {
    card.addEventListener('mouseenter', function () {
      this.style.transform = 'translateY(-1px)';
    });
    card.addEventListener('mouseleave', function () {
      this.style.transform = '';
    });
  });

  // -----------------------------------------------------------------------
  // 10. Table row click → navigate to result (history page)
  // -----------------------------------------------------------------------
  document.querySelectorAll('tr[data-href]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function (e) {
      if (!e.target.closest('button, a, form')) {
        window.location.href = row.getAttribute('data-href');
      }
    });
  });

});
