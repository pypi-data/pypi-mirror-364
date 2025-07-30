"""
Context Overflow MCP Server

A Model Context Protocol (MCP) server for the Context Overflow Q&A platform.
Provides native tools for Claude Code to interact with programming Q&A content.
"""

__version__ = "1.0.0"
__author__ = "Venkatesh"
__email__ = "venkatesh@contextoverflow.com"

from .server import main

__all__ = ["main"]