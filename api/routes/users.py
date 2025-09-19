from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List
from datetime import datetime, timedelta

from api.services import models, schemas
from api.services.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["End-User Alerts"],
)

@router.get("/{user_id}/alerts", response_model=List[schemas.UserAlert])
def get_user_alerts(user_id: int, db: Session = Depends(get_db)):
    """
    Get all active, non-expired, non-archived alerts for a specific user.
    This is the core logic for the user's dashboard.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()
    
    # Find all relevant alerts for the user
    alerts_query = db.query(models.Alert).filter(
        models.Alert.is_archived == False,
        models.Alert.start_time <= now,
        or_(models.Alert.expiry_time == None, models.Alert.expiry_time > now)
    ).filter(
        or_(
            models.Alert.is_org_wide == True,
            models.Alert.target_teams.any(id=user.team_id),
            models.Alert.target_users.any(id=user.id)
        )
    )

    alerts = alerts_query.all()
    
    # Prepare the response with personalized status
    response = []
    for alert in alerts:
        status_obj = db.query(models.UserAlertStatus).filter_by(user_id=user_id, alert_id=alert.id).first()
        if not status_obj:
            # If no status exists, it's implicitly UNREAD
            status_obj = models.UserAlertStatus(status=schemas.UserAlertStatusEnum.UNREAD, snoozed_until=None)

        response.append({
            "id": alert.id,
            "title": alert.title,
            "message_body": alert.message_body,
            "severity": alert.severity,
            "start_time": alert.start_time,
            "personal_status": {
                "status": status_obj.status,
                "snoozed_until": status_obj.snoozed_until,
            }
        })
    return response

@router.post("/{user_id}/alerts/{alert_id}/snooze", status_code=204)
def snooze_alert(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    """Snooze an alert for the current day."""
    status_obj = db.query(models.UserAlertStatus).filter_by(user_id=user_id, alert_id=alert_id).first()
    
    # Snooze until the end of the current day (in UTC)
    end_of_day = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

    if status_obj:
        status_obj.snoozed_until = end_of_day
    else:
        status_obj = models.UserAlertStatus(
            user_id=user_id, 
            alert_id=alert_id,
            snoozed_until=end_of_day
        )
        db.add(status_obj)
    
    db.commit()
    return

@router.post("/{user_id}/alerts/{alert_id}/read", status_code=204)
def mark_alert_as_read(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read."""
    status_obj = db.query(models.UserAlertStatus).filter_by(user_id=user_id, alert_id=alert_id).first()
    
    if status_obj:
        status_obj.status = schemas.UserAlertStatusEnum.READ
    else:
        status_obj = models.UserAlertStatus(
            user_id=user_id, 
            alert_id=alert_id,
            status=schemas.UserAlertStatusEnum.READ
        )
        db.add(status_obj)
        
    db.commit()
    return