FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY execution/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY shared/ ./shared/
COPY execution/ ./execution/

ENV PYTHONPATH=/app

RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./execution \
    --grpc_python_out=./execution \
    ./proto/trading.proto

CMD ["python", "-m", "execution.main"]
