from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

class Keyboards:
    """Keyboard factory for bot"""
    
    @staticmethod
    def start_keyboard(is_premium: bool = False):
        """Main start keyboard"""
        buttons = [
            [
                InlineKeyboardButton("✨ Get Premium", callback_data="get_premium"),
                InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help"),
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ]
        ]
        
        if is_premium:
            buttons[0] = [
                InlineKeyboardButton("👑 Premium Active", callback_data="premium_info"),
                InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
            ]
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def help_keyboard():
        """Help keyboard"""
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def back_button():
        """Simple back button"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="start")
        ]])
    
    @staticmethod
    def force_sub_keyboard(channel_url: str = None, group_url: str = None):
        """Force subscription keyboard"""
        buttons = []
        
        if channel_url:
            buttons.append([InlineKeyboardButton("📢 Join Channel", url=channel_url)])
        if group_url:
            buttons.append([InlineKeyboardButton("👥 Join Group", url=group_url)])
        
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check_subscription")])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def premium_keyboard():
        """Premium information keyboard"""
        buttons = [
            [
                InlineKeyboardButton("🎟️ Redeem Token", callback_data="redeem_token")
            ],
            [
                InlineKeyboardButton("💰 Buy Premium", url="https://t.me/YourPaymentBot")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="start")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def admin_keyboard():
        """Admin panel keyboard"""
        buttons = [
            [
                InlineKeyboardButton("🎫 Generate Token", callback_data="admin_gen_token"),
                InlineKeyboardButton("🔑 Generate Reset", callback_data="admin_gen_reset")
            ],
            [
                InlineKeyboardButton("👥 Manage Groups", callback_data="admin_groups"),
                InlineKeyboardButton("🚫 Manage Sites", callback_data="admin_sites")
            ],
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def cancel_keyboard():
        """Cancel operation keyboard"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]])
    
    @staticmethod
    def confirm_keyboard(action: str):
        """Confirm action keyboard"""
        buttons = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def bypass_result_keyboard(original_link: str, bypassed_link: str):
        """Bypass result keyboard"""
        buttons = [
            [InlineKeyboardButton("🔗 Open Link", url=bypassed_link)],
            [InlineKeyboardButton("🔄 Bypass Another", callback_data="start")]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def group_list_keyboard(groups: list):
        """Groups management keyboard"""
        buttons = []
        for group in groups[:10]:  # Limit to 10 groups
            group_name = group.get("group_name", "Unknown")[:30]
            buttons.append([
                InlineKeyboardButton(
                    f"📌 {group_name}",
                    callback_data=f"group_info_{group['group_id']}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton("➕ Add Group", callback_data="admin_add_group"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def site_list_keyboard(sites: list):
        """Sites management keyboard"""
        buttons = []
        for site in sites[:10]:  # Limit to 10 sites
            domain = site.get("domain", "Unknown")[:30]
            buttons.append([
                InlineKeyboardButton(
                    f"🚫 {domain}",
                    callback_data=f"site_info_{site.get('domain')}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton("➕ Add Site", callback_data="admin_add_site"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_panel")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def broadcast_keyboard():
        """Broadcast message keyboard"""
        buttons = [
            [
                InlineKeyboardButton("📤 Send to All", callback_data="broadcast_all"),
                InlineKeyboardButton("👑 Premium Only", callback_data="broadcast_premium")
            ],
            [
                InlineKeyboardButton("🆓 Free Only", callback_data="broadcast_free"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def link_keyboard():
        """Main menu keyboard for link input"""
        return ReplyKeyboardMarkup(
            [
                [KeyboardButton("🔗 Bypass Link")],
                [KeyboardButton("📊 My Stats"), KeyboardButton("❓ Help")]
            ],
            resize_keyboard=True
        )
    
    @staticmethod
    def remove_keyboard():
        """Remove keyboard"""
        from pyrogram.types import ReplyKeyboardRemove
        return ReplyKeyboardRemove()
