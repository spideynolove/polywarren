import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
EXECUTION_GRPC_ADDR = os.getenv("EXECUTION_GRPC_ADDR", "execution:50051")
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
