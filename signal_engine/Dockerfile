FROM python:3.12-slim

WORKDIR /app

COPY signal_engine/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY signal_engine/ ./signal_engine/

ENV PYTHONPATH=/app

CMD ["python", "-m", "signal_engine.main"]
