# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libp2p-tools \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama CLI
RUN wget https://ollama.com/download/ollama-linux-amd64 && \
    chmod +x ollama-linux-amd64 && \
    mv ollama-linux-amd64 /usr/local/bin/ollama

# Copy application code
COPY ./app ./app

# Install Weaviate
RUN wget https://github.com/weaviate/weaviate/releases/download/v1.18.0/weaviate-linux-amd64 && \
    chmod +x weaviate-linux-amd64 && \
    mv weaviate-linux-amd64 /usr/local/bin/weaviate

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]