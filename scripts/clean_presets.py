#!/usr/bin/env python3
"""Script to clean and categorize preset files."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from data_processing import clean_presets

if __name__ == "__main__":
    clean_presets()