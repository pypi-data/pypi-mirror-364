#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Chinese Translator
High-performance Chinese to English translation tool with multi-threading and batch processing
"""

__version__ = "1.0.0"
__author__ = "Enhanced Chinese Translator Team"
__email__ = "support@enhanced-translator.com"
__description__ = "High-performance Chinese to English translation tool with multi-threading and batch processing"

from .translator import EnhancedChineseTranslator

__all__ = [
    "EnhancedChineseTranslator",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]