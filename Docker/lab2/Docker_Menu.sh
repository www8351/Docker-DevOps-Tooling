#!/usr/bin/env bash
#
# Lab 2 menu:
#   1. Pull Portainer + nginx images
#   2. Create N nginx containers on chosen ports, print each container IP
#   3. Create a Portainer container, save its IP to a log file
#   4. Create web/index.html, run an nginx container that mounts it
#
set -euo pipefail

H=$(hostname -I 2>/dev/null | awk '{print $1}')
HOST=${H:-localhost}

while true; do
	echo -e "\nMenu:"
	echo -e "1. Pull Portainer + nginx images"
	echo -e "2. Create nginx container(s) on chosen ports, print IPs"
	echo -e "3. Create a Portainer container, save its IP to a log file"
	echo -e "4. Create web/index.html and run an nginx container mounting it\n"
	read -rp "Choice: " CH

	case "$CH" in
		1)
			echo -e "\nPulling images...\n"
			sudo docker pull portainer/portainer-ce:latest
			sudo docker pull nginx:latest
			;;
		2)
			read -rp "How many nginx containers? " NUM
			if [[ ! "$NUM" =~ ^[0-9]+$ ]]; then
				echo "Need a number." >&2
				continue
			fi
			for ((i = 1; i <= NUM; i++)); do
				echo "Container $i:"
				read -rp "  Name: " NAME
				read -rp "  Host port: " PORT
				[[ -z "$NAME" || -z "$PORT" ]] && { echo "  Skipped (name/port missing)."; continue; }
				sudo docker run -itd -p "$PORT:80" --name "$NAME" nginx:latest
				sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$NAME"
			done
			echo "Done"
			;;
		3)
			read -rp "Name for the Portainer container: " NAMEUI
			read -rp "Host port for Portainer: " PORTUI
			if [[ -z "$NAMEUI" || -z "$PORTUI" ]]; then
				echo "Name and port are both required." >&2
				continue
			fi
			sudo docker run -d -p "$PORTUI:9000" \
				-v /var/run/docker.sock:/var/run/docker.sock \
				--name "portainer_${NAMEUI}" \
				portainer/portainer-ce:latest
			sleep 3
			IP=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "portainer_${NAMEUI}")
			echo "$IP" > "${NAMEUI}_out.log"
			echo "IP saved to ${NAMEUI}_out.log"
			;;
		4)
			echo -e "Creating web/ and index.html ...\n"
			mkdir -p web
			echo "<h1>Hello from $(hostname)</h1>" > web/index.html
			read -rp "Name for the nginx container: " NAME
			read -rp "Host port: " PORT
			if [[ -z "$NAME" || -z "$PORT" ]]; then
				echo "Name and port are both required." >&2
				continue
			fi
			sudo docker run -d -p "$PORT:80" --name "$NAME" \
				-v "$(pwd)/web:/usr/share/nginx/html:ro" nginx:latest
			sleep 3
			echo "Served file:"
			wget -q -O- "http://$HOST:$PORT" || echo "  (not reachable yet)"
			echo -e "\nDone!"
			;;
		*)
			echo -e "\nEnter 1-4 only!"
			;;
	esac

	read -rp $'\nExit? [y/N] ' EXIT
	case "$EXIT" in
		y|Y|yes|Yes) break ;;
	esac
done
