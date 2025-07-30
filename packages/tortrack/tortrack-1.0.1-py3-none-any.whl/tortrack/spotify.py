import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from typing import Dict, List, Optional, Union

class SpotifyService:
    """
    Spotify API service with Tor support
    """
    
    def __init__(self, tor_manager=None):
        self.tor_manager = tor_manager
        self.logger = logging.getLogger(__name__)
        
        # get credentials from environment or use defaults
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        
        if not self.client_id or not self.client_secret:
            self.logger.warning("Spotify credentials not found in environment")
            self.logger.info("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to enable Spotify API")
        
        self.sp = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Spotify client with optional Tor proxy"""
        try:
            if not self.client_id or not self.client_secret:
                return
            
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # use Tor session if available
            session = None
            if self.tor_manager and self.tor_manager.is_running:
                session = self.tor_manager.get_session()
                self.logger.debug("Using Tor proxy for Spotify API")
            
            self.sp = spotipy.Spotify(
                auth_manager=auth_manager,
                requests_session=session,
                requests_timeout=15
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup Spotify client: {e}")
            self.sp = None
    
    async def get_track_info(self, spotify_url: str) -> Optional[Union[Dict, List]]:
        """
        Get track information from Spotify URL
        Works with track, album, and playlist URLs
        """
        if not self.sp:
            self.logger.error("Spotify client not available")
            return None
        
        try:
            # extract ID from URL
            url_parts = spotify_url.split('/')
            if len(url_parts) < 2:
                return None
            
            track_type = url_parts[-2] 
            track_id = url_parts[-1].split('?')[0]
            
            if track_type == 'track':
                return await self._get_single_track(track_id)
            elif track_type == 'album':
                return await self._get_album_tracks(track_id)
            elif track_type == 'playlist':
                return await self._get_playlist_tracks(track_id)
            else:
                self.logger.error(f"Unsupported URL type: {track_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing Spotify URL {spotify_url}: {e}")
            return None
    
    async def _get_single_track(self, track_id: str) -> Optional[Dict]:
        """Get single track info"""
        try:
            track = self.sp.track(track_id)
            return self._format_track_info(track)
        except Exception as e:
            self.logger.error(f"Error getting track {track_id}: {e}")
            return None
    
    async def _get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from album"""
        try:
            album = self.sp.album(album_id)
            tracks = []
            
            for track in album['tracks']['items']:
                # add album info to track
                track['album'] = {
                    'name': album['name'],
                    'images': album['images']
                }
                tracks.append(self._format_track_info(track))
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error getting album {album_id}: {e}")
            return []
    
    async def _get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from playlist"""
        try:
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        tracks.append(self._format_track_info(item['track']))
                
                # handle pagination
                results = self.sp.next(results) if results['next'] else None
            
            return tracks
        except Exception as e:
            self.logger.error(f"Error getting playlist {playlist_id}: {e}")
            return []
    
    def _format_track_info(self, track: Dict) -> Dict:
        """Format track info into standard format"""
        try:
            return {
                "id": track.get('id', ''),
                "name": track.get('name', 'Unknown Title'),
                "artist": track['artists'][0]['name'] if track.get('artists') else 'Unknown Artist',
                "album": track.get('album', {}).get('name', 'Unknown Album'),
                "duration_ms": track.get('duration_ms', 0),
                "cover_url": (
                    track.get('album', {}).get('images', [{}])[0].get('url')
                    if track.get('album', {}).get('images') else None
                ),
                "spotify_url": f"https://open.spotify.com/track/{track.get('id', '')}"
            }
        except Exception as e:
            self.logger.error(f"Error formatting track info: {e}")
            return {
                "id": "",
                "name": "Unknown Title",
                "artist": "Unknown Artist",
                "album": "Unknown Album",
                "duration_ms": 0,
                "cover_url": None,
                "spotify_url": ""
            }