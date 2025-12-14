import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from config import Config
from database.mongodb import db
from bot.utils.keyboards import Keyboards
from bot.utils.helpers import (
    parse_duration, format_duration, format_bot_stats,
    parse_command_args, get_domain
)
from bot.middlewares.auth import admin_only

logger = logging.getLogger(__name__)

# Admin Panel
@Client.on_message(filters.command("admin") & filters.private)
@admin_only
async def admin_panel(client: Client, message: Message):
    """Show admin panel"""
    admin_text = """
👨‍💼 **Admin Panel**

Welcome to the admin control panel.
Select an option below to manage the bot.

**Available Actions:**
• Generate premium tokens
• Generate reset keys
• Manage allowed groups
• Manage restricted sites
• View statistics
• Broadcast messages
• Configure settings
"""
    
    await message.reply_text(admin_text, reply_markup=Keyboards.admin_keyboard())

# Generate Token Command
@Client.on_message(filters.command("generate_token") & filters.private)
@admin_only
async def generate_token_command(client: Client, message: Message):
    """Generate premium access token"""
    args = parse_command_args(message.text)
    
    if not args:
        await message.reply_text(
            "**Usage:** `/generate_token <duration>`\n\n"
            "**Examples:**\n"
            "• `/generate_token 1d` - 1 day\n"
            "• `/generate_token 7d` - 7 days\n"
            "• `/generate_token 1m` - 1 month\n"
            "• `/generate_token 1h` - 1 hour"
        )
        return
    
    try:
        duration_days = parse_duration(args[0])
        token = await db.create_token(duration_days, message.from_user.id)
        
        token_text = f"""
🎫 **Premium Token Generated**

**Token:** `{token}`
**Duration:** {format_duration(duration_days)}
**Valid Until:** {duration_days} days from activation

**Share this token with the user to activate premium.**
Token can be used only once.

Use /redeem command to activate.
"""
        
        await message.reply_text(token_text)
        
        # Log to channel
        if Config.LOG_CHANNEL:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"🎫 **Token Generated**\n\n"
                f"**By:** {message.from_user.first_name} (`{message.from_user.id}`)\n"
                f"**Duration:** {format_duration(duration_days)}"
            )
        
    except ValueError as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Generate Reset Key Command
@Client.on_message(filters.command("generate_reset") & filters.private)
@admin_only
async def generate_reset_command(client: Client, message: Message):
    """Generate reset key"""
    reset_key = await db.create_reset_key(message.from_user.id)
    
    reset_text = f"""
🔑 **Reset Key Generated**

**Key:** `{reset_key}`

**Share this key with free users to reset their daily limit.**
Key can be used only once.

Use /reset command to use this key.
"""
    
    await message.reply_text(reset_text)
    
    # Log to channel
    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"🔑 **Reset Key Generated**\n\n"
            f"**By:** {message.from_user.first_name} (`{message.from_user.id}`)"
        )

# Add Group Command
@Client.on_message(filters.command("add_group"))
@admin_only
async def add_group_command(client: Client, message: Message):
    """Add group to allowed list"""
    # This should be used in the group to add
    if message.chat.type == "private":
        await message.reply_text(
            "⚠️ Use this command in the group you want to add!"
        )
        return
    
    await db.add_allowed_group(
        message.chat.id,
        message.chat.title,
        message.from_user.id
    )
    
    await message.reply_text(
        f"✅ **Group Added**\n\n"
        f"**Group:** {message.chat.title}\n"
        f"**ID:** `{message.chat.id}`\n\n"
        f"Bot can now work in this group!"
    )
    
    # Log to channel
    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"👥 **Group Added**\n\n"
            f"**Group:** {message.chat.title}\n"
            f"**ID:** `{message.chat.id}`\n"
            f"**By:** {message.from_user.first_name} (`{message.from_user.id}`)"
        )

# Remove Group Command
@Client.on_message(filters.command("remove_group"))
@admin_only
async def remove_group_command(client: Client, message: Message):
    """Remove group from allowed list"""
    args = parse_command_args(message.text)
    
    if not args:
        await message.reply_text(
            "**Usage:** `/remove_group <group_id>`\n\n"
            "**Example:** `/remove_group -1001234567890`"
        )
        return
    
    try:
        group_id = int(args[0])
        result = await db.remove_allowed_group(group_id)
        
        if result.deleted_count > 0:
            await message.reply_text(f"✅ Group removed successfully!")
        else:
            await message.reply_text(f"❌ Group not found in allowed list!")
            
    except ValueError:
        await message.reply_text("❌ Invalid group ID!")

# Restrict Site Command
@Client.on_message(filters.command(["restrict_site", "add_site"]))
@admin_only
async def restrict_site_command(client: Client, message: Message):
    """Add site to restricted list"""
    args = parse_command_args(message.text)
    
    if not args:
        await message.reply_text(
            "**Usage:** `/restrict_site <domain>`\n\n"
            "**Examples:**\n"
            "• `/restrict_site example.com`\n"
            "• `/restrict_site spam-site.net`"
        )
        return
    
    domain = args[0].lower().replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
    
    await db.add_restricted_site(domain, message.from_user.id)
    
    await message.reply_text(
        f"✅ **Site Restricted**\n\n"
        f"**Domain:** `{domain}`\n\n"
        f"Links from this site will be blocked!"
    )
    
    # Log to channel
    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"🚫 **Site Restricted**\n\n"
            f"**Domain:** `{domain}`\n"
            f"**By:** {message.from_user.first_name} (`{message.from_user.id}`)"
        )

# Remove Restricted Site Command
@Client.on_message(filters.command("remove_site"))
@admin_only
async def remove_site_command(client: Client, message: Message):
    """Remove site from restricted list"""
    args = parse_command_args(message.text)
    
    if not args:
        await message.reply_text(
            "**Usage:** `/remove_site <domain>`\n\n"
            "**Example:** `/remove_site example.com`"
        )
        return
    
    domain = args[0].lower()
    result = await db.remove_restricted_site(domain)
    
    if result.deleted_count > 0:
        await message.reply_text(f"✅ Site removed from restricted list!")
    else:
        await message.reply_text(f"❌ Site not found in restricted list!")

# Bot Statistics Command
@Client.on_message(filters.command("stats") & filters.private)
@admin_only
async def bot_stats_command(client: Client, message: Message):
    """Show bot statistics"""
    stats = await db.get_bot_stats()
    stats_text = format_bot_stats(stats)
    
    await message.reply_text(stats_text)

# Set User Limit Command
@Client.on_message(filters.command("set_limit"))
@admin_only
async def set_limit_command(client: Client, message: Message):
    """Set user daily limit"""
    args = parse_command_args(message.text)
    
    if len(args) < 2:
        await message.reply_text(
            "**Usage:** `/set_limit <user_id> <limit>`\n\n"
            "**Example:** `/set_limit 123456789 50`\n"
            "Use -1 for unlimited"
        )
        return
    
    try:
        user_id = int(args[0])
        limit = int(args[1])
        
        await db.update_user(user_id, {"daily_limit": limit})
        
        await message.reply_text(
            f"✅ **Limit Updated**\n\n"
            f"**User ID:** `{user_id}`\n"
            f"**New Limit:** {limit if limit != -1 else 'Unlimited'}"
        )
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID or limit!")

# Ban User Command
@Client.on_message(filters.command("ban"))
@admin_only
async def ban_user_command(client: Client, message: Message):
    """Ban a user"""
    args = parse_command_args(message.text)
    
    if not args:
        # Check if replying to a message
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            await message.reply_text(
                "**Usage:** `/ban <user_id>` or reply to user's message"
            )
            return
    else:
        try:
            user_id = int(args[0])
        except ValueError:
            await message.reply_text("❌ Invalid user ID!")
            return
    
    await db.update_user(user_id, {"is_banned": True})
    
    await message.reply_text(
        f"✅ **User Banned**\n\n"
        f"**User ID:** `{user_id}`"
    )

# Unban User Command
@Client.on_message(filters.command("unban"))
@admin_only
async def unban_user_command(client: Client, message: Message):
    """Unban a user"""
    args = parse_command_args(message.text)
    
    if not args:
        await message.reply_text("**Usage:** `/unban <user_id>`")
        return
    
    try:
        user_id = int(args[0])
        await db.update_user(user_id, {"is_banned": False})
        
        await message.reply_text(
            f"✅ **User Unbanned**\n\n"
            f"**User ID:** `{user_id}`"
        )
        
    except ValueError:
        await message.reply_text("❌ Invalid user ID!")

# Broadcast Command
@Client.on_message(filters.command("broadcast") & filters.private)
@admin_only
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to users"""
    if not message.reply_to_message:
        await message.reply_text(
            "⚠️ Reply to a message to broadcast it!\n\n"
            "The replied message will be sent to all users."
        )
        return
    
    await message.reply_text(
        "📢 **Broadcast Message**\n\n"
        "Who should receive this message?",
        reply_markup=Keyboards.broadcast_keyboard()
    )

# Broadcast Callbacks
@Client.on_callback_query(filters.regex("^broadcast_"))
async def broadcast_callback(client: Client, callback: CallbackQuery):
    """Handle broadcast callbacks"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⚠️ Admin only!", show_alert=True)
        return
    
    broadcast_type = callback.data.split("_")[1]
    
    # Get the message to broadcast
    if not callback.message.reply_to_message:
        await callback.answer("❌ Original message not found!", show_alert=True)
        return
    
    broadcast_msg = callback.message.reply_to_message
    
    # Get users based on type
    if broadcast_type == "all":
        users = await db.get_all_users()
        user_type = "all users"
    elif broadcast_type == "premium":
        users = [u for u in await db.get_all_users() if u.get("is_premium")]
        user_type = "premium users"
    elif broadcast_type == "free":
        users = [u for u in await db.get_all_users() if not u.get("is_premium")]
        user_type = "free users"
    else:
        await callback.answer("❌ Invalid option!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"📤 Broadcasting to {len(users)} {user_type}...\n\n"
        f"This may take a while. Please wait..."
    )
    
    success = 0
    failed = 0
    blocked = 0
    
    for user in users:
        try:
            await broadcast_msg.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.05)  # Avoid flood
            
        except FloodWait as e:
            await asyncio.sleep(e.value)
            continue
        except (UserIsBlocked, InputUserDeactivated):
            blocked += 1
            continue
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast error for user {user['user_id']}: {e}")
            continue
    
    result_text = f"""
✅ **Broadcast Complete**

**Target:** {user_type}
**Total Users:** {len(users)}
**Successful:** {success}
**Blocked Bot:** {blocked}
**Failed:** {failed}
"""
    
    await callback.message.edit_text(result_text)
    
    # Log to channel
    if Config.LOG_CHANNEL:
        await client.send_message(Config.LOG_CHANNEL, result_text)

# Admin Callback Handlers
@Client.on_callback_query(filters.regex("^admin_"))
async def admin_callbacks(client: Client, callback: CallbackQuery):
    """Handle admin panel callbacks"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("⚠️ Admin only!", show_alert=True)
        return
    
    action = callback.data.replace("admin_", "")
    
    if action == "stats":
        stats = await db.get_bot_stats()
        stats_text = format_bot_stats(stats)
        await callback.message.edit_text(stats_text, reply_markup=Keyboards.back_button())
    
    elif action == "groups":
        groups = await db.get_all_allowed_groups()
        await callback.message.edit_text(
            f"👥 **Allowed Groups** ({len(groups)})\n\n"
            f"Use /add_group in a group to add it.",
            reply_markup=Keyboards.group_list_keyboard(groups)
        )
    
    elif action == "sites":
        sites = await db.get_all_restricted_sites()
        await callback.message.edit_text(
            f"🚫 **Restricted Sites** ({len(sites)})\n\n"
            f"Use /restrict_site <domain> to add.",
            reply_markup=Keyboards.site_list_keyboard(sites)
        )
    
    elif action == "panel":
        admin_text = """
👨‍💼 **Admin Panel**

Welcome to the admin control panel.
Select an option below to manage the bot.
"""
        await callback.message.edit_text(admin_text, reply_markup=Keyboards.admin_keyboard())
