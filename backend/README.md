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
# Required: Mapbox Token (for satellite images)
MAP=your_mapbox_token_here

# Optional: AWS (Landsat data is public, no credentials needed)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-west-2
GOOGLE_APPLICATION_CREDENTIALS=vertex-access.json
VERTEX_PROJECT_ID=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_KEY=
SUPABASE_URL=
MAP=
```

**Where to get API keys:**
- **Mapbox Token**: https://account.mapbox.com/access-tokens/

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
│   │   ├── heatmap.py         # Heatmap endpoints
│   │   └── location_description.py  # AI analysis endpoints
│   ├── services/
│   │   ├── grid_service.py    # Grid generation & heat scores
│   │   ├── landsat_service.py # Landsat temperature data
│   │   ├── sentinel_service.py # Sentinel-2 NDVI data
│   │   ├── stac_service.py    # Satellite scene discovery
│   │   └── location_description_service.py  # AI image analysis
│   ├── models/
│   │   ├── heatmap.py         # Pydantic models
│   │   └── location_description.py
│   └── core/
│       ├── config.py          # Configuration
│       └── geo.py             # Geospatial utilities
├── cache/                      # Temporary data storage
├── vertex-access.json         # Google Cloud service account
├── requirements.txt
├── .env                       # Environment variables
└── README.md
```

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

### Heatmap Workflow:

1. **Input**: GPS coordinates + radius
2. **Grid Generation**: Creates grid cells (30m or custom size)
3. **Landsat Data**: Fetches surface temperature from AWS
4. **Sentinel-2 Data**: Gets vegetation index (NDVI)
5. **Heat Score Calculation**: `heat_score = temperature - (0.3 × NDVI)`
6. **Output**: JSON with all grid cells or interactive map

### AI Analysis Workflow:

1. **Input**: GPS coordinates + zoom level
2. **Fetch Satellite Image**: Downloads from Mapbox
3. **Save Image**: Stores locally in `cache/satellite_images/`
4. **AI Analysis**: Sends to Google Vertex AI (Gemini Vision)
5. **Output**: Natural language description of the location

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

