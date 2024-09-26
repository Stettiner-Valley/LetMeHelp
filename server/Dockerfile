FROM python:3.10-slim

EXPOSE 8765

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt update && apt install -y curl

# To ensure mounts end up with the right permissions on Linux systems,
# create a non-root user with the provided UID and GUID.
RUN addgroup --gid ${GROUP_ID} letmehelp \
    && adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} letmehelp

RUN mkdir -p /home/letmehelp/src && \
    chown -R ${USER_ID}:${GROUP_ID} /home/letmehelp

RUN pip install poetry

USER letmehelp

WORKDIR /home/letmehelp/src

COPY entrypoint.sh /entrypoint.sh
COPY shell.sh /shell.sh

ENTRYPOINT /entrypoint.sh