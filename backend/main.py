import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import UPLOAD_DIR, MAX_FILE_SIZE_MB
from backend.detector import detect_damage
from backend.report_generator import generate_report
from backend.pdf_generator import generate_pdf

app = FastAPI(
    title="AI Field Inspector",
    description="Vision + LLM for Infrastructure Damage Detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def _save_upload(file: UploadFile) -> str:
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, unique_name)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return dest


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Field Inspector",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (jpeg, png, etc.).")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")
    await file.seek(0)

    image_path = _save_upload(file)
    filename = os.path.basename(image_path)

    return {
        "message": "Image uploaded successfully",
        "filename": filename,
        "image_url": f"/uploads/{filename}",
        "image_path": image_path,
    }


@app.post("/api/detect")
async def run_detection(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")
    await file.seek(0)

    image_path = _save_upload(file)
    filename = os.path.basename(image_path)
    results = detect_damage(image_path)

    return {
        "filename": filename,
        "image_url": f"/uploads/{filename}",
        "image_size": results["image_size"],
        "classification": results.get("classification"),
        "detections": results["detections"],
        "detection_count": len(results["detections"]),
    }


@app.post("/api/report")
async def create_report(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")
    await file.seek(0)

    image_path = _save_upload(file)
    filename = os.path.basename(image_path)
    results = detect_damage(image_path)
    report = generate_report(results["detections"], image_name=filename)

    return {
        "filename": filename,
        "image_url": f"/uploads/{filename}",
        "image_size": results["image_size"],
        "detections": results["detections"],
        "report": report,
    }


@app.post("/api/inspect")
async def full_inspection(file: UploadFile = File(...)):
    t0 = time.perf_counter()

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")
    await file.seek(0)

    image_path = _save_upload(file)
    filename = os.path.basename(image_path)
    results = detect_damage(image_path)
    report = generate_report(results["detections"], image_name=filename)
    processing_time = round(time.perf_counter() - t0, 2)
    pdf_path = generate_pdf(report, image_name=filename, image_path=image_path, processing_time=processing_time)
    pdf_filename = os.path.basename(pdf_path)

    return {
        "filename": filename,
        "image_url": f"/uploads/{filename}",
        "image_size": results["image_size"],
        "classification": results.get("classification"),
        "detections": results["detections"],
        "detection_count": len(results["detections"]),
        "report": report,
        "pdf_url": f"/uploads/{pdf_filename}",
        "pdf_filename": pdf_filename,
        "processing_time_seconds": processing_time,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/report/pdf/{filename}")
async def download_pdf(filename: str):
    pdf_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
