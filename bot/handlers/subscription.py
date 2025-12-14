import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import Config
from database.mongodb import db
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import format_duration
from bot.middlewares.auth import check_subscription
from bot.handlers.notifications import notification_system

logger = logging.getLogger(__name__)

# Redeem Token Command
@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_token_command(client: Client, message: Message):
    """Handle token redemption"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text(
            "🎟️ **Redeem Premium Token**\n\n"
            "**Usage:** `/redeem <token>`\n\n"
            "**Example:** `/redeem abc123xyz456`\n\n"
            "You can get premium tokens from:\n"
            "• @YourPaymentBot\n"
            "• Bot administrator\n"
            "• Promotions and giveaways"
        )
        return
    
    token = args[1].strip()
    
    # Process token
    processing_msg = await message.reply_text("🔄 Validating token...")
    
    result = await db.use_token(token, message.from_user.id)
    
    if result["success"]:
        # Get token details for duration
        token_data = await db.get_token(token)
        duration_days = token_data.get("duration_days", 0) if token_data else 0
        
        await processing_msg.edit_text(
            f"✅ **Premium Activated!**\n\n"
            f"🎉 Congratulations! You now have premium access.\n\n"
            f"**Duration:** {format_duration(duration_days)}\n"
            f"**Benefits:**\n"
            f"✨ Unlimited link bypassing\n"
            f"✨ Priority processing\n"
            f"✨ Faster speeds\n"
            f"✨ Premium support\n\n"
            f"Thank you for upgrading! 💖",
            reply_markup=Keyboards.back_button()
        )
        
        # Send welcome notification
        if notification_system:
            await notification_system.send_welcome_premium(message.from_user.id, duration_days)
        
        # Log to channel
        if Config.LOG_CHANNEL:
            try:
                await client.send_message(
                    Config.LOG_CHANNEL,
                    f"🎫 **Premium Activated**\n\n"
                    f"**User:** {message.from_user.first_name} (`{message.from_user.id}`)\n"
                    f"**Duration:** {format_duration(duration_days)}\n"
                    f"**Token:** `{token[:10]}...`"
                )
            except:
                pass
    else:
        await processing_msg.edit_text(
            f"❌ **{result['message']}**\n\n"
            f"Please check your token and try again.\n\n"
            f"**Common Issues:**\n"
            f"• Token already used\n"
            f"• Token expired\n"
            f"• Invalid token format\n\n"
            f"Contact admin if you need help.",
            reply_markup=Keyboards.back_button()
        )

# Reset Limit Command
@Client.on_message(filters.command("reset") & filters.private)
async def reset_limit_command(client: Client, message: Message):
    """Handle reset key usage"""
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text(
            "🔑 **Reset Daily Limit**\n\n"
            "**Usage:** `/reset <key>`\n\n"
            "**Example:** `/reset xyz789abc123`\n\n"
            "Reset keys are provided by the bot admin.\n"
            "Each key can be used only once."
        )
        return
    
    reset_key = args[1].strip()
    
    # Process reset key
    processing_msg = await message.reply_text("🔄 Validating reset key...")
    
    result = await db.use_reset_key(reset_key, message.from_user.id)
    
    if result["success"]:
        user = await db.get_user(message.from_user.id)
        
        await processing_msg.edit_text(
            f"✅ **Limit Reset Successfully!**\n\n"
            f"Your daily limit has been reset.\n\n"
            f"**New Stats:**\n"
            f"• Daily Limit: {user.get('daily_limit', 0)} links\n"
            f"• Used Today: 0 links\n"
            f"• Remaining: {user.get('daily_limit', 0)} links\n\n"
            f"You can now bypass more links! 🎉",
            reply_markup=Keyboards.back_button()
        )
        
        # Log to channel
        if Config.LOG_CHANNEL:
            try:
                await client.send_message(
                    Config.LOG_CHANNEL,
                    f"🔑 **Limit Reset**\n\n"
                    f"**User:** {message.from_user.first_name} (`{message.from_user.id}`)\n"
                    f"**Key:** `{reset_key[:10]}...`"
                )
            except:
                pass
    else:
        await processing_msg.edit_text(
            f"❌ **{result['message']}**\n\n"
            f"Please check your reset key and try again.\n\n"
            f"Contact admin to get a valid reset key.",
            reply_markup=Keyboards.back_button()
        )

# Redeem Token Callback
@Client.on_callback_query(filters.regex("^redeem_token$"))
async def redeem_token_callback(client: Client, callback: CallbackQuery):
    """Handle redeem token callback"""
    await callback.message.edit_text(
        "🎟️ **Redeem Premium Token**\n\n"
        "To redeem your premium token, use:\n"
        "`/redeem YOUR_TOKEN`\n\n"
        "**Example:**\n"
        "`/redeem abc123xyz456`\n\n"
        "**Where to get tokens?**\n"
        "• Purchase from @YourPaymentBot\n"
        "• Receive from admin\n"
        "• Win in giveaways",
        reply_markup=Keyboards.back_button()
    )

# Check Subscription Callback (for force sub)
@Client.on_callback_query(filters.regex("^check_subscription$"))
async def check_subscription_callback(client: Client, callback: CallbackQuery):
    """Check if user has subscribed to required channels"""
    sub_status = await check_subscription(client, callback.from_user.id)
    
    if sub_status["subscribed"]:
        await callback.message.edit_text(
            "✅ **Subscription Verified!**\n\n"
            "Thank you for joining! You can now use the bot.\n\n"
            "Send /start to begin.",
            reply_markup=Keyboards.back_button()
        )
        await callback.answer("✅ Subscription verified!", show_alert=True)
    else:
        missing_text = ""
        for item_type, item_name in sub_status["missing"]:
            if item_type == "channel":
                missing_text += f"📢 {item_name}\n"
            elif item_type == "group":
                missing_text += f"👥 {item_name}\n"
        
        await callback.answer(
            f"⚠️ Please join all required channels/groups first!\n\n{missing_text}",
            show_alert=True
        )

# Premium Features Info
@Client.on_message(filters.command("premium") & filters.private)
async def premium_info_command(client: Client, message: Message):
    """Show premium information"""
    user = await db.get_user(message.from_user.id)
    
    if user and user.get("is_premium"):
        from datetime import datetime
        days_left = (user["subscription_end_date"] - datetime.utcnow()).days if user.get("subscription_end_date") else 0
        
        premium_info = f"""
👑 **Your Premium Status**

**Status:** Active ✅
**Expires in:** {days_left} days
**Daily Limit:** Unlimited
**Total Bypassed:** {user.get('total_links_bypassed', 0)} links

**Your Premium Benefits:**
✨ Unlimited link bypassing
✨ Priority processing queue
✨ Faster bypass speeds
✨ No ads or delays
✨ Premium support
✨ Early access to features

Thank you for being a premium member! 💖
"""
        
        await message.reply_text(premium_info, reply_markup=Keyboards.back_button())
    else:
        premium_text = """
👑 **Premium Membership**

Unlock unlimited power with premium!

**Premium Benefits:**
✨ Unlimited link bypassing
✨ Priority processing queue
✨ Faster bypass speed
✨ No ads or delays
✨ Premium support
✨ Early access to features

**Pricing:**
• 1 Month - $5
• 3 Months - $12
• 6 Months - $20
• 1 Year - $35

**How to Get Premium:**
1️⃣ Purchase from @YourPaymentBot
2️⃣ Receive premium token
3️⃣ Use /redeem <token>

Or click the button below!
"""
        
        await message.reply_text(premium_text, reply_markup=Keyboards.premium_keyboard())

# Subscription Status Command
@Client.on_message(filters.command("subscription") & filters.private)
async def subscription_status_command(client: Client, message: Message):
    """Show subscription status"""
    user = await db.get_user(message.from_user.id)
    
    if not user:
        await message.reply_text("❌ User not found!")
        return
    
    from datetime import datetime
    
    if user.get("is_premium"):
        days_left = (user["subscription_end_date"] - datetime.utcnow()).days if user.get("subscription_end_date") else 0
        expiry_date = user["subscription_end_date"].strftime("%Y-%m-%d") if user.get("subscription_end_date") else "N/A"
        
        status_text = f"""
📊 **Subscription Status**

**Plan:** 👑 Premium
**Status:** Active ✅
**Expires On:** {expiry_date}
**Days Remaining:** {days_left} days

**Daily Limit:** Unlimited
**Used Today:** {user.get('links_bypassed_today', 0)} links
**Total Bypassed:** {user.get('total_links_bypassed', 0)} links

Your premium benefits are active! 💖
"""
    else:
        status_text = f"""
📊 **Subscription Status**

**Plan:** 🆓 Free
**Status:** Active ✅

**Daily Limit:** {user.get('daily_limit', 0)} links
**Used Today:** {user.get('links_bypassed_today', 0)} links
**Remaining:** {user.get('daily_limit', 0) - user.get('links_bypassed_today', 0)} links
**Total Bypassed:** {user.get('total_links_bypassed', 0)} links

Upgrade to premium for unlimited access!
"""
    
    await message.reply_text(status_text, reply_markup=Keyboards.premium_keyboard() if not user.get("is_premium") else Keyboards.back_button())
