/**
 * LifeLens - Task Management View
 */

const TasksView = {
  tasks: [],
  filterStatus: 'all',
  filterCategory: 'all',

  async load() {
    try {
      let url = '/api/tasks';
      const params = new URLSearchParams();
      if (this.filterStatus !== 'all') params.append('status', this.filterStatus);
      if (this.filterCategory !== 'all') params.append('category', this.filterCategory);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch tasks');
      this.tasks = await res.json();
      this.render();
      this.populateTaskFilterCategories();
    } catch (err) {
      console.error('Task load error:', err);
    }
  },

  render() {
    const listEl = document.getElementById('tasks-list-container');
    const countEl = document.getElementById('tasks-total-count');
    if (!listEl) return;

    if (countEl) countEl.textContent = `${this.tasks.length} total`;

    if (this.tasks.length === 0) {
      listEl.innerHTML = `
        <div class="p-8 text-center bg-surface-container-lowest rounded-xl border border-surface-container-high/60">
          <span class="material-symbols-outlined text-[36px] text-on-surface-variant mb-2">check_circle</span>
          <p class="font-headline-sm text-on-surface">No tasks found</p>
          <p class="font-body-sm text-on-surface-variant mt-1">Add your next cognitive priority to begin tracking.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = this.tasks.map(t => {
      const isCompleted = t.status === 'completed';
      const priorityColors = {
        'Urgent': 'bg-red-50 text-red-700 border-red-200',
        'High': 'bg-amber-50 text-amber-700 border-amber-200',
        'Medium': 'bg-teal-50 text-teal-700 border-teal-200',
        'Low': 'bg-slate-50 text-slate-600 border-slate-200',
      };
      const badgeStyle = priorityColors[t.priority] || priorityColors['Medium'];

      return `
        <div class="p-4 rounded-xl bg-surface-container-lowest border border-surface-container-high/60 shadow-sm hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group">
          <div class="flex items-start gap-3.5 min-w-0">
            <button onclick="TasksView.toggleTask(${t.id})" class="mt-0.5 w-5 h-5 rounded border flex items-center justify-center transition-colors ${
              isCompleted ? 'bg-primary border-primary text-white' : 'border-slate-300 hover:border-primary'
            }">
              ${isCompleted ? '<span class="material-symbols-outlined text-[15px]">check</span>' : ''}
            </button>
            <div class="min-w-0">
              <h3 class="font-body-md font-semibold text-on-surface ${isCompleted ? 'line-through text-on-surface-variant' : ''} truncate">
                ${t.title}
              </h3>
              <div class="flex flex-wrap items-center gap-2 mt-1 font-body-sm text-on-surface-variant text-[12px]">
                <span class="px-2 py-0.5 rounded-full border text-[11px] font-medium font-mono ${badgeStyle}">
                  ${t.priority}
                </span>
                <span class="px-2 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-medium text-[11px]">
                  ${t.category}
                </span>
                <span class="flex items-center gap-1 font-mono text-[11px]">
                  <span class="material-symbols-outlined text-[14px]">timer</span>
                  ${t.estimated_duration_minutes}m est
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 self-end sm:self-auto">
            ${!isCompleted ? `
              <button onclick="TasksView.startFocusOnTask(${t.id}, '${escape(t.title)}', ${t.estimated_duration_minutes})" class="px-3 py-1.5 rounded-lg bg-surface-container-low text-primary hover:bg-primary hover:text-white font-body-sm font-medium transition-colors flex items-center gap-1 text-[12px]">
                <span class="material-symbols-outlined text-[14px]">play_arrow</span>
                <span>Focus</span>
              </button>
            ` : ''}
            <button onclick="TasksView.deleteTask(${t.id})" class="p-1.5 rounded-lg text-on-surface-variant hover:text-error hover:bg-error-container/20 transition-colors" title="Delete Task">
              <span class="material-symbols-outlined text-[17px]">delete</span>
            </button>
          </div>
        </div>
      `;
    }).join('');
  },

  async toggleTask(taskId) {
    try {
      const res = await fetch(`/api/tasks/${taskId}/toggle`, { method: 'PATCH' });
      if (!res.ok) throw new Error('Failed to toggle task status');
      await this.load();
      if (window.DashboardView) window.DashboardView.load();
    } catch (err) {
      App.showToast('Could not toggle task status', 'error');
    }
  },

  async deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      const res = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete task');
      App.showToast('Task deleted successfully');
      await this.load();
      if (window.DashboardView) window.DashboardView.load();
    } catch (err) {
      App.showToast('Could not delete task', 'error');
    }
  },

  startFocusOnTask(taskId, taskTitle, duration) {
    if (window.TimerView) {
      window.TimerView.selectTask(taskId, unescape(taskTitle), duration);
    }
    App.showView('focus-timer');
  },

  populateTaskFilterCategories() {
    const select = document.getElementById('task-category-filter');
    if (!select) return;
    const currentVal = select.value;
    const categories = ['all', 'Work', 'Deep Work', 'Study', 'Health', 'Personal'];
    select.innerHTML = categories.map(c => `
      <option value="${c}" ${c === currentVal ? 'selected' : ''}>${c === 'all' ? 'All Categories' : c}</option>
    `).join('');
  },

  setupForm() {
    const form = document.getElementById('new-task-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const titleInput = document.getElementById('task-title-input');
      const categoryInput = document.getElementById('task-category-input');
      const priorityInput = document.getElementById('task-priority-input');
      const durationInput = document.getElementById('task-duration-input');

      const payload = {
        title: titleInput.value.trim(),
        category: categoryInput.value,
        priority: priorityInput.value,
        estimated_duration_minutes: parseInt(durationInput.value) || 25,
      };

      try {
        const res = await fetch('/api/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to create task');
        
        App.showToast('Priority task added');
        form.reset();
        document.getElementById('task-modal')?.classList.add('hidden');
        await this.load();
        if (window.DashboardView) window.DashboardView.load();
      } catch (err) {
        App.showToast('Error creating task', 'error');
      }
    });

    // Filter controls
    const statusSelect = document.getElementById('task-status-filter');
    if (statusSelect) {
      statusSelect.addEventListener('change', (e) => {
        this.filterStatus = e.target.value;
        this.load();
      });
    }

    const catSelect = document.getElementById('task-category-filter');
    if (catSelect) {
      catSelect.addEventListener('change', (e) => {
        this.filterCategory = e.target.value;
        this.load();
      });
    }
  }
};

window.TasksView = TasksView;
window.addEventListener('DOMContentLoaded', () => {
  TasksView.setupForm();
});
