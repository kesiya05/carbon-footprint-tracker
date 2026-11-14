from app.seed import seed

ENTRY = {"day": "2025-03-10", "branch": "Branch 1", "category": "electricity", "quantity": 1000}


def test_add_entry_computes_emissions(client):
    r = client.post("/api/entries", json=ENTRY)
    assert r.status_code == 201
    assert r.json()["co2e_kg"] == 230.0
    assert r.json()["unit"] == "kWh"


def test_rejects_unknown_category_and_bad_quantity(client):
    assert client.post("/api/entries", json={**ENTRY, "category": "magic"}).status_code == 422
    assert client.post("/api/entries", json={**ENTRY, "quantity": 0}).status_code == 422
    assert client.post("/api/entries", json={**ENTRY, "quantity": -5}).status_code == 422
    assert client.post("/api/entries", json={**ENTRY, "branch": ""}).status_code == 422


def test_filter_and_delete(client):
    a = client.post("/api/entries", json=ENTRY).json()
    client.post("/api/entries", json={**ENTRY, "branch": "Branch 2", "category": "diesel", "quantity": 10})
    assert len(client.get("/api/entries").json()) == 2
    assert [e["branch"] for e in client.get("/api/entries?branch=Branch 2").json()] == ["Branch 2"]
    assert len(client.get("/api/entries?category=electricity").json()) == 1
    assert client.delete(f"/api/entries/{a['id']}").status_code == 204
    assert client.delete(f"/api/entries/{a['id']}").status_code == 404
    assert len(client.get("/api/entries").json()) == 1


def test_summary_math(client):
    client.post("/api/entries", json=ENTRY)  # 230
    client.post("/api/entries", json={**ENTRY, "day": "2025-04-02", "category": "beef", "quantity": 10})  # 270
    s = client.get("/api/summary").json()
    assert s["total_kg"] == 500.0
    assert s["by_category"][0]["key"] == "beef" and s["by_category"][0]["share"] == 0.54
    assert [m["key"] for m in s["by_month"]] == ["2025-03", "2025-04"]
    assert client.get("/api/summary?branch=Nowhere").json()["total_kg"] == 0


def test_goal_progress_statuses(client):
    client.post("/api/entries", json=ENTRY)  # 230 kg in March
    client.put("/api/goals", json={"branch": "Branch 1", "month": "2025-03", "target_kg": 200})
    client.put("/api/goals", json={"branch": "Branch 9", "month": "2025-03", "target_kg": 100})
    client.put("/api/goals", json={"branch": "Branch 1", "month": "2025-03", "target_kg": 250})  # update, not duplicate
    prog = {p["branch"]: p for p in client.get("/api/goals/progress?month=2025-03").json()}
    assert prog["Branch 1"]["status"] == "watch" and prog["Branch 1"]["used_pct"] == 92.0
    assert prog["Branch 9"]["status"] == "on_track" and prog["Branch 9"]["actual_kg"] == 0
    assert client.put("/api/goals", json={"branch": "x", "month": "2025-13", "target_kg": 1}).status_code == 422


def test_homepage_served(client):
    assert "Carbon Footprint Tracker" in client.get("/").text


def test_seed_creates_demo_data(client, db_session):
    n = seed(db_session)
    assert n == 7 * 12 * 9
    s = client.get("/api/summary").json()
    assert len(s["by_branch"]) == 7 and len(s["by_month"]) == 12
    assert s["by_category"][0]["key"] == "beef"
