# 🚀 Complete Deployment Guide

## 📋 Pre-Deployment Checklist

### Required
- [ ] Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- [ ] Telegram API ID & Hash from [my.telegram.org](https://my.telegram.org)
- [ ] MongoDB Database (Atlas free tier works great)
- [ ] Admin Telegram User ID

### Optional but Recommended
- [ ] Log Channel ID
- [ ] Feedback Channel ID
- [ ] Force Subscribe Channel/Group
- [ ] Service credentials (GDToT, Uptobox, etc.)

---

## 🌐 MongoDB Setup

### Using MongoDB Atlas (Free)

1. **Create Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free account

2. **Create Cluster**
   - Choose FREE tier (M0)
   - Select your preferred region
   - Name your cluster

3. **Create Database User**
   - Go to Database Access
   - Add New Database User
   - Choose Password authentication
   - Save username and password

4. **Configure Network Access**
   - Go to Network Access
   - Add IP Address
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add specific IPs for better security

5. **Get Connection String**
   - Go to Clusters
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

---

## 💻 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/Link-Bypasser-Bot.git
cd Link-Bypasser-Bot
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_ID=12345678
API_HASH=1234567890abcdef1234567890abcdef
ADMIN_IDS=123456789,987654321
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=link_bypasser_db
PORT=5000
```

### 5. Run the Bot
```bash
# Start bot
python main.py

# In another terminal, start Flask (optional)
python app.py
```

### 6. Test the Bot
- Open Telegram
- Search for your bot
- Send `/start`
- Test with a sample link

---

## 🟣 Heroku Deployment

### Method 1: Using Heroku CLI

1. **Install Heroku CLI**
```bash
# Windows (using Chocolatey)
choco install heroku-cli

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku App**
```bash
heroku create your-bot-name
```

4. **Set Environment Variables**
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set ADMIN_IDS=your_admin_ids
heroku config:set DATABASE_NAME=link_bypasser_db
heroku config:set FREE_USER_LIMIT=10
heroku config:set REFERRAL_ENABLED=True
heroku config:set USE_WEBHOOK=True
heroku config:set WEBHOOK_URL=https://your-bot-name.herokuapp.com
```

5. **Deploy**
```bash
git push heroku main
```

6. **Scale Dynos**
```bash
heroku ps:scale worker=1 web=1
```

7. **View Logs**
```bash
heroku logs --tail
```

### Method 2: Using Heroku Dashboard

1. Go to [Heroku Dashboard](https://dashboard.heroku.com/)
2. Click "New" → "Create new app"
3. Enter app name and region
4. Go to "Settings" → "Config Vars"
5. Add all environment variables
6. Go to "Deploy" tab
7. Connect your GitHub repository
8. Enable automatic deploys (optional)
9. Click "Deploy Branch"

### Heroku-Specific Files

Ensure you have:
- `Procfile` (worker and web processes)
- `runtime.txt` (Python version)
- `requirements.txt` (dependencies)

---

## 🚂 Railway Deployment

### Method 1: GitHub Integration

1. **Sign up on Railway**
   - Go to [Railway.app](https://railway.app/)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variables**
   - Go to Variables tab
   - Add all required variables from `.env.example`

4. **Deploy**
   - Railway auto-deploys on push
   - Monitor deployment in logs

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# Add variables
railway variables set BOT_TOKEN=your_token
```

### Railway Benefits
- ✅ Free $5 monthly credit
- ✅ Automatic SSL
- ✅ Fast deployments
- ✅ Easy environment management
- ✅ Great for webhooks

---

## 🖥️ VPS Deployment

### Ubuntu/Debian VPS

1. **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Python 3.11**
```bash
sudo apt install python3.11 python3.11-venv python3-pip -y
```

3. **Clone Repository**
```bash
cd /opt
sudo git clone https://github.com/yourusername/Link-Bypasser-Bot.git
cd Link-Bypasser-Bot
```

4. **Create Virtual Environment**
```bash
sudo python3.11 -m venv venv
source venv/bin/activate
```

5. **Install Dependencies**
```bash
pip install -r requirements.txt
```

6. **Configure Environment**
```bash
sudo nano .env
# Paste your environment variables
```

7. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/linkbot.service
```

Add this content:
```ini
[Unit]
Description=Link Bypasser Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Link-Bypasser-Bot
Environment="PATH=/opt/Link-Bypasser-Bot/venv/bin"
ExecStart=/opt/Link-Bypasser-Bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable linkbot
sudo systemctl start linkbot
```

9. **Check Status**
```bash
sudo systemctl status linkbot
sudo journalctl -u linkbot -f  # View logs
```

### Using Screen (Alternative)

```bash
# Install screen
sudo apt install screen -y

# Start screen session
screen -S linkbot

# Run bot
python main.py

# Detach: Ctrl+A then D
# Reattach: screen -r linkbot
```

### Using PM2 (Recommended)

```bash
# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# Start bot
pm2 start main.py --name linkbot --interpreter python3

# Auto-start on reboot
pm2 startup
pm2 save

# Useful commands
pm2 status
pm2 logs linkbot
pm2 restart linkbot
pm2 stop linkbot
```

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run bot
CMD ["python", "main.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: always
    env_file:
      - .env
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs
    depends_on:
      - mongodb

  mongodb:
    image: mongo:6
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## ☁️ Other Cloud Platforms

### Google Cloud Run

```bash
# Install gcloud CLI
# Then:
gcloud run deploy linkbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### AWS EC2

1. Launch EC2 instance (t2.micro free tier)
2. SSH into instance
3. Follow VPS deployment steps
4. Configure security groups for port 5000

### DigitalOcean App Platform

1. Connect GitHub repository
2. Add environment variables
3. Deploy with one click

---

## 🔧 Post-Deployment Configuration

### 1. Setup Webhook (if using)

```bash
# Get bot info
curl https://api.telegram.org/bot<TOKEN>/getMe

# Set webhook
curl https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/webhook

# Check webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### 2. Create Telegram Channels

```bash
# Create channels
1. Log channel (for errors/notifications)
2. Feedback channel (for user feedback)
3. Force subscribe channel (optional)

# Get channel IDs
1. Add bot to channels as admin
2. Send a message to channel
3. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
4. Find channel ID (starts with -100)
```

### 3. Test All Features

- [ ] Start bot with `/start`
- [ ] Bypass a link
- [ ] Generate premium token
- [ ] Test referral system
- [ ] Send feedback
- [ ] Request a site
- [ ] Check admin panel
- [ ] Test broadcast
- [ ] Verify force subscribe

### 4. Monitor Performance

```bash
# Check bot logs
tail -f bot.log

# Monitor system resources
htop

# Check MongoDB connections
# In MongoDB Atlas: Metrics tab

# Monitor Heroku
heroku logs --tail
```

---

## 🔒 Security Best Practices

1. **Environment Variables**
   - Never commit `.env` to git
   - Use different tokens for dev/prod
   - Rotate tokens periodically

2. **MongoDB Security**
   - Enable IP whitelist
   - Use strong passwords
   - Enable encryption at rest

3. **Bot Security**
   - Verify admin IDs correctly
   - Implement rate limiting
   - Monitor for abuse
   - Regular security updates

4. **Server Security** (VPS)
```bash
# Setup firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
```

---

## 🐛 Troubleshooting

### Bot Not Starting

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list

# Check environment variables
printenv | grep BOT_TOKEN

# Test MongoDB connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('OK')"
```

### Database Connection Issues

```bash
# Test MongoDB URI
mongosh "your_mongodb_uri"

# Check network access in Atlas
# Ensure 0.0.0.0/0 is whitelisted

# Verify database name
```

### Webhook Not Working

```bash
# Check webhook status
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Delete webhook
curl https://api.telegram.org/bot<TOKEN>/deleteWebhook

# Set webhook again
curl https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/webhook

# Ensure HTTPS (webhooks require SSL)
```

### Memory Issues (Heroku)

```bash
# Check dyno usage
heroku ps

# Restart dyno
heroku restart

# Scale up if needed (paid)
heroku ps:scale worker=1:standard-1x
```

---

## 📊 Monitoring & Maintenance

### Log Monitoring

```bash
# Heroku
heroku logs --tail

# VPS
tail -f bot.log
sudo journalctl -u linkbot -f

# Docker
docker-compose logs -f
```

### Database Maintenance

- Regular backups (MongoDB Atlas auto-backups)
- Monitor storage usage
- Clean old cache entries
- Index optimization

### Performance Monitoring

- Response times
- Success rates
- Error rates
- User growth
- Resource usage

---

## 🔄 Updates & Maintenance

### Updating the Bot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
# Heroku: git push heroku main
# Railway: git push (auto-deploys)
# VPS: sudo systemctl restart linkbot
# Docker: docker-compose up -d --build
```

### Database Migration

If you need to update database schema:

```python
# Create migration script
# migrations/001_add_referral_fields.py

async def migrate():
    await db.users.update_many(
        {},
        {"$set": {"referral_code": None, "total_referrals": 0}}
    )
```

---

## 📞 Support & Resources

### Official Resources
- [Pyrogram Documentation](https://docs.pyrogram.org/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Community
- GitHub Issues: Report bugs
- Telegram Group: @YourSupportGroup
- Email: support@yourdomain.com

### Paid Support
For priority support, custom features, or deployment assistance:
- Email: premium@yourdomain.com
- Telegram: @YourUsername

---

## ✅ Final Checklist

- [ ] Bot token configured
- [ ] MongoDB connected
- [ ] Admin IDs set
- [ ] Channels created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] All features tested
- [ ] Monitoring setup
- [ ] Backup configured
- [ ] Documentation read
- [ ] Security reviewed
- [ ] Performance optimized

---

**Congratulations! Your Link Bypasser Bot is now live! 🎉**

For questions or issues, refer to the troubleshooting section or contact support.
