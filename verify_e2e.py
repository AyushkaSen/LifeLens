import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

# 1. Test Index HTML
res_root = client.get("/")
assert res_root.status_code == 200, f"Root failed: {res_root.status_code}"
assert "LifeLens" in res_root.text, "Brand missing in HTML"
assert "plotly-2.35.2" in res_root.text, "Plotly CDN missing"
print("[PASS] Root HTML served successfully with Plotly and LifeLens UI")

# 2. Test Task Creation
task_payload = {
    "title": "Deep Learning Architecture Review",
    "category": "Deep Work",
    "priority": "High",
    "estimated_duration_minutes": 45,
}
res_task = client.post("/api/tasks", json=task_payload)
assert res_task.status_code == 201, f"Task create failed: {res_task.text}"
task_data = res_task.json()
task_id = task_data["id"]
print(f"[PASS] Created Task ID {task_id}: {task_data['title']}")

# 3. Test Pomodoro Focus Session Tied to Task
timer_payload = {
    "task_id": task_id,
    "planned_duration_minutes": 45,
    "actual_duration_minutes": 48.5,
    "status": "completed",
    "notes": "Deep focus sprint completed",
}
res_timer = client.post("/api/timer/sessions", json=timer_payload)
assert res_timer.status_code == 201, f"Timer session failed: {res_timer.text}"
timer_data = res_timer.json()
print(f"[PASS] Recorded Focus Session ID {timer_data['id']} for Task \"{timer_data['task_title']}\": {timer_data['actual_duration_minutes']} mins")

# 4. Test Structured Meal Logging
meal_payload = {
    "meal_type": "Breakfast",
    "notes": "High-protein morning fuel",
    "items": [
        {"food_name": "Whole Egg, Raw or Cooked", "quantity": 2.0, "unit": "egg"},
        {"food_name": "Rolled Oats / Oatmeal (Dry)", "quantity": 1.0, "unit": "cup"},
        {"food_name": "Banana, Fresh", "quantity": 1.0, "unit": "banana"},
    ],
}
res_meal = client.post("/api/meals", json=meal_payload)
assert res_meal.status_code == 201, f"Meal create failed: {res_meal.text}"
meal_data = res_meal.json()
print(f"[PASS] Logged Meal ID {meal_data['id']}: {meal_data['total_calories']} kcal, {meal_data['total_protein_g']}g Protein, {len(meal_data['items'])} items")

# 5. Verify Analytics Dashboard
res_dash = client.get("/api/analytics/dashboard?days=7")
assert res_dash.status_code == 200, f"Dashboard failed: {res_dash.text}"
dash_data = res_dash.json()

print("\n[PASS] Dashboard Metric Cards:")
for c in dash_data["cards"]:
    print(f"   - {c['title']}: {c['value']} ({c['subtext']})")

print("\n[PASS] Plotly Charts Generated:")
for plot_key, plot_spec in dash_data["plots"].items():
    traces = len(plot_spec.get("data", []))
    print(f"   - {plot_key}: {traces} trace(s) rendered")

print("\n=== ALL PHASE 1 MVP COMPONENTS OPERATIONAL END-TO-END! ===")
