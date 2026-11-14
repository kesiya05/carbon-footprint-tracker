"""Fill the database with SYNTHETIC demo data: 7 branches, 12 months.

    python -m app.seed

The numbers are random but seeded, so everyone gets the same demo. Not real restaurant data.
"""
import random
from datetime import date

from . import models
from .db import Base, SessionLocal, engine
from .factors import FACTORS, co2e

BRANCHES = [f"Branch {i}" for i in range(1, 8)]
# typical monthly quantity per branch (rough, synthetic)
MONTHLY = {"electricity": 5200, "natural_gas": 900, "diesel": 140, "food_waste": 310, "beef": 160,
           "poultry": 260, "dairy": 220, "vegetables": 520, "water": 120}


def seed(db, year: int = 2025, seed_value: int = 7) -> int:
    rnd = random.Random(seed_value)
    n = 0
    for bi, branch in enumerate(BRANCHES):
        size = 0.8 + bi * 0.07
        for month in range(1, 13):
            winter = 1.25 if month in (12, 1, 2) else 1.0
            for cat, base in MONTHLY.items():
                qty = base * size * rnd.uniform(0.85, 1.15) * (winter if cat in ("natural_gas", "electricity") else 1.0)
                db.add(models.Entry(day=date(year, month, 15), branch=branch, category=cat, quantity=round(qty, 1),
                                    unit=FACTORS[cat]["unit"], co2e_kg=co2e(cat, round(qty, 1)), note="synthetic"))
                n += 1
    db.commit()
    return n


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        print("added", seed(s), "demo entries")
