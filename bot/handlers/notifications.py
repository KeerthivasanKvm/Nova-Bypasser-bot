import logging
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client
from config import Config
from database.mongodb import db
from bot.utils.keyboards import Keyboards

logger = logging.getLogger(__name__)

class NotificationSystem:
    """Premium subscription notification system"""
    
    def __init__(self, client: Client):
        self.client = client
        self.running = False
    
    async def start(self):
        """Start the notification system"""
        self.running = True
        logger.info("Notification system started")
        
        # Run notification checks in background
        asyncio.create_task(self.notification_loop())
    
    async def stop(self):
        """Stop the notification system"""
        self.running = False
        logger.info("Notification system stopped")
    
    async def notification_loop(self):
        """Main notification loop - runs every hour"""
        while self.running:
            try:
                await self.check_expiring_subscriptions()
                await self.check_limit_warnings()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Notification loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_expiring_subscriptions(self):
        """Check and notify users about expiring premium subscriptions"""
        try:
            # Get all premium users
            users = await db.users.find({"is_premium": True}).to_list(length=None)
            
            now = datetime.utcnow()
            
            for user in users:
                try:
                    user_id = user.get("user_id")
                    sub_end = user.get("subscription_end_date")
                    
                    if not sub_end:
                        continue
                    
                    # Calculate days remaining
                    time_remaining = sub_end - now
                    days_remaining = time_remaining.days
                    hours_remaining = time_remaining.seconds // 3600
                    
                    # Check if already notified today
                    last_notified = user.get("last_notification_date")
                    today = now.date().isoformat()
                    
                    if last_notified == today:
                        continue  # Already notified today
                    
                    # Notification thresholds
                    notification_sent = False
                    
                    # 30 days before expiry
                    if days_remaining == 30:
                        await self.send_expiry_notification(
                            user_id,
                            days_remaining,
                            "🔔 **Premium Expiry Reminder**",
                            "Your premium subscription will expire in **30 days**.\n\n"
                            "Renew now to continue enjoying unlimited bypassing!"
                        )
                        notification_sent = True
                    
                    # 7 days before expiry
                    elif days_remaining == 7:
                        await self.send_expiry_notification(
                            user_id,
                            days_remaining,
                            "⚠️ **Premium Expiring Soon**",
                            "Your premium subscription will expire in **7 days**.\n\n"
                            "Don't miss out on unlimited access - renew today!"
                        )
                        notification_sent = True
                    
                    # 3 days before expiry
                    elif days_remaining == 3:
                        await self.send_expiry_notification(
                            user_id,
                            days_remaining,
                            "🚨 **Premium Expiring Very Soon!**",
                            "Your premium subscription will expire in just **3 days**!\n\n"
                            "Renew now to avoid losing your benefits."
                        )
                        notification_sent = True
                    
                    # 1 day before expiry
                    elif days_remaining == 1:
                        await self.send_expiry_notification(
                            user_id,
                            days_remaining,
                            "🔴 **Last Day of Premium!**",
                            "Your premium subscription expires **tomorrow**!\n\n"
                            "This is your last chance to renew without interruption."
                        )
                        notification_sent = True
                    
                    # Expiry day (if less than 24 hours but hasn't expired yet)
                    elif days_remaining == 0 and hours_remaining > 0:
                        await self.send_expiry_notification(
                            user_id,
                            0,
                            "⏰ **Premium Expires Today!**",
                            f"Your premium subscription expires in **{hours_remaining} hours**!\n\n"
                            "Renew immediately to keep your unlimited access."
                        )
                        notification_sent = True
                    
                    # Just expired (within last hour)
                    elif days_remaining < 0 and abs(days_remaining) == 0 and not user.get("expiry_notified"):
                        await self.send_expired_notification(user_id)
                        notification_sent = True
                        
                        # Mark as notified
                        await db.users.update_one(
                            {"user_id": user_id},
                            {"$set": {"expiry_notified": True}}
                        )
                    
                    # Update last notification date
                    if notification_sent:
                        await db.users.update_one(
                            {"user_id": user_id},
                            {"$set": {"last_notification_date": today}}
                        )
                
                except Exception as e:
                    logger.error(f"Error notifying user {user.get('user_id')}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error checking expiring subscriptions: {e}")
    
    async def send_expiry_notification(self, user_id: int, days_remaining: int, title: str, message: str):
        """Send expiry reminder notification"""
        try:
            keyboard = Keyboards.premium_keyboard()
            
            full_message = f"{title}\n\n{message}\n\n"
            
            if days_remaining > 0:
                full_message += f"⏰ **Time Remaining:** {days_remaining} day{'s' if days_remaining != 1 else ''}\n\n"
            
            full_message += "**Renew Premium:**\n"
            full_message += "• Use `/redeem <token>` if you have a token\n"
            full_message += "• Contact admin for purchase options\n\n"
            full_message += "Thank you for being a premium member! 💎"
            
            await self.client.send_message(
                user_id,
                full_message,
                reply_markup=keyboard
            )
            
            logger.info(f"Expiry notification sent to user {user_id} ({days_remaining} days)")
            
        except Exception as e:
            logger.error(f"Failed to send expiry notification to {user_id}: {e}")
    
    async def send_expired_notification(self, user_id: int):
        """Send notification when premium has expired"""
        try:
            message = (
                "😢 **Your Premium Has Expired**\n\n"
                "Your premium subscription has just expired.\n\n"
                "**What happens now:**\n"
                "• Daily limit: Back to free tier (10 links/day)\n"
                "• No priority queue\n"
                "• Standard bypass speed\n\n"
                "**Want to continue premium?**\n"
                "Renew now to regain all premium benefits!\n\n"
                "We hope to see you back soon! 💙"
            )
            
            keyboard = Keyboards.premium_keyboard()
            
            await self.client.send_message(
                user_id,
                message,
                reply_markup=keyboard
            )
            
            logger.info(f"Expiry notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send expired notification to {user_id}: {e}")
    
    async def check_limit_warnings(self):
        """Check and warn users approaching their daily limit"""
        try:
            # Get all free users
            users = await db.users.find({"is_premium": False}).to_list(length=None)
            
            today = datetime.utcnow().date().isoformat()
            
            for user in users:
                try:
                    user_id = user.get("user_id")
                    used_today = user.get("links_bypassed_today", 0)
                    daily_limit = user.get("daily_limit", Config.FREE_USER_LIMIT)
                    
                    # Skip if no limit or unlimited
                    if daily_limit <= 0:
                        continue
                    
                    # Calculate percentage used
                    percentage = (used_today / daily_limit) * 100
                    
                    # Check if already warned today
                    last_warned = user.get("last_limit_warning_date")
                    
                    if last_warned == today:
                        continue  # Already warned today
                    
                    warning_sent = False
                    
                    # 80% warning
                    if percentage >= 80 and percentage < 90:
                        remaining = daily_limit - used_today
                        await self.send_limit_warning(
                            user_id,
                            used_today,
                            daily_limit,
                            remaining,
                            "⚠️ **80% of Daily Limit Used**",
                            f"You've used **{used_today}/{daily_limit}** links today.\n"
                            f"Only **{remaining} links** remaining!"
                        )
                        warning_sent = True
                    
                    # 90% warning
                    elif percentage >= 90 and percentage < 100:
                        remaining = daily_limit - used_today
                        await self.send_limit_warning(
                            user_id,
                            used_today,
                            daily_limit,
                            remaining,
                            "🚨 **90% of Daily Limit Used!**",
                            f"You've used **{used_today}/{daily_limit}** links today.\n"
                            f"Only **{remaining} links** left!\n\n"
                            "Consider upgrading to premium for unlimited access."
                        )
                        warning_sent = True
                    
                    # 100% reached
                    elif percentage >= 100 and not user.get("limit_reached_notified"):
                        await self.send_limit_reached(user_id, daily_limit)
                        warning_sent = True
                        
                        # Mark as notified
                        await db.users.update_one(
                            {"user_id": user_id},
                            {"$set": {"limit_reached_notified": True}}
                        )
                    
                    # Update last warning date
                    if warning_sent:
                        await db.users.update_one(
                            {"user_id": user_id},
                            {"$set": {"last_limit_warning_date": today}}
                        )
                
                except Exception as e:
                    logger.error(f"Error warning user {user.get('user_id')}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error checking limit warnings: {e}")
    
    async def send_limit_warning(self, user_id: int, used: int, limit: int, remaining: int, title: str, message: str):
        """Send daily limit warning"""
        try:
            full_message = f"{title}\n\n{message}\n\n"
            full_message += "**Options:**\n"
            full_message += "• Wait for daily reset (midnight UTC)\n"
            full_message += "• Use a reset key if you have one\n"
            full_message += "• Upgrade to premium for unlimited access\n\n"
            full_message += "Use /premium to learn more!"
            
            keyboard = Keyboards.premium_keyboard()
            
            await self.client.send_message(
                user_id,
                full_message,
                reply_markup=keyboard
            )
            
            logger.info(f"Limit warning sent to user {user_id} ({used}/{limit})")
            
        except Exception as e:
            logger.error(f"Failed to send limit warning to {user_id}: {e}")
    
    async def send_limit_reached(self, user_id: int, limit: int):
        """Send notification when daily limit is reached"""
        try:
            message = (
                "🛑 **Daily Limit Reached**\n\n"
                f"You've used all **{limit} links** for today.\n\n"
                "**What now?**\n"
                "• Wait for reset (midnight UTC)\n"
                "• Use a reset key: `/reset <key>`\n"
                "• Upgrade to premium for unlimited access\n\n"
                "**Premium Benefits:**\n"
                "✨ Unlimited bypassing\n"
                "✨ Priority queue\n"
                "✨ Faster speeds\n\n"
                "Use /premium to upgrade!"
            )
            
            keyboard = Keyboards.premium_keyboard()
            
            await self.client.send_message(
                user_id,
                message,
                reply_markup=keyboard
            )
            
            logger.info(f"Limit reached notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send limit reached notification to {user_id}: {e}")
    
    async def send_welcome_premium(self, user_id: int, duration_days: int):
        """Send welcome message to new premium users"""
        try:
            message = (
                "🎉 **Welcome to Premium!**\n\n"
                "Congratulations! Your premium subscription is now active.\n\n"
                "**Your Premium Benefits:**\n"
                "✨ Unlimited link bypassing\n"
                "✨ Priority processing queue\n"
                "✨ Faster bypass speeds\n"
                "✨ No ads or delays\n"
                "✨ Early access to new features\n"
                "✨ Premium support\n\n"
                f"**Duration:** {duration_days} days\n\n"
                "Enjoy your premium experience! 💎"
            )
            
            await self.client.send_message(user_id, message)
            
            logger.info(f"Welcome premium message sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome premium to {user_id}: {e}")
    
    async def send_referral_reward(self, user_id: int, reward_amount: int):
        """Notify user about referral rewards"""
        try:
            message = (
                "🎁 **Referral Reward Earned!**\n\n"
                f"You earned **{reward_amount} bonus links** for your referral!\n\n"
                "Keep sharing your referral link to earn more rewards.\n\n"
                "Use /referral to get your link!"
            )
            
            await self.client.send_message(user_id, message)
            
            logger.info(f"Referral reward notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send referral reward to {user_id}: {e}")

# Global notification system instance (initialized in main.py)
notification_system = None

def init_notifications(client: Client):
    """Initialize notification system"""
    global notification_system
    notification_system = NotificationSystem(client)
    return notification_system
