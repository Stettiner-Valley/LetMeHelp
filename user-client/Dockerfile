FROM python:3.11.6-slim-bookworm

RUN apt update
RUN apt install -y gcc git build-essential libgl1-mesa-dev libglib2.0-0 libfontconfig1-dev libdbus-1-dev libfreetype6-dev libicu-dev libudev-dev libinput-dev libxkbcommon-dev libssl-dev libpng-dev libjpeg-dev libglib2.0-dev
RUN pip install pywebview pywebview[qt] pyinstaller eel

RUN useradd -m letmehelp
USER letmehelp

ENV PATH="/home/letmehelp/.local/bin:${PATH}"

WORKDIR /home/letmehelp

CMD ["tail", "-f", "/dev/null"]