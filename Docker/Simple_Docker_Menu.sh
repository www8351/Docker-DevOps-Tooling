#!/usr/bin/env bash
#
# Simple Docker menu:
#   1. Pull an image from Docker Hub
#   2. Delete an image
#   3. Deploy a container
#
set -euo pipefail

# First non-loopback IP of this host (used for info only).
H=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "Host IP: ${H:-unknown}"

while true; do
	echo -e "\n\t\t\t<< Menu (3 options) >>\n"
	echo -e "1. Pull image from Docker Hub\n2. Delete an image\n3. Deploy a container\n"
	read -rp "Choice: " CH

	case "$CH" in
		1)
			read -rp $'\nEnter the name of the image: ' IMAGE
			if [[ -n "$IMAGE" ]] && sudo docker pull "$IMAGE"; then
				echo "OK"
			else
				echo "Image not found or pull failed." >&2
			fi
			;;
		2)
			sudo docker images
			read -rp $'\nWhich image ID do you want to remove? ' RMI
			if [[ -n "$RMI" ]] && sudo docker rmi "$RMI"; then
				echo -e "\nRemoved image '$RMI'\n"
			else
				echo -e "\nImage ID not found: try again.\n" >&2
			fi
			;;
		3)
			echo -e "\nCreating a container."
			read -rp "Image to run: " NAME_I
			read -rp "Name your container: " TAG
			if [[ -z "$NAME_I" || -z "$TAG" ]]; then
				echo "Image and name are both required." >&2
				continue
			fi
			# Keep the container alive with a trivial foreground loop.
			sudo docker run -itd --name "$TAG" "$NAME_I" \
				/bin/bash -c 'while true; do hostname -I; sleep 1; done'
			;;
		*)
			echo "Enter 1-3 only!"
			continue
			;;
	esac

	read -rp $'\nExit? [y/N] ' EXIT
	case "$EXIT" in
		y|Y|yes|Yes) break ;;
	esac
done
