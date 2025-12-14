import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    
    # Admin Configuration
    ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]
    
    # MongoDB Configuration
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "link_bypasser_db")
    
    # Flask Configuration
    FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")
    PORT = int(os.environ.get("PORT", 5000))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
    
    # Force Subscription Configuration
    FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")  # Channel username with @
    FORCE_SUB_GROUP = os.environ.get("FORCE_SUB_GROUP", "")  # Group username with @
    
    # Rate Limiting Configuration
    FREE_USER_LIMIT = int(os.environ.get("FREE_USER_LIMIT", "10"))  # Links per day
    PREMIUM_USER_LIMIT = int(os.environ.get("PREMIUM_USER_LIMIT", "-1"))  # -1 = unlimited
    
    # Bot Working Mode
    WORK_IN_GROUPS_ONLY = os.environ.get("WORK_IN_GROUPS_ONLY", "False").lower() == "true"
    
    # Bypasser Service Credentials
    GDTOT_CRYPT = os.environ.get("GDTOT_CRYPT", "")
    XSRF_TOKEN = os.environ.get("XSRF_TOKEN", "")
    LARAVEL_SESSION = os.environ.get("LARAVEL_SESSION", "")
    DRIVEFIRE_CRYPT = os.environ.get("DRIVEFIRE_CRYPT", "")
    KOLOP_CRYPT = os.environ.get("KOLOP_CRYPT", "")
    HUBDRIVE_CRYPT = os.environ.get("HUBDRIVE_CRYPT", "")
    KATDRIVE_CRYPT = os.environ.get("KATDRIVE_CRYPT", "")
    UPTOBOX_TOKEN = os.environ.get("UPTOBOX_TOKEN", "")
    TERA_COOKIE = os.environ.get("TERA_COOKIE", "")
    CLOUDFLARE_COOKIE = os.environ.get("CLOUDFLARE_COOKIE", "")
    
    # Cache Configuration
    CACHE_EXPIRY_DAYS = int(os.environ.get("CACHE_EXPIRY_DAYS", "30"))
    
    # Logging
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "")  # Channel ID for logging
    
    # Referral System
    REFERRAL_ENABLED = os.environ.get("REFERRAL_ENABLED", "True").lower() == "true"
    REFERRAL_BONUS_LINKS = int(os.environ.get("REFERRAL_BONUS_LINKS", "5"))  # Bonus links per referral
    REFERRAL_BONUS_DURATION_DAYS = int(os.environ.get("REFERRAL_BONUS_DURATION_DAYS", "1"))  # Bonus validity
    MIN_REFERRALS_FOR_PREMIUM = int(os.environ.get("MIN_REFERRALS_FOR_PREMIUM", "10"))  # Refs for 1 day premium
    
    # Webhook Configuration
    USE_WEBHOOK = os.environ.get("USE_WEBHOOK", "False").lower() == "true"
    
    # Feedback System
    FEEDBACK_CHANNEL = os.environ.get("FEEDBACK_CHANNEL", "")  # Channel for user feedback
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        errors = []
        
        if not Config.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not Config.API_ID:
            errors.append("API_ID is required")
        if not Config.API_HASH:
            errors.append("API_HASH is required")
        if not Config.MONGODB_URI:
            errors.append("MONGODB_URI is required")
        if not Config.ADMIN_IDS:
            errors.append("At least one ADMIN_ID is required")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
