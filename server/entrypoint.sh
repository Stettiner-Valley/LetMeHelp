#!/bin/bash

cd /home/letmehelp/src

if [ -f pyproject.toml ]; then
    poetry install
fi

echo "Running the server"

# Enable when deploying
# poetry run python -m server &

# Keep the container alive
tail -f /dev/null