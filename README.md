# Discord Auto-Kick Bot v3.0
Discord bot that automatically kicks members who don't verify within a set time period.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your bot token
```

### 3. Run the Bot

```bash
python main.py
```

Or with token as argument:
```bash
python main.py YOUR_BOT_TOKEN
```

## ⚙️ Configuration

Edit `config.py` to change default settings:

```python
UNVERIFIED_ROLE_NAME = "Unverified"
KICK_AFTER_MINUTES = 30
CHECK_INTERVAL_MINUTES = 1
SEND_DM_BEFORE_KICK = False
```

## 📋 Available Commands

### Slash Commands (Recommended)

- `/setup` - Configure role and kick timer
- `/status` - View tracked members
- `/setlogchannel` - Set where kick logs go
- `/toggledm` - Enable/disable DM notifications
- `/help` - Show all commands

### Prefix Commands (Legacy)

- `!setup` - Configure settings
- `!autokick_help` - Show help

## 🔧 Customization

### Change Check Interval

Edit `config.py`:
```python
CHECK_INTERVAL_MINUTES = 5  # Check every 5 minutes
```

### Change Embed Colors

Edit `config.py`:
```python
COLOR_INFO = 0x3498db      # Blue
COLOR_SUCCESS = 0x2ecc71   # Green
COLOR_WARNING = 0xf39c12   # Orange
COLOR_ERROR = 0xe74c3c     # Red
```

### Modify Kick Log Format

Edit `utils/logger.py` to customize the log embed appearance.

### Add New Commands

1. For slash commands: Edit `commands/slash_commands.py`
2. For prefix commands: Edit `commands/prefix_commands.py`

## 📝 Data Files

The bot creates these files automatically:

- `unverified_members.json` - Tracks which members are unverified
- `guild_configs.json` - Stores per-server settings

**Don't delete these while the bot is running!**
