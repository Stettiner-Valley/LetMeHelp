#!/bin/bash
docker compose up -d
docker compose exec -it user-client /bin/bash