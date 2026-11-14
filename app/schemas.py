from datetime import date

from pydantic import BaseModel, Field, field_validator

from .factors import FACTORS


class EntryIn(BaseModel):
    day: date
    branch: str = Field(min_length=1, max_length=60)
    category: str
    quantity: float = Field(gt=0)
    note: str = Field(default="", max_length=200)

    @field_validator("category")
    @classmethod
    def known_category(cls, v: str) -> str:
        if v not in FACTORS:
            raise ValueError(f"unknown category '{v}', use one of: {', '.join(FACTORS)}")
        return v


class GoalIn(BaseModel):
    branch: str = Field(min_length=1, max_length=60)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    target_kg: float = Field(gt=0)
