"""
Pydantic Models für Missionen.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MissionAction(BaseModel):
    """Einzelne Aktion innerhalb einer Mission."""
    priority: str = Field(..., description="high, medium, low")
    action: str = Field(..., description="Name der Aktion")
    description: str = Field(..., description="Detailbeschreibung")


class MissionCreate(BaseModel):
    """Request für Mission-Erstellung."""
    user_id: str = Field(..., description="UUID des Users")
    parent_cell_id: Optional[str] = Field(None, description="Parent Cell ID")
    child_cell_id: Optional[str] = Field(None, description="Child Cell ID")
    cell_analysis_id: Optional[str] = Field(None, description="Cell Analysis ID")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    mission_type: Optional[str] = Field("analyze_hotspot", description="Mission Type")
    heat_risk_score: Optional[float] = Field(None, ge=0, le=100)
    required_actions: List[MissionAction] = Field(default_factory=list)


class MissionResponse(BaseModel):
    """Mission Response für Frontend."""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    lat: float
    lng: float
    heatRisk: float  # Frontend erwartet camelCase
    reasons: List[str]
    actions: List[str]
    completed: bool
    imageUrl: Optional[str] = None
    
    # Additional Backend Fields
    parent_cell_id: Optional[str] = None
    child_cell_id: Optional[str] = None
    cell_analysis_id: Optional[str] = None
    mission_type: Optional[str] = None
    status: str = "pending"
    points_earned: int = 0
    distance_to_user: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class MissionUpdate(BaseModel):
    """Update einer Mission."""
    status: Optional[str] = Field(None, description="pending, active, completed, cancelled")
    points_earned: Optional[int] = Field(None, ge=0)


class MissionListResponse(BaseModel):
    """Liste von Missionen mit Metadaten."""
    missions: List[MissionResponse]
    total_count: int
    pending_count: int
    completed_count: int
    user_id: Optional[str] = None

