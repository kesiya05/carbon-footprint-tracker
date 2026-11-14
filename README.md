# Carbon Footprint Tracker

Log activities (electricity, travel, food, waste), turn them into CO2e using emission factors, and track progress against a reduction goal.

## What it does

- Emission-factor table you can inspect through the API
- Entries by category and date with totals and shares
- Monthly goal with progress tracking

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API docs. With Docker: `docker compose up` (uses PostgreSQL). The default database is a local SQLite file, so it works with no setup.

## Tests

```bash
ruff check . && pytest
```

## Notes

Emission factors are example values for demonstration, not an official inventory. Check them against your national factors before using real numbers.

MIT licensed. Built by Kesiya Ann Sony.
