#!/bin/bash
docker compose up -d
docker compose exec -it server /shell.sh