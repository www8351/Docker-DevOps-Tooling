FROM ubuntu:24.04

LABEL maintainer="refael malka"

COPY counter.sh /usr/local/bin/counter.sh
RUN chmod +x /usr/local/bin/counter.sh

# Single layer: install tools, then clean apt cache to keep the image small.
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		python3 \
		openssh-server \
		net-tools \
		tcpdump \
		sshpass; \
	rm -rf /var/lib/apt/lists/*

# Route app logs to the container's stdout/stderr (must create the dir first).
RUN mkdir -p /var/log/my \
	&& ln -sf /dev/stdout /var/log/my/access.log \
	&& ln -sf /dev/stderr /var/log/my/error.log

CMD ["/usr/local/bin/counter.sh"]
