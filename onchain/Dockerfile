FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY onchain/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY shared/ ./shared/
COPY onchain/ ./onchain/

ENV PYTHONPATH=/app

RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./onchain \
    --grpc_python_out=./onchain \
    ./proto/trading.proto

CMD ["python", "-m", "onchain.main"]
