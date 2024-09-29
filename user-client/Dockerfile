FROM golang:1.23.1-bookworm

ARG NODE_MAJOR=20
ARG PNPM_VERSION=9.0.3
ARG UPX_VERSION=4.2.4

RUN export DEBIAN_FRONTEND=noninteractive && apt update && apt install -y ca-certificates curl gnupg unzip git xz-utils gcc libgtk-3-dev libwebkit2gtk-4.0-dev libglib2.0-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install nodejs -y \
    && npm install --global pnpm@${PNPM_VERSION} \
    && curl -Ls https://github.com/upx/upx/releases/download/v${UPX_VERSION}/upx-${UPX_VERSION}-amd64_linux.tar.xz -o - | tar xvJf - -C /tmp \
    && cp /tmp/upx-${UPX_VERSION}-amd64_linux/upx /usr/local/bin/ \
    && chmod +x /usr/local/bin/upx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/wailsapp/wails/v2/cmd/wails@latest

ARG USER_ID=1000
ARG GROUP_ID=1000

# To ensure mounts end up with the right permissions on Linux systems,
# create a non-root user with the provided UID and GUID.
RUN addgroup --gid ${GROUP_ID} letmehelp \
    && adduser --disabled-password --gecos '' --uid ${USER_ID} --gid ${GROUP_ID} letmehelp

ENV GOMODCACHE=/home/letmehelp/gocache
RUN mkdir -p $GOMODCACHE

ENV NPM_CONFIG_PREFIX=/home/letmehelp/.npm-global
ENV PATH=$NPM_CONFIG_PREFIX/bin:$PATH

RUN mkdir -p /home/letmehelp/src && \
    chown -R ${USER_ID}:${GROUP_ID} /home/letmehelp && \
    chown -R ${USER_ID}:${GROUP_ID} /go

USER letmehelp

WORKDIR /home/letmehelp/src

CMD ["tail", "-f", "/dev/null"]