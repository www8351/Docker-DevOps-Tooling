#!/usr/bin/env sh
# shellcheck shell=sh
#
# Print an incrementing counter twice a second. Runs as the image CMD.
# POSIX sh (no bashisms) so it runs on Alpine's busybox without bash.
#
set -eu

counter=0
while true; do
	sleep 0.5
	echo "$counter"
	counter=$((counter + 1))
done
