# 🔥 HeatQuest Backend

**API for analyzing urban heat islands using satellite data and AI.**

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### 2. **Configure Environment**

Create a `.env` file in the `backend/` folder:

```env
# Mapbox (Required for satellite images)
MAP=pk.eyJ1IjoieW91ci10b2tlbiIsImEiOiJja...

# Supabase (Required for database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AWS (Optional - Landsat/Sentinel data is public)
AWS_REGION=us-west-2

# AI Providers (at least one required)
OPENAI_API_KEY=sk-...                    # OpenAI GPT-4 Vision
GOOGLE_GEMINI_API_KEY=...                # Google Gemini API
GOOGLE_CLOUD_PROJECT=your-project-id     # For Vertex AI
VERTEX_AI_CREDENTIALS=vertex-access.json # Service Account JSON
```

**Where to get API keys:**
- **Mapbox Token**: https://account.mapbox.com/access-tokens/
- **Supabase**: https://supabase.com (create free project)
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Cloud**: https://console.cloud.google.com

### 3. **Run the Server**

```bash
python -m uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**

### 4. **Test the API**

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Test Endpoint**: http://localhost:8000/api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=500

---

## 📡 Available APIs

### 1. **Heatmap API** - Landsat Temperature Analysis

Get temperature and heat scores for any location:

```bash
GET /api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
```

**Parameters:**
- `lat`, `lon`: GPS coordinates
- `radius_m`: Search radius in meters (default: 500m)
- `cell_size_m`: Grid cell size (default: 30m, Landsat resolution)

**Returns:** JSON with grid cells containing:
- `temp`: Temperature in °C
- `ndvi`: Vegetation index
- `heat_score`: Combined heat risk score

**Visualization:**
```bash
GET /api/v1/grid-heat-score-map-radius?lat=51.5323&lon=-0.0531&radius_m=500
```
Returns an interactive HTML map.

---

### 2. **Location Description API** - AI Analysis

Get AI-generated descriptions of satellite images:

```bash
GET /api/v1/describe-location?lat=51.5074&lon=-0.1278&zoom=17
```

**Parameters:**
- `lat`, `lon`: GPS coordinates
- `zoom`: Zoom level (1-20, default: 17)
- `width`, `height`: Image size in pixels (default: 640x640)

**Returns:** JSON with:
- `description`: AI-generated text description
- `image_path`: Path to saved satellite image
- `ai_provider`: Which AI model was used
- `image_provider`: Satellite image source

**Example Response:**
```json
{
  "description": "The satellite image shows a densely built urban area with many buildings and streets. In the center, there are several large structures and minimal vegetation.",
  "lat": 51.5074,
  "lon": -0.1278,
  "image_path": "cache/satellite_images/satellite_51.5074_-0.1278_20251109_054135.png",
  "image_provider": "Mapbox Satellite",
  "ai_provider": "Google Vertex AI (gemini-2.0-flash)",
  "confidence": "high"
}
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | REST API |
| **Satellite Data** | Landsat 8/9 (AWS) | Surface temperature |
| **Vegetation Data** | Sentinel-2 | NDVI calculation |
| **Satellite Images** | Mapbox | Visual satellite imagery |
| **AI Vision** | Google Vertex AI (Gemini 2.0) | Image analysis |
| **Geospatial** | Rasterio, GeoPandas | Data processing |

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/v1/
│   │   ├── heatmap.py         # Heatmap + Auto-Analysis endpoints
│   │   ├── missions.py        # Mission CRUD endpoints
│   │   ├── location_description.py  # AI analysis endpoints
│   │   └── test.py            # Health check endpoints
│   ├── services/              # Business Logic Layer
│   │   ├── grid_service.py              # Grid generation & calculations
│   │   ├── landsat_service.py           # Temperature data from AWS
│   │   ├── sentinel_service.py          # NDVI vegetation data
│   │   ├── stac_service.py              # Satellite scene search
│   │   ├── parent_cell_service.py       # Smart caching system
│   │   ├── location_description_service.py  # AI image analysis
│   │   ├── mission_generation_service.py    # Auto-mission creation
│   │   └── visualization_service.py     # PNG heatmap generation
│   ├── models/                # Data Models
│   │   ├── heatmap.py         # Heatmap request/response
│   │   ├── mission.py         # Mission models
│   │   └── location_description.py  # AI analysis models
│   └── core/                  # Core Configuration
│       ├── config.py          # Environment settings
│       ├── supabase_client.py # Database connection
│       ├── aws_client.py      # AWS S3 client
│       └── geo.py             # Geospatial utilities
├── cache/
│   └── satellite_images/      # Downloaded satellite images
├── vertex-access.json         # Google Cloud credentials
├── requirements.txt
├── .env                       # Environment variables
└── README.md
```

---

## 🔧 Services Explained

### Core Services

#### 1. **grid_service.py** - Grid Generation & Heat Score Calculation
**Purpose:** Creates geographical grid cells and calculates heat scores

**Main Functions:**
- `generate_grid_cells(center_lat, center_lon, radius_m, cell_size_m)` - Creates grid of cells around a point
- `calculate_heat_score(temperature, ndvi)` - Computes heat risk: `temp - (0.3 × NDVI) - 15`
- `assign_to_parent_cell(lat, lon)` - Maps coordinates to parent cell (5km grid)

**Use Case:** Called by heatmap API to create analysis grid

---

#### 2. **landsat_service.py** - Temperature Data from Landsat 8/9
**Purpose:** Fetches surface temperature from AWS Landsat archive

**Main Functions:**
- `get_temperature_for_location(lat, lon)` - Downloads Landsat thermal band (B10)
- `search_landsat_scenes(bbox, days_back)` - Finds available satellite scenes
- `extract_temperature(band_data)` - Converts DN values to Celsius

**Data Source:** AWS Public Dataset (Landsat Collection 2)  
**Resolution:** 30m per pixel  
**Update Frequency:** Every 16 days

---

#### 3. **sentinel_service.py** - Vegetation Data (NDVI)
**Purpose:** Calculates vegetation index from Sentinel-2 satellite

**Main Functions:**
- `get_ndvi_for_location(lat, lon)` - Fetches red/NIR bands and calculates NDVI
- `calculate_ndvi(red_band, nir_band)` - Formula: `(NIR - RED) / (NIR + RED)`

**Data Source:** AWS Public Dataset (Sentinel-2)  
**Resolution:** 10m per pixel  
**Range:** -1.0 (water) to +1.0 (dense vegetation)

---

#### 4. **stac_service.py** - Satellite Scene Discovery
**Purpose:** Searches for available satellite imagery using STAC API

**Main Functions:**
- `search_landsat_stac(bbox, date_range)` - Finds Landsat scenes
- `search_sentinel_stac(bbox, date_range)` - Finds Sentinel-2 scenes
- `get_best_scene(scenes)` - Selects scene with least cloud cover

**STAC Endpoints:**
- Landsat: `https://landsatlook.usgs.gov/stac-server`
- Sentinel: `https://earth-search.aws.element84.com/v1`

---

#### 5. **parent_cell_service.py** - Smart Caching System
**Purpose:** Reduces API calls by 90% through intelligent caching

**How it works:**
1. **Parent Cells** - 5km × 5km grid covering the world
2. **Child Cells** - 30m × 30m detailed analysis cells
3. **Caching** - Once analyzed, data persists in Supabase

**Main Functions:**
- `find_or_create_parent_cell(lat, lon)` - Gets/creates 5km parent cell
- `get_cached_child_cells(parent_cell_id)` - Retrieves analyzed cells
- `should_analyze_cell(heat_score)` - Decides if cell needs AI analysis

**Database Tables:**
- `parent_cells` - 5km grid cache
- `child_cells` - 30m detailed cells
- `cell_analyses` - AI analysis results

---

#### 6. **location_description_service.py** - AI Image Analysis
**Purpose:** Analyzes satellite images with multiple AI providers

**Supported AI Providers:**
1. **Google Vertex AI (Gemini 2.0 Flash)** - Primary
2. **OpenAI GPT-4 Vision** - Fallback
3. **Google Gemini API** - Alternative

**Main Functions:**
- `describe_location(lat, lon, zoom)` - Full analysis pipeline
- `_fetch_satellite_image()` - Downloads from Mapbox or Google Maps
- `_analyze_with_vertex_ai()` - Sends to Gemini Vision
- `_analyze_with_openai()` - Sends to GPT-4 Vision

**Output:**
- Description of visible features
- Main cause of heat stress
- 2-4 suggested cooling actions

---

#### 7. **mission_generation_service.py** - Auto-Mission Creation
**Purpose:** Automatically creates missions from hotspot detection

**Workflow:**
1. User scans location → Hotspots detected (heat_score > 15)
2. AI analyzes hotspot → Gets description + actions
3. Service creates mission → Saves to Supabase
4. Mission appears on map → User can accept

**Main Functions:**
- `generate_mission_from_analysis(cell_analysis, user_id)` - Creates mission
- `_generate_mission_title(analysis)` - Smart title based on location type
- `_generate_mission_description(analysis)` - Uses AI summary
- `_generate_mission_reasons(analysis)` - Heat stress causes
- `_generate_suggested_actions(analysis)` - Actionable steps

**Mission Types:**
- `auto_generated` - From hotspot analysis
- `user_discovered` - User-submitted
- `community` - Shared missions

---

#### 8. **visualization_service.py** - Heatmap PNG Generation
**Purpose:** Creates visual heatmap images for download/sharing

**Main Functions:**
- `generate_heatmap_png(grid_cells)` - Creates PNG from grid data
- `apply_color_gradient(heat_scores)` - Maps scores to colors (blue→yellow→red)
- `overlay_on_map(heatmap, base_map)` - Combines with satellite image

**Output:** PNG file with color-coded heat visualization

---

### Core Modules

#### 9. **supabase_client.py** - Database Connection
**Purpose:** Manages PostgreSQL database connection via Supabase

**Features:**
- Connection pooling
- Auto-reconnect on failure
- Type-safe queries with Supabase SDK

**Tables:**
- `profiles` - User accounts & stats
- `missions` - All missions
- `parent_cells` - 5km cache grid
- `child_cells` - 30m analysis cells
- `cell_analyses` - AI analysis results

---

#### 10. **aws_client.py** - AWS S3 Access
**Purpose:** Connects to AWS for Landsat/Sentinel data

**Features:**
- Anonymous access (no credentials needed)
- Optimized for public datasets
- COG (Cloud-Optimized GeoTIFF) support

**Datasets:**
- `s3://usgs-landsat/collection02/level-2/`
- `s3://sentinel-s2-l2a/`

---

## 🔑 Authentication Setup

### For Vertex AI (AI Analysis)

The `vertex-access.json` file is **already configured** with:
- **Project**: `sunlit-analyst-477704-b6`
- **Region**: `us-east4`
- **Model**: Gemini 2.0 Flash (auto-selected)

**No additional setup needed!** ✅

---

## 📊 How It Works

### Complete Workflow (with Smart Caching):

```
User Opens Map
    ↓
1. Frontend requests heatmap (lat, lon, radius, user_id)
    ↓
2. Backend checks Parent Cell (5km grid)
    ├─ Found → Load cached child cells from database
    └─ Not Found → Create new parent cell
    ↓
3. Grid Service generates 30m cells in radius
    ↓
4. For each cell:
    ├─ Landsat Service → Get temperature
    ├─ Sentinel Service → Get NDVI
    └─ Calculate heat_score = temp - (0.3 × NDVI) - 15
    ↓
5. Identify hotspots (heat_score > 15)
    ↓
6. For top 3 hotspots (not yet analyzed):
    ├─ Location Description Service → AI analyzes satellite image
    ├─ Mission Generation Service → Creates mission
    └─ Save to database (cell_analyses, missions)
    ↓
7. Return heatmap + auto-generated missions
    ↓
Frontend displays map with mission markers
```

### Smart Caching Benefits:

- **First scan**: Full analysis (~10 seconds)
- **Cached scan**: Instant response (~0.5 seconds)
- **Reduced AI calls**: Only new hotspots analyzed
- **Database-backed**: Data persists across sessions

---

## 🧪 Example Use Cases

### 1. Analyze a City Block
```bash
http://localhost:8000/api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=200&cell_size_m=30
```
Returns temperature data for each 30m×30m cell in a 200m radius.

### 2. Find Hot Spots
Filter results where `heat_score > 30` to identify urban heat islands.

### 3. Generate AI Descriptions
```bash
http://localhost:8000/api/v1/describe-location?lat=51.5074&lon=-0.1278
```
Get AI analysis: "Densely built urban area with minimal green spaces..."

---

## 🐛 Troubleshooting

### Issue: "No Landsat scene found"
**Solution**: The location might not have recent Landsat coverage. Try:
- Different coordinates
- Larger search radius
- Check if coordinates are over land (not ocean)

### Issue: "Vertex AI API error"
**Solution**: 
- Ensure `vertex-access.json` is in the backend folder
- Check that Vertex AI API is enabled in Google Cloud Console

### Issue: "Module not found"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Interactive documentation with:
- All endpoints listed
- Try-it-out functionality
- Request/response schemas
- Example payloads

---

## 🌍 Supported Regions

**Landsat Coverage**: Global (excludes polar regions)

**Best Coverage**: 
- Europe ✅
- North America ✅
- Asia ✅
- South America ✅
- Africa ✅
- Australia ✅

---

## 🚀 Performance

- **Grid Generation**: < 1 second for 1000 cells
- **Temperature Analysis**: ~0.5-2 seconds per location (with caching)
- **AI Analysis**: ~3-5 seconds per image
- **Batch Processing**: Processes 100+ cells in parallel

---

## 📦 Dependencies

**Core:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

**Geospatial:**
- `rasterio` - Raster data I/O
- `geopandas` - Geospatial operations
- `shapely` - Geometric objects
- `rasterstats` - Zonal statistics

**Satellite Data:**
- `boto3` - AWS S3 access (Landsat)
- `requests` - HTTP requests

**AI:**
- `google-auth` - Google Cloud authentication
- `google-cloud-aiplatform` - Vertex AI SDK

---

## 👥 Team Setup

**For teammates to run the backend:**

1. Clone the repository
2. Install Python 3.11+
3. Run:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Create `.env` with Mapbox token
5. Run: `python -m uvicorn app.main:app --reload`
6. Open: http://localhost:8000/docs

**That's it!** ✅

---

## 📞 Support

**Issues?** Check:
1. API Documentation: http://localhost:8000/docs
2. Logs in terminal
3. Verify `.env` file exists with `MAP` token

---

## 🎯 Quick Reference

| What you need | Where to get it |
|---------------|----------------|
| **Mapbox Token** | https://account.mapbox.com/access-tokens/ |
| **Python 3.11+** | https://www.python.org/downloads/ |
| **Google Cloud** | Already configured! ✅ |

**Start coding:** 🚀
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

