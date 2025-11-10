import logging
from typing import Dict, List, Tuple, Union, Optional

import numpy as np

try:
    import matplotlib.cm as mpl_cm
except ImportError:  # pragma: no cover - fallback falls matplotlib fehlt
    mpl_cm = None

logger = logging.getLogger(__name__)


class HotspotDetector:
    """Dynamische Hotspot-Erkennung für HeatQuest."""

    @staticmethod
    def _extract_heat_scores(cells: List[Dict]) -> List[float]:
        return [c["heat_score"] for c in cells if c.get("heat_score") is not None]

    @classmethod
    def detect_by_percentile(
        cls,
        cells: List[Dict],
        top_percentile: float = 0.05,
    ) -> Tuple[List[Dict], float]:
        """Identifiziert die heißesten X Prozent als Hotspots."""
        heat_scores = cls._extract_heat_scores(cells)

        if not heat_scores:
            logger.warning("HotspotDetector: Keine Heat Scores verfügbar (percentile).")
            return [], 0.0

        percentile = max(min(top_percentile, 1.0), 0.0)
        threshold = float(np.percentile(heat_scores, (1 - percentile) * 100))

        hotspots = [c for c in cells if c.get("heat_score", 0) >= threshold]

        logger.info("🔥 Percentile-Methode")
        logger.info(
            "   Daten: Min=%.2f, Max=%.2f, Median=%.2f",
            min(heat_scores),
            max(heat_scores),
            float(np.median(heat_scores)),
        )
        logger.info(
            "   Threshold: %.2f (Top %.0f%%) → %d/%d Hotspots",
            threshold,
            percentile * 100,
            len(hotspots),
            len(cells),
        )

        return hotspots, threshold

    @classmethod
    def detect_by_stddev(
        cls,
        cells: List[Dict],
        sigma: float = 1.5,
    ) -> Tuple[List[Dict], float]:
        """Erkennt Hotspots über Standardabweichung."""
        heat_scores = cls._extract_heat_scores(cells)

        if not heat_scores:
            logger.warning("HotspotDetector: Keine Heat Scores verfügbar (stddev).")
            return [], 0.0

        mean = float(np.mean(heat_scores))
        std = float(np.std(heat_scores))
        threshold = mean + (sigma * std)

        hotspots = [c for c in cells if c.get("heat_score", 0) >= threshold]

        logger.info("📊 StdDev-Methode")
        logger.info("   µ=%.2f, σ=%.2f, Threshold (µ + %.1fσ)=%.2f", mean, std, sigma, threshold)
        logger.info("   Hotspots: %d/%d", len(hotspots), len(cells))

        return hotspots, threshold

    @classmethod
    def detect_by_color(
        cls,
        cells: List[Dict],
        red_threshold: int = 200,
        contrast_threshold: int = 50,
        colormap: str = "YlOrRd",
    ) -> Tuple[List[Dict], str]:
        """Verwendet die Karten-Farbskala zur Hotspot-Erkennung."""
        if mpl_cm is None:
            logger.warning(
                "HotspotDetector: matplotlib nicht verfügbar – Color-Methode übersprungen."
            )
            return [], "matplotlib-missing"

        heat_scores = cls._extract_heat_scores(cells)

        if not heat_scores:
            logger.warning("HotspotDetector: Keine Heat Scores verfügbar (color).")
            return [], "N/A"

        min_score = min(heat_scores)
        max_score = max(heat_scores)
        score_range = max(max_score - min_score, 1e-6)

        cmap = mpl_cm.get_cmap(colormap)
        hotspots: List[Dict] = []

        for cell in cells:
            score = cell.get("heat_score")
            if score is None:
                continue

            normalized = (score - min_score) / score_range
            rgba = cmap(normalized)

            r = int(rgba[0] * 255)
            g = int(rgba[1] * 255)
            b = int(rgba[2] * 255)

            avg_other = (g + b) / 2
            is_red = r >= red_threshold
            has_contrast = r > (avg_other + contrast_threshold)

            if is_red and has_contrast:
                cell["_debug_rgb"] = (r, g, b)
                hotspots.append(cell)

        threshold_info = f"R≥{red_threshold}, Δ>{contrast_threshold}"

        logger.info("🎨 Color-Methode")
        logger.info("   Score-Range: %.2f - %.2f", min_score, max_score)
        logger.info("   Threshold: %s → %d/%d Hotspots", threshold_info, len(hotspots), len(cells))

        return hotspots, threshold_info

    @classmethod
    def detect_auto(
        cls,
        cells: List[Dict],
        method: str = "adaptive",
        **kwargs: Union[float, int, str],
    ) -> Tuple[List[Dict], Union[float, str]]:
        """Auto-Dispatcher für verschiedene Hotspot-Erkennungen."""
        method = (method or "adaptive").lower()

        if method == "percentile":
            return cls.detect_by_percentile(cells, **kwargs)

        if method == "stddev":
            return cls.detect_by_stddev(cells, **kwargs)

        if method == "color":
            return cls.detect_by_color(cells, **kwargs)

        if method == "adaptive":
            heat_scores = cls._extract_heat_scores(cells)

            if not heat_scores:
                logger.warning("HotspotDetector: Keine Heat Scores verfügbar (adaptive).")
                return [], 0.0

            mean = float(np.mean(heat_scores))
            std = float(np.std(heat_scores))
            cv = (std / mean) if mean else 0.0

            if cv > 0.3:
                logger.info("🤖 AUTO: Hohe Varianz (CV=%.2f) → StdDev", cv)
                return cls.detect_by_stddev(cells, sigma=kwargs.get("sigma", 1.5))

            logger.info("🤖 AUTO: Niedrige Varianz (CV=%.2f) → Percentile", cv)
            return cls.detect_by_percentile(cells, top_percentile=kwargs.get("top_percentile", 0.05))

        raise ValueError(f"Unbekannte Hotspot-Methode: {method}")


hotspot_detector = HotspotDetector()


