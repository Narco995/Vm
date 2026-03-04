# 🤖 Advanced Telegram AI Bot — Vm

Powered by **GPT-4o · Whisper · DALL-E 3 · Mistral AI** with long-term memory, documents, code execution, research, automation, and a live web dashboard.

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Document Generation** | Word (.docx) and PDF reports |
| 🔬 **Deep Research** | AI-powered topic research with web context |
| 💻 **Code Execution** | Write and run Python in sandbox |
| 🎙 **Voice Messages** | Transcribe via Whisper + respond |
| 🖼 **Image Generation** | DALL-E 3 + GPT-4 Vision analysis |
| 📊 **Data Analysis** | CSV, Excel, JSON insights |
| 🧠 **Long-term Memory** | SQLite-persisted conversation history |
| ⚙️ **Automations** | APScheduler recurring tasks |
| 🌐 **Web Dashboard** | Live stats on any browser / iOS Safari |

## 🚀 Quick Start

```bash
git clone https://github.com/Narco995/Vm.git && cd Vm
cp .env.example .env   # then edit with your API keys
chmod +x deploy/deploy.sh && ./deploy/deploy.sh
```

## 📋 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome menu |
| `/pdf [topic]` | Generate PDF |
| `/doc [topic]` | Generate Word doc |
| `/code [task]` | Write & run Python |
| `/research [topic]` | Deep research |
| `/image [prompt]` | DALL-E 3 image |
| `/report [topic]` | Structured report |
| `/remember [note]` | Save memory |
| `/memory` | View notes |
| `/style` | Change response style |
| `/automate name\|task\|schedule` | Schedule task |
| `/status` | Bot status |

## 🏗 Project Structure

```
Vm/
├── main.py                     # Bot entry point
├── config.py                   # Configuration
├── web_dashboard.py            # Web UI (port 8080)
├── bot/
│   ├── handlers/               # command, message, voice, image, file, callback
│   ├── services/               # ai, pdf, docx, code, research, data, file, automation
│   ├── orchestrator/           # Intent detection & multi-step
│   └── utils/formatters.py
├── database/db_manager.py      # SQLite via aiosqlite
├── scripts/webhook_listener.py # GitHub webhook auto-deploy
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml      # Bot + Dashboard + Portainer + Watchtower
│   └── deploy.sh
└── .github/workflows/
    ├── deploy.yml              # CI/CD on push to main
    └── rollback.yml            # Auto-rollback on failure
```

## 🐳 Docker Stack

| Container | Port | Purpose |
|---|---|---|
| `vm-telegram-bot` | — | Main bot |
| `vm-dashboard` | 8080 | Web stats UI |
| `vm-portainer` | 9000 | Docker management |
| `vm-watchtower` | — | Auto-updates |

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `OPENAI_API_KEY` | GPT-4o, Whisper, DALL-E 3 |
| `MISTRAL_API_KEY` | Mistral Large |
| `AI_MODEL` | `gpt-4o` (default) |
| `DATABASE_PATH` | SQLite path |
| `MAX_MEMORY_MESSAGES` | Conversation history limit |

## 🔄 CI/CD

Every `git push` to `main` → validates → builds Docker image → deploys to server via SSH → auto-rollbacks on failure.

See `GITHUB_CONNECT.md` for SSH key setup.
