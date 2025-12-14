from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class User:
    """User model"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    is_premium: bool = False
    subscription_end_date: Optional[datetime] = None
    daily_limit: int = 10
    links_bypassed_today: int = 0
    total_links_bypassed: int = 0
    joined_date: datetime = field(default_factory=datetime.utcnow)
    last_reset: str = field(default_factory=lambda: datetime.utcnow().date().isoformat())
    is_banned: bool = False
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    total_referrals: int = 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "is_premium": self.is_premium,
            "subscription_end_date": self.subscription_end_date,
            "daily_limit": self.daily_limit,
            "links_bypassed_today": self.links_bypassed_today,
            "total_links_bypassed": self.total_links_bypassed,
            "joined_date": self.joined_date,
            "last_reset": self.last_reset,
            "is_banned": self.is_banned
        }
    
    def can_bypass(self) -> bool:
        """Check if user can bypass more links"""
        if self.is_premium and self.daily_limit == -1:
            return True
        return self.links_bypassed_today < self.daily_limit

@dataclass
class Link:
    """Link cache model"""
    original_link: str
    bypassed_link: str
    bypass_type: str = "unknown"
    created_at: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "original_link": self.original_link,
            "bypassed_link": self.bypassed_link,
            "bypass_type": self.bypass_type,
            "created_at": self.created_at,
            "usage_count": self.usage_count
        }

@dataclass
class Token:
    """Access token model"""
    token: str
    duration_days: int
    created_by: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    is_used: bool = False
    used_by: Optional[int] = None
    used_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "token": self.token,
            "duration_days": self.duration_days,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "expiry_date": self.expiry_date,
            "is_used": self.is_used,
            "used_by": self.used_by,
            "used_at": self.used_at
        }
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        if self.is_used:
            return False
        if self.expiry_date and self.expiry_date < datetime.utcnow():
            return False
        return True

@dataclass
class AllowedGroup:
    """Allowed group model"""
    group_id: int
    group_name: str
    added_by: int
    added_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "added_by": self.added_by,
            "added_at": self.added_at,
            "is_active": self.is_active
        }

@dataclass
class RestrictedSite:
    """Restricted site model"""
    domain: str
    added_by: int
    added_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    reason: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "domain": self.domain,
            "added_by": self.added_by,
            "added_at": self.added_at,
            "is_active": self.is_active,
            "reason": self.reason
        }
