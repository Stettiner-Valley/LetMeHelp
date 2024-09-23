FROM lscr.io/linuxserver/webtop:debian-xfce

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    libreoffice

COPY libreoffice /config/.config/libreoffice

COPY presentation.odp /config/presentation.odp
RUN chown abc:abc /config/presentation.odp

COPY startup.sh /config/startup.sh
COPY startup.desktop /config/.config/autostart/startup.desktop
COPY opt /opt
RUN chmod 644 /config/.config/autostart/startup.desktop

