import os
import logging
import shutil
import tempfile
import asyncio
import yt_dlp
from pathlib import Path
from typing import Dict, Optional

class MusicDownloader:
    """
    Downloads music from YouTube with Tor anonymity
    """
    
    def __init__(self, tor_manager=None):
        self.tor_manager = tor_manager
        self.logger = logging.getLogger(__name__)
        
        # setup temp directory
        self.temp_dir = Path(tempfile.gettempdir()) / "tortrack_downloads"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def download_track(self, track_info: Dict) -> Optional[str]:
        """
        Download track and return file path
        """
        if not track_info or not track_info.get('name'):
            self.logger.error("Invalid track info provided")
            return None
        
        # create search query
        query = f"{track_info['name']} {track_info['artist']}"
        self.logger.info(f"Downloading: {query}")
        
        # create unique temp directory for this download
        download_dir = self.temp_dir / f"download_{os.getpid()}_{id(track_info)}"
        download_dir.mkdir(exist_ok=True)
        
        try:
            # setup yt-dlp options
            ydl_opts = self._get_ydl_options(str(download_dir))
            
            # run download in thread to avoid blocking
            file_path = await asyncio.to_thread(
                self._download_with_ytdlp, 
                query, 
                ydl_opts
            )
            
            if file_path and os.path.exists(file_path):
                self.logger.info(f"Download successful: {file_path}")
                return file_path
            else:
                self.logger.error(f"Download failed for: {query}")
                return None
                
        except Exception as e:
            self.logger.error(f"Download error for {query}: {e}")
            return None
        finally:
            # cleanup will be handled by caller
            pass
    
    def _get_ydl_options(self, output_dir: str) -> dict:
        """Get yt-dlp configuration"""
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
        }
        
        # add proxy if Tor is enabled
        if self.tor_manager and self.tor_manager.is_running:
            opts['proxy'] = f'socks5://127.0.0.1:{self.tor_manager.socks_port}'
            self.logger.debug("Using Tor proxy for download")
        
        return opts
    
    def _download_with_ytdlp(self, query: str, ydl_opts: dict) -> str | None:
        """
        Actual download using yt-dlp (runs in thread)
        """
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # search for the track
                search_query = f"ytsearch1:{query}"
                
                # extract info first to get the filename
                info = ydl.extract_info(search_query, download=False)
                if not info or 'entries' not in info or not info['entries']:
                    return None
                
                # download the track
                ydl.download([search_query])
                
                # find the downloaded file
                output_dir = Path(ydl_opts['outtmpl']).parent
                
                # look for mp3 files in output directory
                mp3_files = list(output_dir.glob('*.mp3'))
                if mp3_files:
                    return str(mp3_files[0])  # return first mp3 found
                
                # if no mp3, look for any audio files
                audio_files = []
                for ext in ['*.mp3', '*.m4a', '*.webm', '*.opus']:
                    audio_files.extend(output_dir.glob(ext))
                
                if audio_files:
                    return str(audio_files[0])
                
                return None
                
        except Exception as e:
            self.logger.error(f"yt-dlp download error: {e}")
            return None
    
    def cleanup_file(self, file_path: str):
        """Clean up downloaded file and its directory"""
        try:
            if file_path and os.path.exists(file_path):
                # remove the file
                os.remove(file_path)
                
                # try to remove the directory if it's empty
                parent_dir = os.path.dirname(file_path)
                if parent_dir and parent_dir != str(self.temp_dir):
                    try:
                        os.rmdir(parent_dir)
                    except OSError:
                        pass  # directory not empty, that's ok
                        
        except Exception as e:
            self.logger.debug(f"Cleanup error: {e}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files"""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.temp_dir.rglob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):  # convert hours to seconds
                        try:
                            file_path.unlink()
                            self.logger.debug(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            self.logger.debug(f"Could not clean file {file_path}: {e}")
            
            # try to remove empty directories
            for dir_path in self.temp_dir.rglob('*'):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                    except Exception:
                        pass
                        
        except Exception as e:
            self.logger.debug(f"Cleanup error: {e}")