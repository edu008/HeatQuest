-- ============================================
-- QUICK TEST SCHEMA - Only the most important tables
-- For quick testing of Parent/Child logic
-- ============================================

-- 1. Parent-Cells (Large areas ~1km)
CREATE TABLE IF NOT EXISTS public.parent_cells (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cell_key TEXT UNIQUE NOT NULL,
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    bbox_min_lat DOUBLE PRECISION NOT NULL,
    bbox_min_lon DOUBLE PRECISION NOT NULL,
    bbox_max_lat DOUBLE PRECISION NOT NULL,
    bbox_max_lon DOUBLE PRECISION NOT NULL,
    child_cells_count INTEGER DEFAULT 0,
    total_scans INTEGER DEFAULT 0,
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    landsat_scene_id TEXT,
    sentinel_scene_id TEXT,
    ndvi_source TEXT,
    avg_temperature DOUBLE PRECISION,
    avg_ndvi DOUBLE PRECISION,
    avg_heat_score DOUBLE PRECISION,
    hotspot_percentage FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast search
CREATE INDEX IF NOT EXISTS parent_cells_cell_key_idx ON public.parent_cells(cell_key);

-- RLS
ALTER TABLE public.parent_cells ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Parent-Cells are publicly readable"
    ON public.parent_cells FOR SELECT
    USING (true);

CREATE POLICY IF NOT EXISTS "System can create Parent-Cells"
    ON public.parent_cells FOR INSERT
    WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "System can update Parent-Cells"
    ON public.parent_cells FOR UPDATE
    USING (true);

-- 2. Child-Cells (Small cells 30-200m)
CREATE TABLE IF NOT EXISTS public.child_cells (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    parent_cell_id UUID REFERENCES public.parent_cells(id) ON DELETE CASCADE NOT NULL,
    cell_id TEXT NOT NULL,
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    lat_min DOUBLE PRECISION NOT NULL,
    lat_max DOUBLE PRECISION NOT NULL,
    lon_min DOUBLE PRECISION NOT NULL,
    lon_max DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION,
    ndvi DOUBLE PRECISION,
    heat_score DOUBLE PRECISION,
    cell_size_m FLOAT,
    pixel_count INTEGER,
    is_hotspot BOOLEAN DEFAULT FALSE,
    analyzed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS child_cells_parent_idx ON public.child_cells(parent_cell_id);
CREATE INDEX IF NOT EXISTS child_cells_hotspot_idx ON public.child_cells(is_hotspot) WHERE is_hotspot = TRUE;

-- RLS
ALTER TABLE public.child_cells ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Child-Cells are publicly readable"
    ON public.child_cells FOR SELECT
    USING (true);

CREATE POLICY IF NOT EXISTS "System can create Child-Cells"
    ON public.child_cells FOR INSERT
    WITH CHECK (true);

-- 3. Helper Function: Update Parent-Cell Stats
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

-- 4. Trigger: Auto-Update Stats
CREATE OR REPLACE FUNCTION trigger_update_parent_stats()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_parent_cell_stats(NEW.parent_cell_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS child_cells_insert_trigger ON public.child_cells;
CREATE TRIGGER child_cells_insert_trigger
    AFTER INSERT ON public.child_cells
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_parent_stats();

-- SUCCESS!
DO $$
BEGIN
    RAISE NOTICE '✅ Quick Test Schema successfully created!';
    RAISE NOTICE '📊 Tables: parent_cells, child_cells';
    RAISE NOTICE '🧪 Ready for testing!';
END $$;

