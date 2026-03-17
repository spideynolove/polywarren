FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY signal_engine/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY shared/ ./shared/
COPY signal_engine/ ./signal_engine/

ENV PYTHONPATH=/app

RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./signal_engine \
    --grpc_python_out=./signal_engine \
    ./proto/trading.proto

CMD ["python", "-m", "signal_engine.main"]
