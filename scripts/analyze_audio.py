#!/usr/bin/env python3
"""Script to analyze audio previews and generate qualification data."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from audio_analysis import analyze_audio

if __name__ == "__main__":
    analyze_audio()