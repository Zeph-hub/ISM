"""
Notification Service Models
Defines Pydantic models for notification management.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class NotificationPriority(str, Enum):
    """Notification priority level"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationBase(BaseModel):
    """Base notification model"""
    recipient_id: int
    title: str
    content: str
    notification_type: NotificationType


class NotificationCreate(NotificationBase):
    """Notification creation model"""
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class Notification(NotificationBase):
    """Notification response model"""
    id: int
    priority: NotificationPriority
    status: NotificationStatus
    read: bool = False
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationTemplateBase(BaseModel):
    """Base notification template model"""
    name: str
    subject: str
    content: str
    notification_type: NotificationType


class NotificationTemplateCreate(NotificationTemplateBase):
    """Template creation model"""
    variables: Optional[list[str]] = []  # e.g., ["student_name", "course_title"]


class NotificationTemplate(NotificationTemplateBase):
    """Template response model"""
    id: int
    variables: Optional[list[str]] = []
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkNotificationBase(BaseModel):
    """Base bulk notification model"""
    recipient_ids: list[int]
    title: str
    content: str
    notification_type: NotificationType


class BulkNotificationCreate(BulkNotificationBase):
    """Bulk notification creation model"""
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None


class BulkNotification(BulkNotificationBase):
    """Bulk notification response model"""
    id: int
    priority: NotificationPriority
    total_recipients: int
    sent_count: int = 0
    failed_count: int = 0
    status: str  # "pending", "in_progress", "completed"
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationPreferenceBase(BaseModel):
    """Base notification preference model"""
    user_id: int
    email_notifications: bool = True
    sms_notifications: bool = False
    in_app_notifications: bool = True
    push_notifications: bool = False


class NotificationPreferenceUpdate(BaseModel):
    """Notification preference update model"""
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


class NotificationPreference(NotificationPreferenceBase):
    """Notification preference response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationChannelBase(BaseModel):
    """Base notification channel model (for SMS, email service integration)"""
    name: str
    channel_type: NotificationType
    is_active: bool = True
    configuration: dict  # Provider-specific config


class NotificationChannel(NotificationChannelBase):
    """Notification channel response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationLogBase(BaseModel):
    """Base notification log model"""
    notification_id: int
    status: NotificationStatus
    details: Optional[str] = None


class NotificationLog(NotificationLogBase):
    """Notification log response model"""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True
