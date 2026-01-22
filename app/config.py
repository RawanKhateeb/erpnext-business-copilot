from pathlib import Path
import os
from dotenv import load_dotenv

# טוען את .env משורש הפרויקט
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

ERP_URL = os.getenv("ERP_URL", "http://localhost:8080")
ERP_API_KEY = os.getenv("ERP_API_KEY", "")
ERP_API_SECRET = os.getenv("ERP_API_SECRET", "")
