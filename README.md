# 🔗 Link Bypasser Bot

A powerful Telegram bot that bypasses ad links, generates direct download links, and jumps paywalls with advanced features like referral system, feedback management, and MongoDB caching.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green.svg)](https://docs.pyrogram.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🔥 Core Features
- ✅ **Multi-Site Support** - Bypass 25+ popular link shortener and file hosting sites
- ✅ **10 Bypass Methods** - HTML, CSS, JavaScript, Browser Automation, and more
- ✅ **Cloudflare Bypass** - Advanced scraping to bypass Cloudflare protection
- ✅ **Browser Automation** - Selenium-based bypass for complex JavaScript sites
- ✅ **Smart Detection** - Automatically identifies best bypass method
- ✅ **MongoDB Caching** - Smart caching system to speed up repeated requests
- ✅ **Direct Link Generation** - Convert shortened links to direct download URLs
- ✅ **Paywall Bypass** - Jump over paywalls and access restricted content
- ✅ **~85% Success Rate** - Combines multiple methods for high success rate

### 👥 User Management
- 🆓 **Free & Premium Tiers** - Two-tier subscription system
- 👑 **Premium Features** - Unlimited bypassing, priority queue, faster speeds
- 🎫 **Token System** - One-time use premium access tokens
- 🔑 **Universal Reset Keys** - Admin-generated keys to reset user limits
- 📊 **User Statistics** - Track usage, referrals, and subscription status

### 🎁 Referral System
- 📢 **Referral Program** - Invite friends and earn bonus links
- 💰 **Referral Rewards** - Configurable bonuses for each referral
- 🏆 **Free Premium** - Get premium access by referring friends
- ⚡ **Toggle System** - Admin can enable/disable referrals anytime

### 💬 Feedback & Support
- 📝 **Error Reporting** - Users can report broken or unsupported links
- 💭 **Feedback System** - Send suggestions and bug reports
- 🌐 **Site Requests** - Request support for new websites
- 👍 **Upvote System** - Community voting on requested sites
- 📢 **Admin Dashboard** - Review and manage all feedback

### 🛡️ Admin Controls
- 👨‍💼 **Full Admin Panel** - Complete bot management interface
- 🎫 **Token Generator** - Create premium tokens with custom durations
- 🔑 **Reset Key System** - Generate universal limit reset keys
- 👥 **Group Management** - Allow/restrict bot usage in groups
- 🚫 **Site Restrictions** - Block specific domains from bypassing
- 📊 **Statistics Dashboard** - View comprehensive bot analytics
- 📢 **Broadcast System** - Send messages to all/premium/free users
- ⚙️ **Dynamic Settings** - Toggle features on-the-fly

### 🔐 Security & Performance
- 🔒 **Force Subscription** - Require channel/group membership
- 🚀 **Rate Limiting** - Prevent abuse with configurable limits
- 🌐 **Dual Mode** - Support both webhook and polling modes
- 📱 **Group-Only Mode** - Restrict bot to authorized groups only
- ⚡ **Async Operations** - Non-blocking async/await architecture
- 💾 **Smart Caching** - Reduce server load with MongoDB caching

## 📦 Installation

### Prerequisites
- Python 3.11+
- MongoDB Database
- Telegram Bot Token
- Telegram API ID & Hash

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Link-Bypasser-Bot.git
cd Link-Bypasser-Bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

5. **Run the bot**
```bash
python main.py
```

## 🚀 Deployment

### Heroku Deployment

```bash
# Install Heroku CLI
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set BOT_TOKEN=your_token
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set ADMIN_IDS=your_admin_ids

# Deploy
git push heroku main

# Scale workers
heroku ps:scale worker=1 web=1
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### VPS Deployment

```bash
# Clone and setup
git clone https://github.com/yourusername/Link-Bypasser-Bot.git
cd Link-Bypasser-Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env

# Run with systemd or screen
screen -S bot
python main.py
```

## ⚙️ Configuration

### Required Environment Variables

```env
# Telegram Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
ADMIN_IDS=123456789,987654321

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=link_bypasser_db

# Flask Configuration
PORT=5000
WEBHOOK_URL=https://your-app.herokuapp.com
```

### Optional Configuration

```env
# Force Subscription
FORCE_SUB_CHANNEL=@your_channel
FORCE_SUB_GROUP=@your_group

# Rate Limiting
FREE_USER_LIMIT=10
PREMIUM_USER_LIMIT=-1

# Referral System
REFERRAL_ENABLED=True
REFERRAL_BONUS_LINKS=5
MIN_REFERRALS_FOR_PREMIUM=10

# Webhook Mode
USE_WEBHOOK=False

# Logging
LOG_CHANNEL=-1001234567890
FEEDBACK_CHANNEL=-1001234567890
```

## 📝 Bot Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/bypass <link>` or `/b <link>` - Bypass a link
- `/stats` - View your statistics
- `/referral` - Referral program info
- `/redeem <token>` - Redeem premium token
- `/reset <key>` - Use reset key
- `/report <link>` - Report broken link
- `/feedback <message>` - Send feedback
- `/request <site>` - Request new site support

### Admin Commands
- `/admin` - Admin panel
- `/generate_token <duration>` - Generate premium token
- `/generate_reset` - Generate universal reset key
- `/add_group` - Add group to whitelist
- `/remove_group <id>` - Remove group
- `/restrict_site <domain>` - Restrict a site
- `/remove_site <domain>` - Remove restriction
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - Bot statistics
- `/broadcast` - Broadcast message
- `/toggle_referral` - Toggle referral system
- `/view_feedback` - View all feedback
- `/review_feedback <id> <status>` - Review feedback
- `/review_request <id> <status>` - Review site request

## 🌐 Supported Sites

- GDToT, GDFlix
- Sharer.pw, FilePress
- Drivefire, Hubdrive, Katdrive, Kolop
- Uptobox, Terabox
- LinkVertise, Link-to.net
- Adf.ly, Ay.gy
- GPLinks, Ouo.io
- Shortingly, Bit.ly
- Droplink, Linkbox
- WeTransfer
- **And 100+ more through universal bypass methods!**

### 🔓 Bypass Methods

The bot uses **10 different bypass techniques** to handle various protection methods:

1. **HTML Form Submission** - Auto-submits forms with hidden fields
2. **CSS Hidden Elements** - Finds links hidden by CSS
3. **JavaScript Execution** - Executes JS to extract dynamic URLs
4. **Meta Refresh** - Bypasses meta refresh redirects
5. **Iframe/Embed** - Extracts from iframes and embeds
6. **Base64 Decoding** - Decodes encoded links
7. **URL Parameters** - Extracts from query parameters
8. **Data Attributes** - Finds URLs in HTML5 data attributes
9. **Cloudflare Bypass** - Handles Cloudflare protection
10. **Browser Automation** - Selenium for complex JavaScript sites

**Success Rate:** ~85% across all link types

For detailed technical documentation, see [BYPASS_METHODS.md](BYPASS_METHODS.md)

## 📊 Features Breakdown

### Referral System
- **How It Works**: Users get a unique referral link
- **Rewards**: Bonus links for each successful referral
- **Premium Path**: Refer enough users to get free premium
- **Admin Control**: Can be toggled on/off anytime

### Feedback System
- **Report Issues**: Users can report broken links
- **Error Tracking**: Automatic error logging and reporting
- **Suggestions**: Users can suggest improvements
- **Admin Review**: All feedback reviewed by admins

### Site Request System
- **Request Support**: Users can request new sites
- **Community Voting**: Upvote popular requests
- **Status Tracking**: Track request status
- **Implementation**: Admins mark when implemented

## 🔒 Security

- Environment variables for sensitive data
- MongoDB connection encryption
- Rate limiting to prevent abuse
- Admin-only commands protection
- Force subscription verification
- Ban system for rule violators

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Support

If you find this project helpful, please:
- ⭐ Star this repository
- 🐛 Report bugs
- 💡 Suggest new features
- 🤝 Contribute code

## 📧 Contact

- Telegram: [@YourUsername](https://t.me/YourUsername)
- Email: your.email@example.com
- Issues: [GitHub Issues](https://github.com/yourusername/Link-Bypasser-Bot/issues)

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API framework
- [Motor](https://github.com/mongodb/motor) - Async MongoDB driver
- [Flask](https://github.com/pallets/flask) - Web framework
- [Cloudscraper](https://github.com/VeNoMouS/cloudscraper) - Cloudflare bypass

---

Made with ❤️ by [Your Name](https://github.com/yourusername)
