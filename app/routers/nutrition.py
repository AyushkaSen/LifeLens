from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    FoodReferenceRead,
    NutritionCalculateRequest,
    NutritionCalculateResponse,
)
from app.services import nutrition_service

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition Engine"])


@router.get("/search", response_model=List[FoodReferenceRead])
def search_food_database(
    q: str = Query("", description="Food name search query"),
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return nutrition_service.search_foods(q, db, limit=limit)


@router.post("/calculate", response_model=NutritionCalculateResponse)
def calculate_food_nutrition(
    calc_in: NutritionCalculateRequest,
    db: Session = Depends(get_db),
):
    return nutrition_service.calculate_nutrition(
        food_name=calc_in.food_name,
        quantity=calc_in.quantity,
        unit=calc_in.unit,
        db=db,
    )
