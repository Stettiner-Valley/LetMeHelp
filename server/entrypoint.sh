#!/bin/bash

cd /home/letmehelp/src

if [ -f pyproject.toml ]; then
    poetry install
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Missing OPENAI_API_KEY environment variable. Please add it to .env file and restart the Docker container."
  exit 1
fi

# Run the server in the background
poetry run python -m server &

# Get the PID
PID=$!

echo "Server running with PID $PID"

# Listen to the FIFO pipe and re-run the server
# To restart, just run the command "restart-server" :)
tail -f /tmp/restart-server | while IFS='' read line; do
    echo "Killing the server with PID $PID"
    kill -9 "$PID"
    poetry run python -m server &
    PID=$!
    echo "Restarted the server with $PID"
done

# Keep the container alive
tail -f /dev/null