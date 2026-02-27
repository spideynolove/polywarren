FROM python:3.12-slim

WORKDIR /app

COPY onchain/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY onchain/ ./onchain/

ENV PYTHONPATH=/app

CMD ["python", "-m", "onchain.main"]
