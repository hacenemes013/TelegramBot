# Telegram Message Forwarder Bot

A small Telegram bot I created back in 2024 for a telegram channel. it receives messages from anyone who writes to it and forwards them to your personal Telegram chat, together with the sender's name, username, and ID. It works as a simple contact inbox or feedback bot without exposing your personal account.

## Features

- Forwards **text**, **photos**, **documents**, **voice messages**, **videos**, **audio files**, **video notes**, and **stickers**
- Adds sender info (full name, @username or "no username", and Telegram ID) to every forwarded message
- Keeps captions on photos, documents, videos, and audio
- Confirms to the sender only when the message was actually forwarded
- Tells the sender when a message type is not supported
- Replies with an error message if forwarding fails
- Logs activity and full error tracebacks to the console
- Ignores bot commands (messages starting with `/`)
- Reads secrets from environment variables (no tokens in the source code)

## Requirements

- Python 3.9+
- [python-telegram-bot](https://python-telegram-bot.org/) v20 or newer (async API)

## Installation

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install "python-telegram-bot>=20.0"
```

## Setup

### 1. Create the bot

1. Open Telegram and talk to [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the steps.
3. Copy the **bot token** BotFather gives you.

### 2. Find your chat ID

Send any message to a bot such as [@userinfobot](https://t.me/userinfobot) (or [@RawDataBot](https://t.me/RawDataBot)) and copy your numeric ID.

> **Important:** open a conversation with your new bot and press **Start** at least once. Telegram bots cannot message you until you have started them.

### 3. Set the environment variables

The bot reads its configuration from two environment variables and exits with an error message if either is missing.

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Token from BotFather |
| `YOUR_CHAT_ID` | Your numeric Telegram chat ID |

**Linux / macOS**

```bash
export BOT_TOKEN="your-bot-token"
export YOUR_CHAT_ID="your-numeric-chat-id"
```

**Windows (PowerShell)**

```powershell
$env:BOT_TOKEN="your-bot-token"
$env:YOUR_CHAT_ID="your-numeric-chat-id"
```

## Usage

```bash
python bot.py
```

You should see `Bot is starting...` in the console. Anyone who sends a message to your bot will have it forwarded to your chat:

```
📩 New message from Jane Doe (@janedoe, id: 123456789):

Hello, I have a question about the course.
```

The sender receives: `✅ Your message has been received!`

## How it works

| Part | Role |
|------|------|
| `Application.builder().token(...)` | Creates the bot application |
| `MessageHandler(filters.ALL & ~filters.COMMAND, forward_message)` | Catches every non-command message |
| `sender_label()` | Builds the sender header (name, username, ID) |
| `forward_message()` | Detects the message type and re-sends it to `YOUR_CHAT_ID` with sender info |
| `application.run_polling()` | Starts long polling to receive updates |

## Supported message types

| Type | Forwarded as |
|------|--------------|
| Text | Text message with sender header |
| Photo | Highest-resolution photo with caption |
| Document | File with caption |
| Voice | Voice message with caption |
| Video | Video with caption |
| Audio | Audio file with caption |
| Video note | Header message, then the video note |
| Sticker | Header message, then the sticker |

Any other type (locations, contacts, polls, etc.) is not forwarded, and the sender is told it isn't supported. To add more, create another `elif message.<type>:` branch following the same pattern.

## Known limitations

- There is no reply feature: you see the message but cannot answer through the bot.
- Messages are forwarded one at a time. Albums (several photos sent together) arrive as separate messages.
- Runs with polling only (no webhook setup).
- Anyone can message the bot, and there is no spam protection or rate limiting.

## Security notes

- **Keep your bot token secret.** Anyone with it can control your bot. If it has been exposed (pasted publicly, committed to GitHub, shared in a chat), revoke it immediately via BotFather (`/revoke`) and generate a new one.
- Never hardcode the token in the source. If you use a `.env` file, add it to `.gitignore`.
- The `httpx` logger is set to warning level because its request logs include the bot token in the URL.
- Treat forwarded content (links, files) with caution, since it comes from anyone.

