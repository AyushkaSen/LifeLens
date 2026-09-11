/**
 * LifeLens - Structured Meal Logging & Nutrition Controller
 */

const MealsView = {
  items: [],
  meals: [],

  async load() {
    this.resetForm();
    await this.loadMealHistory();
  },

  resetForm() {
    this.items = [
      { food_name: '', quantity: 1, unit: 'serving', calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0, fiber_g: 0 }
    ];
    this.renderItemRows();
    this.updateLiveMacroTotals();

    const timeInput = document.getElementById('meal-time-input');
    if (timeInput) {
      const now = new Date();
      timeInput.value = now.toTimeString().substring(0, 5);
    }
  },

  renderItemRows() {
    const container = document.getElementById('meal-items-container');
    if (!container) return;

    container.innerHTML = this.items.map((item, idx) => `
      <div class="p-3.5 rounded-xl bg-surface-container-low border border-surface-container-high/60 flex flex-col sm:flex-row sm:items-center gap-3 relative item-row" data-index="${idx}">
        <div class="flex-1 relative">
          <label class="block font-mono text-[10px] uppercase text-on-surface-variant mb-1">Food Item</label>
          <input 
            type="text" 
            value="${item.food_name}" 
            placeholder="Search e.g. eggs, oatmeal, chicken..." 
            oninput="MealsView.onFoodInput(${idx}, this.value)"
            class="w-full h-9 px-3 text-body-sm rounded-lg bg-white border border-surface-container-high text-on-surface focus:outline-none focus:ring-1 focus:ring-primary-container"
          />
          <div id="autocomplete-list-${idx}" class="absolute left-0 right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-surface-container-high z-30 max-h-48 overflow-y-auto hidden"></div>
        </div>

        <div class="w-24">
          <label class="block font-mono text-[10px] uppercase text-on-surface-variant mb-1">Qty</label>
          <input 
            type="number" 
            step="0.1" 
            min="0.1" 
            value="${item.quantity}" 
            oninput="MealsView.onQtyChange(${idx}, this.value)"
            class="w-full h-9 px-3 text-body-sm rounded-lg bg-white border border-surface-container-high text-on-surface font-mono focus:outline-none focus:ring-1 focus:ring-primary-container"
          />
        </div>

        <div class="w-32">
          <label class="block font-mono text-[10px] uppercase text-on-surface-variant mb-1">Unit</label>
          <select 
            onchange="MealsView.onUnitChange(${idx}, this.value)"
            class="w-full h-9 px-2 text-body-sm rounded-lg bg-white border border-surface-container-high text-on-surface font-mono focus:outline-none focus:ring-1 focus:ring-primary-container"
          >
            <option value="serving" ${item.unit === 'serving' ? 'selected' : ''}>serving</option>
            <option value="g" ${item.unit === 'g' ? 'selected' : ''}>grams (g)</option>
            <option value="oz" ${item.unit === 'oz' ? 'selected' : ''}>ounces (oz)</option>
            <option value="egg" ${item.unit === 'egg' ? 'selected' : ''}>egg</option>
            <option value="slice" ${item.unit === 'slice' ? 'selected' : ''}>slice</option>
            <option value="cup" ${item.unit === 'cup' ? 'selected' : ''}>cup</option>
            <option value="tbsp" ${item.unit === 'tbsp' ? 'selected' : ''}>tbsp</option>
            <option value="item" ${item.unit === 'item' ? 'selected' : ''}>item</option>
          </select>
        </div>

        <div class="w-28 text-right self-end sm:self-center pt-2 sm:pt-0">
          <span class="block font-mono font-bold text-primary text-[12px]">${item.calories} kcal</span>
          <span class="block font-mono text-[11px] text-on-surface-variant">P: ${item.protein_g}g</span>
        </div>

        ${this.items.length > 1 ? `
          <button type="button" onclick="MealsView.removeItem(${idx})" class="p-1 rounded text-on-surface-variant hover:text-error transition-colors self-end sm:self-center">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        ` : ''}
      </div>
    `).join('');
  },

  addItem() {
    this.items.push({ food_name: '', quantity: 1, unit: 'serving', calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0, fiber_g: 0 });
    this.renderItemRows();
  },

  removeItem(idx) {
    if (this.items.length > 1) {
      this.items.splice(idx, 1);
      this.renderItemRows();
      this.updateLiveMacroTotals();
    }
  },

  async onFoodInput(idx, query) {
    this.items[idx].food_name = query;
    const dropdown = document.getElementById(`autocomplete-list-${idx}`);
    if (!dropdown) return;

    if (query.trim().length < 2) {
      dropdown.classList.add('hidden');
      dropdown.innerHTML = '';
      return;
    }

    try {
      const res = await fetch(`/api/nutrition/search?q=${encodeURIComponent(query.trim())}&limit=6`);
      if (!res.ok) return;
      const results = await res.json();

      if (results.length === 0) {
        dropdown.innerHTML = `<div class="p-2.5 text-body-sm text-on-surface-variant text-center">No reference foods found</div>`;
        dropdown.classList.remove('hidden');
        return;
      }

      dropdown.innerHTML = results.map(r => `
        <div 
          onclick="MealsView.selectReferenceFood(${idx}, '${escape(r.name)}', ${r.serving_size}, '${r.serving_unit}')"
          class="px-3 py-2 text-body-sm hover:bg-surface-container cursor-pointer border-b border-surface-container-high/40 last:border-none flex items-center justify-between"
        >
          <div>
            <p class="font-medium text-on-surface">${r.name}</p>
            <p class="font-mono text-[11px] text-on-surface-variant">${r.category || 'General'} • ${r.calories_per_100g} kcal/100g</p>
          </div>
          <span class="font-mono text-[11px] text-primary">P: ${r.protein_g || r.protein_per_100g}g</span>
        </div>
      `).join('');
      dropdown.classList.remove('hidden');
    } catch (err) {
      console.error('Autocomplete error:', err);
    }
  },

  selectReferenceFood(idx, foodNameEscaped, servingSize, servingUnit) {
    const foodName = unescape(foodNameEscaped);
    this.items[idx].food_name = foodName;
    const dropdown = document.getElementById(`autocomplete-list-${idx}`);
    if (dropdown) dropdown.classList.add('hidden');
    this.recalculateItem(idx);
  },

  onQtyChange(idx, qty) {
    this.items[idx].quantity = parseFloat(qty) || 1.0;
    this.recalculateItem(idx);
  },

  onUnitChange(idx, unit) {
    this.items[idx].unit = unit;
    this.recalculateItem(idx);
  },

  async recalculateItem(idx) {
    const item = this.items[idx];
    if (!item.food_name || item.food_name.trim().length === 0) return;

    try {
      const res = await fetch('/api/nutrition/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          food_name: item.food_name,
          quantity: item.quantity,
          unit: item.unit
        })
      });
      if (!res.ok) return;
      const calc = await res.json();

      item.calories = calc.calories;
      item.protein_g = calc.protein_g;
      item.carbs_g = calc.carbs_g;
      item.fat_g = calc.fat_g;
      item.fiber_g = calc.fiber_g;

      this.renderItemRows();
      this.updateLiveMacroTotals();
    } catch (err) {
      console.error('Calculation error:', err);
    }
  },

  updateLiveMacroTotals() {
    const totalCal = this.items.reduce((acc, i) => acc + (i.calories || 0), 0);
    const totalProt = this.items.reduce((acc, i) => acc + (i.protein_g || 0), 0);
    const totalCarb = this.items.reduce((acc, i) => acc + (i.carbs_g || 0), 0);
    const totalFat = this.items.reduce((acc, i) => acc + (i.fat_g || 0), 0);
    const totalFib = this.items.reduce((acc, i) => acc + (i.fiber_g || 0), 0);

    const calEl = document.getElementById('meal-total-calories');
    const protEl = document.getElementById('meal-total-protein');
    const carbEl = document.getElementById('meal-total-carbs');
    const fatEl = document.getElementById('meal-total-fat');
    const fibEl = document.getElementById('meal-total-fiber');

    if (calEl) calEl.textContent = `${Math.round(totalCal)} kcal`;
    if (protEl) protEl.textContent = `${Math.round(totalProt * 10) / 10}g`;
    if (carbEl) carbEl.textContent = `${Math.round(totalCarb * 10) / 10}g`;
    if (fatEl) fatEl.textContent = `${Math.round(totalFat * 10) / 10}g`;
    if (fibEl) fibEl.textContent = `${Math.round(totalFib * 10) / 10}g`;
  },

  async submitMeal(e) {
    e.preventDefault();
    const typeSelect = document.getElementById('meal-type-select');
    const notesInput = document.getElementById('meal-notes-input');

    const validItems = this.items.filter(i => i.food_name && i.food_name.trim().length > 0);
    if (validItems.length === 0) {
      App.showToast('Please add at least one valid food item', 'error');
      return;
    }

    const payload = {
      meal_type: typeSelect ? typeSelect.value : 'Lunch',
      notes: notesInput ? notesInput.value.trim() : '',
      items: validItems.map(i => ({
        food_name: i.food_name.trim(),
        quantity: i.quantity,
        unit: i.unit
      }))
    };

    try {
      const res = await fetch('/api/meals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Failed to save meal');
      App.showToast('Meal logged successfully!');
      this.resetForm();
      await this.loadMealHistory();
      if (window.DashboardView) window.DashboardView.load();
    } catch (err) {
      App.showToast('Could not save meal', 'error');
    }
  },

  async loadMealHistory() {
    const listEl = document.getElementById('meals-history-list');
    if (!listEl) return;

    try {
      const res = await fetch('/api/meals?limit=20');
      if (!res.ok) throw new Error('Failed to load meals');
      this.meals = await res.json();

      if (this.meals.length === 0) {
        listEl.innerHTML = '<p class="text-body-sm text-on-surface-variant text-center py-6">No meals logged yet today.</p>';
        return;
      }

      listEl.innerHTML = this.meals.map(m => {
        const timeStr = new Date(m.meal_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const itemsSummary = m.items.map(it => `${it.quantity} ${it.unit} ${it.food_name}`).join(', ');

        return `
          <div class="p-4 rounded-xl bg-surface-container-lowest border border-surface-container-high/60 shadow-sm hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-headline-sm text-on-surface text-[15px] font-semibold">${m.meal_type}</span>
                <span class="font-mono text-[11px] px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">${timeStr}</span>
                ${m.notes ? `<span class="text-body-sm text-on-surface-variant italic text-[12px]">• "${m.notes}"</span>` : ''}
              </div>
              <p class="font-body-sm text-on-surface-variant text-[13px] line-clamp-1">${itemsSummary}</p>
              <div class="flex items-center gap-3 mt-2 font-mono text-[11px] text-on-surface-variant">
                <span>Calories: <strong class="text-primary font-bold">${Math.round(m.total_calories)} kcal</strong></span>
                <span>P: <strong>${Math.round(m.total_protein_g)}g</strong></span>
                <span>C: <strong>${Math.round(m.total_carbs_g)}g</strong></span>
                <span>F: <strong>${Math.round(m.total_fat_g)}g</strong></span>
              </div>
            </div>
            <button onclick="MealsView.deleteMeal(${m.id})" class="p-1.5 rounded-lg text-on-surface-variant hover:text-error hover:bg-error-container/20 transition-colors self-end sm:self-center" title="Delete Meal">
              <span class="material-symbols-outlined text-[17px]">delete</span>
            </button>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.error('Load meals error:', err);
    }
  },

  async deleteMeal(mealId) {
    if (!confirm('Are you sure you want to delete this meal log?')) return;
    try {
      const res = await fetch(`/api/meals/${mealId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete meal');
      App.showToast('Meal log deleted');
      await this.loadMealHistory();
      if (window.DashboardView) window.DashboardView.load();
    } catch (err) {
      App.showToast('Could not delete meal', 'error');
    }
  }
};

window.MealsView = MealsView;

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('add-meal-item-btn')?.addEventListener('click', () => MealsView.addItem());
  document.getElementById('meal-log-form')?.addEventListener('submit', (e) => MealsView.submitMeal(e));
});
