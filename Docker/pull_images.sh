#!/usr/bin/env bash
#
# Pull an image from Docker Hub by name.
#
set -euo pipefail

read -rp "Enter the name of the image: " IMAGE
if [[ -z "$IMAGE" ]]; then
	echo "No image name given." >&2
	exit 1
fi

# Pull directly and rely on the exit code instead of scraping `docker search`.
if sudo docker pull "$IMAGE"; then
	echo "OK: pulled '$IMAGE'"
else
	echo "Image not found or pull failed: '$IMAGE'" >&2
	exit 1
fi
