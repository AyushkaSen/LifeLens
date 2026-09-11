/**
 * LifeLens - Core SPA Controller
 */

const App = {
  activeView: 'dashboard',

  init() {
    this.setupNavigation();
    this.updateHeaderDate();
    this.showView('dashboard');
  },

  setupNavigation() {
    document.querySelectorAll('[data-path]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const view = link.getAttribute('data-path');
        this.showView(view);
      });
    });

    // Quick Log button in header
    const quickLogBtn = document.getElementById('quick-log-btn');
    if (quickLogBtn) {
      quickLogBtn.addEventListener('click', () => {
        this.showView('meals');
        setTimeout(() => {
          document.getElementById('meal-food-input')?.focus();
        }, 100);
      });
    }
  },

  showView(viewName) {
    this.activeView = viewName;

    // Update nav links styling
    document.querySelectorAll('[data-path]').forEach(link => {
      const path = link.getAttribute('data-path');
      if (path === viewName) {
        link.classList.add('bg-surface-container', 'text-on-surface', 'font-medium');
        link.classList.remove('text-on-surface-variant');
      } else {
        link.classList.remove('bg-surface-container', 'text-on-surface', 'font-medium');
        link.classList.add('text-on-surface-variant');
      }
    });

    // Hide all view panels
    document.querySelectorAll('.view-panel').forEach(panel => {
      panel.classList.add('hidden');
    });

    // Show target view panel
    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.remove('hidden');
    }

    // Trigger view-specific refreshes
    if (viewName === 'dashboard') {
      if (window.DashboardView) DashboardView.load();
    } else if (viewName === 'tasks') {
      if (window.TasksView) TasksView.load();
    } else if (viewName === 'focus-timer') {
      if (window.TimerView) TimerView.load();
    } else if (viewName === 'meals') {
      if (window.MealsView) MealsView.load();
    }
  },

  updateHeaderDate() {
    const el = document.getElementById('header-date-display');
    if (el) {
      const now = new Date();
      const options = { weekday: 'long', month: 'short', day: 'numeric' };
      el.textContent = now.toLocaleDateString('en-US', options);
    }
  },

  showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    const isError = type === 'error';
    toast.className = `flex items-center gap-2.5 px-4 py-3 rounded-lg shadow-lg text-body-sm font-medium transition-all transform duration-300 translate-y-2 opacity-0 ${
      isError ? 'bg-red-900 text-white' : 'bg-primary-container text-white'
    }`;
    
    toast.innerHTML = `
      <span class="material-symbols-outlined text-[18px]">${isError ? 'error' : 'check_circle'}</span>
      <span>${message}</span>
    `;

    toastContainer.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
