from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime
from typing import Dict

from api.services import models, schemas
from api.services.database import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

@router.get("/dashboard", response_model=schemas.AnalyticsDashboard)
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """
    Provides a dashboard with system-wide metrics on alert performance.
    """
    now = datetime.utcnow()

    # --- 1. Overall Stats ---
    total_alerts = db.query(func.count(models.Alert.id)).scalar()
    total_deliveries = db.query(func.count(models.NotificationDelivery.id)).scalar()
    
    total_reads_query = db.query(func.count(models.UserAlertStatus.id)).filter(
        models.UserAlertStatus.status == models.UserAlertStatusEnum.READ
    ).scalar()
    
    active_snoozes_query = db.query(func.count(models.UserAlertStatus.id)).filter(
        models.UserAlertStatus.snoozed_until > now
    ).scalar()

    overall_stats = schemas.OverallStats(
        total_alerts_created=total_alerts,
        total_notifications_sent=total_deliveries,
        total_reads=total_reads_query,
        active_snoozes=active_snoozes_query,
    )

    # --- 2. Severity Breakdown ---
    severity_counts_query = db.query(
        models.Alert.severity,
        func.count(models.Alert.id)
    ).group_by(models.Alert.severity).all()
    
    # Convert list of tuples to a dictionary for easy access
    severity_map: Dict[str, int] = {sev.name: count for sev, count in severity_counts_query}

    severity_breakdown = schemas.SeverityBreakdown(
        critical=severity_map.get("CRITICAL", 0),
        warning=severity_map.get("WARNING", 0),
        info=severity_map.get("INFO", 0),
    )

    # --- 3. Per-Alert Performance ---
    # This is a more complex query joining alerts with aggregated stats
    
    # Subquery for notification counts per alert
    delivery_counts = db.query(
        models.NotificationDelivery.alert_id,
        func.count(models.NotificationDelivery.id).label("delivery_count")
    ).group_by(models.NotificationDelivery.alert_id).subquery()

    # Subquery for read and snooze counts per alert
    status_counts = db.query(
        models.UserAlertStatus.alert_id,
        func.count(case((models.UserAlertStatus.status == models.UserAlertStatusEnum.READ, 1))).label("read_count"),
        func.count(case((models.UserAlertStatus.snoozed_until > now, 1))).label("snooze_count")
    ).group_by(models.UserAlertStatus.alert_id).subquery()

    # Main query to assemble the performance data
    alerts_performance_query = db.query(
        models.Alert.id,
        models.Alert.title,
        func.coalesce(delivery_counts.c.delivery_count, 0).label("notifications_sent"),
        func.coalesce(status_counts.c.read_count, 0).label("read_count"),
        func.coalesce(status_counts.c.snooze_count, 0).label("snooze_count")
    ).outerjoin(
        delivery_counts, models.Alert.id == delivery_counts.c.alert_id
    ).outerjoin(
        status_counts, models.Alert.id == status_counts.c.alert_id
    ).order_by(models.Alert.id).all()

    alerts_performance = [
        schemas.AlertPerformance(
            alert_id=row.id,
            alert_title=row.title,
            notifications_sent=row.notifications_sent,
            read_count=row.read_count,
            snooze_count=row.snooze_count,
        ) for row in alerts_performance_query
    ]

    # --- Assemble final dashboard object ---
    return schemas.AnalyticsDashboard(
        overall_stats=overall_stats,
        severity_breakdown=severity_breakdown,
        alerts_performance=alerts_performance
    )