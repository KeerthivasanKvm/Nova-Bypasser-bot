import logging
from functools import wraps
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from config import Config
from database.mongodb import db
from bot.utils.helpers import is_group_chat, is_private_chat

logger = logging.getLogger(__name__)

async def check_user(client: Client, message: Message):
    """Check and create user if not exists"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        # Create new user
        user = await db.create_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        logger.info(f"New user created: {user_id}")
        
        # Send welcome notification to log channel
        if Config.LOG_CHANNEL:
            try:
                await client.send_message(
                    Config.LOG_CHANNEL,
                    f"🆕 **New User**\n\n"
                    f"**ID:** `{user_id}`\n"
                    f"**Name:** {message.from_user.first_name}\n"
                    f"**Username:** @{message.from_user.username or 'None'}"
                )
            except:
                pass
    else:
        # Check if premium expired
        await db.check_premium_expired(user_id)
    
    return user

def admin_only(func):
    """Decorator to restrict command to admins only"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.from_user.id not in Config.ADMIN_IDS:
            await message.reply_text("⚠️ This command is only for admins!")
            return
        return await func(client, message)
    return wrapper

def check_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in Config.ADMIN_IDS

async def check_subscription(client: Client, user_id: int) -> dict:
    """Check if user has subscribed to required channels/groups"""
    result = {"subscribed": True, "missing": []}
    
    # Check channel subscription
    if Config.FORCE_SUB_CHANNEL:
        try:
            channel_username = Config.FORCE_SUB_CHANNEL.replace("@", "")
            member = await client.get_chat_member(channel_username, user_id)
            if member.status in ["kicked", "left"]:
                result["subscribed"] = False
                result["missing"].append(("channel", Config.FORCE_SUB_CHANNEL))
        except Exception as e:
            logger.error(f"Error checking channel subscription: {e}")
            result["subscribed"] = False
            result["missing"].append(("channel", Config.FORCE_SUB_CHANNEL))
    
    # Check group subscription
    if Config.FORCE_SUB_GROUP:
        try:
            group_username = Config.FORCE_SUB_GROUP.replace("@", "")
            member = await client.get_chat_member(group_username, user_id)
            if member.status in ["kicked", "left"]:
                result["subscribed"] = False
                result["missing"].append(("group", Config.FORCE_SUB_GROUP))
        except Exception as e:
            logger.error(f"Error checking group subscription: {e}")
            result["subscribed"] = False
            result["missing"].append(("group", Config.FORCE_SUB_GROUP))
    
    return result

def subscription_required(func):
    """Decorator to check subscription before executing command"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        sub_status = await check_subscription(client, message.from_user.id)
        
        if not sub_status["subscribed"]:
            from bot.utils.keyboards import Keyboards
            
            # Build subscription message
            text = "⚠️ **Subscription Required**\n\n"
            text += "Please join the following to use this bot:\n\n"
            
            channel_url = None
            group_url = None
            
            for item_type, item_name in sub_status["missing"]:
                if item_type == "channel":
                    text += f"📢 Channel: {item_name}\n"
                    channel_url = f"https://t.me/{item_name.replace('@', '')}"
                elif item_type == "group":
                    text += f"👥 Group: {item_name}\n"
                    group_url = f"https://t.me/{item_name.replace('@', '')}"
            
            await message.reply_text(
                text,
                reply_markup=Keyboards.force_sub_keyboard(channel_url, group_url)
            )
            return
        
        return await func(client, message)
    return wrapper

async def check_group_permission(client: Client, chat_id: int) -> bool:
    """Check if bot has permission to work in this group"""
    # If groups only mode is disabled, allow all
    if not Config.WORK_IN_GROUPS_ONLY:
        return True
    
    # Check if group is in allowed list
    is_allowed = await db.is_group_allowed(chat_id)
    return is_allowed

def group_permission_required(func):
    """Decorator to check group permission"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        # Skip check for private chats
        if is_private_chat(message.chat.type):
            # If bot should work only in groups, block private chats
            if Config.WORK_IN_GROUPS_ONLY:
                await message.reply_text(
                    "⚠️ **Bot Works Only in Groups**\n\n"
                    "This bot is configured to work only in authorized groups.\n"
                    "Please contact the admin to add your group."
                )
                return
            # Otherwise allow private chats
            return await func(client, message)
        
        # For group chats, check permission
        if is_group_chat(message.chat.type):
            has_permission = await check_group_permission(client, message.chat.id)
            
            if not has_permission:
                await message.reply_text(
                    "⚠️ **Unauthorized Group**\n\n"
                    "This bot is not authorized to work in this group.\n"
                    "Please contact the admin to request access."
                )
                return
        
        return await func(client, message)
    return wrapper

async def check_rate_limit(user_id: int) -> dict:
    """Check if user has exceeded rate limit"""
    user = await db.get_user(user_id)
    
    if not user:
        return {"allowed": False, "message": "User not found"}
    
    # Premium users with unlimited limit
    if user.get("is_premium") and user.get("daily_limit") == -1:
        return {"allowed": True, "remaining": "Unlimited"}
    
    # Check daily limit
    used = user.get("links_bypassed_today", 0)
    limit = user.get("daily_limit", Config.FREE_USER_LIMIT)
    
    if used >= limit:
        return {
            "allowed": False,
            "message": f"Daily limit reached ({limit} links)",
            "used": used,
            "limit": limit
        }
    
    return {
        "allowed": True,
        "remaining": limit - used,
        "used": used,
        "limit": limit
    }

def rate_limit_required(func):
    """Decorator to check rate limit before executing"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        rate_check = await check_rate_limit(message.from_user.id)
        
        if not rate_check["allowed"]:
            text = f"⚠️ **{rate_check['message']}**\n\n"
            text += "Upgrade to premium for unlimited bypassing!\n"
            text += "Or use a reset key to reset your limit.\n\n"
            text += "Contact admin for more info."
            
            await message.reply_text(text)
            return
        
        return await func(client, message)
    return wrapper

async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    user = await db.get_user(user_id)
    return user.get("is_banned", False) if user else False

def ban_check(func):
    """Decorator to check if user is banned"""
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if await is_user_banned(message.from_user.id):
            await message.reply_text(
                "🚫 **You are banned from using this bot**\n\n"
                "Contact admin if you think this is a mistake."
            )
            return
        return await func(client, message)
    return wrapper

# Combined decorator for all checks
def protected_command(func):
    """Combined protection decorator"""
    @wraps(func)
    @ban_check
    @subscription_required
    @group_permission_required
    async def wrapper(client: Client, message: Message):
        await check_user(client, message)
        return await func(client, message)
    return wrapper
