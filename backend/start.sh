#!/usr/bin/env bash
# Production start script for Render / Railway / similar PaaS.
#
# - Applies pending Alembic migrations on every deploy
# - Boots uvicorn binding to the platform-provided $PORT
# - Uses `exec` so signals (SIGTERM on redeploys) reach uvicorn cleanly

set -euo pipefail

echo "→ Running database migrations..."
alembic upgrade head

echo "→ Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"