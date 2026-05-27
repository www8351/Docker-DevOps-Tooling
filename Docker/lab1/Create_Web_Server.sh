#!/usr/bin/env bash
#
# Create one or more web-server containers from a chosen image
# (nginx, jenkins, httpd, adejonge/helloworld) and curl each one.
#
set -euo pipefail

H=$(hostname -I 2>/dev/null | awk '{print $1}')
HOST=${H:-localhost}

echo "Options: nginx | jenkins | httpd | adejonge/helloworld"
read -rp "Enter the image name: " IMAGE
read -rp "Enter the host port: " PORT
read -rp "How many containers of '$IMAGE'? " NUM

if [[ -z "$IMAGE" || -z "$PORT" || ! "$NUM" =~ ^[0-9]+$ ]]; then
	echo "Image, port, and a numeric count are required." >&2
	exit 1
fi

# Map the friendly name to a real Docker Hub image + its internal port.
case "$IMAGE" in
	jenkins)              REPO="jenkins/jenkins"; CPORT=8080 ;;
	nginx)                REPO="nginx";           CPORT=80 ;;
	httpd|apache|apache2) REPO="httpd";           CPORT=80 ;;
	adejonge/helloworld)  REPO="adejonge/helloworld"; CPORT=80 ;;
	*)
		echo "Unsupported image. Choose: nginx, jenkins, httpd, adejonge/helloworld." >&2
		exit 1
		;;
esac

sudo docker pull "$REPO:latest"
for ((i = 1; i <= NUM; i++)); do
	# Each container needs a distinct host port.
	HOSTPORT=$((PORT + i - 1))
	sudo docker run -d -p "$HOSTPORT:$CPORT" "$REPO:latest"
	echo "Started $REPO on http://$HOST:$HOSTPORT"
	wget -q -O- "http://$HOST:$HOSTPORT" >/dev/null || echo "  (not reachable yet)"
done
