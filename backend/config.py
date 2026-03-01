import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "models/yolov8n.pt")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE_MB = 10
DAMAGE_CLASSES = ["crack", "corrosion", "leak", "misalignment"]

SEVERITY_MAP = {
    "critical": 0.85,
    "high": 0.70,
    "medium": 0.50,
    "low": 0.0,
}
