"""
Notification Service Routes
Implements notification management endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from .models import (
    Notification, NotificationCreate, NotificationTemplate, NotificationTemplateCreate,
    BulkNotification, BulkNotificationCreate, NotificationPreference,
    NotificationPreferenceUpdate, NotificationChannel, NotificationStatus
)

# Mock database
NOTIFICATIONS_DB = {}
TEMPLATES_DB = {}
PREFERENCES_DB = {}
CHANNELS_DB = {
    1: {
        "id": 1,
        "name": "Email Service",
        "channel_type": "email",
        "is_active": True,
        "configuration": {"provider": "smtp"},
        "created_at": datetime.utcnow()
    }
}
NOTIFICATION_ID_COUNTER = 1

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


# ===== NOTIFICATIONS =====
@router.post("", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def send_notification(notification_data: NotificationCreate) -> Notification:
    """
    Send a notification to a user.
    
    **Best Practice**: Validate user preferences before sending
    """
    global NOTIFICATION_ID_COUNTER
    
    # Check user notification preferences
    prefs = next((p for p in PREFERENCES_DB.values() if p["user_id"] == notification_data.recipient_id), None)
    if prefs:
        # Check if this notification type is enabled for user
        if notification_data.notification_type == "email" and not prefs.get("email_notifications", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email notifications disabled for this user"
            )
    
    notification_id = NOTIFICATION_ID_COUNTER
    NOTIFICATION_ID_COUNTER += 1
    
    new_notification = {
        "id": notification_id,
        "recipient_id": notification_data.recipient_id,
        "title": notification_data.title,
        "content": notification_data.content,
        "notification_type": notification_data.notification_type,
        "priority": notification_data.priority,
        "status": "pending" if notification_data.scheduled_at else "sent",
        "read": False,
        "scheduled_at": notification_data.scheduled_at,
        "sent_at": datetime.utcnow() if not notification_data.scheduled_at else None,
        "read_at": None,
        "metadata": notification_data.metadata,
        "created_at": datetime.utcnow()
    }
    
    NOTIFICATIONS_DB[notification_id] = new_notification
    return Notification(**new_notification)


@router.get("", response_model=List[Notification])
async def list_notifications(user_id: int = None, unread_only: bool = False, skip: int = 0, limit: int = 10) -> List[Notification]:
    """
    List notifications with filtering.
    
    **Best Practice**: Show most recent first and support inbox-style views
    """
    notifications = list(NOTIFICATIONS_DB.values())
    
    if user_id:
        notifications = [n for n in notifications if n["recipient_id"] == user_id]
    
    if unread_only:
        notifications = [n for n in notifications if not n["read"]]
    
    notifications = sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    return [Notification(**n) for n in notifications[skip:skip + limit]]


@router.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: int) -> Notification:
    """Get a specific notification."""
    notification = NOTIFICATIONS_DB.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return Notification(**notification)


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: int) -> Notification:
    """Mark a notification as read."""
    notification = NOTIFICATIONS_DB.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification["read"] = True
    notification["read_at"] = datetime.utcnow()
    notification["status"] = "read"
    
    return Notification(**notification)


@router.post("/users/{user_id}/read-all")
async def mark_all_as_read(user_id: int) -> dict:
    """Mark all notifications as read for a user."""
    user_notifications = [n for n in NOTIFICATIONS_DB.values() if n["recipient_id"] == user_id]
    
    for notification in user_notifications:
        if not notification["read"]:
            notification["read"] = True
            notification["read_at"] = datetime.utcnow()
            notification["status"] = "read"
    
    return {"marked_as_read": len(user_notifications)}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int):
    """Delete a notification."""
    if notification_id not in NOTIFICATIONS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    del NOTIFICATIONS_DB[notification_id]


# ===== BULK NOTIFICATIONS =====
@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def send_bulk_notification(bulk_data: BulkNotificationCreate) -> dict:
    """
    Send notifications to multiple users.
    
    **Best Practice**: Use background tasks for bulk operations
    """
    sent_count = 0
    failed_count = 0
    
    for recipient_id in bulk_data.recipient_ids:
        try:
            notification_data = NotificationCreate(
                recipient_id=recipient_id,
                title=bulk_data.title,
                content=bulk_data.content,
                notification_type=bulk_data.notification_type,
                priority=bulk_data.priority,
                scheduled_at=bulk_data.scheduled_at
            )
            
            await send_notification(notification_data)
            sent_count += 1
        except Exception as e:
            failed_count += 1
    
    return {
        "total_recipients": len(bulk_data.recipient_ids),
        "sent_count": sent_count,
        "failed_count": failed_count,
        "status": "completed"
    }


# ===== NOTIFICATION TEMPLATES =====
@router.post("/templates", response_model=NotificationTemplate, status_code=status.HTTP_201_CREATED)
async def create_template(template_data: NotificationTemplateCreate) -> NotificationTemplate:
    """
    Create a notification template.
    
    **Best Practice**: Support variable substitution for personalization
    """
    template_id = len(TEMPLATES_DB) + 1
    new_template = {
        "id": template_id,
        "name": template_data.name,
        "subject": template_data.subject,
        "content": template_data.content,
        "notification_type": template_data.notification_type,
        "variables": template_data.variables or [],
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    TEMPLATES_DB[template_id] = new_template
    return NotificationTemplate(**new_template)


@router.get("/templates", response_model=List[NotificationTemplate])
async def list_templates() -> List[NotificationTemplate]:
    """List all notification templates."""
    return [NotificationTemplate(**t) for t in TEMPLATES_DB.values()]


@router.get("/templates/{template_id}", response_model=NotificationTemplate)
async def get_template(template_id: int) -> NotificationTemplate:
    """Get a specific template."""
    template = TEMPLATES_DB.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return NotificationTemplate(**template)


@router.post("/templates/{template_id}/send")
async def send_with_template(template_id: int, recipient_id: int, variables: dict = None) -> Notification:
    """
    Send notification using a template with variable substitution.
    
    **Best Practice**: Validate variables against template definition
    """
    template = TEMPLATES_DB.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Substitute variables in content
    content = template["content"]
    if variables:
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
    
    notification_data = NotificationCreate(
        recipient_id=recipient_id,
        title=template["subject"],
        content=content,
        notification_type=template["notification_type"]
    )
    
    return await send_notification(notification_data)


# ===== NOTIFICATION PREFERENCES =====
@router.post("/preferences/{user_id}", response_model=NotificationPreference, status_code=status.HTTP_201_CREATED)
async def create_notification_preference(user_id: int, prefs_data: NotificationPreferenceUpdate = None) -> NotificationPreference:
    """Create notification preferences for a user."""
    
    preference_id = len(PREFERENCES_DB) + 1
    new_preference = {
        "id": preference_id,
        "user_id": user_id,
        "email_notifications": True if prefs_data is None else prefs_data.email_notifications if prefs_data.email_notifications is not None else True,
        "sms_notifications": False if prefs_data is None else prefs_data.sms_notifications if prefs_data.sms_notifications is not None else False,
        "in_app_notifications": True if prefs_data is None else prefs_data.in_app_notifications if prefs_data.in_app_notifications is not None else True,
        "push_notifications": False if prefs_data is None else prefs_data.push_notifications if prefs_data.push_notifications is not None else False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    PREFERENCES_DB[preference_id] = new_preference
    return NotificationPreference(**new_preference)


@router.get("/preferences/{user_id}", response_model=NotificationPreference)
async def get_notification_preference(user_id: int) -> NotificationPreference:
    """Get notification preferences for a user."""
    prefs = next((p for p in PREFERENCES_DB.values() if p["user_id"] == user_id), None)
    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    return NotificationPreference(**prefs)


@router.put("/preferences/{user_id}", response_model=NotificationPreference)
async def update_notification_preference(user_id: int, prefs_update: NotificationPreferenceUpdate) -> NotificationPreference:
    """Update notification preferences."""
    prefs = next((p for p in PREFERENCES_DB.values() if p["user_id"] == user_id), None)
    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    if prefs_update.email_notifications is not None:
        prefs["email_notifications"] = prefs_update.email_notifications
    if prefs_update.sms_notifications is not None:
        prefs["sms_notifications"] = prefs_update.sms_notifications
    if prefs_update.in_app_notifications is not None:
        prefs["in_app_notifications"] = prefs_update.in_app_notifications
    if prefs_update.push_notifications is not None:
        prefs["push_notifications"] = prefs_update.push_notifications
    
    prefs["updated_at"] = datetime.utcnow()
    return NotificationPreference(**prefs)


# ===== NOTIFICATION CHANNELS =====
@router.post("/channels", status_code=status.HTTP_201_CREATED)
async def create_notification_channel(channel_data) -> dict:
    """Create a notification channel (email, SMS provider, etc)."""
    channel_id = len(CHANNELS_DB) + 1
    new_channel = {
        "id": channel_id,
        "name": channel_data.get("name"),
        "channel_type": channel_data.get("channel_type"),
        "is_active": True,
        "configuration": channel_data.get("configuration", {}),
        "created_at": datetime.utcnow()
    }
    
    CHANNELS_DB[channel_id] = new_channel
    return {"id": channel_id, "message": "Channel created successfully"}


@router.get("/channels")
async def list_notification_channels() -> List[dict]:
    """List all notification channels."""
    return list(CHANNELS_DB.values())


# ===== NOTIFICATION STATISTICS =====
@router.get("/stats/summary")
async def get_notification_stats() -> dict:
    """Get notification statistics."""
    total = len(NOTIFICATIONS_DB)
    read = sum(1 for n in NOTIFICATIONS_DB.values() if n["read"])
    unread = total - read
    
    by_type = {}
    for n in NOTIFICATIONS_DB.values():
        ntype = n["notification_type"]
        by_type[ntype] = by_type.get(ntype, 0) + 1
    
    return {
        "total_notifications": total,
        "read": read,
        "unread": unread,
        "by_type": by_type,
        "total_templates": len(TEMPLATES_DB)
    }
