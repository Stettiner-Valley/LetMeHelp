#!/bin/bash
docker run --rm -d \
  --name=letmehelp-testenv-linux \
  -p 3000:3000 \
  letmehelp-testenv:linux