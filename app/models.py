from datetime import date

from sqlalchemy import Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[date] = mapped_column(Date, index=True)
    branch: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(12))
    co2e_kg: Mapped[float] = mapped_column(Float)
    note: Mapped[str] = mapped_column(String(200), default="")


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (UniqueConstraint("branch", "month"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch: Mapped[str] = mapped_column(String(60))
    month: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    target_kg: Mapped[float] = mapped_column(Float)
