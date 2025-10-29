"""Preset file cleaning and categorization module."""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from ..config import config
from ..utils import get_logger


class PresetCleaner:
    """Handles cleaning and categorizing preset files."""

    def __init__(self):
        """Initialize the preset cleaner with configuration."""
        self.logger = get_logger('preset_cleaner')
        self.source_folder = config.get_path('paths.source_folder')
        self.clean_folder = config.get_path('paths.clean_preset_folder')
        self.metadata_file = config.get_path('paths.metadata_file')
        self.supported_extensions = config.get('vst.supported_extensions', ['.fxp', '.serumpreset'])
        self.categories = config.get('categories', {})
        self.default_category = config.get('default_category', 'UNKNOWN')
        self.default_subcategory = config.get('default_subcategory', 'UNTITLED')

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be ASCII-safe and filesystem-friendly.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove file extension for processing
        name_base = Path(filename).stem

        # Force ASCII: Remove all non-ASCII characters
        sanitized = name_base.encode('ascii', 'ignore').decode('ascii')

        # Clean up: Replace spaces and other unsafe chars with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]+', '_', sanitized)

        # Clean up double underscores
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')

        return sanitized

    def categorize_preset(self, filename: str) -> Tuple[str, str, int, int]:
        """Categorize a preset based on its filename.

        Args:
            filename: Preset filename

        Returns:
            Tuple of (category, subcategory, note, preview_length_ms)
        """
        clean_name = re.sub(r'[_\-\s]+', ' ', filename.lower())
        clean_name = re.sub(r'(\.fxp|\.serumpreset)', '', clean_name).strip()

        # Check against each category
        for category, settings in self.categories.items():
            keywords = settings.get('keywords', [])
            if any(keyword in clean_name for keyword in keywords):
                subcategory = settings.get('subcategory', self.default_subcategory)
                note = settings.get('note', config.get('audio.other_note', 60))
                preview_length = settings.get('preview_length_ms', config.get('audio.preview_length_ms', 5000))
                return category, subcategory, note, preview_length

        # Default category
        return (self.default_category,
                self.default_subcategory,
                config.get('audio.other_note', 60),
                config.get('audio.preview_length_ms', 5000))

    def process_presets(self) -> List[Dict]:
        """Process all presets in the source folder.

        Returns:
            List of metadata dictionaries for processed presets
        """
        self.logger.info(f"Starting preset processing from: {self.source_folder}")

        # Ensure output directories exist
        self.clean_folder.mkdir(parents=True, exist_ok=True)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        metadata_rows = []
        processed_count = 0

        # Walk through source folder
        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if not any(file.lower().endswith(ext) for ext in self.supported_extensions):
                    continue

                old_path = Path(root) / file

                # Categorize the preset
                category, subcategory, note, preview_length = self.categorize_preset(file)

                # Sanitize filename
                sanitized_name = self.sanitize_filename(file)
                file_extension = Path(file).suffix

                # Create new filename
                new_filename = f"{category}_{subcategory}_{sanitized_name}{file_extension}"
                new_filename = re.sub(r'_+', '_', new_filename)  # Clean double underscores

                new_path = self.clean_folder / new_filename

                # Copy file
                try:
                    shutil.copy2(old_path, new_path)
                    self.logger.debug(f"Copied: {old_path} -> {new_path}")
                except IOError as e:
                    self.logger.error(f"Failed to copy {old_path}: {e}")
                    continue

                # Generate metadata
                metadata_rows.append({
                    "filename": new_filename,
                    "category": category,
                    "subcategory": subcategory,
                    "suggested_preview_length_ms": preview_length,
                    "suggested_note": note
                })

                processed_count += 1

        self.logger.info(f"Successfully processed {processed_count} presets")
        return metadata_rows

    def save_metadata(self, metadata_rows: List[Dict]) -> None:
        """Save metadata to CSV file.

        Args:
            metadata_rows: List of metadata dictionaries
        """
        import csv

        fieldnames = ["filename", "category", "subcategory", "suggested_preview_length_ms", "suggested_note"]

        with open(self.metadata_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata_rows)

        self.logger.info(f"Metadata saved to: {self.metadata_file}")


def clean_presets():
    """Main function to clean and categorize presets."""
    cleaner = PresetCleaner()
    metadata = cleaner.process_presets()
    cleaner.save_metadata(metadata)
    print(f"✅ Processing complete! Cleaned presets saved to: {cleaner.clean_folder}")


if __name__ == "__main__":
    clean_presets()