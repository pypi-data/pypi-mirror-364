#!/usr/bin/env python3
"""
TorTrack CLI - Simple command line interface
"""

import argparse
import os
import sys
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="TorTrack - Simple Telegram Bot for Music Downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tortrack YOUR_BOT_TOKEN                 # Start bot with Tor
  tortrack YOUR_BOT_TOKEN --no-tor        # Start without Tor
  tortrack YOUR_BOT_TOKEN --mongo mongodb://localhost:27017/mydb
  
Get bot token from @BotFather on Telegram.
        """
    )
    
    parser.add_argument(
        "token", 
        help="Telegram bot token from @BotFather"
    )
    
    parser.add_argument(
        "--no-tor", 
        action="store_true",
        help="Disable Tor anonymity (not recommended)"
    )
    
    parser.add_argument(
        "--mongo",
        default="mongodb://localhost:27017/tortrack",
        help="MongoDB connection URI (default: mongodb://localhost:27017/tortrack)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="tortrack 1.0.0"
    )
    
    args = parser.parse_args()
    
    # validate token format
    if not args.token or len(args.token.split(':')) != 2:
        print("❌ Invalid bot token format!")
        print("Get a token from @BotFather on Telegram")
        print("Format should be: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        sys.exit(1)
    
    # check for required dependencies
    try:
        from .bot import TelegramBot
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install tortrack")
        sys.exit(1)
    
    # set environment variables for Spotify (if not already set)
    if not os.getenv('SPOTIFY_CLIENT_ID'):
        print("⚠️  Spotify credentials not found!")
        print("Set these environment variables:")
        print("export SPOTIFY_CLIENT_ID='your_client_id'")
        print("export SPOTIFY_CLIENT_SECRET='your_client_secret'")
        print("Get credentials from: https://developer.spotify.com/dashboard")
        print("\nBot will work without Spotify API but with limited functionality.\n")
    
    # show startup info
    print("🎵 TorTrack Music Bot")
    print("=" * 40)
    print(f"Token: {args.token[:10]}...")
    print(f"Tor: {'Enabled' if not args.no_tor else 'Disabled'}")
    print(f"Database: {args.mongo}")
    print("=" * 40)
    
    # warn about Tor
    if args.no_tor:
        print("⚠️  WARNING: Running without Tor anonymity!")
        print("Your IP address will be visible to download sources.")
        print("Use --no-tor only for testing purposes.\n")
    
    # create and run bot
    try:
        bot = TelegramBot(
            token=args.token,
            use_tor=not args.no_tor,
            mongo_uri=args.mongo
        )
        
        print("🚀 Starting bot...")
        print("Press Ctrl+C to stop")
        print()
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()