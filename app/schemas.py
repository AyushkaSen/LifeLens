from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Task Schemas
# ==========================================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="Work", max_length=50)
    priority: str = Field(default="Medium", max_length=20)
    deadline: Optional[datetime] = None
    estimated_duration_minutes: int = Field(default=25, ge=1, le=1440)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    completed_at: Optional[datetime] = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==========================================
# Focus Session Schemas
# ==========================================

class FocusSessionBase(BaseModel):
    task_id: Optional[int] = None
    planned_duration_minutes: int = Field(default=25, ge=1, le=720)
    actual_duration_minutes: float = Field(default=0.0, ge=0.0)
    status: str = Field(default="completed")
    notes: Optional[str] = None


class FocusSessionCreate(FocusSessionBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class FocusSessionRead(FocusSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime
    task_title: Optional[str] = None


# ==========================================
# Nutrition & Meal Schemas
# ==========================================

class MealItemBase(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=150)
    quantity: float = Field(default=1.0, gt=0.0)
    unit: str = Field(default="serving", max_length=50)


class MealItemCreate(MealItemBase):
    pass


class MealItemRead(MealItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_id: int
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    matched_food_id: Optional[str] = None
    created_at: datetime


class MealBase(BaseModel):
    meal_type: str = Field(default="Lunch", max_length=30)
    meal_time: Optional[datetime] = None
    notes: Optional[str] = None


class MealCreate(MealBase):
    items: List[MealItemCreate] = Field(..., min_length=1)


class MealRead(MealBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_time: datetime
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    created_at: datetime
    items: List[MealItemRead] = []


class FoodReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: Optional[str] = None
    serving_size: float
    serving_unit: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    common_units: Optional[Dict[str, float]] = None


class NutritionCalculateRequest(BaseModel):
    food_name: str
    quantity: float = 1.0
    unit: str = "serving"


class NutritionCalculateResponse(BaseModel):
    food_name: str
    quantity: float
    unit: str
    matched_food_id: Optional[str] = None
    matched_food_name: Optional[str] = None
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    is_exact_match: bool


# ==========================================
# Dashboard & Analytics Schemas
# ==========================================

class MetricCard(BaseModel):
    title: str
    value: str
    subtext: str
    progress: Optional[float] = None
    trend: Optional[str] = None


class DashboardOverview(BaseModel):
    cards: List[MetricCard]
    plots: Dict[str, Any]  # Plotly figure JSON specs
