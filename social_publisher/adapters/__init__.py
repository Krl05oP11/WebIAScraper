"""
Adaptadores para diferentes plataformas de redes sociales
"""
from .base import SocialMediaAdapter, PostContent, PostResult
from .linkedin import LinkedInAdapter
from .twitter import TwitterAdapter
from .bluesky import BlueskyAdapter
from .telegram import TelegramAdapter

__all__ = [
    'SocialMediaAdapter',
    'PostContent',
    'PostResult',
    'LinkedInAdapter',
    'TwitterAdapter',
    'BlueskyAdapter',
    'TelegramAdapter'
]
