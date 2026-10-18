#!/usr/bin/env sh
# shellcheck shell=sh
#
# Print an incrementing counter twice a second. Runs as the image CMD.
# POSIX sh (no bashisms) so it runs on Alpine's busybox without bash.
#
# Every loop also touches a heartbeat file. `counter.sh --healthcheck` exits
# non-zero when that file is missing or older than COUNTER_HEARTBEAT_MAX_AGE
# seconds, so the container healthcheck catches a stalled loop instead of
# only checking that some process exists.
#
set -eu

heartbeat="${COUNTER_HEARTBEAT:-/tmp/counter.heartbeat}"
max_age="${COUNTER_HEARTBEAT_MAX_AGE:-10}"

if [ "${1:-}" = "--healthcheck" ]; then
	[ -f "$heartbeat" ] || exit 1
	age=$(($(date +%s) - $(stat -c %Y "$heartbeat")))
	if [ "$age" -le "$max_age" ]; then
		exit 0
	fi
	exit 1
fi

counter=0
while true; do
	sleep 0.5
	echo "$counter"
	touch "$heartbeat"
	counter=$((counter + 1))
done
