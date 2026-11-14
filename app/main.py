from collections import defaultdict
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import models
from .db import Base, engine, get_db
from .factors import FACTORS, co2e
from .schemas import EntryIn, GoalIn

app = FastAPI(title="Carbon Footprint Tracker")
Base.metadata.create_all(engine)
STATIC = Path(__file__).parent / "static"


def entry_out(e: models.Entry) -> dict:
    return {"id": e.id, "day": e.day.isoformat(), "branch": e.branch, "category": e.category,
            "quantity": e.quantity, "unit": e.unit, "co2e_kg": e.co2e_kg, "note": e.note}


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/api/factors")
def factors():
    return FACTORS


@app.post("/api/entries", status_code=201)
def add_entry(body: EntryIn, db: Session = Depends(get_db)):
    e = models.Entry(day=body.day, branch=body.branch.strip(), category=body.category, quantity=body.quantity,
                     unit=FACTORS[body.category]["unit"], co2e_kg=co2e(body.category, body.quantity), note=body.note)
    db.add(e)
    db.commit()
    return entry_out(e)


@app.get("/api/entries")
def list_entries(branch: str | None = None, category: str | None = None, start: date | None = None,
                 end: date | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Entry)
    if branch:
        q = q.filter(models.Entry.branch == branch)
    if category:
        q = q.filter(models.Entry.category == category)
    if start:
        q = q.filter(models.Entry.day >= start)
    if end:
        q = q.filter(models.Entry.day <= end)
    return [entry_out(e) for e in q.order_by(models.Entry.day.desc(), models.Entry.id.desc()).limit(500)]


@app.delete("/api/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    e = db.get(models.Entry, entry_id)
    if e is None:
        raise HTTPException(404, "Entry not found")
    db.delete(e)
    db.commit()


@app.get("/api/summary")
def summary(branch: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Entry)
    if branch:
        q = q.filter(models.Entry.branch == branch)
    by_cat, by_month, by_branch = defaultdict(float), defaultdict(float), defaultdict(float)
    for e in q:
        by_cat[e.category] += e.co2e_kg
        by_month[e.day.strftime("%Y-%m")] += e.co2e_kg
        by_branch[e.branch] += e.co2e_kg
    total = sum(by_cat.values())
    rows = lambda d: [{"key": k, "co2e_kg": round(v, 2)} for k, v in sorted(d.items())]  # noqa: E731
    cats = [{"key": k, "co2e_kg": round(v, 2), "share": round(v / total, 4) if total else 0}
            for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1])]
    return {"total_kg": round(total, 2), "by_category": cats, "by_month": rows(by_month), "by_branch": rows(by_branch)}


@app.put("/api/goals")
def set_goal(body: GoalIn, db: Session = Depends(get_db)):
    g = db.query(models.Goal).filter_by(branch=body.branch, month=body.month).first()
    if g is None:
        g = models.Goal(branch=body.branch, month=body.month, target_kg=body.target_kg)
        db.add(g)
    else:
        g.target_kg = body.target_kg
    db.commit()
    return {"branch": g.branch, "month": g.month, "target_kg": g.target_kg}


@app.get("/api/goals/progress")
def goal_progress(month: str, db: Session = Depends(get_db)):
    out = []
    for g in db.query(models.Goal).filter_by(month=month).order_by(models.Goal.branch):
        actual = sum(e.co2e_kg for e in db.query(models.Entry).filter(models.Entry.branch == g.branch)
                     if e.day.strftime("%Y-%m") == month)
        pct = actual / g.target_kg
        out.append({"branch": g.branch, "month": month, "target_kg": g.target_kg, "actual_kg": round(actual, 2),
                    "used_pct": round(pct * 100, 1), "status": "over" if pct > 1 else ("watch" if pct > 0.85 else "on_track")})
    return out
