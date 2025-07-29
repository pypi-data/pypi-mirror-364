"""
AI-powered changelog generator with smart caching and async processing.

A high-performance command-line tool that generates beautiful changelogs from git commit history
using the Claude API. Features include smart caching, async processing, and GitHub integration.
"""

__version__ = "1.0.0"
__author__ = "Anant Duggal"
__email__ = "aduggal@uwaterloo.ca"

# Import the main function from the enhanced generator
from .changelog_generator_enhanced import main

__all__ = ["main"] 