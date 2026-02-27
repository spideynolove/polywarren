FROM python:3.12-slim

WORKDIR /app

COPY bot/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY bot/ ./bot/

ENV PYTHONPATH=/app

RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./bot \
    --grpc_python_out=./bot \
    ./proto/trading.proto

CMD ["python", "-m", "bot.main"]
