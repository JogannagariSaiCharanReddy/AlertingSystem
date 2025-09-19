from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from typing import List, Tuple

from services import models
from core.notifications import get_notification_channel

def find_users_needing_reminders(db: Session) -> List[Tuple[models.User, models.Alert]]:
    """
    Finds all pairs of (user, alert) that require a notification right now.
    
    A user needs a reminder if:
    1. The alert is active, not archived, and has reminders enabled.
    2. The user is a target of the alert (org-wide, team, or individual).
    3. The user has not marked the alert as READ.
    4. The user's snooze period for the alert has expired.
    """
    now = datetime.utcnow()
    
    # Subquery to find alerts that are currently active
    active_alerts = db.query(models.Alert.id).filter(
        models.Alert.is_archived == False,
        models.Alert.reminder_enabled == True,
        models.Alert.start_time <= now,
        or_(models.Alert.expiry_time == None, models.Alert.expiry_time > now)
    ).subquery()
    
    # Main query to find users who need a reminder
    users_to_notify = db.query(models.User, models.Alert). \
        join(models.Alert, or_(
            models.Alert.is_org_wide == True,
            models.Alert.target_teams.any(id=models.User.team_id),
            models.Alert.target_users.any(id=models.User.id)
        )). \
        outerjoin(models.UserAlertStatus, and_(
            models.UserAlertStatus.user_id == models.User.id,
            models.UserAlertStatus.alert_id == models.Alert.id
        )). \
        filter(models.Alert.id.in_(active_alerts)). \
        filter(
            or_(
                # Condition 1: No status record exists, so it's implicitly UNREAD and not snoozed
                models.UserAlertStatus.id == None,
                # Condition 2: A status record exists, but it's UNREAD and not snoozed
                and_(
                    models.UserAlertStatus.status == models.UserAlertStatusEnum.UNREAD,
                    or_(
                        models.UserAlertStatus.snoozed_until == None,
                        models.UserAlertStatus.snoozed_until <= now
                    )
                )
            )
        ).all()
        
    return users_to_notify

def process_reminders(db: Session):
    """
    Orchestrates the process of finding and sending reminders.
    """
    users_and_alerts = find_users_needing_reminders(db)
    
    if not users_and_alerts:
        print("INFO: No reminders to send at this time.")
        return {"message": "No reminders to send."}

    # For now, we only support the "IN_APP" channel
    notification_channel = get_notification_channel("IN_APP")
    
    for user, alert in users_and_alerts:
        notification_channel.send(db, user, alert)
        
    db.commit() # Commit all the new delivery logs at once
    
    return {"message": f"Successfully sent {len(users_and_alerts)} reminders."}