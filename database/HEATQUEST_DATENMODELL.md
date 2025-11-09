# 🔥 HeatQuest Datenmodell – Angepasst an deine Implementierung

Basierend auf deinem tatsächlichen Backend mit FastAPI, Landsat, Sentinel-2 und Vertex AI.

---

## 🎯 Überblick

**HeatQuest Backend macht:**
1. **Grid-Generierung** um GPS-Punkt → on-demand Zellen (30m-200m)
2. **Landsat + Sentinel-2** → Temperatur, NDVI, Heat Score pro Zelle
3. **Vertex AI / Gemini** → AI-Beschreibung von Satellitenbildern
4. **Supabase** → User, Discoveries, Missions

**→ Kein statisches Parent/Child-System, sondern dynamische Analyse um User-Position!**

---

## 🗺️ Datenmodell – Tabellenübersicht

```
┌─────────────┐
│  profiles   │  User-Daten & Fortschritt
└──────┬──────┘
       │
       ├──────────────────────────┐
       │                          │
┌──────▼───────┐          ┌───────▼────────┐
│ discoveries  │          │   missions     │
│ (Hotspots)   │          │   (Aufgaben)   │
└──────┬───────┘          └───────┬────────┘
       │                          │
┌──────▼────────┐        ┌────────▼─────────┐
│ cell_analyses │        │ user_locations   │
│ (AI-Beschr.)  │        │ (GPS-Tracking)   │
└───────────────┘        └──────────────────┘
```

---

## 📋 Tabellen im Detail

### 1️⃣ profiles (bereits implementiert ✅)
**Zweck:** User-Verwaltung mit Gamification

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | User-ID (Supabase Auth) |
| `username` | TEXT | Anzeigename |
| `avatar_url` | TEXT | Profilbild |
| `points` | INTEGER | Gesammelte Punkte |
| `level` | INTEGER | Aktuelles Level |
| `missions_completed` | INTEGER | Anzahl abgeschlossener Missionen |
| `created_at` | TIMESTAMP | Registrierung |
| `updated_at` | TIMESTAMP | Letztes Update |

**Status:** ✅ Existiert bereits in Supabase

---

### 2️⃣ discoveries (bereits implementiert ✅, erweitert unten)
**Zweck:** Gespeicherte Hitze-Hotspots vom User

**Aktuell:**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | Discovery-ID |
| `user_id` | UUID (FK) | → profiles.id |
| `location_name` | TEXT | Ortsname |
| `latitude` | FLOAT | Center-Koordinate |
| `longitude` | FLOAT | Center-Koordinate |
| `heat_score` | FLOAT | Durchschnittlicher Heat Score |
| `temperature` | FLOAT | Durchschnittstemperatur (°C) |
| `ndvi` | FLOAT | Durchschnittlicher NDVI |
| `ai_description` | TEXT | Gemini-Beschreibung |
| `image_url` | TEXT | Mapbox-Satellitenbild |
| `created_at` | TIMESTAMP | Entdeckungsdatum |

**NEU hinzufügen (für Grid-Daten):**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `cell_size_m` | FLOAT | Zellengröße (30m, 100m, 200m) |
| `radius_m` | FLOAT | Analysierter Radius um Punkt |
| `total_cells` | INTEGER | Anzahl analysierter Grid-Zellen |
| `hotspot_cells` | INTEGER | Anzahl Hitze-Zellen (>Threshold) |
| `scene_id` | TEXT | Landsat Scene-ID |
| `ndvi_source` | TEXT | Sentinel-2 Quelle |
| `grid_data` | JSONB | Komprimierte Grid-Zellen-Daten |

**`grid_data` Format (JSONB):**
```json
{
  "cells": [
    {
      "cell_id": "cell_0_0",
      "lat_min": 51.5314,
      "lat_max": 51.5317,
      "lon_min": -0.0540,
      "lon_max": -0.0537,
      "temp": 28.5,
      "ndvi": 0.25,
      "heat_score": 28.4,
      "is_hotspot": true
    }
  ],
  "bounds": {
    "lat_min": 51.5300,
    "lat_max": 51.5350,
    "lon_min": -0.0550,
    "lon_max": -0.0500
  }
}
```

---

### 3️⃣ cell_analyses (NEU)
**Zweck:** Detaillierte AI-Analysen einzelner Grid-Zellen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | Analyse-ID |
| `discovery_id` | UUID (FK) | → discoveries.id |
| `cell_id` | TEXT | z.B. "cell_142_312" |
| `latitude` | FLOAT | Zellen-Zentrum |
| `longitude` | FLOAT | Zellen-Zentrum |
| `temperature` | FLOAT | Temperatur dieser Zelle (°C) |
| `ndvi` | FLOAT | NDVI dieser Zelle |
| `heat_score` | FLOAT | Heat Score dieser Zelle |
| `is_hotspot` | BOOLEAN | TRUE wenn heat_score > threshold |
| `ai_summary` | TEXT | Kurzbeschreibung (Gemini) |
| `main_cause` | TEXT | Hauptursache (z.B. "Asphalt") |
| `suggested_actions` | JSONB | Liste von Maßnahmen |
| `confidence` | FLOAT | KI-Konfidenz (0-1) |
| `image_url` | TEXT | Mapbox-Bild dieser Zelle |
| `gemini_model` | TEXT | Verwendetes Modell |
| `created_at` | TIMESTAMP | Analyse-Zeitpunkt |

**`suggested_actions` Format (JSONB):**
```json
[
  {
    "action": "Plant street trees",
    "priority": "high",
    "estimated_cooling": 2.5,
    "feasibility": "medium"
  },
  {
    "action": "Install cool pavements",
    "priority": "medium",
    "estimated_cooling": 1.5,
    "feasibility": "high"
  }
]
```

---

### 4️⃣ missions (bereits implementiert ✅, erweitert unten)
**Zweck:** Klima-Missionen aus AI-Analysen

**Aktuell:**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | Mission-ID |
| `user_id` | UUID (FK) | → profiles.id |
| `mission_type` | TEXT | Art der Mission |
| `status` | TEXT | 'pending' / 'completed' |
| `points_earned` | INTEGER | Verdiente Punkte |
| `completed_at` | TIMESTAMP | Abschlusszeitpunkt |
| `created_at` | TIMESTAMP | Erstellung |

**NEU hinzufügen:**
| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `discovery_id` | UUID (FK) | → discoveries.id (optional) |
| `cell_analysis_id` | UUID (FK) | → cell_analyses.id (optional) |
| `latitude` | FLOAT | Mission-Koordinate |
| `longitude` | FLOAT | Mission-Koordinate |
| `title` | TEXT | Mission-Titel |
| `description` | TEXT | Detailbeschreibung |
| `heat_risk_score` | FLOAT | Hitze-Risiko (0-100) |
| `required_actions` | JSONB | Liste erforderlicher Aktionen |
| `created_by_system` | BOOLEAN | TRUE wenn auto-generiert |
| `distance_to_user` | FLOAT | Entfernung vom User (m) |

**Mission-Typen:**
- `analyze_hotspot` – Hitze-Hotspot analysieren
- `document_cool_spot` – Kühleren Bereich dokumentieren
- `compare_areas` – Zwei Bereiche vergleichen
- `suggest_solution` – Lösungsvorschlag einreichen

---

### 5️⃣ user_locations (NEU)
**Zweck:** GPS-Tracking der User-Bewegungen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | Datensatz-ID |
| `user_id` | UUID (FK) | → profiles.id |
| `latitude` | FLOAT | GPS-Koordinate |
| `longitude` | FLOAT | GPS-Koordinate |
| `accuracy` | FLOAT | GPS-Genauigkeit (m) |
| `recorded_at` | TIMESTAMP | Zeitpunkt der Aufzeichnung |
| `mission_id` | UUID (FK) | → missions.id (optional) |
| `discovery_id` | UUID (FK) | → discoveries.id (optional) |
| `context` | TEXT | 'exploring' / 'mission' / 'analyzing' |
| `device_info` | JSONB | Geräte-Metadaten (optional) |

**Zweck:**
- Zeige Heatmap der User-Bewegungen
- "Du warst schon hier!" Feature
- Proximity-basierte Mission-Benachrichtigungen
- Statistik: "Du hast 5 km erkundet!"

---

### 6️⃣ analysis_sessions (NEU, optional)
**Zweck:** Gruppiere zusammenhängende Analysen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID (PK) | Session-ID |
| `user_id` | UUID (FK) | → profiles.id |
| `center_lat` | FLOAT | Zentrum der Session |
| `center_lon` | FLOAT | |
| `radius_m` | FLOAT | Analysierter Radius |
| `total_discoveries` | INTEGER | Anzahl Discoveries |
| `total_cells_analyzed` | INTEGER | Anzahl Grid-Zellen |
| `average_heat_score` | FLOAT | Durchschnitt |
| `hotspot_percentage` | FLOAT | % Hotspot-Zellen |
| `started_at` | TIMESTAMP | Beginn |
| `ended_at` | TIMESTAMP | Ende |
| `duration_seconds` | INTEGER | Dauer |

**Nutzen:** Zeige "Session-Report" mit Statistiken

---

## 🔁 Workflow / Data Flow

### 1. User öffnet App & wählt Position
```
Frontend → GPS-Position (lat, lon)
         → Wähle Radius (500m)
         → Wähle Zellengröße (30m)
```

### 2. Backend generiert Grid & berechnet Heat Scores
```python
# grid_service.py
grid_cells = grid_service.generate_grid(
    lat=51.5323,
    lon=-0.0531,
    radius_m=500,
    cell_size_m=30
)

cell_results = grid_service.calculate_grid_heat_scores_batch(
    grid_cells=grid_cells
)
# → Liste von GridCellResponse mit temp, ndvi, heat_score
```

**Speichere in DB:**
```sql
INSERT INTO discoveries (
    user_id, location_name, latitude, longitude,
    heat_score, temperature, ndvi,
    cell_size_m, radius_m, total_cells, grid_data
) VALUES (...)
```

### 3. Identifiziere Hotspots
```python
hotspots = [
    cell for cell in cell_results 
    if cell.heat_score > threshold  # z.B. > 28°C
]
```

### 4. AI-Analyse für jeden Hotspot
```python
# location_description_service.py
for hotspot in hotspots:
    analysis = location_description_service.describe_location(
        lat=hotspot.center_lat,
        lon=hotspot.center_lon,
        zoom=18,
        temperature=hotspot.temp,
        ndvi=hotspot.ndvi
    )
    
    # Speichere in DB
    INSERT INTO cell_analyses (
        discovery_id, cell_id, latitude, longitude,
        temperature, ndvi, heat_score,
        ai_summary, main_cause, suggested_actions
    )
```

### 5. Generiere Missionen aus Analysen
```python
for analysis in cell_analyses:
    if analysis.is_hotspot:
        mission = {
            "title": f"Cool Down {analysis.location_name}",
            "description": analysis.ai_summary,
            "required_actions": analysis.suggested_actions,
            "heat_risk_score": analysis.heat_score,
            "latitude": analysis.latitude,
            "longitude": analysis.longitude
        }
        
        INSERT INTO missions (...)
```

### 6. User-Bewegung tracken
```python
# Frontend sendet alle 30 Sekunden
POST /api/v1/track-location
{
  "latitude": 51.5325,
  "longitude": -0.0532,
  "accuracy": 10.5,
  "context": "exploring"
}

# Backend speichert
INSERT INTO user_locations (
    user_id, latitude, longitude, accuracy,
    recorded_at, context
)
```

### 7. Mission abschließen
```python
# User klickt "Mission abschließen"
UPDATE missions 
SET status = 'completed', 
    completed_at = NOW(),
    points_earned = 100
WHERE id = mission_id

# Update User-Profil
UPDATE profiles 
SET points = points + 100,
    missions_completed = missions_completed + 1
WHERE id = user_id
```

---

## 🔧 SQL Schema für Supabase

```sql
-- ============================================
-- ERWEITERE discoveries
-- ============================================
ALTER TABLE public.discoveries 
ADD COLUMN cell_size_m FLOAT DEFAULT 30,
ADD COLUMN radius_m FLOAT DEFAULT 500,
ADD COLUMN total_cells INTEGER DEFAULT 0,
ADD COLUMN hotspot_cells INTEGER DEFAULT 0,
ADD COLUMN scene_id TEXT,
ADD COLUMN ndvi_source TEXT,
ADD COLUMN grid_data JSONB;

-- ============================================
-- NEUE TABELLE: cell_analyses
-- ============================================
CREATE TABLE IF NOT EXISTS public.cell_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    discovery_id UUID REFERENCES public.discoveries(id) ON DELETE CASCADE NOT NULL,
    cell_id TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION,
    ndvi DOUBLE PRECISION,
    heat_score DOUBLE PRECISION,
    is_hotspot BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    main_cause TEXT,
    suggested_actions JSONB,
    confidence FLOAT DEFAULT 0.0,
    image_url TEXT,
    gemini_model TEXT DEFAULT 'gemini-2.0-flash-exp',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX cell_analyses_discovery_idx ON public.cell_analyses(discovery_id);
CREATE INDEX cell_analyses_hotspot_idx ON public.cell_analyses(is_hotspot) WHERE is_hotspot = TRUE;
CREATE INDEX cell_analyses_heat_score_idx ON public.cell_analyses(heat_score DESC);

-- RLS
ALTER TABLE public.cell_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Cell analyses sind öffentlich lesbar"
    ON public.cell_analyses FOR SELECT
    USING (true);

CREATE POLICY "User können eigene analyses erstellen"
    ON public.cell_analyses FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.discoveries 
            WHERE id = cell_analyses.discovery_id 
            AND user_id = auth.uid()
        )
    );

-- ============================================
-- ERWEITERE missions
-- ============================================
ALTER TABLE public.missions
ADD COLUMN discovery_id UUID REFERENCES public.discoveries(id) ON DELETE SET NULL,
ADD COLUMN cell_analysis_id UUID REFERENCES public.cell_analyses(id) ON DELETE SET NULL,
ADD COLUMN latitude DOUBLE PRECISION,
ADD COLUMN longitude DOUBLE PRECISION,
ADD COLUMN title TEXT,
ADD COLUMN description TEXT,
ADD COLUMN heat_risk_score FLOAT,
ADD COLUMN required_actions JSONB,
ADD COLUMN created_by_system BOOLEAN DEFAULT FALSE,
ADD COLUMN distance_to_user FLOAT;

-- ============================================
-- NEUE TABELLE: user_locations
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy FLOAT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    mission_id UUID REFERENCES public.missions(id) ON DELETE SET NULL,
    discovery_id UUID REFERENCES public.discoveries(id) ON DELETE SET NULL,
    context TEXT CHECK (context IN ('exploring', 'mission', 'analyzing')),
    device_info JSONB
);

-- Indexes
CREATE INDEX user_locations_user_idx ON public.user_locations(user_id);
CREATE INDEX user_locations_time_idx ON public.user_locations(recorded_at DESC);
CREATE INDEX user_locations_coords_idx ON public.user_locations USING GIST (
    ll_to_earth(latitude, longitude)
);

-- RLS
ALTER TABLE public.user_locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User können eigene Locations sehen"
    ON public.user_locations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "User können eigene Locations erstellen"
    ON public.user_locations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- NEUE TABELLE: analysis_sessions (optional)
-- ============================================
CREATE TABLE IF NOT EXISTS public.analysis_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    radius_m FLOAT NOT NULL,
    total_discoveries INTEGER DEFAULT 0,
    total_cells_analyzed INTEGER DEFAULT 0,
    average_heat_score FLOAT,
    hotspot_percentage FLOAT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER
);

-- RLS
ALTER TABLE public.analysis_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User können eigene Sessions sehen"
    ON public.analysis_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "User können eigene Sessions erstellen"
    ON public.analysis_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

---

## 📊 Unterschied zum Beispiel-Modell

| Beispiel | HeatQuest | Warum? |
|----------|-----------|--------|
| `parent_cells` | ❌ Nicht nötig | HeatQuest generiert Zellen on-demand um User-Position |
| `child_cells` | ✅ `discoveries` + `grid_data` | Grid-Daten werden in JSONB gespeichert |
| `cell_analyses` | ✅ `cell_analyses` | Detaillierte AI-Analysen pro Zelle |
| `missions` | ✅ `missions` | Erweitert um Discovery/Analysis-Links |
| `user_locations` | ✅ `user_locations` | GPS-Tracking für Proximity-Features |
| `users` | ✅ `profiles` | Bereits vorhanden mit Gamification |

---

## 🚀 Next Steps

### 1. SQL Schema ausführen
```sql
-- Führe in Supabase SQL Editor aus
-- Siehe oben: "SQL Schema für Supabase"
```

### 2. Backend erweitern
```python
# app/core/supabase_client.py

async def save_discovery_with_grid(
    user_id: str,
    location_name: str,
    latitude: float,
    longitude: float,
    cell_results: List[GridCellResponse],
    scene_id: str,
    ndvi_source: str,
    radius_m: float,
    cell_size_m: float
):
    """Speichere Discovery mit vollständigen Grid-Daten"""
    
    # Berechne Aggregat-Werte
    temps = [c.temp for c in cell_results if c.temp]
    ndvis = [c.ndvi for c in cell_results if c.ndvi]
    scores = [c.heat_score for c in cell_results if c.heat_score]
    
    hotspots = [c for c in cell_results if c.heat_score and c.heat_score > 28]
    
    # Erstelle Grid-Data JSONB
    grid_data = {
        "cells": [
            {
                "cell_id": c.cell_id,
                "lat_min": c.lat_min,
                "lat_max": c.lat_max,
                "lon_min": c.lon_min,
                "lon_max": c.lon_max,
                "temp": c.temp,
                "ndvi": c.ndvi,
                "heat_score": c.heat_score,
                "is_hotspot": c.heat_score > 28 if c.heat_score else False
            }
            for c in cell_results
        ],
        "bounds": {
            "lat_min": min(c.lat_min for c in cell_results),
            "lat_max": max(c.lat_max for c in cell_results),
            "lon_min": min(c.lon_min for c in cell_results),
            "lon_max": max(c.lon_max for c in cell_results)
        }
    }
    
    # Speichere Discovery
    discovery = await supabase_service.client.table('discoveries').insert({
        'user_id': user_id,
        'location_name': location_name,
        'latitude': latitude,
        'longitude': longitude,
        'heat_score': sum(scores) / len(scores) if scores else None,
        'temperature': sum(temps) / len(temps) if temps else None,
        'ndvi': sum(ndvis) / len(ndvis) if ndvis else None,
        'cell_size_m': cell_size_m,
        'radius_m': radius_m,
        'total_cells': len(cell_results),
        'hotspot_cells': len(hotspots),
        'scene_id': scene_id,
        'ndvi_source': ndvi_source,
        'grid_data': grid_data
    }).execute()
    
    return discovery.data[0]
```

### 3. Frontend anpassen
```typescript
// Nach Grid-Analyse
const discovery = await fetch('/api/v1/save-discovery', {
  method: 'POST',
  body: JSON.stringify({
    location_name: "Bahnhofplatz Bern",
    latitude: 46.9491,
    longitude: 7.4386,
    grid_data: gridResults,
    radius_m: 500,
    cell_size_m: 30
  })
})
```

---

## ✅ Vorteile dieses Modells

1. **Flexibel:** Passt zu deinem dynamischen Grid-System
2. **Effizient:** JSONB für Grid-Daten (keine 1000+ Rows pro Discovery)
3. **AI-Ready:** Separate `cell_analyses` für detaillierte Beschreibungen
4. **Gamification:** Missions aus Analysen, GPS-Tracking für Proximity
5. **Erweiterbar:** Leicht neue Features hinzufügen (z.B. Heatmap-Overlays)

Soll ich dir jetzt den kompletten SQL-Code oder die Backend-Integration erstellen? 🚀

