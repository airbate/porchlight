#!/usr/bin/env bash
# 72h continuous soak (M2 acceptance): backend :8000 + simulator :8322,
# one random signed scenario every 4–7 minutes. Logs to repo root soak*.log.
# Stop early: `pkill -f soak.sh; pkill -f 'uvicorn.*(8000|8322)'`
set -u
cd "$(dirname "$0")/../backend"

export RING_WEBHOOK_SECRET="soak-secret"
export DATABASE_PATH="$PWD/soak.db"
export SNAPSHOTS_DIR="$PWD/soak_snaps"
export PORCHLIGHT_INGEST_URL="http://127.0.0.1:8000/events/ingest"
mkdir -p "$SNAPSHOTS_DIR"

uv run uvicorn app.main:app --port 8000 >> ../soak_backend.log 2>&1 &
BACK=$!
sleep 3
uv run uvicorn simulator.main:app --port 8322 >> ../soak_sim.log 2>&1 &
SIM=$!
sleep 3

SCEN=(visitor package_delivery loitering fall_suspected ambient_noise)
END=$((SECONDS + 72 * 3600))
echo "$(date '+%F %T') soak started (pid $$), ends in 72h" >> ../soak.log

while [ "$SECONDS" -lt "$END" ]; do
  sleep $((240 + RANDOM % 180))
  s=${SCEN[$((RANDOM % 5))]}
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "http://127.0.0.1:8322/trigger?scenario=$s" || echo "000")
  echo "$(date '+%F %T') trigger $s -> $code" >> ../soak.log
done

kill "$BACK" "$SIM" 2>/dev/null
echo "$(date '+%F %T') soak finished cleanly" >> ../soak.log
