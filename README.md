# 🔍 AI Field Inspector

**Vision + LLM for Infrastructure Damage Detection**

> *Hackathon 2026 — Best AI Inspection (Caterpillar Track)*

---

## 🎯 The Problem

Infrastructure inspections today are **manual, slow, subjective, dangerous, and expensive**.

- Inspectors visually scan sites and write reports by hand
- Early-stage damage is often missed
- Small cracks → big failures; late detection → accidents, losses, downtime

Caterpillar's world = heavy machinery + field inspections + safety-critical operations.

---

## 💡 The Solution

**AI Field Inspector uses computer vision to detect infrastructure damage from images and automatically generates a professional inspection report using AI — making inspections faster, safer, and smarter.**

---

## 🏗️ System Architecture

```
┌─────────────────┐     ┌────────────────────────────────────────────┐
│   React Frontend│     │           FastAPI Backend                   │
│                 │     │                                            │
│  Upload Image ──┼────►│  /api/inspect                              │
│                 │     │     ├─ Save image                          │
│  View Bounding  │     │     ├─ YOLOv8 damage detection             │
│  Boxes + Report │◄────┤     ├─ LLM report generation (GPT/Gemini) │
│                 │     │     └─ PDF generation                      │
│  Download PDF   │     │                                            │
└─────────────────┘     └────────────────────────────────────────────┘
```

---

## 🔍 Core Features

### Damage Detection (Computer Vision)
- Detects: **Cracks, Corrosion, Leaks, Misalignment**
- Each detection includes: bounding box, damage type, confidence score, severity level
- Powered by YOLOv8 (with simulation fallback for demo)

### AI Reasoning (LLM)
- Converts raw detections into human-readable explanations
- Severity assessment per finding
- Specific recommended actions
- Powered by OpenAI GPT-4o or Google Gemini

### Auto Inspection Report
- Executive summary
- Detailed findings table
- Inspection checklist
- Safety recommendations
- Responsible AI disclaimer
- Timestamp & image reference
- **Instant PDF download**

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Computer Vision** | YOLOv8 (ultralytics) |
| **LLM** | OpenAI GPT-4o / Google Gemini |
| **Backend** | FastAPI (Python) |
| **Frontend** | React |
| **PDF Generation** | fpdf2 |
| **Image Processing** | Pillow |

---

## 📁 Project Structure

```
ai-field-inspector/
│
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── config.py             # Configuration & env vars
│   ├── detector.py           # YOLOv8 damage detection
│   ├── report_generator.py   # LLM report generation
│   ├── pdf_generator.py      # PDF report creation
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main application
│   │   ├── App.css           # Styles
│   │   └── components/
│   │       ├── Header.js
│   │       ├── UploadSection.js
│   │       ├── DetectionResults.js
│   │       ├── ReportView.js
│   │       └── Footer.js
│   └── package.json
│
├── models/                   # YOLO model weights
├── uploads/                  # Uploaded images & generated PDFs
├── .env.example              # Environment config template
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) OpenAI or Google Gemini API key

### 1. Clone & Setup Backend

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Copy and configure environment
cd ..
cp .env.example .env
# Edit .env with your API keys (optional — works without them too)
```

### 2. Start Backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Start Frontend

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`

### 4. Use the Application

1. Open `http://localhost:3000`
2. Upload a site or drone inspection image
3. Click **"Run AI Inspection"**
4. View damage detections with bounding boxes
5. Read the AI-generated inspection report
6. Download the PDF report

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload an inspection image |
| `POST` | `/api/detect` | Upload + run damage detection |
| `POST` | `/api/report` | Upload + detect + generate AI report |
| `POST` | `/api/inspect` | **Full pipeline**: detect + report + PDF |
| `GET` | `/api/report/pdf/{filename}` | Download generated PDF |

---

## 🧠 How Detection Works

1. **Image uploaded** → saved to server
2. **YOLOv8 inference** → identifies damage regions with bounding boxes
3. **Classification** → each detection labeled: crack / corrosion / leak / misalignment
4. **Confidence scoring** → 0.0 to 1.0 confidence per detection
5. **Severity mapping** → critical (≥0.85) / high (≥0.70) / medium (≥0.50) / low

> When no fine-tuned YOLO model is available, the system uses a realistic simulation engine to ensure demos always work.

---

## 📄 Report Generation

The LLM receives structured detection data and produces:

```json
{
  "summary": "Executive summary...",
  "overall_risk_level": "high",
  "findings": [...],
  "safety_notes": [...],
  "checklist": [...],
  "responsible_ai_note": "AI assists — it does not replace — expert judgment."
}
```

This is then rendered in the UI **and** converted to a professional PDF.

---

## 🛡️ Responsible AI

- **AI assists, not replaces** inspectors
- Human validates all results before action
- No automated enforcement
- All detections include **explainable confidence scores**
- Every report includes a responsible AI disclaimer

---

## 🔮 Future Extensions

- 🚁 Drone video inspection (real-time feed)
- 📡 Real-time site monitoring dashboard
- 🏗️ Integration with Caterpillar machinery & IoT
- 📈 Predictive maintenance timelines
- 🥽 AR inspection overlays
- 📊 Historical damage tracking & trend analysis
---

*Built for Hackathon 2026 — Best AI Inspection (Caterpillar Track)*
