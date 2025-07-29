# Dockerfile
FROM python:3.10-slim

WORKDIR /usr/src/main

COPY requirements.txt .

RUN apt-get update && apt-get install -y curl build-essential libgmp3-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Default values for the P2P network.  These can be overridden in
# docker‑compose.yml for each service.  ``P2P_PORT`` controls which
# TCP port the node listens on for P2P traffic and ``BOOTSTRAP_PEERS``
# should be a comma separated list of ``host:port`` entries used for
# bootstrapping peer discovery.
ENV P2P_PORT="9000"
ENV BOOTSTRAP_PEERS=""

CMD ["python", "-u", "app/main.py"]