import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os

from .spotify import SpotifyService
from .downloader import MusicDownloader

# router for all message handlers
router = Router()

# global services - will be set by setup_handlers
db = None
spotify_service = None
downloader = None
logger = logging.getLogger(__name__)

# daily download limit for non-VIP users
DAILY_LIMIT = 5

def setup_handlers(dp, database, tor_manager):
    """Setup message handlers with services"""
    global db, spotify_service, downloader
    
    db = database
    spotify_service = SpotifyService(tor_manager)
    downloader = MusicDownloader(tor_manager)
    
    # register router
    dp.include_router(router)
    logger.info("Message handlers initialized")

@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome message"""
    welcome_text = """
🎵 <b>TorTrack Music Bot</b>

Welcome! Send me a Spotify link and I'll download it for you.

<b>Supported links:</b>
• Spotify tracks
• Spotify albums  
• Spotify playlists

<b>Features:</b>
• Anonymous downloads via Tor
• High quality MP3 (192kbps)
• Fast and reliable

Just send me a link to get started! 🚀
    """
    await message.answer(welcome_text)

@router.message(Command("help"))
async def help_command(message: Message):
    """Help message"""
    help_text = """
🆘 <b>How to use TorTrack:</b>

1️⃣ Send me a Spotify link
2️⃣ Wait for download to complete
3️⃣ Enjoy your music!

<b>Supported formats:</b>
• https://open.spotify.com/track/...
• https://open.spotify.com/album/...
• https://open.spotify.com/playlist/...

<b>Limits:</b>
• Free users: 5 downloads per day
• VIP users: Unlimited downloads

<b>Commands:</b>
/start - Welcome message
/help - This help message
/stats - Your download statistics
    """
    await message.answer(help_text)

@router.message(Command("stats"))
async def stats_command(message: Message):
    """User statistics"""
    try:
        user_id = message.from_user.id
        downloads_today = await db.get_user_downloads_today(user_id) if db else 0
        is_vip = await db.is_vip_user(user_id) if db else False
        
        status = "VIP 👑" if is_vip else "Free"
        limit_text = "Unlimited" if is_vip else f"{downloads_today}/{DAILY_LIMIT}"
        
        stats_text = f"""
📊 <b>Your Statistics</b>

👤 Status: {status}
📥 Downloads today: {limit_text}
🔄 Remaining: {'∞' if is_vip else max(0, DAILY_LIMIT - downloads_today)}

🧅 Tor anonymity: {'Enabled ✅' if downloader.tor_manager and downloader.tor_manager.is_running else 'Disabled ❌'}
        """
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await message.answer("❌ Could not get statistics right now")

@router.message(F.text.contains("open.spotify.com"))
async def handle_spotify_link(message: Message):
    """Handle Spotify links"""
    try:
        user_id = message.from_user.id
        spotify_url = message.text.strip()
        
        # check if user has reached daily limit
        if db:
            downloads_today = await db.get_user_downloads_today(user_id)
            is_vip = await db.is_vip_user(user_id)
            
            if not is_vip and downloads_today >= DAILY_LIMIT:
                await message.answer(
                    f"❌ Daily limit reached ({DAILY_LIMIT} downloads)\n"
                    "Try again tomorrow or contact admin for VIP access."
                )
                return
        
        # send processing message
        status_msg = await message.answer("⏳ Processing your request...")
        
        # get track info from Spotify
        track_info = await spotify_service.get_track_info(spotify_url)
        if not track_info:
            await status_msg.edit_text("❌ Could not get track information from Spotify")
            return
        
        # handle single track vs multiple tracks
        if isinstance(track_info, list):
            await handle_multiple_tracks(message, status_msg, track_info, user_id)
        else:
            await handle_single_track(message, status_msg, track_info, user_id)
            
    except Exception as e:
        logger.error(f"Error handling Spotify link: {e}")
        await message.answer("❌ Something went wrong. Please try again.")

async def handle_single_track(message: Message, status_msg: Message, track_info: dict, user_id: int):
    """Handle single track download"""
    try:
        # check if track is already archived
        if db:
            archived_file_id = await db.is_track_archived(track_info['id'])
            if archived_file_id:
                await status_msg.edit_text("📁 Found in archive, sending...")
                try:
                    await message.answer_audio(archived_file_id)
                    await db.increment_user_downloads(user_id)
                    await status_msg.delete()
                    return
                except Exception:
                    # archived file might be invalid, continue with fresh download
                    pass
        
        # update status
        await status_msg.edit_text(f"🎵 Downloading: {track_info['name']} - {track_info['artist']}")
        
        # download the track
        file_path = await downloader.download_track(track_info)
        if not file_path:
            await status_msg.edit_text("❌ Download failed. Please try again.")
            return
        
        # send the audio file
        await status_msg.edit_text("📤 Uploading...")
        
        with open(file_path, 'rb') as audio_file:
            sent_message = await message.answer_audio(
                audio_file,
                title=track_info['name'],
                performer=track_info['artist'],
                caption=f"🎵 {track_info['name']}\n👤 {track_info['artist']}\n💿 {track_info['album']}"
            )
        
        # archive the track and update user stats
        if db:
            await db.archive_track(track_info['id'], sent_message.audio.file_id, track_info)
            await db.increment_user_downloads(user_id)
        
        # cleanup
        downloader.cleanup_file(file_path)
        await status_msg.delete()
        
        logger.info(f"Successfully processed track for user {user_id}: {track_info['name']}")
        
    except Exception as e:
        logger.error(f"Error processing single track: {e}")
        await status_msg.edit_text("❌ Failed to process track")

async def handle_multiple_tracks(message: Message, status_msg: Message, tracks: list, user_id: int):
    """Handle multiple tracks (album/playlist)"""
    try:
        total_tracks = len(tracks)
        
        if total_tracks > 50:
            await status_msg.edit_text("❌ Too many tracks! Limit is 50 tracks per request.")
            return
        
        await status_msg.edit_text(f"📋 Found {total_tracks} tracks. Starting download...")
        
        successful = 0
        failed = 0
        
        for i, track_info in enumerate(tracks, 1):
            try:
                # update progress
                await status_msg.edit_text(
                    f"⏳ Processing {i}/{total_tracks}\n"
                    f"🎵 {track_info['name']} - {track_info['artist']}\n"
                    f"✅ Success: {successful} | ❌ Failed: {failed}"
                )
                
                # check archive first
                if db:
                    archived_file_id = await db.is_track_archived(track_info['id'])
                    if archived_file_id:
                        try:
                            await message.answer_audio(archived_file_id)
                            successful += 1
                            continue
                        except Exception:
                            pass  # archived file invalid, download fresh
                
                # download track
                file_path = await downloader.download_track(track_info)
                if file_path:
                    # send audio
                    with open(file_path, 'rb') as audio_file:
                        sent_message = await message.answer_audio(
                            audio_file,
                            title=track_info['name'],
                            performer=track_info['artist']
                        )
                    
                    # archive
                    if db:
                        await db.archive_track(track_info['id'], sent_message.audio.file_id, track_info)
                    
                    # cleanup
                    downloader.cleanup_file(file_path)
                    successful += 1
                else:
                    failed += 1
                
                # small delay between downloads
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing track {i}: {e}")
                failed += 1
        
        # update user stats
        if db:
            for _ in range(successful):
                await db.increment_user_downloads(user_id)
        
        # final message
        await status_msg.edit_text(
            f"✅ Download complete!\n"
            f"Success: {successful}/{total_tracks}\n" +
            (f"Failed: {failed}" if failed > 0 else "")
        )
        
    except Exception as e:
        logger.error(f"Error processing multiple tracks: {e}")
        await status_msg.edit_text("❌ Failed to process playlist/album")

@router.message()
async def handle_other_messages(message: Message):
    """Handle other messages"""
    await message.answer(
        "🎵 Send me a Spotify link to download music!\n\n"
        "Example: https://open.spotify.com/track/...\n"
        "Use /help for more information."
    )