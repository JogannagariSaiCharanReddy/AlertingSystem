from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from api.services import models

class NotificationChannel(ABC):
    """Abstract base class for all notification channels."""
    @abstractmethod
    def send(self, db: Session, user: models.User, alert: models.Alert):
        pass

class InAppNotificationChannel(NotificationChannel):
    """
    'Sends' a notification by creating a delivery log entry.
    In a real app, this might also send a WebSocket message.
    """
    def send(self, db: Session, user: models.User, alert: models.Alert):
        print(f"INFO: Generating IN_APP notification for user {user.id} for alert {alert.id}")
        
        delivery_log = models.NotificationDelivery(
            alert_id=alert.id,
            user_id=user.id,
            channel="IN_APP"
        )
        db.add(delivery_log)
        # The session will be committed by the calling service.

# --- Factory to get the desired channel ---
def get_notification_channel(channel_name: str) -> NotificationChannel:
    if channel_name.upper() == "IN_APP":
        return InAppNotificationChannel()
    # In the future, we would add Email, SMS, etc.
    # elif channel_name.upper() == "EMAIL":
    #     return EmailNotificationChannel()
    else:
        raise ValueError(f"Unsupported notification channel: {channel_name}")