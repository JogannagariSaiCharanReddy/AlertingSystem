from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Enum, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from .database import Base

# --- Enum Definitions ---
class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class UserAlertStatusEnum(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"

# --- Association Tables for Visibility ---
alert_target_users = Table('alert_target_users', Base.metadata,
    Column('alert_id', Integer, ForeignKey('alerts.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

alert_target_teams = Table('alert_target_teams', Base.metadata,
    Column('alert_id', Integer, ForeignKey('alerts.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

# --- Core Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="members")
    created_alerts = relationship("Alert", back_populates="created_by")
    alert_statuses = relationship("UserAlertStatus", back_populates="user", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    members = relationship("User", back_populates="team")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    message_body = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO, nullable=False)
    
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    expiry_time = Column(DateTime(timezone=True), nullable=True)
    
    reminder_enabled = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Visibility fields
    is_org_wide = Column(Boolean, default=False)
    
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="created_alerts")

    # Many-to-Many relationships for visibility
    target_users = relationship("User", secondary=alert_target_users)
    target_teams = relationship("Team", secondary=alert_target_teams)

    user_statuses = relationship("UserAlertStatus", back_populates="alert", cascade="all, delete-orphan")

class UserAlertStatus(Base):
    """Tracks the interaction of a specific user with a specific alert."""
    __tablename__ = "user_alert_status"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)

    status = Column(Enum(UserAlertStatusEnum), default=UserAlertStatusEnum.UNREAD, nullable=False)
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="alert_statuses")
    alert = relationship("Alert", back_populates="user_statuses")

class NotificationDelivery(Base):
    """A log to track every notification sent. Useful for analytics."""
    __tablename__ = "notification_deliveries"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(String, nullable=False) # e.g., "IN_APP", "EMAIL"
    sent_at = Column(DateTime(timezone=True), server_default=func.now())