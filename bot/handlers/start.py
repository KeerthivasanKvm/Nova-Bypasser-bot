import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import Config
from database.mongodb import db
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import format_user_stats, get_user_mention
from bot.middlewares.auth import protected_command, check_user
from bot.handlers.notifications import notification_system

logger = logging.getLogger(__name__)

# Start Command
@Client.on_message(filters.command("start") & filters.private)
@protected_command
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user = await db.get_user(message.from_user.id)
    
    # Check for referral code
    if len(message.text.split()) > 1:
        arg = message.text.split()[1]
        if arg.startswith("ref_") and Config.REFERRAL_ENABLED:
            try:
                referrer_id = int(arg.replace("ref_", ""))
                
                # Check if user hasn't been referred before
                if not await db.has_been_referred(message.from_user.id) and referrer_id != message.from_user.id:
                    # Create referral
                    success = await db.create_referral(referrer_id, message.from_user.id)
                    
                    if success:
                        # Give bonus to both users
                        await db.update_user(
                            message.from_user.id,
                            {"$inc": {"daily_limit": Config.REFERRAL_BONUS_LINKS}}
                        )
                        await db.update_user(
                            referrer_id,
                            {"$inc": {"daily_limit": Config.REFERRAL_BONUS_LINKS, "total_referrals": 1}}
                        )
                        
                        # Notify referrer
                        try:
                            await client.send_message(
                                referrer_id,
                                f"🎉 **New Referral!**\n\n"
                                f"Someone joined using your referral link!\n"
                                f"You earned {Config.REFERRAL_BONUS_LINKS} extra links!\n\n"
                                f"Total referrals: {await db.get_referral_count(referrer_id)}"
                            )
                            
                            # Send referral reward notification
                            if notification_system:
                                await notification_system.send_referral_reward(
                                    referrer_id,
                                    Config.REFERRAL_BONUS_LINKS
                                )
                        except:
                            pass
                        
                        # Welcome message with bonus
                        welcome_text = f"""
👋 **Welcome {message.from_user.first_name}!**

🎁 You joined via referral link!
You received {Config.REFERRAL_BONUS_LINKS} bonus links!

I'm a powerful link bypasser bot that can:
✅ Bypass ad links and shorteners
✅ Generate direct download links
✅ Jump paywalls
✅ Cloudflare protection bypass

{'👑 You are a Premium user!' if user.get('is_premium') else f'🆓 You are using Free plan ({user.get("daily_limit", Config.FREE_USER_LIMIT)} links/day)'}

**Quick Start:**
Just send me any link and I'll bypass it for you!
"""
                        await message.reply_text(
                            welcome_text,
                            reply_markup=Keyboards.start_keyboard(user.get("is_premium", False))
                        )
                        return
            except:
                pass
    
    welcome_text = f"""
👋 **Welcome {message.from_user.first_name}!**

I'm a powerful link bypasser bot that can:
✅ Bypass ad links and shorteners
✅ Generate direct download links
✅ Jump paywalls
✅ Cloudflare protection bypass

{'👑 You are a Premium user!' if user.get('is_premium') else '🆓 You are using Free plan'}

**Quick Start:**
Just send me any link and I'll bypass it for you!

**Free Users:** {Config.FREE_USER_LIMIT} links per day
**Premium Users:** Unlimited bypassing
"""
    
    await message.reply_text(
        welcome_text,
        reply_markup=Keyboards.start_keyboard(user.get("is_premium", False))
    )

# Help Command
@Client.on_message(filters.command("help"))
@protected_command
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    help_text = """
📖 **Help - How to Use**

**Basic Usage:**
1. Send me any supported link
2. Or use: `/bypass <link>` or `/b <link>`
3. Wait for processing
4. Get your bypassed link!

**Commands:**
/start - Start the bot
/help - Show this help
/bypass or /b - Bypass a link
/stats - Your statistics
/referral - Referral program
/redeem - Redeem premium token
/reset - Use reset key

**Feedback & Support:**
/report - Report broken link
/feedback - Send feedback
/request - Request new site support

**Supported Sites:**
• GDToT, GDFlix
• SharerPW, FileCrypt
• Drivefire, Hubdrive, Katdrive
• Uptobox, Terabox
• LinkVertise, ShortLinks
• And many more...

**Premium Features:**
👑 Unlimited bypassing
👑 Priority processing
👑 Faster bypass speed
👑 Early access to new features

**Referral Program:**
🎁 Invite friends and earn rewards!
Use /referral to get your link

**Need Help?**
Contact: @YourSupportUsername
"""
    
    await message.reply_text(help_text, reply_markup=Keyboards.help_keyboard())

# Stats Command
@Client.on_message(filters.command("stats"))
@protected_command
async def stats_command(client: Client, message: Message):
    """Handle /stats command"""
    user = await db.get_user(message.from_user.id)
    
    if not user:
        await message.reply_text("❌ User not found!")
        return
    
    stats_text = format_user_stats(user)
    await message.reply_text(stats_text, reply_markup=Keyboards.back_button())

# Callback Query Handler for Start Menu
@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client: Client, callback: CallbackQuery):
    """Handle start callback"""
    await check_user(client, callback.message)
    user = await db.get_user(callback.from_user.id)
    
    welcome_text = f"""
👋 **Welcome back {callback.from_user.first_name}!**

I'm a powerful link bypasser bot that can:
✅ Bypass ad links and shorteners
✅ Generate direct download links
✅ Jump paywalls
✅ Cloudflare protection bypass

{'👑 You are a Premium user!' if user.get('is_premium') else '🆓 You are using Free plan'}

**Quick Start:**
Just send me any link and I'll bypass it for you!
"""
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=Keyboards.start_keyboard(user.get("is_premium", False))
    )

# Help Callback
@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Handle help callback"""
    help_text = """
📖 **Help - How to Use**

**Basic Usage:**
1. Send me any supported link
2. Wait for processing
3. Get your bypassed link!

**Supported Sites:**
• GDToT, GDFlix
• SharerPW, FileCrypt
• Drivefire, Hubdrive, Katdrive
• Uptobox, Terabox
• LinkVertise, ShortLinks
• And many more...

**Commands:**
/start - Start the bot
/help - Show this help
/stats - Your statistics
/redeem - Redeem premium token
/reset - Use reset key

**Premium Features:**
👑 Unlimited bypassing
👑 Priority processing
👑 Faster bypass speed
👑 Early access to new features
"""
    
    await callback.message.edit_text(help_text, reply_markup=Keyboards.help_keyboard())

# My Stats Callback
@Client.on_callback_query(filters.regex("^my_stats$"))
async def stats_callback(client: Client, callback: CallbackQuery):
    """Handle stats callback"""
    user = await db.get_user(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ User not found!", show_alert=True)
        return
    
    stats_text = format_user_stats(user)
    await callback.message.edit_text(stats_text, reply_markup=Keyboards.back_button())

# About Callback
@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, callback: CallbackQuery):
    """Handle about callback"""
    about_text = """
ℹ️ **About Link Bypasser Bot**

**Version:** 2.0.0
**Developer:** @YourUsername

**Features:**
✅ Multi-site link bypassing
✅ Direct link generation
✅ Paywall bypass
✅ Cloudflare protection
✅ MongoDB caching
✅ Premium & Free tiers
✅ Group management
✅ Admin controls

**Technology:**
• Python 3.11
• Pyrogram
• MongoDB
• Flask
• Cloudscraper

**Support:**
Contact @YourSupportUsername

**Donate:**
Support development: @YourPaymentBot
"""
    
    await callback.message.edit_text(about_text, reply_markup=Keyboards.back_button())

# Get Premium Callback
@Client.on_callback_query(filters.regex("^get_premium$"))
async def get_premium_callback(client: Client, callback: CallbackQuery):
    """Handle get premium callback"""
    premium_text = """
👑 **Premium Membership**

**Premium Benefits:**
✨ Unlimited link bypassing
✨ Priority processing queue
✨ Faster bypass speed
✨ No ads or delays
✨ Early access to features
✨ Premium support

**Pricing:**
• 1 Month - $5
• 3 Months - $12
• 6 Months - $20
• 1 Year - $35

**How to Get Premium:**
1️⃣ Purchase from @YourPaymentBot
2️⃣ Receive premium token
3️⃣ Use /redeem command with token

Or use the button below to redeem a token!
"""
    
    await callback.message.edit_text(premium_text, reply_markup=Keyboards.premium_keyboard())

# Premium Info Callback
@Client.on_callback_query(filters.regex("^premium_info$"))
async def premium_info_callback(client: Client, callback: CallbackQuery):
    """Handle premium info callback"""
    user = await db.get_user(callback.from_user.id)
    
    if not user or not user.get("is_premium"):
        await callback.answer("You are not a premium user!", show_alert=True)
        return
    
    from datetime import datetime
    days_left = (user["subscription_end_date"] - datetime.utcnow()).days if user.get("subscription_end_date") else 0
    
    premium_info = f"""
👑 **Your Premium Status**

**Status:** Active ✅
**Expires in:** {days_left} days
**Daily Limit:** Unlimited
**Total Bypassed:** {user.get('total_links_bypassed', 0)} links

**Premium Benefits:**
✨ Unlimited link bypassing
✨ Priority processing
✨ Faster speeds
✨ Premium support

Thank you for being a premium member! 💖
"""
    
    await callback.message.edit_text(premium_info, reply_markup=Keyboards.back_button())

# Close Callback
@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, callback: CallbackQuery):
    """Handle close callback"""
    await callback.message.delete()

# Cancel Callback
@Client.on_callback_query(filters.regex("^cancel$"))
async def cancel_callback(client: Client, callback: CallbackQuery):
    """Handle cancel callback"""
    await callback.message.edit_text(
        "❌ Operation cancelled!",
        reply_markup=Keyboards.back_button()
)
