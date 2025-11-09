-- Create profiles table
CREATE TABLE public.profiles (
  id uuid NOT NULL,
  username text UNIQUE,
  avatar_url text,
  points integer DEFAULT 0,
  level integer DEFAULT 1,
  missions_completed integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view all profiles"
  ON public.profiles FOR SELECT
  USING (true);

CREATE POLICY "Users can update their own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
  ON public.profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Create parent_cells table
CREATE TABLE public.parent_cells (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  cell_key text NOT NULL UNIQUE,
  center_lat double precision NOT NULL,
  center_lon double precision NOT NULL,
  bbox_min_lat double precision NOT NULL,
  bbox_min_lon double precision NOT NULL,
  bbox_max_lat double precision NOT NULL,
  bbox_max_lon double precision NOT NULL,
  child_cells_count integer DEFAULT 0,
  total_scans integer DEFAULT 0,
  last_scanned_at timestamp with time zone,
  landsat_scene_id text,
  sentinel_scene_id text,
  ndvi_source text,
  avg_temperature double precision,
  avg_ndvi double precision,
  avg_heat_score double precision,
  hotspot_percentage double precision,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT parent_cells_pkey PRIMARY KEY (id)
);

-- Enable RLS on parent_cells
ALTER TABLE public.parent_cells ENABLE ROW LEVEL SECURITY;

-- RLS Policies for parent_cells (read-only for all authenticated users)
CREATE POLICY "Anyone can view parent cells"
  ON public.parent_cells FOR SELECT
  USING (true);

-- Create child_cells table
CREATE TABLE public.child_cells (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  parent_cell_id uuid NOT NULL,
  cell_id text NOT NULL,
  center_lat double precision NOT NULL,
  center_lon double precision NOT NULL,
  lat_min double precision NOT NULL,
  lat_max double precision NOT NULL,
  lon_min double precision NOT NULL,
  lon_max double precision NOT NULL,
  temperature double precision,
  ndvi double precision,
  heat_score double precision,
  cell_size_m double precision,
  pixel_count integer,
  is_hotspot boolean DEFAULT false,
  analyzed boolean DEFAULT false,
  ai_analysis_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT child_cells_pkey PRIMARY KEY (id),
  CONSTRAINT child_cells_parent_cell_id_fkey FOREIGN KEY (parent_cell_id) REFERENCES public.parent_cells(id) ON DELETE CASCADE
);

-- Enable RLS on child_cells
ALTER TABLE public.child_cells ENABLE ROW LEVEL SECURITY;

-- RLS Policies for child_cells
CREATE POLICY "Anyone can view child cells"
  ON public.child_cells FOR SELECT
  USING (true);

-- Create cell_analyses table
CREATE TABLE public.cell_analyses (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  child_cell_id uuid NOT NULL,
  parent_cell_id uuid NOT NULL,
  latitude double precision NOT NULL,
  longitude double precision NOT NULL,
  temperature double precision,
  ndvi double precision,
  heat_score double precision,
  ai_summary text,
  main_cause text,
  suggested_actions jsonb,
  confidence double precision DEFAULT 0.0,
  image_url text,
  gemini_model text DEFAULT 'gemini-2.0-flash-exp'::text,
  created_at timestamp with time zone DEFAULT now(),
  mission_generated boolean DEFAULT false,
  CONSTRAINT cell_analyses_pkey PRIMARY KEY (id),
  CONSTRAINT cell_analyses_child_cell_id_fkey FOREIGN KEY (child_cell_id) REFERENCES public.child_cells(id) ON DELETE CASCADE,
  CONSTRAINT cell_analyses_parent_cell_id_fkey FOREIGN KEY (parent_cell_id) REFERENCES public.parent_cells(id) ON DELETE CASCADE
);

-- Enable RLS on cell_analyses
ALTER TABLE public.cell_analyses ENABLE ROW LEVEL SECURITY;

-- RLS Policies for cell_analyses
CREATE POLICY "Anyone can view cell analyses"
  ON public.cell_analyses FOR SELECT
  USING (true);

-- Create missions table
CREATE TABLE public.missions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  parent_cell_id uuid,
  child_cell_id uuid,
  cell_analysis_id uuid,
  latitude double precision NOT NULL,
  longitude double precision NOT NULL,
  title text NOT NULL,
  description text,
  mission_type text,
  heat_risk_score double precision,
  required_actions jsonb,
  status text DEFAULT 'pending'::text CHECK (status = ANY (ARRAY['pending'::text, 'active'::text, 'completed'::text, 'cancelled'::text])),
  points_earned integer DEFAULT 0,
  created_by_system boolean DEFAULT false,
  distance_to_user double precision,
  created_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  completed_by_user_id uuid,
  CONSTRAINT missions_pkey PRIMARY KEY (id),
  CONSTRAINT missions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
  CONSTRAINT missions_parent_cell_id_fkey FOREIGN KEY (parent_cell_id) REFERENCES public.parent_cells(id) ON DELETE SET NULL,
  CONSTRAINT missions_child_cell_id_fkey FOREIGN KEY (child_cell_id) REFERENCES public.child_cells(id) ON DELETE SET NULL,
  CONSTRAINT missions_cell_analysis_id_fkey FOREIGN KEY (cell_analysis_id) REFERENCES public.cell_analyses(id) ON DELETE SET NULL,
  CONSTRAINT missions_completed_by_user_id_fkey FOREIGN KEY (completed_by_user_id) REFERENCES public.profiles(id) ON DELETE SET NULL
);

-- Enable RLS on missions
ALTER TABLE public.missions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for missions
CREATE POLICY "Users can view their own missions"
  ON public.missions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own missions"
  ON public.missions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own missions"
  ON public.missions FOR UPDATE
  USING (auth.uid() = user_id);

-- Create discoveries table
CREATE TABLE public.discoveries (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  parent_cell_id uuid NOT NULL,
  location_name text NOT NULL,
  latitude double precision NOT NULL,
  longitude double precision NOT NULL,
  radius_m double precision NOT NULL,
  cell_size_m double precision NOT NULL,
  total_cells_viewed integer,
  hotspot_cells_found integer,
  avg_temperature double precision,
  avg_ndvi double precision,
  avg_heat_score double precision,
  image_url text,
  notes text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT discoveries_pkey PRIMARY KEY (id),
  CONSTRAINT discoveries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
  CONSTRAINT discoveries_parent_cell_id_fkey FOREIGN KEY (parent_cell_id) REFERENCES public.parent_cells(id) ON DELETE CASCADE
);

-- Enable RLS on discoveries
ALTER TABLE public.discoveries ENABLE ROW LEVEL SECURITY;

-- RLS Policies for discoveries
CREATE POLICY "Users can view their own discoveries"
  ON public.discoveries FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own discoveries"
  ON public.discoveries FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view all discoveries"
  ON public.discoveries FOR SELECT
  USING (true);

-- Create user_locations table
CREATE TABLE public.user_locations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  latitude double precision NOT NULL,
  longitude double precision NOT NULL,
  accuracy double precision,
  context text CHECK (context = ANY (ARRAY['exploring'::text, 'mission'::text, 'analyzing'::text])),
  mission_id uuid,
  parent_cell_id uuid,
  recorded_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_locations_pkey PRIMARY KEY (id),
  CONSTRAINT user_locations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
  CONSTRAINT user_locations_mission_id_fkey FOREIGN KEY (mission_id) REFERENCES public.missions(id) ON DELETE SET NULL,
  CONSTRAINT user_locations_parent_cell_id_fkey FOREIGN KEY (parent_cell_id) REFERENCES public.parent_cells(id) ON DELETE SET NULL
);

-- Enable RLS on user_locations
ALTER TABLE public.user_locations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_locations
CREATE POLICY "Users can view their own locations"
  ON public.user_locations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own locations"
  ON public.user_locations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_parent_cells_updated_at
  BEFORE UPDATE ON public.parent_cells
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_child_cells_updated_at
  BEFORE UPDATE ON public.child_cells
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();