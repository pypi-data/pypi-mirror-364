#!/usr/bin/env python3
"""
AUTO-blogger - AI-Powered WordPress Automation Tool

A comprehensive WordPress automation tool that combines AI content generation,
Getty Images integration, and comprehensive SEO optimization.

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW/AUTO-blogger
"""

__version__ = "1.0.0"
__author__ = "AryanVBW"
__email__ = "AryanVBW@gmail.com"
__description__ = "Automated WordPress Blog Posting Tool with AI Integration"
__url__ = "https://github.com/AryanVBW/AUTO-blogger"

# Import main components for easy access
try:
    from .gui_blogger import BlogAutomationGUI, main
    from .automation_engine import BlogAutomationEngine
    from .log_manager import *
    from .css_selector_extractor import CSSelectorExtractor
except ImportError as e:
    # Handle import errors gracefully
    import warnings
    warnings.warn(f"Some components could not be imported: {e}")
    
    # Define fallback main function
    def main():
        """Fallback main function"""
        try:
            from .gui_blogger import main as gui_main
            gui_main()
        except ImportError:
            print("Error: Could not import GUI components. Please ensure all dependencies are installed.")
            print("Run: pip install auto-blogger[dev] to install all dependencies.")
            return 1
        return 0

# Package metadata
__all__ = [
    "BlogAutomationGUI",
    "BlogAutomationEngine", 
    "CSSelectorExtractor",
    "main",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__"
]

# Entry point for console scripts
def cli_main():
    """Console script entry point"""
    import sys
    sys.exit(main())