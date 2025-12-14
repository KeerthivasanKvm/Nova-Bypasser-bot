import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database.mongodb import db
from bot.utils.helpers import extract_urls, get_domain, truncate_text
from bot.utils.keyboards import Keyboards
from bot.middlewares.auth import protected_command, rate_limit_required
from bypasser.core import LinkBypasser

logger = logging.getLogger(__name__)

# Initialize bypasser
bypasser = LinkBypasser()

# URL Handler - Main bypass logic
@Client.on_message(filters.text & filters.private)
@protected_command
@rate_limit_required
async def handle_url(client: Client, message: Message):
    """Handle URL bypass requests"""
    
    # Extract URLs from message
    urls = extract_urls(message.text)
    
    if not urls:
        # Not a URL, might be a command or regular text
        return
    
    # Process first URL
    url = urls[0]
    
    # Check if site is restricted
    if await db.is_site_restricted(url):
        domain = get_domain(url)
        await message.reply_text(
            f"🚫 **Site Restricted**\n\n"
            f"Links from `{domain}` are not allowed!\n"
            f"Contact admin for more information."
        )
        return
    
    # Send processing message
    processing_msg = await message.reply_text(
        "🔄 **Processing your link...**\n\n"
        "Please wait, this may take a moment."
    )
    
    try:
        # Check cache first
        cached = await db.get_cached_link(url)
        
        if cached:
            bypassed_link = cached["bypassed_link"]
            await db.increment_link_usage(url)
            
            result_text = f"""
✅ **Link Bypassed Successfully!**

**Original Link:**
`{truncate_text(url, 50)}`

**Bypassed Link:**
`{bypassed_link}`

**Source:** 💾 Cache
**Bypass Type:** {cached.get('bypass_type', 'Unknown')}

Click the button below to open the link!
"""
            
            await processing_msg.edit_text(
                result_text,
                reply_markup=Keyboards.bypass_result_keyboard(url, bypassed_link)
            )
            
            # Increment user usage
            await db.increment_user_usage(message.from_user.id)
            
            logger.info(f"Cache hit for {url} by user {message.from_user.id}")
            return
        
        # No cache, perform bypass
        await processing_msg.edit_text(
            "🔄 **Bypassing link...**\n\n"
            "⏳ This might take 10-30 seconds..."
        )
        
        result = await bypasser.bypass(url)
        
        if result["success"]:
            bypassed_link = result["bypassed_url"]
            bypass_type = result.get("type", "unknown")
            
            # Save to cache
            await db.save_bypass_result(url, bypassed_link, bypass_type)
            
            result_text = f"""
✅ **Link Bypassed Successfully!**

**Original Link:**
`{truncate_text(url, 50)}`

**Bypassed Link:**
`{bypassed_link}`

**Source:** 🔥 Fresh Bypass
**Bypass Type:** {bypass_type.title()}

Click the button below to open the link!
"""
            
            await processing_msg.edit_text(
                result_text,
                reply_markup=Keyboards.bypass_result_keyboard(url, bypassed_link)
            )
            
            # Increment user usage
            await db.increment_user_usage(message.from_user.id)
            
            # Log to channel
            if Config.LOG_CHANNEL:
                try:
                    await client.send_message(
                        Config.LOG_CHANNEL,
                        f"✅ **New Bypass**\n\n"
                        f"**User:** {message.from_user.first_name} (`{message.from_user.id}`)\n"
                        f"**Type:** {bypass_type}\n"
                        f"**Domain:** {get_domain(url)}"
                    )
                except:
                    pass
            
            logger.info(f"Successfully bypassed {url} by user {message.from_user.id}")
            
        else:
            error_msg = result.get("error", "Unknown error occurred")
            
            await processing_msg.edit_text(
                f"❌ **Bypass Failed**\n\n"
                f"**Error:** {error_msg}\n\n"
                f"**Possible Reasons:**\n"
                f"• Link format not supported\n"
                f"• Site protection detected\n"
                f"• Link expired or invalid\n"
                f"• Service temporarily unavailable\n\n"
                f"Please try again or contact support.",
                reply_markup=Keyboards.back_button()
            )
            
            logger.warning(f"Bypass failed for {url}: {error_msg}")
    
    except Exception as e:
        logger.error(f"Error bypassing {url}: {str(e)}")
        
        await processing_msg.edit_text(
            f"❌ **An error occurred**\n\n"
            f"Please try again later or contact support.\n\n"
            f"Error: {str(e)[:100]}",
            reply_markup=Keyboards.back_button()
        )

# Batch URL Handler (for groups with multiple links)
@Client.on_message(filters.text & filters.group)
@protected_command
async def handle_group_url(client: Client, message: Message):
    """Handle URLs in group chats"""
    
    urls = extract_urls(message.text)
    
    if not urls:
        return
    
    # Check rate limit
    from bot.middlewares.auth import check_rate_limit
    rate_check = await check_rate_limit(message.from_user.id)
    
    if not rate_check["allowed"]:
        # Silently ignore in groups if limit exceeded
        return
    
    # Process only first URL in groups
    url = urls[0]
    
    # Check if site is restricted
    if await db.is_site_restricted(url):
        return
    
    # Check cache
    cached = await db.get_cached_link(url)
    
    if cached:
        bypassed_link = cached["bypassed_link"]
        await db.increment_link_usage(url)
        
        await message.reply_text(
            f"✅ **Link Bypassed!**\n\n"
            f"`{bypassed_link}`\n\n"
            f"💾 From Cache",
            reply_markup=Keyboards.bypass_result_keyboard(url, bypassed_link)
        )
        
        await db.increment_user_usage(message.from_user.id)
        return
    
    # Perform bypass
    try:
        result = await bypasser.bypass(url)
        
        if result["success"]:
            bypassed_link = result["bypassed_url"]
            bypass_type = result.get("type", "unknown")
            
            await db.save_bypass_result(url, bypassed_link, bypass_type)
            
            await message.reply_text(
                f"✅ **Link Bypassed!**\n\n"
                f"`{bypassed_link}`\n\n"
                f"🔥 Fresh Bypass",
                reply_markup=Keyboards.bypass_result_keyboard(url, bypassed_link)
            )
            
            await db.increment_user_usage(message.from_user.id)
        
    except Exception as e:
        logger.error(f"Error bypassing in group: {str(e)}")
