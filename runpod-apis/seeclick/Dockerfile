FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /workspace

COPY handler.py .

RUN git clone https://github.com/njucckevin/SeeClick.git && \
    pip install -r SeeClick/requirements.txt && \
    pip install fastapi uvicorn


CMD ["python3", "handler.py"]

