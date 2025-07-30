"""Media Agent MCP Server - A Model Context Protocol server for media processing."""

from . import ai_models, media_selectors, storage, video
from .server import main

__version__ = "0.1.0"
__all__ = ['ai_models', 'selectors', 'storage', 'video', 'main']