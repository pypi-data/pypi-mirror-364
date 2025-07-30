"""
Main entry point for running LLM Toolkit as a module.

This allows users to run the application using:
    python -m llmtoolkit
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())