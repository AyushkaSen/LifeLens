from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="Work")  # Work, Deep Work, Study, Health, Personal
    priority = Column(String(20), nullable=False, default="Medium")  # Low, Medium, High, Urgent
    status = Column(String(20), nullable=False, default="pending")  # pending, in_progress, completed, cancelled
    deadline = Column(DateTime, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=False, default=25)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    focus_sessions = relationship("FocusSession", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_created_at", "created_at"),
    )


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    start_time = Column(DateTime, nullable=False, default=func.now())
    end_time = Column(DateTime, nullable=True)
    planned_duration_minutes = Column(Integer, nullable=False, default=25)
    actual_duration_minutes = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="completed")  # completed, interrupted, paused, abandoned
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    task = relationship("Task", back_populates="focus_sessions")

    __table_args__ = (
        Index("idx_focus_sessions_start_time", "start_time"),
        Index("idx_focus_sessions_task_id", "task_id"),
    )


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meal_type = Column(String(30), nullable=False, default="Lunch")  # Breakfast, Lunch, Dinner, Snack, Pre-Workout, Post-Workout
    meal_time = Column(DateTime, nullable=False, default=func.now())
    notes = Column(Text, nullable=True)
    total_calories = Column(Float, nullable=False, default=0.0)
    total_protein_g = Column(Float, nullable=False, default=0.0)
    total_carbs_g = Column(Float, nullable=False, default=0.0)
    total_fat_g = Column(Float, nullable=False, default=0.0)
    total_fiber_g = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=func.now())

    items = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_meals_meal_time", "meal_time"),
    )


class MealItem(Base):
    __tablename__ = "meal_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    food_name = Column(String(150), nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String(50), nullable=False, default="serving")  # g, oz, cup, tbsp, slice, item, serving
    calories = Column(Float, nullable=False, default=0.0)
    protein_g = Column(Float, nullable=False, default=0.0)
    carbs_g = Column(Float, nullable=False, default=0.0)
    fat_g = Column(Float, nullable=False, default=0.0)
    fiber_g = Column(Float, nullable=False, default=0.0)
    matched_food_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    meal = relationship("Meal", back_populates="items")

    __table_args__ = (
        Index("idx_meal_items_meal_id", "meal_id"),
    )


class FoodReference(Base):
    __tablename__ = "food_reference"

    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=True)
    serving_size = Column(Float, nullable=False, default=100.0)
    serving_unit = Column(String(20), nullable=False, default="g")
    calories_per_100g = Column(Float, nullable=False, default=0.0)
    protein_per_100g = Column(Float, nullable=False, default=0.0)
    carbs_per_100g = Column(Float, nullable=False, default=0.0)
    fat_per_100g = Column(Float, nullable=False, default=0.0)
    fiber_per_100g = Column(Float, nullable=False, default=0.0)
    common_units = Column(JSON, nullable=True)
