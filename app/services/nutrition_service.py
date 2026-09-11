import json
import os
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.config import USDA_DATA_PATH
from app.models import FoodReference, Meal, MealItem
from app.schemas import (
    FoodReferenceRead,
    NutritionCalculateResponse,
    MealCreate,
    MealRead,
    MealItemRead,
)

# In-memory food cache for rapid lookups
_FOOD_CACHE: List[dict] = []


def load_food_cache() -> List[dict]:
    global _FOOD_CACHE
    if not _FOOD_CACHE and os.path.exists(USDA_DATA_PATH):
        with open(USDA_DATA_PATH, "r", encoding="utf-8") as f:
            _FOOD_CACHE = json.load(f)
    return _FOOD_CACHE


def seed_food_reference_db(db: Session):
    """Seed the SQLite food_reference table from bundled USDA dataset if empty."""
    count = db.query(FoodReference).count()
    if count == 0:
        foods = load_food_cache()
        for item in foods:
            ref = FoodReference(
                id=item["id"],
                name=item["name"],
                category=item.get("category"),
                serving_size=item.get("serving_size", 100.0),
                serving_unit=item.get("serving_unit", "g"),
                calories_per_100g=item.get("calories_per_100g", 0.0),
                protein_per_100g=item.get("protein_per_100g", 0.0),
                carbs_per_100g=item.get("carbs_per_100g", 0.0),
                fat_per_100g=item.get("fat_per_100g", 0.0),
                fiber_per_100g=item.get("fiber_per_100g", 0.0),
                common_units=item.get("common_units", {}),
            )
            db.add(ref)
        db.commit()


def ensure_seeded(db: Session):
    count = db.query(FoodReference).count()
    if count == 0:
        seed_food_reference_db(db)


def search_foods(query: str, db: Session, limit: int = 15) -> List[FoodReferenceRead]:
    ensure_seeded(db)
    q = query.strip().lower()
    if not q:
        items = db.query(FoodReference).limit(limit).all()
        return [FoodReferenceRead.model_validate(item) for item in items]

    # Search in DB
    items = (
        db.query(FoodReference)
        .filter(FoodReference.name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    return [FoodReferenceRead.model_validate(item) for item in items]


def find_best_food_match(food_name: str, db: Session) -> Optional[FoodReference]:
    ensure_seeded(db)
    name_clean = food_name.strip().lower()

    # 1. Exact ID or Exact Name
    id_match = db.query(FoodReference).filter(FoodReference.id == name_clean).first()
    if id_match:
        return id_match

    exact = db.query(FoodReference).filter(FoodReference.name.ilike(name_clean)).first()
    if exact:
        return exact

    # 2. Common natural aliases
    aliases = {
        "egg": "egg_whole_raw",
        "eggs": "egg_whole_raw",
        "toast": "whole_wheat_bread",
        "bread": "whole_wheat_bread",
        "rice": "white_rice_cooked",
        "chicken": "chicken_breast_cooked",
        "salmon": "salmon_atlantic_cooked",
        "oats": "rolled_oats",
        "oatmeal": "rolled_oats",
        "yogurt": "greek_yogurt_plain_0",
        "milk": "milk_whole_3_25",
        "beef": "ground_beef_90_10",
        "steak": "ground_beef_90_10",
    }
    if name_clean in aliases:
        alias_match = db.query(FoodReference).filter(FoodReference.id == aliases[name_clean]).first()
        if alias_match:
            return alias_match

    # 3. Search matching candidates and rank
    candidates = db.query(FoodReference).filter(FoodReference.name.ilike(f"%{name_clean}%")).all()
    if not candidates:
        words = [w for w in name_clean.split() if len(w) > 2]
        for w in words:
            candidates.extend(db.query(FoodReference).filter(FoodReference.name.ilike(f"%{w}%")).all())

    if candidates:
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.id not in seen:
                seen.add(c.id)
                unique_candidates.append(c)

        def score_candidate(cand: FoodReference) -> int:
            cand_lower = cand.name.lower()
            score = 0
            if cand_lower == name_clean:
                score += 100
            if cand_lower.startswith(name_clean):
                score += 50
            if any(w == name_clean for w in cand_lower.replace(",", "").split()):
                score += 40
            if "whole" in cand_lower and ("egg" in name_clean or "wheat" in name_clean):
                score += 25
            if "white" in cand_lower and "white" not in name_clean:
                score -= 35
            return score

        unique_candidates.sort(key=score_candidate, reverse=True)
        return unique_candidates[0]

    return None


def calculate_nutrition(
    food_name: str, quantity: float, unit: str, db: Session
) -> NutritionCalculateResponse:
    matched = find_best_food_match(food_name, db)
    unit_norm = unit.strip().lower()

    if matched:
        # Determine gram multiplier
        common_units = matched.common_units or {}
        gram_weight = None

        # Check explicit unit in common_units
        if unit_norm in common_units:
            gram_weight = quantity * float(common_units[unit_norm])
        elif unit_norm.rstrip("s") in common_units:
            gram_weight = quantity * float(common_units[unit_norm.rstrip("s")])
        elif unit_norm in ["g", "gram", "grams"]:
            gram_weight = quantity
        elif unit_norm in ["oz", "ounce", "ounces"]:
            gram_weight = quantity * 28.3495
        elif unit_norm in ["kg", "kilogram"]:
            gram_weight = quantity * 1000.0
        elif unit_norm in ["serving", "servings"]:
            gram_weight = quantity * matched.serving_size
        else:
            # Fallback to standard serving size
            gram_weight = quantity * matched.serving_size

        factor = gram_weight / 100.0
        calories = round(matched.calories_per_100g * factor, 1)
        protein = round(matched.protein_per_100g * factor, 1)
        carbs = round(matched.carbs_per_100g * factor, 1)
        fat = round(matched.fat_per_100g * factor, 1)
        fiber = round(matched.fiber_per_100g * factor, 1)

        return NutritionCalculateResponse(
            food_name=food_name,
            quantity=quantity,
            unit=unit,
            matched_food_id=matched.id,
            matched_food_name=matched.name,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            fiber_g=fiber,
            is_exact_match=True,
        )

    # Fallback estimate when food is not in reference dataset
    est_calories = round(quantity * 150.0, 1)
    return NutritionCalculateResponse(
        food_name=food_name,
        quantity=quantity,
        unit=unit,
        matched_food_id=None,
        matched_food_name="Generic Estimate",
        calories=est_calories,
        protein_g=round(quantity * 5.0, 1),
        carbs_g=round(quantity * 20.0, 1),
        fat_g=round(quantity * 5.0, 1),
        fiber_g=round(quantity * 2.0, 1),
        is_exact_match=False,
    )


def create_meal(db: Session, meal_in: MealCreate) -> MealRead:
    meal_time = meal_in.meal_time or datetime.now(timezone.utc)

    meal = Meal(
        meal_type=meal_in.meal_type.strip() if meal_in.meal_type else "Lunch",
        meal_time=meal_time,
        notes=meal_in.notes,
        total_calories=0.0,
        total_protein_g=0.0,
        total_carbs_g=0.0,
        total_fat_g=0.0,
        total_fiber_g=0.0,
    )
    db.add(meal)
    db.flush()  # get meal.id

    tot_cal = 0.0
    tot_prot = 0.0
    tot_carb = 0.0
    tot_fat = 0.0
    tot_fib = 0.0
    saved_items = []

    for item_in in meal_in.items:
        calc = calculate_nutrition(item_in.food_name, item_in.quantity, item_in.unit, db)
        item = MealItem(
            meal_id=meal.id,
            food_name=item_in.food_name.strip(),
            quantity=item_in.quantity,
            unit=item_in.unit.strip(),
            calories=calc.calories,
            protein_g=calc.protein_g,
            carbs_g=calc.carbs_g,
            fat_g=calc.fat_g,
            fiber_g=calc.fiber_g,
            matched_food_id=calc.matched_food_id,
        )
        db.add(item)
        db.flush()

        tot_cal += calc.calories
        tot_prot += calc.protein_g
        tot_carb += calc.carbs_g
        tot_fat += calc.fat_g
        tot_fib += calc.fiber_g

        saved_items.append(
            MealItemRead(
                id=item.id,
                meal_id=item.meal_id,
                food_name=item.food_name,
                quantity=item.quantity,
                unit=item.unit,
                calories=item.calories,
                protein_g=item.protein_g,
                carbs_g=item.carbs_g,
                fat_g=item.fat_g,
                fiber_g=item.fiber_g,
                matched_food_id=item.matched_food_id,
                created_at=item.created_at,
            )
        )

    meal.total_calories = round(tot_cal, 1)
    meal.total_protein_g = round(tot_prot, 1)
    meal.total_carbs_g = round(tot_carb, 1)
    meal.total_fat_g = round(tot_fat, 1)
    meal.total_fiber_g = round(tot_fib, 1)

    db.commit()
    db.refresh(meal)

    return MealRead(
        id=meal.id,
        meal_type=meal.meal_type,
        meal_time=meal.meal_time,
        notes=meal.notes,
        total_calories=meal.total_calories,
        total_protein_g=meal.total_protein_g,
        total_carbs_g=meal.total_carbs_g,
        total_fat_g=meal.total_fat_g,
        total_fiber_g=meal.total_fiber_g,
        created_at=meal.created_at,
        items=saved_items,
    )


def get_meals(db: Session, limit: int = 50) -> List[MealRead]:
    meals = db.query(Meal).order_by(desc(Meal.meal_time)).limit(limit).all()
    results = []
    for meal in meals:
        items = [
            MealItemRead(
                id=it.id,
                meal_id=it.meal_id,
                food_name=it.food_name,
                quantity=it.quantity,
                unit=it.unit,
                calories=it.calories,
                protein_g=it.protein_g,
                carbs_g=it.carbs_g,
                fat_g=it.fat_g,
                fiber_g=it.fiber_g,
                matched_food_id=it.matched_food_id,
                created_at=it.created_at,
            )
            for it in meal.items
        ]
        results.append(
            MealRead(
                id=meal.id,
                meal_type=meal.meal_type,
                meal_time=meal.meal_time,
                notes=meal.notes,
                total_calories=meal.total_calories,
                total_protein_g=meal.total_protein_g,
                total_carbs_g=meal.total_carbs_g,
                total_fat_g=meal.total_fat_g,
                total_fiber_g=meal.total_fiber_g,
                created_at=meal.created_at,
                items=items,
            )
        )
    return results


def delete_meal(db: Session, meal_id: int) -> bool:
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        return False
    db.delete(meal)
    db.commit()
    return True
