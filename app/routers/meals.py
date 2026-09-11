from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MealCreate, MealRead
from app.services import nutrition_service

router = APIRouter(prefix="/api/meals", tags=["Meals"])


@router.post("", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def log_meal(meal_in: MealCreate, db: Session = Depends(get_db)):
    if not meal_in.items:
        raise HTTPException(status_code=400, detail="A meal must contain at least one food item")
    return nutrition_service.create_meal(db, meal_in)


@router.get("", response_model=List[MealRead])
def list_meals(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return nutrition_service.get_meals(db, limit=limit)


@router.delete("/{meal_id}", status_code=status.HTTP_200_OK)
def delete_logged_meal(meal_id: int, db: Session = Depends(get_db)):
    success = nutrition_service.delete_meal(db, meal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal not found")
    return {"message": "Meal deleted successfully", "id": meal_id}
