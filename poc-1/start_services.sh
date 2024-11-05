#!/bin/bash

# Start Ollama in the background
nohup ollama serve --host 0.0.0.0 &

# Wait until Ollama is ready by checking the health endpoint (adjust the port as needed)
echo "Waiting for Ollama to be ready..."
while ! curl -s http://localhost:11400/health; do
    sleep 1
done

echo "Ollama is ready. Starting Python application..."

# Start the Python application
python -u app/main.py