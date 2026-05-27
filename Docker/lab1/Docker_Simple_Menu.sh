#!/usr/bin/env bash
#
# Menu:
#   1. Pull an image by name
#   2. Create web container(s) with a chosen image + port, then curl them
#   3. Exit
#
set -euo pipefail

H=$(hostname -I 2>/dev/null | awk '{print $1}')
HOST=${H:-localhost}

while true; do
	echo -e "\n\t<Menu>"
	echo -e "1. Pull an image by name"
	echo -e "2. Create web container(s) with a chosen image + port"
	echo -e "3. Exit\n"
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
			echo "Options: nginx | jenkins | httpd | adejonge/helloworld"
			read -rp "Enter the image name: " IMAGEWEB
			read -rp "Enter the host port: " PORT
			read -rp "How many containers? " NUM
			if [[ -z "$IMAGEWEB" || -z "$PORT" || ! "$NUM" =~ ^[0-9]+$ ]]; then
				echo "Image, port, and a numeric count are required." >&2
				continue
			fi

			case "$IMAGEWEB" in
				jenkins)              REPO="jenkins/jenkins"; CPORT=8080 ;;
				nginx)                REPO="nginx";           CPORT=80 ;;
				httpd|apache|apache2) REPO="httpd";           CPORT=80 ;;
				adejonge/helloworld)  REPO="adejonge/helloworld"; CPORT=80 ;;
				*)
					echo "Unsupported image." >&2
					continue
					;;
			esac

			sudo docker pull "$REPO:latest"
			for ((i = 1; i <= NUM; i++)); do
				HOSTPORT=$((PORT + i - 1))
				sudo docker run -d -p "$HOSTPORT:$CPORT" "$REPO:latest"
				echo "Started $REPO on http://$HOST:$HOSTPORT"
				wget -q -O- "http://$HOST:$HOSTPORT" >/dev/null || echo "  (not reachable yet)"
			done
			;;
		3)
			break
			;;
		*)
			echo "Enter 1-3 only!"
			;;
	esac
done
