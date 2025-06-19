#!/bin/bash

# Start ollama server in background
ollama serve &

sleep 5

# Pull the model (will only download if not present)
ollama pull ${MODEL_NAME}

# Wait forever (keeps foreground process alive)
wait