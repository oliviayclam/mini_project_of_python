from datetime import datetime
from pathlib import Path
import os

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = DATA_DIR / "uploaded_file"
# Allowed file extensions (Optional: modify based on your needs)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'xlsx'}

def upload_file() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR
    return path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS# Create the folder if it doesn't exist yet
os.makedirs(REPORTS_DIR, exist_ok=True)
