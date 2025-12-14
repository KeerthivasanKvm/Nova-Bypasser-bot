import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database.mongodb import db
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import parse_command_args, get_domain
from bot.middlewares.auth import protected_command, admin_only

logger = logging.getLogger(__name__)

# Referral System

@Client.on_message(filters.command("referral") & filters.private)
@protected_command
async def referral_command(client: Client, message: Message):
    """Show referral information"""
    if not Config.REFERRAL_ENABLED:
        await message.reply_text(
            "⚠️ **Referral System Disabled**\n\n"
            "The referral system is currently disabled by the admin."
        )
        return
    
    user = await db.get_user(message.from_user.id)
    stats = await db.get_referral_stats(message.from_user.id)
    
    referral_link = f"https://t.me/{(await client.get_me()).username}?start=ref_{message.from_user.id}"
    
    referral_text = f"""
🎁 **Referral Program**

**Your Referral Link:**
`{referral_link}`

**Your Statistics:**
👥 Total Referrals: {stats['total_referrals']}
✅ Claimed Bonuses: {stats['claimed_bonuses']}
⏳ Unclaimed Bonuses: {stats['unclaimed_bonuses']}

**Referral Rewards:**
• {Config.REFERRAL_BONUS_LINKS} extra links for {Config.REFERRAL_BONUS_DURATION_DAYS} day(s) per referral
• Get {Config.MIN_REFERRALS_FOR_PREMIUM} referrals = 1 day Premium FREE!

**How it works:**
1. Share your referral link
2. When someone joins using your link
3. Both of you get bonus links!

**Current Bonus:** {user.get('daily_limit', Config.FREE_USER_LIMIT)} links/day

Share your link and earn rewards! 🚀
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join this awesome link bypasser bot!")],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])
    
    await message.reply_text(referral_text, reply_markup=keyboard)

# Feedback System

@Client.on_message(filters.command("report") & filters.private)
@protected_command
async def report_command(client: Client, message: Message):
    """Report a broken or unsupported link - Sent directly to admin PM"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply_text(
            "📝 **Report a Link**\n\n"
            "**Usage:** `/report <link> [description]`\n\n"
            "**Examples:**\n"
            "• `/report https://example.com/link Link doesn't work`\n"
            "• `/report https://site.com/file Error: timeout`\n\n"
            "This helps us improve the bot!"
        )
        return
    
    content = args[1]
    parts = content.split(maxsplit=1)
    link = parts[0]
    description = parts[1] if len(parts) > 1 else "No description provided"
    
    # Send directly to all admins
    report_sent = False
    for admin_id in Config.ADMIN_IDS:
        try:
            # Create keyboard for quick actions
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Mark Fixed", callback_data=f"report_fixed_{message.from_user.id}"),
                    InlineKeyboardButton("❌ Invalid", callback_data=f"report_invalid_{message.from_user.id}")
                ],
                [
                    InlineKeyboardButton("💬 Reply to User", callback_data=f"report_reply_{message.from_user.id}")
                ]
            ])
            
            await client.send_message(
                admin_id,
                f"🚨 **NEW LINK REPORT**\n\n"
                f"👤 **User:** {message.from_user.first_name}\n"
                f"🆔 **User ID:** `{message.from_user.id}`\n"
                f"👤 **Username:** @{message.from_user.username or 'None'}\n\n"
                f"🔗 **Link:** `{link}`\n"
                f"📝 **Description:** {description}\n\n"
                f"⏰ **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                f"Click buttons below to respond:",
                reply_markup=keyboard
            )
            report_sent = True
        except Exception as e:
            logger.error(f"Failed to send report to admin {admin_id}: {e}")
    
    if report_sent:
        await message.reply_text(
            "✅ **Report Submitted Successfully!**\n\n"
            f"**Link:** `{link}`\n\n"
            "Your report has been sent directly to the admin team.\n"
            "Thank you for helping us improve! 💙"
        )
    else:
        await message.reply_text(
            "❌ **Failed to submit report**\n\n"
            "Please try again later or contact support directly."
        )

@Client.on_message(filters.command("feedback") & filters.private)
@protected_command
async def feedback_command(client: Client, message: Message):
    """Send general feedback or suggestion - Sent directly to admin PM"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply_text(
            "💭 **Send Feedback**\n\n"
            "**Usage:** `/feedback <your message>`\n\n"
            "**Examples:**\n"
            "• `/feedback Great bot, works perfectly!`\n"
            "• `/feedback Can you add support for XYZ site?`\n"
            "• `/feedback Found a bug in the premium feature`\n\n"
            "We value your feedback!"
        )
        return
    
    content = args[1]
    
    # Send directly to all admins
    feedback_sent = False
    for admin_id in Config.ADMIN_IDS:
        try:
            # Get user info
            user = await db.get_user(message.from_user.id)
            user_status = "👑 Premium" if user and user.get("is_premium") else "🆓 Free"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💬 Reply to User", callback_data=f"feedback_reply_{message.from_user.id}"),
                    InlineKeyboardButton("❤️ Thank User", callback_data=f"feedback_thank_{message.from_user.id}")
                ]
            ])
            
            await client.send_message(
                admin_id,
                f"💭 **NEW FEEDBACK**\n\n"
                f"👤 **User:** {message.from_user.first_name}\n"
                f"🆔 **User ID:** `{message.from_user.id}`\n"
                f"👤 **Username:** @{message.from_user.username or 'None'}\n"
                f"📊 **Status:** {user_status}\n\n"
                f"💬 **Message:**\n{content}\n\n"
                f"⏰ **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                reply_markup=keyboard
            )
            feedback_sent = True
        except Exception as e:
            logger.error(f"Failed to send feedback to admin {admin_id}: {e}")
    
    if feedback_sent:
        await message.reply_text(
            "✅ **Feedback Submitted Successfully!**\n\n"
            "Thank you for your feedback! We appreciate it. 💙\n\n"
            "The admin team will review it shortly."
        )
    else:
        await message.reply_text(
            "❌ **Failed to submit feedback**\n\n"
            "Please try again later or contact support directly."
        )

# Site Request System

@Client.on_message(filters.command("request") & filters.private)
@protected_command
async def request_site_command(client: Client, message: Message):
    """Request support for a new site - Sent directly to admin PM"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply_text(
            "🌐 **Request Site Support**\n\n"
            "**Usage:** `/request <website_url> [description]`\n\n"
            "**Examples:**\n"
            "• `/request https://newsite.com`\n"
            "• `/request example.com Popular file sharing site`\n\n"
            "Request support for new websites!"
        )
        return
    
    content = args[1]
    parts = content.split(maxsplit=1)
    url = parts[0]
    description = parts[1] if len(parts) > 1 else None
    
    # Extract domain
    domain = get_domain(url) or url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    
    # Send directly to all admins
    request_sent = False
    for admin_id in Config.ADMIN_IDS:
        try:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"sitereq_approve_{domain}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"sitereq_reject_{domain}")
                ],
                [
                    InlineKeyboardButton("💬 Ask for More Info", callback_data=f"sitereq_info_{message.from_user.id}")
                ]
            ])
            
            await client.send_message(
                admin_id,
                f"🌐 **NEW SITE REQUEST**\n\n"
                f"👤 **User:** {message.from_user.first_name}\n"
                f"🆔 **User ID:** `{message.from_user.id}`\n"
                f"👤 **Username:** @{message.from_user.username or 'None'}\n\n"
                f"🌐 **Domain:** `{domain}`\n"
                f"🔗 **URL:** `{url}`\n"
                f"📝 **Description:** {description or 'None'}\n\n"
                f"⏰ **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                reply_markup=keyboard
            )
            request_sent = True
        except Exception as e:
            logger.error(f"Failed to send site request to admin {admin_id}: {e}")
    
    if request_sent:
        await message.reply_text(
            "✅ **Site Request Submitted!**\n\n"
            f"**Site:** `{domain}`\n\n"
            "We'll review your request and consider adding support.\n"
            "Thank you for the suggestion! 🎉"
        )
    else:
        await message.reply_text(
            "❌ **Failed to submit request**\n\n"
            "Please try again later."
        )

@Client.on_message(filters.command("requests") & filters.private)
@protected_command
async def view_requests_command(client: Client, message: Message):
    """View site request information"""
    await message.reply_text(
        "🌐 **Site Request System**\n\n"
        "To request support for a new website, use:\n"
        "`/request <website_url> [description]`\n\n"
        "**Example:**\n"
        "`/request https://newsite.com Popular file host`\n\n"
        "Your request will be sent directly to our admin team for review.\n\n"
        "We prioritize requests based on:\n"
        "• Number of requests for the same site\n"
        "• Site popularity\n"
        "• Technical feasibility\n"
        "• Community demand"
    )

# Admin Commands for Feedback Management

# NOTE: Feedback is now sent directly to admin PM, no database storage
# Admin can respond directly using Telegram's reply feature

# Toggle Referral System (Admin)

@Client.on_message(filters.command("toggle_referral") & filters.private)
@admin_only
async def toggle_referral_command(client: Client, message: Message):
    """Toggle referral system on/off"""
    Config.REFERRAL_ENABLED = not Config.REFERRAL_ENABLED
    
    status = "Enabled" if Config.REFERRAL_ENABLED else "Disabled"
    emoji = "✅" if Config.REFERRAL_ENABLED else "❌"
    
    await message.reply_text(
        f"{emoji} **Referral System {status}**\n\n"
        f"The referral system is now **{status.lower()}**."
    )
    
    # Notify log channel
    if Config.LOG_CHANNEL:
        try:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"{emoji} **Referral System {status}**\n\n"
                f"Changed by: {message.from_user.first_name} (`{message.from_user.id}`)"
            )
        except:
            pass

# Admin Callback Handlers for Reports/Feedback

@Client.on_callback_query(filters.regex("^report_"))
async def handle_report_callbacks(client: Client, callback: CallbackQuery):
    """Handle admin responses to reports"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⚠️ Admin only!", show_alert=True)
        return
    
    data = callback.data
    action = data.split("_")[1]
    user_id = int(data.split("_")[2])
    
    if action == "fixed":
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ **Status:** Marked as Fixed",
            reply_markup=None
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "✅ **Your Report Was Resolved!**\n\n"
                "The issue you reported has been fixed.\n"
                "Thank you for helping us improve! 💙"
            )
        except:
            pass
        
        await callback.answer("✅ Marked as fixed and user notified!")
    
    elif action == "invalid":
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ **Status:** Marked as Invalid",
            reply_markup=None
        )
        await callback.answer("❌ Marked as invalid")
    
    elif action == "reply":
        await callback.answer("💬 Reply to this message to send a message to the user", show_alert=True)
        # Store user_id for reply handling
        await callback.message.reply_text(
            f"💬 **Reply Mode Active**\n\n"
            f"Reply to this message to send your response to the user.\n"
            f"**User ID:** `{user_id}`"
        )

@Client.on_callback_query(filters.regex("^feedback_"))
async def handle_feedback_callbacks(client: Client, callback: CallbackQuery):
    """Handle admin responses to feedback"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⚠️ Admin only!", show_alert=True)
        return
    
    data = callback.data
    action = data.split("_")[1]
    user_id = int(data.split("_")[2])
    
    if action == "reply":
        await callback.answer("💬 Reply to this message to respond to the user", show_alert=True)
        await callback.message.reply_text(
            f"💬 **Reply Mode Active**\n\n"
            f"Reply to this message to send your response to the user.\n"
            f"**User ID:** `{user_id}`"
        )
    
    elif action == "thank":
        await callback.message.edit_text(
            callback.message.text + "\n\n❤️ **Status:** User Thanked",
            reply_markup=None
        )
        
        # Send thank you message
        try:
            await client.send_message(
                user_id,
                "💙 **Thank You for Your Feedback!**\n\n"
                "We really appreciate you taking the time to share your thoughts.\n"
                "Your feedback helps us make the bot better for everyone!\n\n"
                "Keep using the bot and stay awesome! 🚀"
            )
        except:
            pass
        
        await callback.answer("❤️ Thank you message sent!")

@Client.on_callback_query(filters.regex("^sitereq_"))
async def handle_sitereq_callbacks(client: Client, callback: CallbackQuery):
    """Handle admin responses to site requests"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⚠️ Admin only!", show_alert=True)
        return
    
    data = callback.data
    action = data.split("_")[1]
    
    if action == "approve":
        domain = data.split("_")[2]
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ **Status:** Approved for Development",
            reply_markup=None
        )
        await callback.answer("✅ Request approved!")
    
    elif action == "reject":
        domain = data.split("_")[2]
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ **Status:** Rejected",
            reply_markup=None
        )
        await callback.answer("❌ Request rejected")
    
    elif action == "info":
        user_id = int(data.split("_")[2])
        await callback.answer("💬 Reply to this message to ask for more information", show_alert=True)
        await callback.message.reply_text(
            f"💬 **Reply Mode Active**\n\n"
            f"Reply to this message to ask the user for more details.\n"
            f"**User ID:** `{user_id}`"
        )

# Callback Handlers

@Client.on_callback_query(filters.regex("^referral_info$"))
async def referral_info_callback(client: Client, callback: CallbackQuery):
    """Handle referral info callback"""
    if not Config.REFERRAL_ENABLED:
        await callback.answer("Referral system is currently disabled!", show_alert=True)
        return
    
    user = await db.get_user(callback.from_user.id)
    stats = await db.get_referral_stats(callback.from_user.id)
    
    referral_link = f"https://t.me/{(await client.get_me()).username}?start=ref_{callback.from_user.id}"
    
    referral_text = f"""
🎁 **Referral Program**

**Your Statistics:**
👥 Total Referrals: {stats['total_referrals']}
✅ Bonuses Claimed: {stats['claimed_bonuses']}

**Rewards:**
• {Config.REFERRAL_BONUS_LINKS} extra links per referral
• {Config.MIN_REFERRALS_FOR_PREMIUM} refs = 1 day Premium!

**Your Link:**
`{referral_link}`
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share", url=f"https://t.me/share/url?url={referral_link}")],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])
    
    await callback.message.edit_text(referral_text, reply_markup=keyboard)
