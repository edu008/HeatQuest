# 🔥 HeatQuest - Urban Heat Island Gamification

Interactive application for analyzing and combating urban heat islands with gamification elements.

## 📋 Project Overview

**HeatQuest** combines satellite data (Landsat, Sentinel-2) with AI analysis and gamification to explore and document urban heat islands in a playful way.

### Key Features:
- 🗺️ **Interactive Map** with real-time temperature analysis
- 🛰️ **Satellite Data Integration** (Landsat 8/9, Sentinel-2)
- 🤖 **AI Image Description** with Google Vertex AI (Gemini Vision)
- 🎮 **Gamification** with missions and leaderboard
- 📊 **Heatmap Visualization** with heat score calculation

---

## 🚀 Getting Started (Local)

### Prerequisites
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Mapbox Token** ([Get free token](https://account.mapbox.com/access-tokens/))

### Step 1: Install Dependencies

```bash
# Frontend Dependencies
npm install

# Backend Dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Step 2: Configure Backend

Create the file `backend/.env`:

```env
MAP=pk.eyJ1IjoieW91ci10b2tlbiIsImEiOiJja...
AWS_REGION=us-west-2
```

**Important:** Replace the placeholder with your [Mapbox Token](https://account.mapbox.com/access-tokens/).

### Step 3: Start Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Access:
- 🌐 **Frontend:** http://localhost:8080
- 📡 **Backend API:** http://localhost:8000/docs

---

## 🌍 Deployment (Online)

### Option 1: Quick Deployment for Prototype

#### Frontend → Lovable (1 Click)
1. Open: https://lovable.dev/projects/dc5dbd94-f3c3-43e8-ab29-0a3f066a9206
2. Click **"Share" → "Publish"**
3. Done! You'll get a public URL

#### Backend → Render.com (Free)
1. Go to: https://render.com
2. Create a **Web Service**
3. Connect your repository
4. Configuration:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
5. Add environment variables:
   - `MAP` = Your Mapbox Token
   - `AWS_REGION` = us-west-2
6. Click **"Create Web Service"**

---

### Option 2: Professional Deployment

#### Frontend → Vercel
```bash
# Create build
npm run build

# Deploy with Vercel CLI
npm install -g vercel
vercel --prod
```

#### Backend → Google Cloud Run
```bash
# Create and deploy Docker image
gcloud run deploy heatquest-backend \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MAP=your_token
```

---

### Option 3: Docker (Local or Server)

```bash
# Start Docker Compose
docker-compose up -d
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MAP=${MAP}
      - AWS_REGION=us-west-2
  
  frontend:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - backend
```

---

## 🛠️ Technology Stack

### Frontend (Port 8080)
| Technology | Purpose |
|------------|---------|
| React 18 + TypeScript | UI Framework |
| Vite | Build Tool |
| Mapbox GL | Interactive Maps |
| Shadcn UI | UI Components |
| React Router | Navigation |
| TanStack Query | State Management |

### Backend (Port 8000)
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| Python 3.11 | Programming Language |
| Landsat 8/9 | Temperature Data (AWS) |
| Sentinel-2 | NDVI/Vegetation Data |
| Mapbox API | Satellite Images |
| Google Vertex AI | AI Image Description (Gemini) |
| Rasterio | Geospatial Data Processing |

---

## 📂 Project Structure

```
HeatQuest/
├── src/                      # Frontend (React)
│   ├── pages/               # Login, Map, Analyze, Profile, etc.
│   ├── components/          # UI Components
│   ├── contexts/            # GameContext (State)
│   └── main.tsx            # Entry Point
│
├── backend/                 # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── main.py         # FastAPI App
│   │   ├── api/v1/         # API Endpoints
│   │   │   ├── heatmap.py  # Temperature Analysis
│   │   │   └── location_description.py  # AI Analysis
│   │   ├── services/       # Business Logic
│   │   │   ├── grid_service.py
│   │   │   ├── landsat_service.py
│   │   │   ├── sentinel_service.py
│   │   │   └── location_description_service.py
│   │   ├── models/         # Pydantic Models
│   │   └── core/           # Config & Utils
│   ├── cache/              # Temp Data
│   ├── requirements.txt    # Python Dependencies
│   └── .env               # Configuration (create yourself!)
│
├── package.json            # NPM Dependencies
├── vite.config.ts         # Vite Configuration
└── README.md              # This File
```

---

## 🔌 API Endpoints

Available after startup at: http://localhost:8000/docs

### 1. Heatmap Analysis
```
GET /api/v1/grid-heat-score-radius
```
**Parameters:**
- `lat`, `lon` - GPS coordinates
- `radius_m` - Search radius in meters (default: 500)
- `cell_size_m` - Cell size (default: 30m)

**Response:** JSON with temperature, NDVI and heat score per grid cell

### 2. AI Image Description
```
GET /api/v1/describe-location
```
**Parameters:**
- `lat`, `lon` - GPS coordinates
- `zoom` - Zoom level (1-20, default: 17)

**Response:** AI-generated location description with satellite image

---

## 🎮 Features

### For Users:
- **Mission System:** Various heat exploration missions
- **Collect Points:** For discovered heat islands
- **Leaderboard:** Compare with other players
- **Profile:** Personal statistics and achievements

### Technical Features:
- **Real-time Temperature Analysis** from Landsat satellite data
- **NDVI Calculation** for vegetation detection
- **Heat Score Algorithm:** `heat_score = temp - (0.3 × NDVI)`
- **AI Image Analysis** with Google Gemini 2.0 Flash
- **Caching System** for faster loading times

---

## 🚨 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Problem: "MAP environment variable not set"
**Solution:** Create `backend/.env` with your Mapbox Token:
```env
MAP=pk.eyJ1IjoieW91ci10b2tlbiIsImEiOiJja...
```

### Problem: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn app.main:app --port 8001
```

### Problem: Frontend cannot reach backend (CORS)
**Solution:** CORS is already enabled in `backend/app/main.py`. Check if backend is running:
```bash
curl http://localhost:8000
```

### Problem: Landsat data not found
**Solution:** 
- Try different coordinates (over land, not ocean)
- Increase search radius: `radius_m=1000`

---

## 📖 Additional Documentation

- **Backend:** See `backend/README.md` for detailed API documentation
- **API Reference:** http://localhost:8000/docs (interactive Swagger UI)
- **Lovable Project:** https://lovable.dev/projects/dc5dbd94-f3c3-43e8-ab29-0a3f066a9206

---

## 🎯 Deployment Recommendations

| Scenario | Frontend | Backend | Duration |
|----------|----------|---------|----------|
| **Local Test** | `npm run dev` | `uvicorn app.main:app --reload` | 2 Min |
| **Quick Demo** | Lovable Publish | Local + ngrok | 5 Min |
| **Prototype Presentation** | Lovable | Render.com (free) | 30 Min |
| **Production** | Vercel | Google Cloud Run / AWS Lambda | 2 Hrs |

---

## ✅ Checklist

Before first start:
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] `npm install` executed
- [ ] `pip install -r backend/requirements.txt` executed
- [ ] Mapbox Token created
- [ ] `backend/.env` file created
- [ ] Backend running (http://localhost:8000/docs accessible)
- [ ] Frontend running (http://localhost:8080 accessible)

---

## 👥 Team / Contact

**Project:** HeatQuest - Urban Heat Island Gamification  
**Lovable URL:** https://lovable.dev/projects/dc5dbd94-f3c3-43e8-ab29-0a3f066a9206

---

## 📄 License

This project was created with [Lovable](https://lovable.dev).
