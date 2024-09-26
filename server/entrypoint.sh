#!/bin/bash

cd /home/letmehelp/src

if [ -f pyproject.toml ]; then
    poetry install
fi

echo "Running the server"
poetry run python -m server