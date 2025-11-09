-- ============================================
-- HeatQuest Datenbank-Schema mit Parent/Child-Grid-System
-- ============================================
-- 
-- Konzept:
-- 1. Parent-Cells = Große Bereiche (z.B. 1km × 1km)
--    → Schnelles Check: "Wurde dieser Bereich schon gescannt?"
-- 2. Child-Cells = Kleine Zellen (30m-200m)
--    → Detaillierte Temperatur/NDVI/Heat Score Daten
-- 3. Wenn User Position öffnet:
--    → Check ob Parent-Cell existiert
--    → Falls JA: Lade Child-Cells (bereits gescannt!)
--    → Falls NEIN: Erstelle Parent-Cell + Child-Cells (neuer Scan)
--
-- ============================================

-- ============================================
-- 1. profiles (bereits vorhanden)
-- ============================================
-- (siehe supabase_schema.sql - keine Änderungen)

-- ============================================
-- 2. parent_cells (NEU)
-- Große Rasterzellen für schnelle Bereichsprüfung
-- ============================================
CREATE TABLE IF NOT EXISTS public.parent_cells (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identifikation
    cell_key TEXT UNIQUE NOT NULL,  -- z.B. "parent_51.53_-0.05" (gerundet auf 2 Dezimalstellen = ~1km)
    
    -- Zentrum der Parent-Cell
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    
    -- Bounding Box (ca. 1km × 1km Bereich)
    bbox_min_lat DOUBLE PRECISION NOT NULL,
    bbox_min_lon DOUBLE PRECISION NOT NULL,
    bbox_max_lat DOUBLE PRECISION NOT NULL,
    bbox_max_lon DOUBLE PRECISION NOT NULL,
    
    -- Metadaten
    child_cells_count INTEGER DEFAULT 0,
    total_scans INTEGER DEFAULT 0,  -- Wie oft wurde dieser Bereich analysiert
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    
    -- Satellitendaten-Info (wiederverwendbar!)
    landsat_scene_id TEXT,
    sentinel_scene_id TEXT,
    ndvi_source TEXT,
    
    -- Aggregierte Statistiken
    avg_temperature DOUBLE PRECISION,
    avg_ndvi DOUBLE PRECISION,
    avg_heat_score DOUBLE PRECISION,
    hotspot_percentage FLOAT,  -- % der Child-Cells die Hotspots sind
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes für schnelle Geo-Suche
CREATE INDEX parent_cells_cell_key_idx ON public.parent_cells(cell_key);
CREATE INDEX parent_cells_center_idx ON public.parent_cells(center_lat, center_lon);
CREATE INDEX parent_cells_bbox_idx ON public.parent_cells USING GIST (
    box(
        point(bbox_min_lon, bbox_min_lat),
        point(bbox_max_lon, bbox_max_lat)
    )
);
CREATE INDEX parent_cells_last_scanned_idx ON public.parent_cells(last_scanned_at DESC);

-- RLS
ALTER TABLE public.parent_cells ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Parent-Cells sind öffentlich lesbar"
    ON public.parent_cells FOR SELECT
    USING (true);

CREATE POLICY "Nur System kann Parent-Cells erstellen"
    ON public.parent_cells FOR INSERT
    WITH CHECK (true);  -- Backend erstellt diese

-- ============================================
-- 3. child_cells (NEU)
-- Kleine Rasterzellen mit detaillierten Daten
-- ============================================
CREATE TABLE IF NOT EXISTS public.child_cells (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Zuordnung zur Parent-Cell
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE CASCADE NOT NULL,
    
    -- Identifikation
    cell_id TEXT NOT NULL,  -- z.B. "cell_142_312"
    
    -- Position
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    
    -- Bounding Box (z.B. 30m × 30m)
    lat_min DOUBLE PRECISION NOT NULL,
    lat_max DOUBLE PRECISION NOT NULL,
    lon_min DOUBLE PRECISION NOT NULL,
    lon_max DOUBLE PRECISION NOT NULL,
    
    -- Satellitendaten
    temperature DOUBLE PRECISION,  -- Celsius
    ndvi DOUBLE PRECISION,  -- -1 bis 1
    heat_score DOUBLE PRECISION,  -- temp - (0.3 * ndvi)
    
    -- Metadaten
    cell_size_m FLOAT,  -- 30, 100, 200
    pixel_count INTEGER,
    
    -- Hotspot-Status
    is_hotspot BOOLEAN DEFAULT FALSE,  -- TRUE wenn heat_score > threshold
    
    -- AI-Analyse-Status
    analyzed BOOLEAN DEFAULT FALSE,
    ai_analysis_id UUID,  -- FK zu cell_analyses (optional)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX child_cells_parent_idx ON public.child_cells(parent_cell_id);
CREATE INDEX child_cells_cell_id_idx ON public.child_cells(cell_id);
CREATE INDEX child_cells_hotspot_idx ON public.child_cells(is_hotspot) WHERE is_hotspot = TRUE;
CREATE INDEX child_cells_heat_score_idx ON public.child_cells(heat_score DESC);
CREATE INDEX child_cells_center_idx ON public.child_cells(center_lat, center_lon);

-- Unique Constraint: Jede cell_id nur einmal pro Parent
CREATE UNIQUE INDEX child_cells_unique_idx ON public.child_cells(parent_cell_id, cell_id);

-- RLS
ALTER TABLE public.child_cells ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Child-Cells sind öffentlich lesbar"
    ON public.child_cells FOR SELECT
    USING (true);

CREATE POLICY "Nur System kann Child-Cells erstellen"
    ON public.child_cells FOR INSERT
    WITH CHECK (true);

-- ============================================
-- 4. cell_analyses
-- AI-Beschreibungen für Hotspot-Zellen
-- ============================================
CREATE TABLE IF NOT EXISTS public.cell_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Zuordnung
    child_cell_id UUID REFERENCES public.child_cells(id) ON DELETE CASCADE NOT NULL,
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE CASCADE NOT NULL,
    
    -- Position (denormalisiert für Performance)
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    
    -- Satellitendaten (denormalisiert)
    temperature DOUBLE PRECISION,
    ndvi DOUBLE PRECISION,
    heat_score DOUBLE PRECISION,
    
    -- AI-Analyse (Gemini/Vertex AI)
    ai_summary TEXT,  -- Kurzbeschreibung
    main_cause TEXT,  -- Hauptursache (Asphalt, fehlende Bäume, etc.)
    suggested_actions JSONB,  -- Liste von Maßnahmen
    confidence FLOAT DEFAULT 0.0,  -- KI-Konfidenz
    
    -- Metadaten
    image_url TEXT,  -- Mapbox Satellitenbild
    gemini_model TEXT DEFAULT 'gemini-2.0-flash-exp',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX cell_analyses_child_idx ON public.cell_analyses(child_cell_id);
CREATE INDEX cell_analyses_parent_idx ON public.cell_analyses(parent_cell_id);
CREATE INDEX cell_analyses_created_idx ON public.cell_analyses(created_at DESC);

-- RLS
ALTER TABLE public.cell_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Cell-Analysen sind öffentlich lesbar"
    ON public.cell_analyses FOR SELECT
    USING (true);

CREATE POLICY "Nur System kann Analysen erstellen"
    ON public.cell_analyses FOR INSERT
    WITH CHECK (true);

-- ============================================
-- 5. discoveries
-- User-Entdeckungen (Link zu Parent-Cell)
-- ============================================
CREATE TABLE IF NOT EXISTS public.discoveries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- User-Zuordnung
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Parent-Cell-Zuordnung (mehrere User können gleiche Parent-Cell entdecken!)
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE CASCADE NOT NULL,
    
    -- Position (kann vom User gewählter Mittelpunkt sein)
    location_name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    
    -- User-spezifische Parameter
    radius_m FLOAT NOT NULL,  -- Welchen Radius hat User gewählt?
    cell_size_m FLOAT NOT NULL,  -- Welche Zellengröße?
    
    -- Statistiken (bezogen auf User's Auswahl)
    total_cells_viewed INTEGER,  -- Wie viele Zellen hat User angeschaut
    hotspot_cells_found INTEGER,  -- Wie viele Hotspots entdeckt
    
    -- Aggregierte Werte (für User's Bereich)
    avg_temperature DOUBLE PRECISION,
    avg_ndvi DOUBLE PRECISION,
    avg_heat_score DOUBLE PRECISION,
    
    -- Metadaten
    image_url TEXT,  -- Optional: Screenshot/Mapbox-Bild
    notes TEXT,  -- User-Notizen
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX discoveries_user_idx ON public.discoveries(user_id);
CREATE INDEX discoveries_parent_idx ON public.discoveries(parent_cell_id);
CREATE INDEX discoveries_created_idx ON public.discoveries(created_at DESC);

-- RLS
ALTER TABLE public.discoveries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Discoveries sind öffentlich lesbar"
    ON public.discoveries FOR SELECT
    USING (true);

CREATE POLICY "User können eigene Discoveries erstellen"
    ON public.discoveries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "User können eigene Discoveries löschen"
    ON public.discoveries FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- 6. missions
-- Aufgaben aus Analysen
-- ============================================
CREATE TABLE IF NOT EXISTS public.missions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Zuordnung
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE SET NULL,
    child_cell_id UUID REFERENCES public.child_cells(id) ON DELETE SET NULL,
    cell_analysis_id UUID REFERENCES public.cell_analyses(id) ON DELETE SET NULL,
    
    -- Position
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    
    -- Mission-Details
    title TEXT NOT NULL,
    description TEXT,
    mission_type TEXT,  -- 'analyze_hotspot', 'document_cool_spot', etc.
    
    -- Daten
    heat_risk_score FLOAT,
    required_actions JSONB,  -- Liste von Aktionen
    
    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    points_earned INTEGER DEFAULT 0,
    
    -- Metadaten
    created_by_system BOOLEAN DEFAULT FALSE,
    distance_to_user FLOAT,  -- Entfernung vom User (m)
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    completed_by_user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX missions_user_idx ON public.missions(user_id);
CREATE INDEX missions_parent_idx ON public.missions(parent_cell_id);
CREATE INDEX missions_status_idx ON public.missions(status);
CREATE INDEX missions_created_idx ON public.missions(created_at DESC);

-- RLS
ALTER TABLE public.missions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Missions sind öffentlich lesbar"
    ON public.missions FOR SELECT
    USING (true);

CREATE POLICY "User können eigene Missions sehen"
    ON public.missions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "User können eigene Missions erstellen"
    ON public.missions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "User können eigene Missions aktualisieren"
    ON public.missions FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================
-- 7. user_locations
-- GPS-Tracking
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- User-Zuordnung
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Position
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy FLOAT,  -- GPS-Genauigkeit in Metern
    
    -- Kontext
    context TEXT CHECK (context IN ('exploring', 'mission', 'analyzing')),
    mission_id UUID REFERENCES public.missions(id) ON DELETE SET NULL,
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE SET NULL,
    
    -- Timestamps
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX user_locations_user_idx ON public.user_locations(user_id);
CREATE INDEX user_locations_time_idx ON public.user_locations(recorded_at DESC);

-- RLS
ALTER TABLE public.user_locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User können eigene Locations sehen"
    ON public.user_locations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "User können eigene Locations erstellen"
    ON public.user_locations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Funktion: Finde Parent-Cell für GPS-Position
CREATE OR REPLACE FUNCTION find_parent_cell_for_position(
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    grid_size DOUBLE PRECISION DEFAULT 0.01  -- ~1km
) RETURNS UUID AS $$
DECLARE
    parent_id UUID;
BEGIN
    SELECT id INTO parent_id
    FROM public.parent_cells
    WHERE bbox_min_lat <= lat
      AND bbox_max_lat >= lat
      AND bbox_min_lon <= lon
      AND bbox_max_lon >= lon
    LIMIT 1;
    
    RETURN parent_id;
END;
$$ LANGUAGE plpgsql;

-- Funktion: Erstelle Parent-Cell-Key
CREATE OR REPLACE FUNCTION create_parent_cell_key(
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    precision_digits INTEGER DEFAULT 2
) RETURNS TEXT AS $$
BEGIN
    RETURN 'parent_' || 
           ROUND(lat::numeric, precision_digits)::text || '_' || 
           ROUND(lon::numeric, precision_digits)::text;
END;
$$ LANGUAGE plpgsql;

-- Funktion: Update Parent-Cell Statistiken
CREATE OR REPLACE FUNCTION update_parent_cell_stats(parent_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.parent_cells
    SET 
        child_cells_count = (
            SELECT COUNT(*) FROM public.child_cells 
            WHERE parent_cell_id = parent_id
        ),
        avg_temperature = (
            SELECT AVG(temperature) FROM public.child_cells 
            WHERE parent_cell_id = parent_id AND temperature IS NOT NULL
        ),
        avg_ndvi = (
            SELECT AVG(ndvi) FROM public.child_cells 
            WHERE parent_cell_id = parent_id AND ndvi IS NOT NULL
        ),
        avg_heat_score = (
            SELECT AVG(heat_score) FROM public.child_cells 
            WHERE parent_cell_id = parent_id AND heat_score IS NOT NULL
        ),
        hotspot_percentage = (
            SELECT 
                CASE 
                    WHEN COUNT(*) = 0 THEN 0
                    ELSE (COUNT(*) FILTER (WHERE is_hotspot = TRUE) * 100.0 / COUNT(*))
                END
            FROM public.child_cells 
            WHERE parent_cell_id = parent_id
        ),
        updated_at = NOW()
    WHERE id = parent_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Auto-Update Parent-Cell Stats wenn Child-Cells hinzugefügt werden
CREATE OR REPLACE FUNCTION trigger_update_parent_stats()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_parent_cell_stats(NEW.parent_cell_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER child_cells_insert_trigger
    AFTER INSERT ON public.child_cells
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_parent_stats();

CREATE TRIGGER child_cells_update_trigger
    AFTER UPDATE ON public.child_cells
    FOR EACH ROW
    WHEN (OLD.temperature IS DISTINCT FROM NEW.temperature OR 
          OLD.ndvi IS DISTINCT FROM NEW.ndvi OR 
          OLD.heat_score IS DISTINCT FROM NEW.heat_score)
    EXECUTE FUNCTION trigger_update_parent_stats();

-- ============================================
-- VIEWS
-- ============================================

-- View: Übersicht aller gescannten Bereiche
CREATE OR REPLACE VIEW public.scanned_areas AS
SELECT 
    p.id,
    p.cell_key,
    p.center_lat,
    p.center_lon,
    p.child_cells_count,
    p.total_scans,
    p.avg_heat_score,
    p.hotspot_percentage,
    p.last_scanned_at,
    p.landsat_scene_id,
    COUNT(DISTINCT d.user_id) as unique_users,
    COUNT(d.id) as total_discoveries
FROM public.parent_cells p
LEFT JOIN public.discoveries d ON d.parent_cell_id = p.id
GROUP BY p.id;

-- View: Leaderboard erweitert
CREATE OR REPLACE VIEW public.leaderboard_extended AS
SELECT 
    p.id,
    p.username,
    p.avatar_url,
    p.points,
    p.level,
    p.missions_completed,
    COUNT(DISTINCT d.parent_cell_id) as areas_explored,
    COUNT(d.id) as total_discoveries,
    ROW_NUMBER() OVER (ORDER BY p.points DESC) as rank
FROM public.profiles p
LEFT JOIN public.discoveries d ON d.user_id = p.id
GROUP BY p.id
ORDER BY p.points DESC
LIMIT 100;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ HeatQuest Parent/Child-Grid-Schema erfolgreich erstellt!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tabellen:';
    RAISE NOTICE '  - parent_cells (große Bereiche ~1km)';
    RAISE NOTICE '  - child_cells (kleine Zellen 30-200m)';
    RAISE NOTICE '  - cell_analyses (AI-Beschreibungen)';
    RAISE NOTICE '  - discoveries (User-Entdeckungen)';
    RAISE NOTICE '  - missions (Aufgaben)';
    RAISE NOTICE '  - user_locations (GPS-Tracking)';
    RAISE NOTICE '';
    RAISE NOTICE '🔧 Helper-Funktionen:';
    RAISE NOTICE '  - find_parent_cell_for_position(lat, lon)';
    RAISE NOTICE '  - create_parent_cell_key(lat, lon)';
    RAISE NOTICE '  - update_parent_cell_stats(parent_id)';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Bereit für HeatQuest mit Community-Features!';
END $$;

