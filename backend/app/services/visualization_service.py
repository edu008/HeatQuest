"""
Visualization Service: Erstellt interaktive Heatmaps mit Folium.
Wie im Jupyter Notebook mit Choropleth-Layers für Heat Scores.
"""

import folium
from folium import plugins
import branca.colormap as cm
from typing import List
import logging

from app.models.heatmap import GridCellResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class VisualizationService:
    """
    Service für die Erstellung interaktiver Heatmaps.
    Nutzt Folium mit Mapbox-Tiles für schöne Karten.
    """
    
    def create_heatmap(
        self,
        grid_cells: List[GridCellResponse],
        bounds: dict
    ) -> str:
        """
        Erstellt eine interaktive Heatmap im HTML-Format.
        
        Wie im Notebook:
        - Choropleth Layer mit Heat Score Farbskala
        - Interaktive Tooltips mit Details
        - Mapbox-Basemap (falls Token verfügbar)
        
        Args:
            grid_cells: Liste von Grid-Zellen mit Heat Scores
            bounds: Bounding Box (lat_min, lat_max, lon_min, lon_max)
        
        Returns:
            HTML-String der interaktiven Karte
        """
        
        logger.info(f"🗺️  Erstelle Heatmap für {len(grid_cells)} Zellen...")
        
        # Berechne Kartenzentrum
        center_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
        center_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
        
        # Erstelle Basis-Karte
        if settings.map:
            # Mit Mapbox (schöner!)
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=14,
                tiles=f'https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/{{z}}/{{x}}/{{y}}?access_token={settings.map}',
                attr='Mapbox'
            )
        else:
            # Fallback: OpenStreetMap
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=14,
                tiles="CartoDB positron"
            )
        
        # Berechne min/max Heat Score für Farbskala
        heat_scores = [cell.heat_score for cell in grid_cells if cell.heat_score is not None]
        
        # Debug: Zeige Anzahl gültiger vs. ungültiger Zellen
        valid_cells = len(heat_scores)
        invalid_cells = len(grid_cells) - valid_cells
        logger.info(f"📊 Gültige Zellen: {valid_cells}, Ungültige: {invalid_cells}")
        
        if not heat_scores:
            logger.error("❌ KEINE GÜLTIGEN HEAT SCORES GEFUNDEN!")
            logger.error("   Alle Grid-Zellen haben heat_score=None")
            logger.error("   Mögliche Ursachen:")
            logger.error("   1. Keine scene_id angegeben → Landsat-Suche fehlgeschlagen")
            logger.error("   2. Koordinaten liegen außerhalb der Landsat-Szene")
            logger.error("   3. Fehler beim Batch-Processing")
            
            # Zeige trotzdem eine leere Karte
            return m._repr_html_()
        
        min_score = min(heat_scores)
        max_score = max(heat_scores)
        
        logger.info(f"Heat Score Range: {min_score:.2f} - {max_score:.2f}")
        
        # Erstelle Farbskala (Gelb → Orange → Rot wie im Bild)
        colormap = cm.LinearColormap(
            colors=['#FFFF99', '#FFCC66', '#FF9933', '#FF6666', '#CC3333'],
            vmin=min_score,
            vmax=max_score,
            caption='Heat Score (Higher = Hotter)'
        )
        
        # Füge jede Zelle als Polygon hinzu
        for cell in grid_cells:
            if cell.heat_score is None:
                continue
            
            # Erstelle Polygon-Koordinaten (Folium verwendet [lat, lon])
            coords = [
                [cell.lat_min, cell.lon_min],
                [cell.lat_min, cell.lon_max],
                [cell.lat_max, cell.lon_max],
                [cell.lat_max, cell.lon_min],
                [cell.lat_min, cell.lon_min]
            ]
            
            # Bestimme Farbe basierend auf Heat Score
            color = colormap(cell.heat_score)
            
            # Erstelle Tooltip mit Details
            tooltip_text = f"""
            <b>Cell: {cell.cell_id}</b><br>
            🌡️ Temp: {cell.temp}°C<br>
            🌿 NDVI: {cell.ndvi}<br>
            🔥 Heat Score: {cell.heat_score}<br>
            📊 Pixels: {cell.pixel_count}
            """
            
            # Füge Polygon zur Karte hinzu (mit dunklem Rand für bessere Sichtbarkeit)
            folium.Polygon(
                locations=coords,
                color='#333333',  # Dunkler Rand
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=0.5,  # Dünne Randlinien
                opacity=1.0,
                tooltip=tooltip_text
            ).add_to(m)
        
        # Füge Farbskala zur Karte hinzu
        colormap.add_to(m)
        
        # Füge Layer-Kontrolle hinzu
        folium.LayerControl().add_to(m)
        
        # Füge Fullscreen-Button hinzu
        plugins.Fullscreen().add_to(m)
        
        logger.info("✅ Heatmap erstellt!")
        
        return m._repr_html_()


# Singleton-Instanz
visualization_service = VisualizationService()

