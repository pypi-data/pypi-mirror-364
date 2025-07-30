"""
TorTrack - Simple Telegram Bot for Music Downloads

A lightweight Python package for running Telegram music download bots
with built-in Tor anonymity support.
"""

from .bot import TelegramBot
from .tor_proxy import TorManager

__version__ = "1.0.0"
__author__ = "Mohammad Hossein Norouzi"

__all__ = ["TelegramBot", "TorManager"]