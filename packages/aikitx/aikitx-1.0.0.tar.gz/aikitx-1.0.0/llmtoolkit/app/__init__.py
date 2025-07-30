"""
LLM Toolkit - Main Package

This package contains the core components of the LLM Toolkit application.
"""

__version__ = "1.0.0"
__author__ = "LLM Toolkit Team"
__license__ = "MIT"
__description__ = "A comprehensive desktop toolkit for working with Large Language Models"

# Import core components
from . import core

# Backends will be imported and registered when needed to avoid circular imports