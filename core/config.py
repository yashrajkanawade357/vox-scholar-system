import os
from dotenv import load_dotenv

# Provide a root base path correctly
load_dotenv()

VOX_SERVICE_URL = os.getenv("VOX_SERVICE_URL", "http://127.0.0.1:8000")
SCHOLAR_SERVICE_URL = os.getenv("SCHOLAR_SERVICE_URL", "http://127.0.0.1:8501")
ZERO_TRUST_SECRET = os.getenv("ZERO_TRUST_SECRET", "super-secret-dev-key")
