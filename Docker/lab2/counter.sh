#!/usr/bin/env bash
#
# Print an incrementing counter twice a second. Runs as the image CMD.
#
set -euo pipefail

counter=0
while true; do
	sleep 0.5
	echo "$counter"
	((counter++))
done
