import re
import validators
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import List, Optional

def is_url(text: str) -> bool:
    """Check if text is a valid URL"""
    return validators.url(text) is True

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return [url for url in urls if is_url(url)]

def get_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return None

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"

def format_duration(days: int) -> str:
    """Format duration in days to human readable format"""
    if days < 1:
        hours = int(days * 24)
        return f"{hours} hour{'s' if hours != 1 else ''}"
    elif days < 30:
        return f"{days} day{'s' if days != 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"

def parse_duration(duration_str: str) -> int:
    """Parse duration string to days (e.g., '1d', '2h', '3m' for months)"""
    duration_str = duration_str.lower().strip()
    
    # Extract number and unit
    match = re.match(r'(\d+)\s*([dhm])', duration_str)
    if not match:
        raise ValueError("Invalid duration format. Use: 1d, 2h, 3m (m for months)")
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'h':  # hours
        return max(1, value // 24)  # Convert to days, minimum 1 day
    elif unit == 'd':  # days
        return value
    elif unit == 'm':  # months
        return value * 30
    else:
        raise ValueError("Invalid duration unit. Use: h (hours), d (days), m (months)")

def calculate_expiry_date(days: int) -> datetime:
    """Calculate expiry date from days"""
    return datetime.utcnow() + timedelta(days=days)

def is_expired(expiry_date: datetime) -> bool:
    """Check if date is expired"""
    return expiry_date < datetime.utcnow() if expiry_date else False

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    return text[:max_length] + "..." if len(text) > max_length else text

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_user_mention(user) -> str:
    """Get user mention string"""
    if user.username:
        return f"@{user.username}"
    return f"[{user.first_name}](tg://user?id={user.id})"

def parse_command_args(text: str) -> List[str]:
    """Parse command arguments from text"""
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        return parts[1].split()
    return []

def is_admin_command(text: str) -> bool:
    """Check if text starts with admin command"""
    admin_commands = [
        '/generate_token', '/create_token',
        '/generate_reset', '/create_reset',
        '/add_group', '/remove_group',
        '/add_site', '/remove_site', '/restrict_site',
        '/ban', '/unban',
        '/stats', '/broadcast',
        '/set_limit', '/reset_limit'
    ]
    return any(text.startswith(cmd) for cmd in admin_commands)

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a progress bar"""
    if total == 0:
        return "░" * length
    
    filled = int((current / total) * length)
    bar = "▓" * filled + "░" * (length - filled)
    percentage = (current / total) * 100
    return f"{bar} {percentage:.1f}%"

def format_user_stats(user: dict) -> str:
    """Format user statistics"""
    status = "👑 Premium" if user.get("is_premium") else "🆓 Free"
    
    stats = f"**User Statistics**\n\n"
    stats += f"**Status:** {status}\n"
    stats += f"**Daily Limit:** {user.get('daily_limit', 0)} links\n"
    stats += f"**Used Today:** {user.get('links_bypassed_today', 0)} links\n"
    stats += f"**Total Bypassed:** {user.get('total_links_bypassed', 0)} links\n"
    
    if user.get("is_premium") and user.get("subscription_end_date"):
        days_left = (user["subscription_end_date"] - datetime.utcnow()).days
        stats += f"**Premium Expires:** {days_left} days\n"
    
    return stats

def format_bot_stats(stats: dict) -> str:
    """Format bot statistics"""
    text = "📊 **Bot Statistics**\n\n"
    text += f"👥 **Total Users:** {stats.get('total_users', 0)}\n"
    text += f"👑 **Premium Users:** {stats.get('premium_users', 0)}\n"
    text += f"🆓 **Free Users:** {stats.get('free_users', 0)}\n"
    text += f"🔗 **Cached Links:** {stats.get('cached_links', 0)}\n"
    text += f"✅ **Total Bypasses:** {stats.get('total_bypasses', 0)}\n"
    return text

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    return filename[:255]

def is_group_chat(chat_type: str) -> bool:
    """Check if chat is a group"""
    return chat_type in ["group", "supergroup"]

def is_private_chat(chat_type: str) -> bool:
    """Check if chat is private"""
    return chat_type == "private"
