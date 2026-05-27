#!/usr/bin/env bash
#
# Create an nginx container, then exec an interactive shell inside it
# (e.g. to edit the served HTML and later `docker commit` a new image).
#
set -euo pipefail

read -rp "Enter a container name: " NAME
read -rp "Which host port maps to nginx (container :80)? " PORT
if [[ -z "$NAME" || -z "$PORT" ]]; then
	echo "Name and port are both required." >&2
	exit 1
fi

sudo docker run -d -p "$PORT:80" --name "$NAME" nginx:latest
sudo docker exec -it "$NAME" bash
