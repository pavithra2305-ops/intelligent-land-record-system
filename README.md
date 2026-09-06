# Intelligent Land Record Digitization & Validation System

An AI-assisted government/enterprise web application that converts scanned and legacy land records (PDF, PNG, JPG) into structured, validated digital land records with confidence scoring, human verification, GIS mapping, and analytics.

---

## 🌟 Key Features

1. **Document Processing Pipeline**:
   - **Upload & Storage**: PDF, PNG, JPG, JPEG drag-and-drop up to 15 MB.
   - **OpenCV Preprocessing**: Grayscale conversion, CLAHE contrast enhancement, denoising, adaptive thresholding, and deskewing.
   - **OCR Service Abstraction**: Tesseract OCR, PyMuPDF, and high-precision Python fallback text extractor.
   - **Document Classification**: Heuristic & keyword hybrid classifier for Ownership Records, Mutation Records, and Sale/Registration Deeds.
   - **AI Field Extraction**: Google Gemini API abstraction with a smart rule-based regex fallback engine that runs locally out-of-the-box.
   - **Confidence Scoring**: Field and document-level confidence calculation (HIGH ≥ 85%, MEDIUM 60-84%, LOW < 60%).
   - **Rule-Based Validation Engine**: Checks required fields, survey number format, plot area ranges, and district-tehsil-village location hierarchy.
   - **Duplicate Detection**: RapidFuzz fuzzy matching against existing records for owner name + survey number + location composite scoring.

2. **Human Verification Workflow**:
   - Verification queue for records requiring QA.
   - 2-Column interactive modal displaying original document preview side-by-side with editable field inputs.
   - Audit trail logging for edits, approvals, and rejections with mandatory comments.

3. **Analytics Dashboard**:
   - Top KPI metrics (Total Documents, Processed, Verified, Pending, Validation Errors, Avg Confidence, Overall Accuracy).
   - Recharts visual graphs (Time series, verification ratio, document type breakdown, district progress).

4. **GIS Land Parcel Visualization**:
   - Interactive Leaflet + OpenStreetMap spatial map rendering cadastral parcel polygons and markers.
   - Selected land plot detail card displaying survey number, owner name, village, district, area, and classification.

---

## 🔑 Demo Login Credentials

In development mode, quick one-click role switching is enabled on the Login screen and Sidebar:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@landgov.in` | `admin123` | Full access (Dashboard, Upload, Verification, GIS, Audit, Users) |
| **VERIFIER** | `verifier@landgov.in` | `verifier123` | QA access (Dashboard, Upload, Verification, GIS) |
| **VIEWER** | `viewer@landgov.in` | `viewer123` | Read-only access (Dashboard, Documents Library, GIS Map) |

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide React icons, Framer Motion, Leaflet / React-Leaflet.
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy ORM, PyMuPDF, OpenCV, RapidFuzz, Google Generative AI (Gemini).
- **Database**: SQLite (default local zero-dependency fallback) / PostgreSQL (production).
- **Security**: JWT authentication, bcrypt password hashing, RBAC authorization middleware.
- **Deployment**: Docker, docker-compose.

---

## 🚀 Quick Start (Local Development)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m app.seed.seed_data
python app/main.py
```
Backend API server will run at: `http://localhost:8000`  
Swagger API Docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend Web App will run at: `http://localhost:3000`

---

## 🐳 Docker Deployment

To run the entire system (PostgreSQL, FastAPI Backend, React Frontend) via Docker Compose:

```bash
docker-compose up --build -d
```
- Web Application: `http://localhost:3000`
- FastAPI Backend: `http://localhost:8000`
- PostgreSQL Database: `localhost:5432`

---

## 🧪 Testing

To run automated backend tests:

```bash
cd backend
pytest
```
