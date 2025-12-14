import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.links = None
        self.tokens = None
        self.allowed_groups = None
        self.restricted_sites = None
        self.stats = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(Config.MONGODB_URI)
            self.db = self.client[Config.DATABASE_NAME]
            
            # Initialize collections
            self.users = self.db.users
            self.links = self.db.links
            self.tokens = self.db.tokens
            self.allowed_groups = self.db.allowed_groups
            self.restricted_sites = self.db.restricted_sites
            self.stats = self.db.stats
            self.referrals = self.db.referrals
            self.feedback = self.db.feedback
            self.site_requests = self.db.site_requests
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("MongoDB connected successfully")
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for optimization"""
        try:
            # Users collection indexes
            await self.users.create_index("user_id", unique=True)
            await self.users.create_index("is_premium")
            await self.users.create_index("subscription_end_date")
            
            # Links collection indexes
            await self.links.create_index("original_link", unique=True)
            await self.links.create_index("created_at")
            await self.links.create_index([("created_at", DESCENDING)])
            
            # Tokens collection indexes
            await self.tokens.create_index("token", unique=True)
            await self.tokens.create_index("is_used")
            await self.tokens.create_index("expiry_date")
            
            # Allowed groups indexes
            await self.allowed_groups.create_index("group_id", unique=True)
            
            # Restricted sites indexes
            await self.restricted_sites.create_index("domain", unique=True)
            
            # Referrals indexes
            await self.referrals.create_index("referrer_id")
            await self.referrals.create_index("referred_id", unique=True)
            
            # Feedback indexes
            await self.feedback.create_index("user_id")
            await self.feedback.create_index("created_at")
            await self.feedback.create_index("status")
            
            # Site requests indexes
            await self.site_requests.create_index("user_id")
            await self.site_requests.create_index("domain")
            await self.site_requests.create_index("status")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    # User Methods
    async def get_user(self, user_id: int):
        """Get user by ID"""
        return await self.users.find_one({"user_id": user_id})
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Create new user"""
        user = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "is_premium": False,
            "subscription_end_date": None,
            "daily_limit": Config.FREE_USER_LIMIT,
            "links_bypassed_today": 0,
            "total_links_bypassed": 0,
            "joined_date": datetime.utcnow(),
            "last_reset": datetime.utcnow().date().isoformat(),
            "is_banned": False
        }
        await self.users.insert_one(user)
        return user
    
    async def update_user(self, user_id: int, update_data: dict):
        """Update user data"""
        return await self.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    async def increment_user_usage(self, user_id: int):
        """Increment user's bypass count"""
        today = datetime.utcnow().date().isoformat()
        user = await self.get_user(user_id)
        
        if user and user.get("last_reset") != today:
            # Reset daily counter
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "links_bypassed_today": 1,
                        "last_reset": today
                    },
                    "$inc": {"total_links_bypassed": 1}
                }
            )
        else:
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "links_bypassed_today": 1,
                        "total_links_bypassed": 1
                    }
                }
            )
    
    async def reset_user_limit(self, user_id: int):
        """Reset user's daily limit"""
        return await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"links_bypassed_today": 0, "last_reset": datetime.utcnow().date().isoformat()}}
        )
    
    async def set_premium(self, user_id: int, duration_days: int):
        """Set user as premium"""
        end_date = datetime.utcnow() + timedelta(days=duration_days)
        return await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "subscription_end_date": end_date,
                    "daily_limit": Config.PREMIUM_USER_LIMIT
                }
            }
        )
    
    async def check_premium_expired(self, user_id: int):
        """Check and update premium status if expired"""
        user = await self.get_user(user_id)
        if user and user.get("is_premium"):
            if user.get("subscription_end_date") and user["subscription_end_date"] < datetime.utcnow():
                await self.users.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "is_premium": False,
                            "subscription_end_date": None,
                            "daily_limit": Config.FREE_USER_LIMIT
                        }
                    }
                )
                return True
        return False
    
    # Link Methods
    async def get_cached_link(self, original_link: str):
        """Get cached bypass result"""
        result = await self.links.find_one({"original_link": original_link})
        if result:
            # Check if cache is expired
            if result.get("created_at"):
                age = datetime.utcnow() - result["created_at"]
                if age.days > Config.CACHE_EXPIRY_DAYS:
                    await self.links.delete_one({"original_link": original_link})
                    return None
        return result
    
    async def save_bypass_result(self, original_link: str, bypassed_link: str, bypass_type: str = "unknown"):
        """Save bypass result to cache"""
        link_data = {
            "original_link": original_link,
            "bypassed_link": bypassed_link,
            "bypass_type": bypass_type,
            "created_at": datetime.utcnow(),
            "usage_count": 1
        }
        await self.links.update_one(
            {"original_link": original_link},
            {"$set": link_data},
            upsert=True
        )
    
    async def increment_link_usage(self, original_link: str):
        """Increment usage count for cached link"""
        await self.links.update_one(
            {"original_link": original_link},
            {"$inc": {"usage_count": 1}}
        )
    
    # Token Methods
    async def create_token(self, duration_days: int, created_by: int):
        """Create access token"""
        import secrets
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(days=duration_days)
        
        token_data = {
            "token": token,
            "duration_days": duration_days,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "expiry_date": expiry,
            "is_used": False,
            "used_by": None,
            "used_at": None
        }
        
        await self.tokens.insert_one(token_data)
        return token
    
    async def get_token(self, token: str):
        """Get token details"""
        return await self.tokens.find_one({"token": token})
    
    async def use_token(self, token: str, user_id: int):
        """Mark token as used and activate premium"""
        token_data = await self.get_token(token)
        
        if not token_data:
            return {"success": False, "message": "Invalid token"}
        
        if token_data["is_used"]:
            return {"success": False, "message": "Token already used"}
        
        if token_data["expiry_date"] < datetime.utcnow():
            return {"success": False, "message": "Token expired"}
        
        # Mark token as used
        await self.tokens.update_one(
            {"token": token},
            {
                "$set": {
                    "is_used": True,
                    "used_by": user_id,
                    "used_at": datetime.utcnow()
                }
            }
        )
        
        # Activate premium
        await self.set_premium(user_id, token_data["duration_days"])
        
        return {"success": True, "message": f"Premium activated for {token_data['duration_days']} days"}
    
    # Reset Key Methods
    async def create_reset_key(self, created_by: int):
        """Create reset key for free users"""
        import secrets
        key = secrets.token_urlsafe(16)
        
        key_data = {
            "key": key,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "is_used": False,
            "used_by": None
        }
        
        await self.db.reset_keys.insert_one(key_data)
        return key
    
    async def use_reset_key(self, key: str, user_id: int):
        """Use reset key to reset user limit"""
        key_data = await self.db.reset_keys.find_one({"key": key})
        
        if not key_data:
            return {"success": False, "message": "Invalid reset key"}
        
        if key_data["is_used"]:
            return {"success": False, "message": "Reset key already used"}
        
        # Mark as used
        await self.db.reset_keys.update_one(
            {"key": key},
            {
                "$set": {
                    "is_used": True,
                    "used_by": user_id,
                    "used_at": datetime.utcnow()
                }
            }
        )
        
        # Reset user limit
        await self.reset_user_limit(user_id)
        
        return {"success": True, "message": "Daily limit reset successfully"}
    
    # Group Management
    async def add_allowed_group(self, group_id: int, group_name: str, added_by: int):
        """Add group to allowed list"""
        group_data = {
            "group_id": group_id,
            "group_name": group_name,
            "added_by": added_by,
            "added_at": datetime.utcnow(),
            "is_active": True
        }
        await self.allowed_groups.update_one(
            {"group_id": group_id},
            {"$set": group_data},
            upsert=True
        )
    
    async def remove_allowed_group(self, group_id: int):
        """Remove group from allowed list"""
        return await self.allowed_groups.delete_one({"group_id": group_id})
    
    async def is_group_allowed(self, group_id: int):
        """Check if group is allowed"""
        group = await self.allowed_groups.find_one({"group_id": group_id})
        return group and group.get("is_active", False)
    
    async def get_all_allowed_groups(self):
        """Get all allowed groups"""
        return await self.allowed_groups.find({"is_active": True}).to_list(length=None)
    
    # Restricted Sites Management
    async def add_restricted_site(self, domain: str, added_by: int):
        """Add site to restricted list"""
        site_data = {
            "domain": domain.lower(),
            "added_by": added_by,
            "added_at": datetime.utcnow(),
            "is_active": True
        }
        await self.restricted_sites.update_one(
            {"domain": domain.lower()},
            {"$set": site_data},
            upsert=True
        )
    
    async def remove_restricted_site(self, domain: str):
        """Remove site from restricted list"""
        return await self.restricted_sites.delete_one({"domain": domain.lower()})
    
    async def is_site_restricted(self, url: str):
        """Check if site is restricted"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        site = await self.restricted_sites.find_one({"domain": domain})
        return site and site.get("is_active", False)
    
    async def get_all_restricted_sites(self):
        """Get all restricted sites"""
        return await self.restricted_sites.find({"is_active": True}).to_list(length=None)
    
    # Statistics
    async def get_bot_stats(self):
        """Get bot statistics"""
        total_users = await self.users.count_documents({})
        premium_users = await self.users.count_documents({"is_premium": True})
        total_links = await self.links.count_documents({})
        total_bypasses = await self.users.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$total_links_bypassed"}}}
        ]).to_list(length=1)
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "free_users": total_users - premium_users,
            "cached_links": total_links,
            "total_bypasses": total_bypasses[0]["total"] if total_bypasses else 0
        }
    
    # Broadcast
    async def get_all_users(self):
        """Get all active users for broadcast"""
        return await self.users.find({"is_banned": False}).to_list(length=None)
    
    # Referral System
    async def create_referral(self, referrer_id: int, referred_id: int):
        """Create a referral record"""
        try:
            referral_data = {
                "referrer_id": referrer_id,
                "referred_id": referred_id,
                "created_at": datetime.utcnow(),
                "bonus_claimed": False
            }
            await self.referrals.insert_one(referral_data)
            return True
        except Exception as e:
            logger.error(f"Error creating referral: {e}")
            return False
    
    async def get_referral_count(self, user_id: int):
        """Get number of successful referrals"""
        return await self.referrals.count_documents({"referrer_id": user_id})
    
    async def get_referrals(self, user_id: int):
        """Get all referrals by user"""
        return await self.referrals.find({"referrer_id": user_id}).to_list(length=None)
    
    async def has_been_referred(self, user_id: int):
        """Check if user was referred by someone"""
        return await self.referrals.find_one({"referred_id": user_id}) is not None
    
    async def claim_referral_bonus(self, referrer_id: int, referred_id: int):
        """Mark referral bonus as claimed"""
        await self.referrals.update_one(
            {"referrer_id": referrer_id, "referred_id": referred_id},
            {"$set": {"bonus_claimed": True, "claimed_at": datetime.utcnow()}}
        )
    
    async def get_referral_stats(self, user_id: int):
        """Get referral statistics for user"""
        total_referrals = await self.get_referral_count(user_id)
        referrals = await self.get_referrals(user_id)
        claimed = sum(1 for r in referrals if r.get("bonus_claimed", False))
        
        return {
            "total_referrals": total_referrals,
            "claimed_bonuses": claimed,
            "unclaimed_bonuses": total_referrals - claimed
        }
    
    # Feedback System
    async def create_feedback(self, user_id: int, feedback_type: str, content: str, link: str = None):
        """Create user feedback"""
        feedback_data = {
            "user_id": user_id,
            "type": feedback_type,  # broken_link, error_report, suggestion
            "content": content,
            "link": link,
            "status": "pending",  # pending, reviewed, resolved
            "created_at": datetime.utcnow(),
            "reviewed_by": None,
            "reviewed_at": None
        }
        result = await self.feedback.insert_one(feedback_data)
        return str(result.inserted_id)
    
    async def get_feedback(self, feedback_id: str):
        """Get feedback by ID"""
        from bson import ObjectId
        return await self.feedback.find_one({"_id": ObjectId(feedback_id)})
    
    async def get_all_feedback(self, status: str = None):
        """Get all feedback, optionally filtered by status"""
        query = {"status": status} if status else {}
        return await self.feedback.find(query).sort("created_at", DESCENDING).to_list(length=100)
    
    async def update_feedback_status(self, feedback_id: str, status: str, admin_id: int):
        """Update feedback status"""
        from bson import ObjectId
        await self.feedback.update_one(
            {"_id": ObjectId(feedback_id)},
            {
                "$set": {
                    "status": status,
                    "reviewed_by": admin_id,
                    "reviewed_at": datetime.utcnow()
                }
            }
        )
    
    # Site Requests
    async def create_site_request(self, user_id: int, domain: str, description: str = None):
        """Create a site support request"""
        request_data = {
            "user_id": user_id,
            "domain": domain.lower(),
            "description": description,
            "status": "pending",  # pending, approved, rejected, implemented
            "upvotes": 1,
            "upvoted_by": [user_id],
            "created_at": datetime.utcnow(),
            "reviewed_by": None,
            "reviewed_at": None
        }
        result = await self.site_requests.insert_one(request_data)
        return str(result.inserted_id)
    
    async def get_site_request(self, request_id: str):
        """Get site request by ID"""
        from bson import ObjectId
        return await self.site_requests.find_one({"_id": ObjectId(request_id)})
    
    async def get_site_requests(self, status: str = None):
        """Get site requests, optionally filtered by status"""
        query = {"status": status} if status else {}
        return await self.site_requests.find(query).sort("upvotes", DESCENDING).to_list(length=50)
    
    async def upvote_site_request(self, request_id: str, user_id: int):
        """Upvote a site request"""
        from bson import ObjectId
        request = await self.get_site_request(request_id)
        
        if request and user_id not in request.get("upvoted_by", []):
            await self.site_requests.update_one(
                {"_id": ObjectId(request_id)},
                {
                    "$inc": {"upvotes": 1},
                    "$push": {"upvoted_by": user_id}
                }
            )
            return True
        return False
    
    async def update_site_request_status(self, request_id: str, status: str, admin_id: int):
        """Update site request status"""
        from bson import ObjectId
        await self.site_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": status,
                    "reviewed_by": admin_id,
                    "reviewed_at": datetime.utcnow()
                }
            }
        )
    
    async def site_request_exists(self, domain: str):
        """Check if site request already exists"""
        return await self.site_requests.find_one({"domain": domain.lower(), "status": {"$in": ["pending", "approved"]}})

# Global database instance
db = Database()
