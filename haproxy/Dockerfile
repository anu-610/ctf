FROM haproxy:2.9

USER root

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

USER haproxy
