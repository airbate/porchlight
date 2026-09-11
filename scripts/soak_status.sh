#!/usr/bin/env bash
# Soak health check: uptime, process state, event counts, failures.
cd "$(dirname "$0")/../backend"
echo "== soak.log tail =="
tail -5 ../soak.log 2>/dev/null || echo "(no soak log)"
echo "== triggers / failures =="
echo "triggers: $(grep -c 'trigger ' ../soak.log 2>/dev/null || echo 0)  failures: $(grep -c '-> 000' ../soak.log 2>/dev/null || echo 0)  non-200: $(grep -cE '-> (000|5[0-9][0-9])' ../soak.log 2>/dev/null || echo 0)"
echo "== processes =="
pgrep -fl "uvicorn app.main:app --port 8000" >/dev/null && echo "backend :8000 alive" || echo "backend :8000 DOWN"
pgrep -fl "uvicorn simulator.main:app --port 8322" >/dev/null && echo "simulator :8322 alive" || echo "simulator :8322 DOWN"
echo "== db =="
[ -f soak.db ] && sqlite3 soak.db "SELECT COUNT(*) AS events, SUM(repeat_count) AS total_incl_merged FROM events; SELECT alert_level, COUNT(*) FROM events WHERE alert_level != 'none' GROUP BY alert_level;" 2>/dev/null || echo "(no soak.db yet)"
echo "== health =="
curl -s --max-time 3 http://127.0.0.1:8000/health || echo "(backend not answering)"
echo
