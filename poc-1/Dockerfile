# Dockerfile
FROM python:3.10-slim

WORKDIR /usr/src/main

COPY requirements.txt .

RUN apt-get update && apt-get install -y curl build-essential libgmp3-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

RUN curl -fSL https://ollama.com/install.sh | sh -x
RUN nohup ollama serve & sleep 5 && ollama pull llama3.2

ENV WHOAMI=""
ENV BOOTSTRAP_URL=""
ENV OLLAMA_HOST=0.0.0.0

CMD ["python", "-u", "app/main.py"]