#!/usr/bin/env bash
#
# Remove an image by ID (chosen from the list shown).
#
set -euo pipefail

sudo docker images
read -rp $'\nWhich image ID do you want to remove? ' RMI
if [[ -z "$RMI" ]]; then
	echo "No image ID given." >&2
	exit 1
fi

# `docker rmi` exit code tells us if the ID was valid; no need to diff lists.
if sudo docker rmi "$RMI"; then
	echo "Removed image '$RMI'"
else
	echo "Image ID not found: try again." >&2
	exit 1
fi
