"""
Progress Tracker Service.
Zeigt Fortschritt von langen Operationen mit Loading-Screen-Style.
"""

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Service für schöne Progress-Ausgaben (Loading-Screen-Style).
    """
    
    def __init__(self, total_steps: int, operation_name: str = "Operation"):
        """
        Initialisiert Progress Tracker.
        
        Args:
            total_steps: Gesamtanzahl der Schritte
            operation_name: Name der Operation
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = datetime.now()
        self.step_logs = []
        
        # Start-Banner
        logger.info("╔" + "═" * 68 + "╗")
        logger.info(f"║  🚀 {operation_name:<60} ║")
        logger.info("╠" + "═" * 68 + "╣")
    
    def step(self, message: str, icon: str = "▶"):
        """
        Nächster Schritt.
        
        Args:
            message: Beschreibung des Schritts
            icon: Icon für diesen Schritt
        """
        self.current_step += 1
        progress_pct = int((self.current_step / self.total_steps) * 100)
        
        # Progress Bar
        bar_length = 20
        filled = int(bar_length * self.current_step / self.total_steps)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Log
        logger.info(f"║  {icon} [{bar}] {progress_pct:3d}% │ {message:<31} ║")
        
        self.step_logs.append({
            'step': self.current_step,
            'message': message,
            'timestamp': datetime.now()
        })
    
    def substep(self, message: str, icon: str = "  ↳"):
        """
        Unter-Schritt (zählt nicht als Haupt-Schritt).
        
        Args:
            message: Beschreibung
            icon: Icon
        """
        logger.info(f"║  {icon} {message:<61} ║")
    
    def success(self, message: Optional[str] = None):
        """
        Operation erfolgreich abgeschlossen.
        
        Args:
            message: Optionale Erfolgsmeldung
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("╠" + "═" * 68 + "╣")
        if message:
            logger.info(f"║  ✅ {message:<62} ║")
        logger.info(f"║  ⏱️  Completed in {elapsed:.2f}s{' ' * (54 - len(str(elapsed)))}║")
        logger.info("╚" + "═" * 68 + "╝")
    
    def error(self, message: str):
        """
        Operation fehlgeschlagen.
        
        Args:
            message: Fehlermeldung
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("╠" + "═" * 68 + "╣")
        logger.info(f"║  ❌ {message:<62} ║")
        logger.info(f"║  ⏱️  Nach {elapsed:.2f}s fehlgeschlagen{' ' * (44 - len(str(elapsed)))}║")
        logger.info("╚" + "═" * 68 + "╝")
    
    def info(self, message: str, icon: str = "ℹ️"):
        """
        Info-Nachricht (ohne Progress-Update).
        
        Args:
            message: Nachricht
            icon: Icon
        """
        logger.info(f"║  {icon} {message:<62} ║")


class ScanProgressTracker(ProgressTracker):
    """Spezialisierter Tracker für Scan-on-Login."""
    
    def __init__(self, user_id: str):
        super().__init__(total_steps=6, operation_name=f"SCAN ON LOGIN")
        self.user_id = user_id
        self.stats = {}
    
    def add_stat(self, key: str, value: any):
        """Fügt Statistik hinzu."""
        self.stats[key] = value


class AnalysisProgressTracker(ProgressTracker):
    """Spezialisierter Tracker für KI-Analyse."""
    
    def __init__(self, cell_count: int):
        super().__init__(total_steps=cell_count * 2, operation_name=f"KI-ANALYSE ({cell_count} Zellen)")
        self.analyzed_count = 0
        self.failed_count = 0
    
    def cell_success(self, cell_id: str):
        """Markiert Zelle als erfolgreich analysiert."""
        self.analyzed_count += 1
        self.step(f"✓ {cell_id} analysiert", "✅")
    
    def cell_failed(self, cell_id: str, error: str):
        """Markiert Zelle als fehlgeschlagen."""
        self.failed_count += 1
        self.step(f"✗ {cell_id} fehlgeschlagen", "❌")
        self.substep(f"Fehler: {error[:50]}", "  ⚠")


# Singleton-Instanzen
_current_tracker: Optional[ProgressTracker] = None


def get_current_tracker() -> Optional[ProgressTracker]:
    """Gibt aktuellen Tracker zurück."""
    return _current_tracker


def set_current_tracker(tracker: Optional[ProgressTracker]):
    """Setzt aktuellen Tracker."""
    global _current_tracker
    _current_tracker = tracker

