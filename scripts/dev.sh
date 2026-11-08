#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && source .env; set +a

[ -d .venv ] || python -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

docker compose up -d
until docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done

[ -d frontend/node_modules ] || (cd frontend && npm install)

trap 'kill 0' EXIT
uvicorn app.main:app --reload &
(cd frontend && npm run dev) &
wait