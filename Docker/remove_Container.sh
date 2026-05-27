#!/usr/bin/env bash
#
# Remove a container by ID (chosen from the list shown).
# Warning: lists all containers, running and stopped.
#
set -euo pipefail

echo -e "Showing all containers:\n"
sudo docker ps -a
read -rp $'\nWhich container ID do you want to remove? ' RM
if [[ -z "$RM" ]]; then
	echo "No container ID given." >&2
	exit 1
fi

if sudo docker rm -f "$RM"; then
	echo "Deleted container '$RM'"
else
	echo "Container ID not found: try again." >&2
	exit 1
fi
