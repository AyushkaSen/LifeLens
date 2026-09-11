/**
 * LifeLens - Dashboard Analytics & Plotly Visualizations
 */

const DashboardView = {
  activeScopeDays: 7,

  async load() {
    try {
      const res = await fetch(`/api/analytics/dashboard?days=${this.activeScopeDays}`);
      if (!res.ok) throw new Error('Failed to load dashboard data');
      const data = await res.json();

      this.renderMetricCards(data.cards);
      this.renderPlotlyCharts(data.plots);
    } catch (err) {
      console.error('Dashboard load error:', err);
    }
  },

  renderMetricCards(cards) {
    if (!cards || cards.length < 4) return;

    // Card 1: Tasks Completed
    const taskCard = cards[0];
    const taskEl = document.getElementById('stat-tasks-val');
    const taskSub = document.getElementById('stat-tasks-sub');
    const taskBar = document.getElementById('stat-tasks-bar');
    if (taskEl) taskEl.innerHTML = `${taskCard.value}`;
    if (taskSub) taskSub.textContent = taskCard.subtext;
    if (taskBar) taskBar.style.width = `${taskCard.progress || 0}%`;

    // Card 2: Focus Duration
    const focusCard = cards[1];
    const focusEl = document.getElementById('stat-focus-val');
    const focusSub = document.getElementById('stat-focus-sub');
    const focusBar = document.getElementById('stat-focus-bar');
    if (focusEl) focusEl.textContent = focusCard.value;
    if (focusSub) focusSub.textContent = focusCard.subtext;
    if (focusBar) focusBar.style.width = `${focusCard.progress || 0}%`;

    // Card 3: Metabolic Fuel
    const fuelCard = cards[2];
    const fuelEl = document.getElementById('stat-fuel-val');
    const fuelSub = document.getElementById('stat-fuel-sub');
    if (fuelEl) fuelEl.textContent = fuelCard.value;
    if (fuelSub) fuelSub.textContent = fuelCard.subtext;

    // Card 4: Streak
    const streakCard = cards[3];
    const streakEl = document.getElementById('stat-streak-val');
    if (streakEl) streakEl.textContent = streakCard.value;
  },

  renderPlotlyCharts(plots) {
    if (!plots || typeof Plotly === 'undefined') return;

    const config = {
      responsive: true,
      displayModeBar: false,
    };

    // 1. Weekly Velocity Area/Line Chart
    if (plots.weekly_velocity && document.getElementById('chart-weekly-velocity')) {
      Plotly.newPlot('chart-weekly-velocity', plots.weekly_velocity.data, plots.weekly_velocity.layout, config);
    }

    // 2. Estimated vs Actual Duration Grouped Bar Chart
    if (plots.est_vs_actual && document.getElementById('chart-est-vs-actual')) {
      Plotly.newPlot('chart-est-vs-actual', plots.est_vs_actual.data, plots.est_vs_actual.layout, config);
    }

    // 3. Total Focus Time Chart
    if (plots.focus_time && document.getElementById('chart-focus-time')) {
      Plotly.newPlot('chart-focus-time', plots.focus_time.data, plots.focus_time.layout, config);
    }

    // 4. Meal Timing Chrono-Distribution
    if (plots.meal_timing && document.getElementById('chart-meal-timing')) {
      Plotly.newPlot('chart-meal-timing', plots.meal_timing.data, plots.meal_timing.layout, config);
    }

    // 5. Macronutrient Split Donut Chart
    if (plots.macro_split && document.getElementById('chart-macro-split')) {
      Plotly.newPlot('chart-macro-split', plots.macro_split.data, plots.macro_split.layout, config);
    }
  },

  setupScopeControls() {
    document.querySelectorAll('.scope-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.scope-btn').forEach(b => {
          b.classList.remove('bg-surface-container-lowest', 'shadow-sm', 'text-on-surface');
          b.classList.add('text-on-surface-variant');
        });
        btn.classList.add('bg-surface-container-lowest', 'shadow-sm', 'text-on-surface');
        btn.classList.remove('text-on-surface-variant');

        const scope = btn.getAttribute('data-scope');
        if (scope === 'today') this.activeScopeDays = 1;
        else if (scope === 'week') this.activeScopeDays = 7;
        else if (scope === 'month') this.activeScopeDays = 30;

        this.load();
      });
    });
  }
};

window.DashboardView = DashboardView;

window.addEventListener('resize', () => {
  const chartIds = [
    'chart-weekly-velocity',
    'chart-est-vs-actual',
    'chart-focus-time',
    'chart-meal-timing',
    'chart-macro-split'
  ];
  chartIds.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.data) {
      Plotly.Plots.resize(el);
    }
  });
});
