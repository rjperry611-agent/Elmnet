# Dockerfile
FROM python:3.10-slim

WORKDIR /usr/src/main

COPY requirements.txt .

RUN apt-get update && apt-get install -y curl build-essential libgmp3-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

ENV WHOAMI=""
ENV BOOTSTRAP_URL=""

CMD ["python", "-u", "app/main.py"]