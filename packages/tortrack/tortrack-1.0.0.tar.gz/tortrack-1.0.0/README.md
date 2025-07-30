# 🎵 TorTrack

**Simple Telegram Bot for Anonymous Music Downloads**

TorTrack is a Python package that lets you run your own Telegram music download bot with built-in Tor anonymity. Just provide a bot token and you're ready to go!

## ⚡ Quick Start

### Installation
```bash
pip install tortrack
```

### Basic Usage
```python
from tortrack import TelegramBot

# That's it! Just give it your bot token
bot = TelegramBot("YOUR_BOT_TOKEN")
bot.run()
```

### Command Line
```bash
# Start with Tor anonymity
tortrack YOUR_BOT_TOKEN

# Start without Tor (not recommended)
tortrack YOUR_BOT_TOKEN --no-tor
```

## 🚀 Features

- **One-line setup** - Just provide your bot token
- **Tor anonymity** - Built-in Tor proxy for anonymous downloads
- **Multiple sources** - Downloads from YouTube, SoundCloud, and more
- **Smart archiving** - Avoids re-downloading the same tracks
- **User limits** - Built-in rate limiting (5 downloads/day for free users)
- **High quality** - 192kbps MP3 downloads
- **Playlist support** - Handles Spotify tracks, albums, and playlists

## 📋 Requirements

- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- MongoDB (optional, for user limits and archiving)
- Tor (optional, for anonymity)

## 🔧 Setup

### 1. Get Bot Token
Message [@BotFather](https://t.me/BotFather) on Telegram:
```
/newbot
YourBotName
yourbotusername_bot
```

### 2. Get Spotify Credentials (Optional)
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create new app
3. Get Client ID and Secret

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### 3. Install Tor (For Anonymity)
```bash
# Ubuntu/Debian
sudo apt install tor

# macOS
brew install tor

# Windows
# Download from https://www.torproject.org/
```

### 4. Start Your Bot
```bash
tortrack YOUR_BOT_TOKEN_HERE
```

## 💻 Advanced Usage

### Custom Configuration
```python
from tortrack import TelegramBot

bot = TelegramBot(
    token="YOUR_BOT_TOKEN",
    use_tor=True,  # Enable Tor anonymity
    mongo_uri="mongodb://localhost:27017/mybot"
)

bot.run()
```

### Library Usage
```python
from tortrack import TelegramBot, TorManager

# Advanced setup with custom Tor configuration
tor_manager = TorManager(socks_port=9050, control_port=9051)
await tor_manager.start()

bot = TelegramBot("YOUR_TOKEN", use_tor=False)
# Use your custom tor_manager instead
```

### Environment Variables
```bash
# Spotify API (optional but recommended)
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"

# MongoDB (optional)
export MONGO_URI="mongodb://localhost:27017/tortrack"
```

## 🎯 Supported Links

Your bot will handle these Spotify URLs:
- `https://open.spotify.com/track/...` - Single tracks
- `https://open.spotify.com/album/...` - Full albums  
- `https://open.spotify.com/playlist/...` - Playlists

## 🛡️ Security & Anonymity

TorTrack uses Tor to:
- Hide your server's IP address
- Prevent rate limiting and IP blocks
- Protect against geographic restrictions
- Maintain anonymity while downloading

**Without Tor:** Your server IP is visible to download sources and may get blocked.

**With Tor:** All traffic goes through Tor network for complete anonymity.

## 📊 Bot Commands

Users can interact with your bot using:
- `/start` - Welcome message
- `/help` - Usage instructions  
- `/stats` - Download statistics
- Send any Spotify link to download

## 🔧 Deployment

### Local Development
```bash
git clone https://github.com/MohammadHNdev/tortrack.git
cd tortrack
pip install -e .
python -m tortrack YOUR_TOKEN
```

### Docker (Coming Soon)
```bash
docker run -e BOT_TOKEN=your_token tortrack/tortrack
```

### Cloud Deployment
Works on any Python hosting platform:
- Railway
- Heroku
- DigitalOcean
- AWS Lambda
- Google Cloud Run

## 🚨 Important Notes

1. **Legal:** Only download music you have rights to
2. **Rate Limits:** Built-in limits prevent abuse
3. **Resources:** Downloads use temporary storage
4. **Tor Setup:** Tor must be installed for anonymity features

## 📝 License

MIT License - Use it however you want!

## 🤝 Contributing

Found a bug? Want a feature? Open an issue or PR!

## 📞 Support

- 🐛 [Report Issues](https://github.com/MohammadHNdev/tortrack/issues)
- 💬 [Discussions](https://github.com/MohammadHNdev/tortrack/discussions)
- 📧 Email: hosein.norozi434@gmail.com

---

**Made with ❤️ by [Mohammad Hossein Norouzi](https://github.com/MohammadHNdev)**