/**
 * LifeLens - Pomodoro & Focus Timer Controller
 */

const TimerView = {
  totalSeconds: 25 * 60,
  remainingSeconds: 25 * 60,
  isRunning: false,
  timerInterval: null,
  selectedTaskId: null,
  selectedTaskTitle: '',
  selectedModeMins: 25,
  sessionStartTime: null,

  async load() {
    this.populateTaskDropdown();
    this.loadSessionHistory();
    this.updateDisplay();
  },

  async populateTaskDropdown() {
    const select = document.getElementById('timer-task-select');
    if (!select) return;

    try {
      const res = await fetch('/api/tasks?status=pending');
      if (!res.ok) throw new Error('Failed to fetch tasks');
      const tasks = await res.json();

      let optionsHtml = '<option value="">-- General Focus Session (No Task) --</option>';
      tasks.forEach(t => {
        const isSelected = this.selectedTaskId == t.id ? 'selected' : '';
        optionsHtml += `<option value="${t.id}" ${isSelected}>${t.title} (${t.estimated_duration_minutes}m est)</option>`;
      });
      select.innerHTML = optionsHtml;
    } catch (err) {
      console.error('Timer task populate error:', err);
    }
  },

  async loadSessionHistory() {
    const listEl = document.getElementById('timer-history-list');
    if (!listEl) return;

    try {
      const res = await fetch('/api/timer/sessions?limit=15');
      if (!res.ok) throw new Error('Failed to fetch sessions');
      const sessions = await res.json();

      if (sessions.length === 0) {
        listEl.innerHTML = '<p class="text-body-sm text-on-surface-variant text-center py-4">No focus blocks recorded yet today.</p>';
        return;
      }

      listEl.innerHTML = sessions.map(s => {
        const dateStr = new Date(s.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
          <div class="flex items-center justify-between p-3 rounded-lg bg-surface-container-low border border-surface-container-high/40">
            <div class="flex items-center gap-3">
              <span class="w-2.5 h-2.5 rounded-full ${s.status === 'completed' ? 'bg-primary-container' : 'bg-amber-500'}"></span>
              <div>
                <p class="font-body-md font-semibold text-on-surface text-[13px]">${s.task_title || 'General Focus Block'}</p>
                <p class="font-mono text-[11px] text-on-surface-variant">${dateStr} • Planned ${s.planned_duration_minutes}m</p>
              </div>
            </div>
            <div class="text-right">
              <span class="font-mono font-bold text-primary text-[13px]">${Math.round(s.actual_duration_minutes)} mins</span>
              <span class="block text-[10px] uppercase font-mono text-on-surface-variant">${s.status}</span>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.error('Session history error:', err);
    }
  },

  selectTask(taskId, taskTitle, durationMins) {
    this.selectedTaskId = taskId;
    this.selectedTaskTitle = taskTitle;
    if (durationMins) {
      this.setDuration(durationMins);
    }
    const select = document.getElementById('timer-task-select');
    if (select) select.value = taskId;
  },

  setDuration(minutes) {
    if (this.isRunning) return;
    this.selectedModeMins = minutes;
    this.totalSeconds = minutes * 60;
    this.remainingSeconds = this.totalSeconds;
    this.updateDisplay();

    // Update active pill button
    document.querySelectorAll('.timer-mode-btn').forEach(btn => {
      if (parseInt(btn.getAttribute('data-mins')) === minutes) {
        btn.classList.add('bg-primary-container', 'text-white');
        btn.classList.remove('bg-surface-container-low', 'text-on-surface');
      } else {
        btn.classList.remove('bg-primary-container', 'text-white');
        btn.classList.add('bg-surface-container-low', 'text-on-surface');
      }
    });
  },

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    if (!this.sessionStartTime) {
      this.sessionStartTime = new Date();
    }

    this.timerInterval = setInterval(() => {
      if (this.remainingSeconds > 0) {
        this.remainingSeconds--;
        this.updateDisplay();
      } else {
        this.complete(true);
      }
    }, 1000);

    this.updateControls();
  },

  pause() {
    if (!this.isRunning) return;
    this.isRunning = false;
    clearInterval(this.timerInterval);
    this.updateControls();
  },

  reset() {
    this.pause();
    this.remainingSeconds = this.totalSeconds;
    this.sessionStartTime = null;
    this.updateDisplay();
    this.updateControls();
  },

  async complete(isAutoFinished = false) {
    this.pause();
    const elapsedSeconds = this.totalSeconds - this.remainingSeconds;
    const actualMinutes = Math.max(1, Math.round((elapsedSeconds / 60) * 10) / 10);

    const taskSelect = document.getElementById('timer-task-select');
    const taskId = taskSelect && taskSelect.value ? parseInt(taskSelect.value) : this.selectedTaskId;

    const payload = {
      task_id: taskId,
      planned_duration_minutes: this.selectedModeMins,
      actual_duration_minutes: actualMinutes,
      status: isAutoFinished || this.remainingSeconds === 0 ? 'completed' : 'interrupted',
      notes: isAutoFinished ? 'Full timer sprint completed' : 'Logged manual session completion',
      start_time: this.sessionStartTime ? this.sessionStartTime.toISOString() : new Date().toISOString(),
      end_time: new Date().toISOString(),
    };

    try {
      const res = await fetch('/api/timer/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to save focus session');
      App.showToast(`Logged ${actualMinutes}m focus session!`);
      this.reset();
      this.loadSessionHistory();
      if (window.DashboardView) window.DashboardView.load();
    } catch (err) {
      App.showToast('Could not save session', 'error');
    }
  },

  updateDisplay() {
    const mins = Math.floor(this.remainingSeconds / 60);
    const secs = this.remainingSeconds % 60;
    const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    const timerNumEl = document.getElementById('timer-time-display');
    if (timerNumEl) timerNumEl.textContent = timeStr;

    // Progress circle
    const circle = document.getElementById('timer-circle-bar');
    if (circle) {
      const circumference = 2 * Math.PI * 88; // r=88
      const progress = (this.totalSeconds - this.remainingSeconds) / this.totalSeconds;
      const offset = circumference * (1 - progress);
      circle.style.strokeDasharray = `${circumference}`;
      circle.style.strokeDashoffset = `${offset}`;
    }
  },

  updateControls() {
    const startBtn = document.getElementById('timer-start-btn');
    const pauseBtn = document.getElementById('timer-pause-btn');

    if (startBtn && pauseBtn) {
      if (this.isRunning) {
        startBtn.classList.add('hidden');
        pauseBtn.classList.remove('hidden');
      } else {
        startBtn.classList.remove('hidden');
        pauseBtn.classList.add('hidden');
      }
    }
  }
};

window.TimerView = TimerView;

window.addEventListener('DOMContentLoaded', () => {
  // Timer mode buttons
  document.querySelectorAll('.timer-mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const mins = parseInt(btn.getAttribute('data-mins'));
      TimerView.setDuration(mins);
    });
  });

  // Controls
  document.getElementById('timer-start-btn')?.addEventListener('click', () => TimerView.start());
  document.getElementById('timer-pause-btn')?.addEventListener('click', () => TimerView.pause());
  document.getElementById('timer-reset-btn')?.addEventListener('click', () => TimerView.reset());
  document.getElementById('timer-finish-btn')?.addEventListener('click', () => TimerView.complete(false));
});
