# 🌱 AI-Based Soil Health Assessment System

A **production-ready FastAPI backend** for soil health assessment, crop recommendation, and fertilizer prediction using machine learning.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📷 Image Upload | Upload soil images (JPG/PNG/WEBP), stored in `uploads/` |
| 🌾 Crop Prediction | RandomForest model recommends the best crop from NPK + climate data |
| 🧪 Fertilizer Prediction | RandomForest model recommends fertilizer from soil + crop data |
| 🗄️ PostgreSQL | Full persistence with SQLAlchemy ORM |
| 📊 Dashboard | Aggregated stats: total images, farms, predictions, top crop & fertilizer |
| 📜 History | Full prediction history with image, farm, crop, and fertilizer |
| 📖 Swagger UI | Auto-generated API docs at `/docs` |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | PostgreSQL + psycopg2 |
| ML | scikit-learn, pandas, numpy, joblib |
| Server | Uvicorn |

---

## 📁 Project Structure

```
soil-health-app/
├── app/
│   ├── main.py              ← FastAPI app, routers, CORS, lifespan
│   ├── config.py            ← Pydantic settings (reads .env)
│   ├── database.py          ← SQLAlchemy engine, session, Base
│   ├── models.py            ← ORM models: Image, Farm, SoilRecord
│   ├── schemas.py           ← Pydantic request/response schemas
│   ├── crud.py              ← Repository layer (all DB operations)
│   ├── routers/
│   │   ├── images.py        ← POST/GET/DELETE /images
│   │   ├── farms.py         ← CRUD /farms
│   │   ├── soil_records.py  ← CRUD /soil-records
│   │   └── prediction.py    ← /predict/crop, /predict/fertilizer, /history, /dashboard
│   └── services/
│       ├── crop_predictor.py       ← Loads crop_model.pkl, exposes predict()
│       └── fertilizer_predictor.py ← Loads fertilizer_model.pkl, exposes predict()
├── ml/
│   ├── generate_datasets.py ← Generates sample training CSVs
│   ├── train_crop.py        ← Trains & saves crop_model.pkl
│   └── train_fertilizer.py  ← Trains & saves fertilizer_model.pkl
├── datasets/
│   ├── Crop_recommendation.csv
│   └── fertilizer_recommendation.csv
├── models/
│   ├── crop_model.pkl
│   └── fertilizer_model.pkl
├── uploads/                 ← Uploaded images stored here
├── .env                     ← Your environment variables (not committed)
├── .env.example             ← Template for .env
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone / open the project

```bash
cd soil-health-app
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Open **pgAdmin 4** and create a new database:

```sql
CREATE DATABASE soil_health_db;
```

Update your `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=soil_health_db
```

### 4. Train ML models

```bash
# Generate sample datasets (skip if you have real CSV files)
python ml/generate_datasets.py

# Train both models
python ml/train_crop.py
python ml/train_fertilizer.py
```

### 5. Run the application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or via main.py directly:

```bash
python app/main.py
```

---

## 📖 API Documentation

Once the server is running, visit:

| URL | Description |
|---|---|
| http://localhost:8000/docs | **Swagger UI** (interactive) |
| http://localhost:8000/redoc | **ReDoc** (read-only) |
| http://localhost:8000/openapi.json | Raw OpenAPI schema |
| http://localhost:8000/health | Health check |

---

## 🔌 API Endpoints

### Images

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/images/` | Upload a soil image |
| GET | `/api/v1/images/` | List all images |
| GET | `/api/v1/images/{id}` | Get image by ID |
| DELETE | `/api/v1/images/{id}` | Delete image |

### Farms

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/farms/` | Register a new farm |
| GET | `/api/v1/farms/` | List all farms |
| GET | `/api/v1/farms/{id}` | Get farm by ID |
| PATCH | `/api/v1/farms/{id}` | Update farm details |
| DELETE | `/api/v1/farms/{id}` | Delete farm |

### Soil Records

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/soil-records/` | Create soil record |
| GET | `/api/v1/soil-records/` | List all records |
| GET | `/api/v1/soil-records/{id}` | Get record by ID |
| GET | `/api/v1/soil-records/farm/{farm_id}` | Records by farm |
| PATCH | `/api/v1/soil-records/{id}` | Update record |
| DELETE | `/api/v1/soil-records/{id}` | Delete record |

### Predictions

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/predict/crop` | Predict crop from NPK + climate |
| POST | `/api/v1/predict/fertilizer` | Predict fertilizer |
| POST | `/api/v1/predict/full/{id}` | Run both predictions on a record |
| GET | `/api/v1/history` | Full prediction history |
| GET | `/api/v1/dashboard` | Aggregated statistics |

---

## 💡 Example Usage

### Upload Image
```bash
curl -X POST http://localhost:8000/api/v1/images/ \
  -F "file=@soil.jpg"
```

### Create Farm
```bash
curl -X POST http://localhost:8000/api/v1/farms/ \
  -H "Content-Type: application/json" \
  -d '{"farmer_name": "Ramesh", "location": "Chittoor"}'
```

### Create Soil Record
```bash
curl -X POST http://localhost:8000/api/v1/soil-records/ \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1, "image_id": 1,
    "N": 90, "P": 42, "K": 43,
    "temperature": 25, "humidity": 80,
    "ph": 6.5, "rainfall": 202,
    "moisture": 60, "soil_type": "Clay", "crop_type": "Rice"
  }'
```

### Predict Crop
```bash
curl -X POST http://localhost:8000/api/v1/predict/crop \
  -H "Content-Type: application/json" \
  -d '{"N":90,"P":42,"K":43,"temperature":25,"humidity":80,"ph":6.5,"rainfall":202}'
```

### Run Full Prediction on Soil Record
```bash
curl -X POST http://localhost:8000/api/v1/predict/full/1
```

### Dashboard
```bash
curl http://localhost:8000/api/v1/dashboard
```

---

## 🤖 ML Model Details

### Crop Model (`crop_model.pkl`)
- **Algorithm**: RandomForestClassifier (200 trees)
- **Features**: N, P, K, temperature, humidity, ph, rainfall
- **Classes**: 22 crops (rice, wheat, maize, cotton, jute, ...)
- **Test Accuracy**: ~98.4%

### Fertilizer Model (`fertilizer_model.pkl`)
- **Algorithm**: RandomForestClassifier (200 trees)
- **Features**: temperature, humidity, moisture, soil_type, crop_type, N, P, K
- **Classes**: 7 fertilizers (Urea, DAP, 14-35-14, 17-17-17, 28-28, 20-20, 10-26-26)
- **Test Accuracy**: ~99.3%

---

## 🗄️ Database Schema

```
images          → id, filename, filepath, uploaded_at
farms           → id, farmer_name, location, created_at
soil_records    → id, farm_id, image_id, N, P, K, temperature, humidity,
                   ph, rainfall, moisture, soil_type, crop_type,
                   crop_prediction, fertilizer_prediction, notes, created_at
```

---

## 📝 License

MIT License — free to use for educational and commercial projects.
