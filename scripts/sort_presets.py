#!/usr/bin/env python3
"""Script to sort and rename presets based on analysis results."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from qualification import sort_presets

if __name__ == "__main__":
    sort_presets()