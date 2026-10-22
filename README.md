# AI Soil Health Monitor

An advanced AI-powered system that analyzes soil health to provide fertilizer dosages, crop recommendations, and future trend predictions. It includes a modern Next.js Progressive Web App (PWA) with Voice AI support.

## Project Structure

- `backend/`: FastAPI application handling all the heavy lifting and logic.
- `backend/ml/`: Machine Learning inference and rule-based diagnostic modules.
- `frontend/`: Next.js 16 PWA (Mobile-first dashboard, Camera uploads, Text-to-Speech).
- `ml_training/`: Jupyter notebooks and scripts used to train the machine learning models.
- `models/`: Exported `.h5` and `.pkl` models.
- `data/`: CSV datasets used for training.

## How to Run

### 1. Start the Backend API
```bash
python -m uvicorn backend.main:app --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

The API will run on `http://127.0.0.1:8000` and the UI will run on `http://localhost:3000`.
