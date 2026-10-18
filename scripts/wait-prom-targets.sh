#!/usr/bin/env sh
# shellcheck shell=sh
#
# Wait until every active Prometheus target reports up, or fail once the
# timeout passes. Replaces a fixed sleep before checking the scrape pipeline.
#
# Usage: scripts/wait-prom-targets.sh [prometheus-url] [timeout-seconds]
# Needs curl and python3.
#
set -eu

url="${1:-http://127.0.0.1:9090}"
timeout="${2:-120}"
deadline=$(($(date +%s) + timeout))

check() {
	curl -fsS "$url/api/v1/targets" | python3 -c '
import json, sys
targets = json.load(sys.stdin)["data"]["activeTargets"]
down = [t["labels"]["job"] for t in targets if t["health"] != "up"]
print("targets:", len(targets), "down:", down)
sys.exit(1 if down or not targets else 0)'
}

while :; do
	if summary=$(check 2>&1); then
		echo "$summary"
		exit 0
	fi
	if [ "$(date +%s)" -ge "$deadline" ]; then
		echo "Prometheus targets not all up after ${timeout}s; last check: $summary" >&2
		exit 1
	fi
	sleep 3
done
