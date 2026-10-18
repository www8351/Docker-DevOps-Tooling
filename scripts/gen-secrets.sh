#!/usr/bin/env sh
# shellcheck shell=sh
#
# Create the admin password files the compose stack mounts as secrets.
# Existing files are left alone, so re-running never rotates a password
# behind your back. Delete a file to have it regenerated, but note that
# Grafana and Portainer read the secret only when their data volume is
# first created: with an existing volume, a regenerated file no longer
# matches the stored password. Run `task clean` first, or reset the
# password in the app.
#
# Usage: scripts/gen-secrets.sh [secrets-dir]   (default: compose/secrets)
#
# The directory is private to you (0700). Each file is 0644 because compose
# bind-mounts secret files with their host permissions and Grafana reads its
# secret as UID 472, not root.
#
set -eu

dir="${1:-$(dirname "$0")/../compose/secrets}"

mkdir -p "$dir"
chmod 0700 "$dir"

for name in grafana_admin_password portainer_admin_password; do
	file="$dir/$name"
	if [ -s "$file" ]; then
		echo "kept      $file"
		continue
	fi
	# 32 alphanumeric characters, no trailing newline.
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32 >"$file"
	chmod 0644 "$file"
	echo "generated $file"
done
