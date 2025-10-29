"""Preset qualification and sorting module."""

import os
import csv
import shutil
import re
from pathlib import Path
from typing import Dict, List, Optional

from ..config import config
from ..utils import get_logger


class PresetSorter:
    """Handles sorting and renaming presets based on analysis results."""

    def __init__(self):
        """Initialize the preset sorter."""
        self.logger = get_logger('preset_sorter')
        self.preview_folder = config.get_path('paths.preview_folder')
        self.clean_preset_folder = config.get_path('paths.clean_preset_folder')
        self.analysis_file = config.get_path('paths.analysis_results')
        self.output_base = config.get_path('paths.output_dir')

        # Column indices in the analysis CSV
        self.column_indices = {
            "filename": 0,    # Column A
            "score": 13,      # Column N (The 1-5 score)
            "attr1": 14,      # Column O
            "attr2": 15,      # Column P
            "attr3": 16,      # Column Q
            "attr4": 17,      # Column R
            "attr5": 18,      # Column S
            "attr6": 19       # Column T
        }

    def sanitize_tag(self, tag: str) -> str:
        """Clean up an attribute tag to be filename-safe.

        Args:
            tag: Raw attribute tag

        Returns:
            Sanitized tag
        """
        if not tag:
            return "N_A"
        # Replace spaces or slashes with underscore
        safe_tag = re.sub(r'[\s/]+', '_', tag)
        # Remove other unsafe characters
        safe_tag = re.sub(r'[^a-zA-Z0-9_.-]', '', safe_tag)
        return safe_tag

    def build_preset_lookup(self, folder_path: Path) -> Optional[Dict[str, str]]:
        """Create a lookup map of presets in the clean folder.

        Args:
            folder_path: Path to clean preset folder

        Returns:
            Dictionary mapping base filenames to full filenames, or None if error
        """
        lookup = {}
        try:
            for filename in os.listdir(folder_path):
                if filename.startswith('.'):
                    continue
                base_name = Path(filename).stem
                lookup[base_name] = filename
        except IOError as e:
            self.logger.error(f"Could not read clean preset folder: {e}")
            return None
        return lookup

    def sort_and_rename(self) -> None:
        """Sort presets by score and rename using attributes."""
        self.logger.info("Starting preset sorting and renaming")

        # Create output folders (1-5)
        for i in range(1, 6):
            (self.output_base / str(i)).mkdir(parents=True, exist_ok=True)

        # Build preset lookup
        preset_lookup = self.build_preset_lookup(self.clean_preset_folder)
        if preset_lookup is None:
            return

        self.logger.info(f"Found {len(preset_lookup)} clean presets")

        processed_count = 0
        error_count = 0

        # Read and process analysis CSV
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                # Skip header
                next(reader, None)

                for row in reader:
                    try:
                        # Extract data from row
                        audio_filename = row[self.column_indices["filename"]]
                        if not audio_filename or not audio_filename.endswith('.wav'):
                            continue

                        score_str = row[self.column_indices["score"]]
                        score = int(float(score_str))

                        if score not in [1, 2, 3, 4, 5]:
                            self.logger.warning(f"Skipping '{audio_filename}'. Invalid score '{score}'.")
                            error_count += 1
                            continue

                        # Get attributes
                        attr1 = self.sanitize_tag(row[self.column_indices["attr1"]])
                        attr2 = self.sanitize_tag(row[self.column_indices["attr2"]])
                        attr3 = self.sanitize_tag(row[self.column_indices["attr3"]])
                        attr4 = self.sanitize_tag(row[self.column_indices["attr4"]])
                        attr5 = self.sanitize_tag(row[self.column_indices["attr5"]])
                        attr6 = self.sanitize_tag(row[self.column_indices["attr6"]])

                    except (IndexError, ValueError) as e:
                        self.logger.warning(f"Skipping row. Could not read data: {e}")
                        error_count += 1
                        continue

                    # Find source files
                    source_audio_path = self.preview_folder / audio_filename

                    # Get base filename for preset lookup
                    base_with_preset_ext = Path(audio_filename).stem
                    base_filename = Path(base_with_preset_ext).stem

                    # Find preset file
                    preset_filename = preset_lookup.get(base_filename)
                    source_preset_path = None
                    preset_extension = ".fxp"  # Default

                    if preset_filename:
                        source_preset_path = self.clean_preset_folder / preset_filename
                        preset_extension = Path(preset_filename).suffix

                    # Build new filenames using attributes only
                    new_base_name = f"{attr1}_{attr2}_{attr3}_{attr4}_{attr5}_{attr6}"
                    new_audio_filename = new_base_name + ".wav"
                    new_preset_filename = new_base_name + preset_extension

                    # Define destination paths
                    dest_folder = self.output_base / str(score)
                    dest_audio_path = dest_folder / new_audio_filename
                    dest_preset_path = dest_folder / new_preset_filename

                    # Copy audio file
                    if source_audio_path.exists():
                        shutil.copy2(source_audio_path, dest_audio_path)
                        processed_count += 1
                    else:
                        self.logger.warning(f"Audio file not found: {source_audio_path}")
                        error_count += 1

                    # Copy preset file
                    if source_preset_path and source_preset_path.exists():
                        shutil.copy2(source_preset_path, dest_preset_path)
                    else:
                        if preset_filename:
                            self.logger.warning(f"Preset file not found: {source_preset_path}")
                        else:
                            self.logger.warning(f"No preset file found for base: {base_filename}")
                        error_count += 1

        except IOError as e:
            self.logger.error(f"Could not read CSV file: {e}")
            return

        self.logger.info(f"Successfully processed {processed_count} files")
        if error_count > 0:
            self.logger.warning(f"Encountered {error_count} errors/warnings")
        self.logger.info(f"All files sorted into: {self.output_base}")


def sort_presets():
    """Main function to sort and rename presets."""
    sorter = PresetSorter()
    sorter.sort_and_rename()
    print("✅ Sorting and renaming complete!")


if __name__ == "__main__":
    sort_presets()