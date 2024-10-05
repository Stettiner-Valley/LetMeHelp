FROM python:3.10-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY baserat ./baserat
ENV PYTHONPATH=/usr/src/app

RUN useradd -M -s /bin/bash baserat && chown -R baserat:baserat /usr/src/app
USER baserat

CMD [ "python", "baserat/main.py" ]
