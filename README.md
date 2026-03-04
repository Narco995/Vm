# 🤖 Telegram AI Bot (Vm)

An intelligent Telegram bot powered by AI models (Google Gemini, OpenAI) with Docker containerization and automated error detection.

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Error Detection & Auto-Fix](#error-detection--auto-fix)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

- 🤖 **AI-Powered Responses** - Supports multiple AI models
  - Google Gemini 2.5 Flash
  - OpenAI GPT-4.1 Mini
  - OpenAI GPT-4.1 Nano

- 🐳 **Docker Containerized** - Easy deployment and isolation
- 🔍 **Automatic Error Detection** - Built-in error detection and auto-fixing
- 📊 **Health Monitoring** - Continuous health checks
- 📝 **Persistent Logging** - Rotating logs with retention policies
- 🔒 **Production-Ready** - Resource limits, security settings, restart policies
- 🚀 **Zero-Downtime Deployment** - Seamless updates

---

## 📦 Requirements

### System Requirements
- **Docker**: 29.1.3 or higher
- **Docker Compose**: 2.40.3 or higher
- **Alpine Linux**: 3.23 or higher (optional, for development)
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: 5GB for container images and data

### Software Dependencies
- Python 3.11 or higher
- curl (for health checks)

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Narco995/Vm.git
cd Vm
```

### Step 2: Install Docker (if not already installed)

**Alpine Linux:**
```bash
apk update && apk add --no-cache docker docker-cli-compose curl
```

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install docker.io docker-compose
```

**macOS (with Homebrew):**
```bash
brew install docker docker-compose
```

### Step 3: Verify Installation

```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 29.1.3
Docker Compose v2.40.3
```

---

## ⚙️ Configuration

### Step 1: Create `.env` File

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

### Step 2: Edit `.env` with Your Credentials

Open `.env` and configure the required variables:

```ini
# TELEGRAM CONFIGURATION
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id

# AI MODEL CONFIGURATION
# Choose one: gemini-2.5-flash, gpt-4.1-mini, gpt-4.1-nano
AI_MODEL=gemini-2.5-flash
AI_API_KEY=your_api_key_here

# RESOURCE LIMITS (optional)
MEMORY_LIMIT=4096
CPU_LIMIT=2.0

# OTHER SETTINGS
ENVIRONMENT=production
DEBUG=false
TZ=UTC
```

### Getting Credentials

**Telegram Bot Token:**
1. Open Telegram and search for `@BotFather`
2. Use `/newbot` command
3. Follow the instructions and copy your token

**AI API Key:**
- **Google Gemini**: Get from [Google AI Studio](https://aistudio.google.com/apikey)
- **OpenAI**: Get from [OpenAI API Keys](https://platform.openai.com/api-keys)

---

## 🚀 Deployment

### Option 1: Automated Deployment (Recommended)

```bash
cd deploy
chmod +x deploy.sh
./deploy.sh
```

This script will:
- ✅ Validate your environment
- ✅ Auto-detect and fix common errors
- ✅ Build Docker containers
- ✅ Start services
- ✅ Verify health status

### Option 2: Manual Deployment

```bash
cd deploy
docker-compose up -d
```

### Step 3: Verify Deployment

```bash
docker-compose ps
```

Expected output:
```
CONTAINER ID   IMAGE           STATUS
abc123...      python:3.11     Up 2 minutes (healthy)
```

---

## 🔧 Error Detection & Auto-Fix

The deployment script automatically detects and fixes these errors:

| # | Error | Auto-Fix |
|---|-------|----------|
| 1 | Invalid AI_MODEL | Defaults to `gemini-2.5-flash` |
| 2 | Missing MEMORY_LIMIT | Sets to 4096MB |
| 3 | Missing CPU_LIMIT | Sets to 2.0 cores |
| 4 | Invalid docker-compose.yml | Shows syntax errors |
| 5 | Docker daemon not running | Fails with clear message |
| 6 | Missing health check port | Auto-configured in compose file |
| 7 | No port exposure | Exposes port 8000 |
| 8 | Bad health check command | Uses curl-based check |

---

## 📊 Monitoring

### View Logs

**Real-time logs:**
```bash
docker-compose logs -f
```

**Last 100 lines:**
```bash
docker-compose logs --tail=100
```

**Specific service logs:**
```bash
docker-compose logs telegram-bot
```

### Health Check Status

```bash
docker-compose ps
# Look for "(healthy)" or "(unhealthy)" status
```

### Container Statistics

```bash
docker stats vm-telegram-bot
```

---

## 🆘 Troubleshooting

### Issue: "Container unhealthy"

**Solution:**
```bash
# Check logs
docker-compose logs telegram-bot

# Restart container
docker-compose restart telegram-bot

# Run error detection
cd deploy && ./deploy.sh
```

### Issue: "API key invalid"

**Solution:**
1. Verify your API key in `.env`
2. Check if the AI model is supported
3. Ensure you have credits/quota in your AI service

### Issue: "Bot not responding to Telegram messages"

**Solution:**
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check bot logs: `docker-compose logs telegram-bot`
3. Ensure container is healthy: `docker-compose ps`

### Issue: "Out of memory (OOM)"

**Solution:**
```bash
# Increase memory limit in .env
MEMORY_LIMIT=8192  # 8GB

# Redeploy
cd deploy && ./deploy.sh
```

### Issue: Docker daemon not running

**Solution:**
```bash
# Start Docker daemon
sudo systemctl start docker

# Alpine Linux
sudo rc-service docker start
```

---

## 📁 Project Structure

```
Vm/
├── README.md              # This file
├── .env                   # Configuration (don't commit to git)
├── .env.example           # Configuration template
├── .gitignore            # Git ignore rules
├── deploy/
│   ├── docker-compose.yml # Docker composition with error fixes
│   └── deploy.sh          # Automated deployment script
└── .git/                 # Git repository
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` to git** - It contains sensitive credentials
2. **Use strong API keys** - Rotate regularly
3. **Keep Docker updated** - `docker pull python:3.11-slim`
4. **Monitor logs** - Check for suspicious activity
5. **Limit resources** - Set appropriate CPU/memory limits
6. **Use environment variables** - Never hardcode secrets

---

## 📞 Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review container logs: `docker-compose logs`
- Create an issue on GitHub

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Last Updated:** 2026-03-04  
**Maintained by:** Narco995
