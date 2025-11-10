# 🔥 HeatQuest - Urban Heat Island Gamification

Turn hot spots into cool spots! An interactive gamified application for discovering and combating urban heat islands.

## 📋 Project Overview

**HeatQuest** combines real-time satellite data analysis with AI-powered insights and gamification to make urban climate action engaging and fun.

### Key Features:
- 🗺️ **Interactive Heatmap** - Real-time temperature visualization with Mapbox
- 🎯 **AI-Generated Missions** - Automatic mission creation from satellite hotspot detection
- 🛰️ **Satellite Data Integration** - Landsat 8/9 for temperature, Sentinel-2 for vegetation (NDVI)
- 🤖 **AI Analysis** - Google Vertex AI (Gemini Vision), OpenAI GPT-4 Vision for image analysis
- 👥 **User Authentication** - Supabase Auth with GitHub/Google OAuth
- 📊 **Smart Caching** - Parent/Child cell system for efficient data storage
- 🏆 **Gamification** - Points, levels, leaderboard, and mission completion tracking

---

## 🚀 Getting Started (Local)

### Prerequisites
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Supabase Account** ([Sign up free](https://supabase.com))
- **Mapbox Token** ([Get free token](https://account.mapbox.com/access-tokens/))
- **AI Provider** (at least one):
  - Google Vertex AI + Service Account JSON
  - OpenAI API Key
  - Google Gemini API Key

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
# Mapbox (Required)
MAP=pk.eyJ1IjoieW91ci10b2tlbiIsImEiOiJja...

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AWS (Required for Landsat data)
AWS_REGION=us-west-2

# AI Providers (at least one required)
OPENAI_API_KEY=sk-...
GOOGLE_GEMINI_API_KEY=...
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_CREDENTIALS=vertex-access.json
```

**Important:** 
- Get Mapbox Token from [here](https://account.mapbox.com/access-tokens/)
- Create Supabase project and run `database/supabase_schema_mit_parent_child.sql`
- At least one AI provider must be configured

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

 ##⏱️ First-run note: The backend analyzes all child cells in the selected area on the initial launch. This initial satellite data processing (heat score + AI) can take few minutes before missions appear. Thanks to the smart cache, subsequent scans run almost in real time.

### Access:
- 🌐 **Frontend:** http://localhost:5173
- 📡 **Backend API:** http://localhost:8000/docs
- 🗄️ **Supabase Studio:** https://supabase.com/dashboard/project/your-project-id

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

### Frontend (Port 5173)
| Technology | Purpose |
|------------|---------|
| React 18 + TypeScript | UI Framework |
| Vite | Build Tool & Dev Server |
| Mapbox GL JS | Interactive Maps |
| Shadcn UI | UI Component Library |
| Supabase JS | Authentication & Database |
| React Router | Navigation |
| Framer Motion | Animations |
| Sonner | Toast Notifications |

### Backend (Port 8000)
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| Python 3.11 | Programming Language |
| Supabase | PostgreSQL Database & Auth |
| Landsat 8/9 (AWS) | Surface Temperature Data |
| Sentinel-2 (AWS) | NDVI/Vegetation Index |
| Mapbox Static API | Satellite Images |
| Google Vertex AI (Gemini) | AI Image Analysis |
| OpenAI GPT-4 Vision | Alternative AI Provider |
| Rasterio | Geospatial Processing |
| STAC API | Satellite Data Discovery |

---

## 📂 Project Structure

```
HeatQuest/
├── frontend/
│   ├── src/
│   │   ├── pages/               # Application Pages
│   │   │   ├── Login.tsx        # Authentication
│   │   │   ├── MapView.tsx      # Main Map + Missions
│   │   │   ├── MissionDetail.tsx # Mission Details
│   │   │   ├── Profile.tsx      # User Profile
│   │   │   ├── Leaderboard.tsx  # Rankings
│   │   │   └── Analyze.tsx      # Image Analysis
│   │   ├── components/          # Reusable Components
│   │   │   ├── MapboxMap.tsx    # Interactive Map
│   │   │   ├── BottomNav.tsx    # Navigation Bar
│   │   │   └── ui/              # Shadcn Components
│   │   ├── contexts/            # React Contexts
│   │   │   ├── AuthContext.tsx  # Supabase Auth
│   │   │   └── GameContext.tsx  # Game State
│   │   ├── hooks/               # Custom Hooks
│   │   │   ├── useHeatmap.ts    # Heatmap Logic
│   │   │   └── useMissions.ts   # Mission Management
│   │   ├── services/            # API Services
│   │   └── lib/                 # Utils & Config
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI Application
│   │   ├── api/v1/              # API Endpoints
│   │   │   ├── heatmap.py       # Heatmap + Auto-Analysis
│   │   │   ├── missions.py      # Mission CRUD
│   │   │   ├── location_description.py  # AI Analysis
│   │   │   └── test.py          # Health Checks
│   │   ├── services/            # Business Logic
│   │   │   ├── grid_service.py              # Grid Calculations
│   │   │   ├── landsat_service.py           # Temperature Data
│   │   │   ├── sentinel_service.py          # NDVI Data
│   │   │   ├── stac_service.py              # Satellite Search
│   │   │   ├── parent_cell_service.py       # Cache System
│   │   │   ├── location_description_service.py  # AI Analysis
│   │   │   ├── mission_generation_service.py    # Auto-Missions
│   │   │   └── visualization_service.py     # PNG Generation
│   │   ├── models/              # Data Models
│   │   │   ├── heatmap.py
│   │   │   ├── mission.py
│   │   │   └── location_description.py
│   │   ├── core/                # Core Configuration
│   │   │   ├── config.py        # Settings
│   │   │   ├── supabase_client.py
│   │   │   └── aws_client.py
│   │   └── cache/               # Cached Satellite Images
│   ├── requirements.txt
│   ├── .env                     # Configuration
│   └── vertex-access.json       # Google Cloud Credentials
│
├── database/
│   └── supabase_schema_mit_parent_child.sql  # Database Schema
│
└── README.md
```

---

## 🔌 API Endpoints

Available after startup at: http://localhost:8000/docs

### 1. Heatmap Analysis (Smart Caching)
```
GET /api/v1/grid-heat-score-radius
```
**Parameters:**
- `lat`, `lon` - GPS coordinates
- `radius_m` - Search radius in meters (default: 500)
- `cell_size_m` - Cell size (default: 30m)
- `use_cache` - Use cached data (default: true)
- `user_id` - Auto-generate missions for this user

**Response:** JSON with temperature, NDVI, heat score per grid cell + auto-generated missions

**Features:**
- Parent/Child Cell caching system
- Automatic AI analysis for hotspots
- Mission generation for high heat score areas

### 2. AI Image Description
```
GET /api/v1/describe-location
```
**Parameters:**
- `lat`, `lon` - GPS coordinates
- `zoom` - Zoom level (1-20, default: 17)

**Response:** AI-generated description, main cause, suggested actions

### 3. Mission Management
```
GET  /api/v1/missions?user_id={id}
POST /api/v1/missions/complete
```
**Features:**
- Automatic mission generation from hotspot analysis
- Distance-based sorting
- Status tracking (pending, active, completed)

---

## 🎮 Features

### For Users:
- **Auto-Generated Missions** - AI detects hotspots and creates missions automatically
- **Interactive Map** - Real-time heatmap with mission markers
- **Points & Levels** - Earn XP by completing missions
- **Leaderboard** - Global rankings and competition
- **Profile** - Personal statistics, completed missions, and progress
- **Social Login** - GitHub/Google OAuth via Supabase

### Technical Features:
- **Smart Caching System** - Parent/Child cells reduce API calls by 90%
- **Real-time Satellite Data** - Landsat 8/9 for temperature, Sentinel-2 for NDVI
- **Heat Score Algorithm:** `heat_score = temperature - (0.3 × NDVI)`
- **Multi-AI Provider Support** - Vertex AI, OpenAI, Google Gemini
- **Automatic Mission Generation** - AI analyzes hotspots and creates actionable missions
- **Database-backed** - Supabase PostgreSQL for users, missions, and analyses

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
