# Runbook — VilaUndo (short)

## Apply migrations
- Set DATABASE_URL to your Postgres (Supabase) and run Alembic migrations:
  alembic -c backend/alembic.ini upgrade head

## Seed DB
- Run: DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname python backend/app/seed.py

## Trigger sync manually
- POST /admin/sync on backend (or curl http://localhost:8000/admin/sync)

## Re-run sync for a date
- Use DB tools to backfill into prices table; see backend/app/seed.py for examples.
