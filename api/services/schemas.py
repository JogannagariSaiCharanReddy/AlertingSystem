from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .models import AlertSeverity, UserAlertStatusEnum

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class User(UserBase):
    id: int
    team_id: Optional[int] = None
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    team_id : int
    email : str
    full_name :str


# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str

class Team(TeamBase):
    id: int
    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    name:str
    id:int



    


# --- Alert Schemas (for Admin Management) ---
class AlertBase(BaseModel):
    title: str
    message_body: str
    severity: AlertSeverity = AlertSeverity.INFO
    start_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    reminder_enabled: bool = True
    is_org_wide: bool = False
    target_user_ids: List[int] = []
    target_team_ids: List[int] = []

class AlertCreate(AlertBase):
    created_by_id: int

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message_body: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    expiry_time: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    is_archived: Optional[bool] = None

class Alert(AlertBase):
    id: int
    created_by: User
    is_archived: bool
    class Config:
        from_attributes = True

# --- User-Facing Alert Schemas ---
class UserAlertStatus(BaseModel):
    status: UserAlertStatusEnum
    snoozed_until: Optional[datetime]
    class Config:
        from_attributes = True

class UserAlert(BaseModel):
    """The view of an alert from an end-user's perspective."""
    id: int
    title: str
    message_body: str
    severity: AlertSeverity
    start_time: datetime
    personal_status: UserAlertStatus
    class Config:
        from_attributes = True


#analytics  schemas
class OverallStats(BaseModel):
    total_alerts_created: int
    total_notifications_sent: int
    total_reads: int
    active_snoozes: int 

class SeverityBreakdown(BaseModel):
    critical: int
    warning: int
    info: int

class AlertPerformance(BaseModel):
    alert_id: int
    alert_title: str
    notifications_sent: int
    read_count: int
    snooze_count: int 

class AnalyticsDashboard(BaseModel):
    overall_stats: OverallStats
    severity_breakdown: SeverityBreakdown
    alerts_performance: List[AlertPerformance]




