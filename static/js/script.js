/* ============================================================
   SMART COLLEGE ACADEMIC HUB — script.js
   ============================================================ */

/* ── Sidebar Toggle ── */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function (e) {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('menuToggle');
  if (sidebar && toggle && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
    if (window.innerWidth <= 800) {
      sidebar.classList.remove('open');
    }
  }
});

/* ── Password Toggle ── */
function togglePassword(fieldId) {
  const field = document.getElementById(fieldId);
  if (!field) return;
  field.type = field.type === 'password' ? 'text' : 'password';
}

/* ── Role Selector Styling ── */
function initRoleSelector() {
  const radios = document.querySelectorAll('.role-option input[type="radio"]');
  radios.forEach(radio => {
    radio.addEventListener('change', () => {
      radios.forEach(r => {
        r.closest('.role-option').querySelector('.role-btn').style.fontWeight = '';
      });
    });
  });
}

/* ── File Drop Zone ── */
function initFileDropZone() {
  const zone = document.getElementById('fileDropZone');
  const input = document.getElementById('id_file');
  const dropContent = document.getElementById('dropContent');
  const dropPreview = document.getElementById('dropPreview');
  const previewIcon = document.getElementById('previewIcon');
  const previewName = document.getElementById('previewName');
  const previewSize = document.getElementById('previewSize');

  if (!zone || !input) return;

  const iconMap = {
    pdf: '📄', ppt: '📊', pptx: '📊',
    doc: '📝', docx: '📝',
    png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️'
  };

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function showPreview(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    previewIcon.textContent = iconMap[ext] || '📁';
    previewName.textContent = file.name;
    previewSize.textContent = formatSize(file.size);
    dropContent.style.display = 'none';
    dropPreview.style.display = 'flex';
  }

  input.addEventListener('change', () => {
    if (input.files && input.files[0]) showPreview(input.files[0]);
  });

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });

  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      showPreview(file);
    }
  });
}

/* ── Upload Form Loading State ── */
function initUploadForm() {
  const form = document.getElementById('uploadForm');
  const submitBtn = document.getElementById('submitBtn');
  if (!form || !submitBtn) return;

  form.addEventListener('submit', () => {
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    if (btnText) btnText.style.display = 'none';
    if (btnLoading) btnLoading.style.display = 'inline';
    submitBtn.disabled = true;
  });
}

/* ── Collapsible Sections ── */
function toggleCollapse(id) {
  const body = document.getElementById(id);
  const icon = document.getElementById(id + 'Icon');
  if (!body) return;
  body.classList.toggle('hidden');
  if (icon) icon.classList.toggle('rotated');
}

/* ── Auto-dismiss Alerts ── */
function initAlerts() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.4s';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });
}

/* ── Notification Badge (Live) ── */
function initNotifPolling() {
  const badge = document.getElementById('notif-count');
  const topbarBadge = document.getElementById('topbar-notif-count');
  if (!badge && !topbarBadge) return;

  function fetchCount() {
    fetch('/api/notifications/count/')
      .then(r => r.json())
      .then(data => {
        const count = data.count || 0;
        if (badge) {
          if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
          } else {
            badge.style.display = 'none';
          }
        }
        if (topbarBadge) {
          topbarBadge.textContent = count > 0 ? `(${count})` : '';
        }
      })
      .catch(() => {});
  }

  fetchCount();
  setInterval(fetchCount, 30000); // Poll every 30s
}

/* ── Timetable empty state check ── */
function checkTimetableEmpty() {
  const sections = document.querySelectorAll('.day-section');
  const emptyEl = document.getElementById('emptyTimetable');
  if (!emptyEl) return;
  emptyEl.style.display = sections.length === 0 ? 'block' : 'none';
}

/* ── Init on DOMContentLoaded ── */
document.addEventListener('DOMContentLoaded', function () {
  initRoleSelector();
  initFileDropZone();
  initUploadForm();
  initAlerts();
  initNotifPolling();
  checkTimetableEmpty();
});
