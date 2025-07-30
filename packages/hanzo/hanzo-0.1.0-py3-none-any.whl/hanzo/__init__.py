"""Hanzo AI CLI - Unified CLI for Local, Private, Free AI Infrastructure.

This package provides the 'hanzo' command which is a wrapper around hanzo-cli.
"""

__version__ = "0.1.0"

# Re-export everything from hanzo_cli if it's installed
try:
    from hanzo_cli import *
except ImportError:
    pass