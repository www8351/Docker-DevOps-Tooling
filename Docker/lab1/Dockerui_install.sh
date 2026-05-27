#!/usr/bin/env bash
#
# Deploy a Docker web UI and verify the page is reachable.
# abh1nav/dockerui is dead; use Portainer CE instead.
#
set -euo pipefail

H=$(hostname -I 2>/dev/null | awk '{print $1}')

read -rp "Enter a container name: " NAME
read -rp "Enter the host port for the UI: " PORT
if [[ -z "$NAME" || -z "$PORT" ]]; then
	echo "Name and port are both required." >&2
	exit 1
fi

sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p "$PORT:9000" \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--name "portainer_${NAME}" \
	portainer/portainer-ce:latest

sleep 3
# Save the landing page so we can confirm the UI is up.
wget -q -O info.txt "http://${H:-localhost}:${PORT}" || true
cat info.txt
