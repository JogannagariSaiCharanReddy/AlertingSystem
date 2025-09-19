from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from datetime import datetime

from api.services import models, schemas
from api.services.database import get_db
from api.core import reminders
router = APIRouter(
    prefix="/admin/alerts",
    tags=["Admin Alerts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Alert, status_code=201)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    # Fetch related objects to ensure they exist
    creator = db.query(models.User).filter(models.User.id == alert.created_by_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creating user not found")
        
    target_users = db.query(models.User).filter(models.User.id.in_(alert.target_user_ids)).all()
    target_teams = db.query(models.Team).filter(models.Team.id.in_(alert.target_team_ids)).all()

    # Create alert instance
    db_alert = models.Alert(
        title=alert.title,
        message_body=alert.message_body,
        severity=alert.severity,
        start_time=alert.start_time or datetime.utcnow(),
        expiry_time=alert.expiry_time,
        reminder_enabled=alert.reminder_enabled,
        is_org_wide=alert.is_org_wide,
        created_by_id=alert.created_by_id,
        target_users=target_users,
        target_teams=target_teams
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[schemas.Alert])
def list_all_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).filter(models.Alert.is_archived == False).offset(skip).limit(limit).all()
    return alerts

@router.post("/trigger-reminders", tags=["Admin Actions"])
def trigger_reminder_processing(db: Session = Depends(get_db)):
    """
    Manually triggers the reminder processing logic.
    In production, this would be replaced by a scheduled cron job.
    """
    result = reminders.process_reminders(db)
    return result

router.get("/{alert_id}", response_model=schemas.Alert)
def get_alert_by_id(alert_id: int, db: Session = Depends(get_db)):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

@router.put("/{alert_id}", response_model=schemas.Alert)
def update_alert(alert_id: int, alert_update: schemas.AlertUpdate, db: Session = Depends(get_db)):
    db_alert = get_alert_by_id(alert_id, db) # Reuse the get function to check existence

    update_data = alert_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_alert, key, value)
        
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}", status_code=204)
def archive_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Archives an alert (soft delete). It will no longer be active.
    """
    db_alert = get_alert_by_id(alert_id, db)
    db_alert.is_archived = True
    db.commit()
    return

@router.get("/", response_model=List[schemas.Alert])
def list_all_alerts(
    severity: Optional[schemas.AlertSeverity] = None,
    is_archived: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Alert).filter(models.Alert.is_archived == is_archived)
    
    if severity:
        query = query.filter(models.Alert.severity == severity)
        
    alerts = query.offset(skip).limit(limit).all()
    return alerts