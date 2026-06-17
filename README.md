# 🤖 Discord Bot

A feature-rich Discord bot built with Python and `discord.py`.

---

## 📦 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env`:
```
DISCORD_TOKEN=your_bot_token_here
PREFIX=!
HIRE_LOG_CHANNEL=hire-log
```

### 3. Enable Discord Intents
In the [Discord Developer Portal](https://discord.com/developers/applications):
- Go to your bot → **Bot** tab
- Enable **Server Members Intent** and **Message Content Intent**

### 4. Run the bot
```bash
python bot.py
```

---

## 📂 File Structure
```
bot/
├── bot.py              # Main entry point
├── requirements.txt
├── .env.example
├── data/
│   └── warnings.json   # Auto-created for warnings storage
└── cogs/
    ├── moderation.py   # Mod commands
    ├── hire.py         # Interactive hire command
    ├── embeds.py       # Embed commands
    └── misc.py         # Utility commands
```

---

## 🔨 Commands

### Moderation (requires appropriate permissions)
| Command | Description |
|---|---|
| `!kick @user [reason]` | Kick a member |
| `!ban @user [reason]` | Ban a member |
| `!unban <user_id>` | Unban a user by ID |
| `!mute @user [minutes] [reason]` | Timeout a member (default: 10 min) |
| `!unmute @user` | Remove timeout |
| `!warn @user [reason]` | Warn a member |
| `!warnings @user` | View a member's warnings |
| `!clearwarnings @user` | Clear all warnings for a member |
| `!purge <amount>` | Delete up to 200 messages |
| `!slowmode <seconds>` | Set channel slowmode (0 to disable) |
| `!lock [reason]` | Lock the current channel |
| `!unlock` | Unlock the current channel |

### Hiring
| Command | Description |
|---|---|
| `!hire` | Start interactive hire flow — asks for user & role, assigns role, logs to hire-log channel |

### Embeds
| Command | Description |
|---|---|
| `!embed "Title" description` | Send a custom embed |
| `!announce #channel "Title" message` | Send an announcement embed with @everyone |
| `!say [#channel] message` | Make the bot send a plain message |

### Misc
| Command | Description |
|---|---|
| `!ping` | Check bot latency |
| `!serverinfo` | Detailed server information |
| `!userinfo [@user]` | User information |
| `!avatar [@user]` | Get a user's avatar |
| `!roleinfo <role>` | Role information |
| `!membercount` | Server member count |
| `!uptime` | Bot uptime |
| `!help` | Command list |
