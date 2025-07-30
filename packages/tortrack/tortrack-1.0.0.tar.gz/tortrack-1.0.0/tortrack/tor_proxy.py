import asyncio
import logging
import socket
import socks
import requests
import random
from stem import Signal
from stem.control import Controller
import subprocess
import time
import os

class TorManager:
    """
    Handles Tor proxy management for anonymous connections
    """
    
    def __init__(self, socks_port: int = 9050, control_port: int = 9051):
        self.socks_port = socks_port
        self.control_port = control_port
        self.tor_process = None
        self.is_running = False
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start Tor service"""
        try:
            # check if tor is already running
            if await self._is_tor_running():
                self.logger.info("Tor is already running")
                self.is_running = True
                return True
            
            # try to start tor
            self.logger.info("Starting Tor service...")
            self.tor_process = subprocess.Popen([
                'tor',
                '--SocksPort', str(self.socks_port),
                '--ControlPort', str(self.control_port),
                '--CookieAuthentication', '0',
                '--HashedControlPassword', '',
                '--DataDirectory', '/tmp/tor_data'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # wait for tor to start
            for i in range(30):  # wait up to 30 seconds
                if await self._is_tor_running():
                    self.is_running = True
                    self.logger.info(f"Tor started successfully on port {self.socks_port}")
                    await self._new_identity()  # get fresh identity
                    return True
                await asyncio.sleep(1)
            
            raise Exception("Tor failed to start within 30 seconds")
            
        except Exception as e:
            self.logger.warning(f"Tor setup failed: {e}")
            self.logger.info("Falling back to direct connection")
            return False
    
    async def stop(self):
        """Stop Tor service"""
        try:
            if self.tor_process:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
            self.is_running = False
            self.logger.info("Tor stopped")
        except Exception as e:
            self.logger.error(f"Error stopping Tor: {e}")
    
    async def _is_tor_running(self):
        """Check if Tor is accessible"""
        try:
            sock = socket.socket()
            result = sock.connect_ex(('127.0.0.1', self.socks_port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def _new_identity(self):
        """Get new Tor identity for fresh IP"""
        try:
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                await asyncio.sleep(2)  # wait for new circuit
                self.logger.debug("New Tor identity acquired")
        except Exception as e:
            self.logger.debug(f"Could not get new identity: {e}")
    
    def get_session(self):
        """Get requests session with Tor proxy configured"""
        session = requests.Session()
        
        if self.is_running:
            # configure SOCKS proxy
            session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            
            # setup socks for other libraries
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.socks_port)
            socket.socket = socks.socksocket
        
        return session
    
    async def rotate_identity(self):
        """Rotate to new Tor identity - useful for avoiding rate limits"""
        if self.is_running:
            await self._new_identity()
            self.logger.info("Identity rotated for fresh anonymity")
        
    def get_current_ip(self):
        """Get current external IP - useful for debugging"""
        try:
            session = self.get_session()
            response = session.get('https://httpbin.org/ip', timeout=10)
            return response.json().get('origin', 'Unknown')
        except Exception as e:
            self.logger.error(f"Could not get IP: {e}")
            return "Unknown"