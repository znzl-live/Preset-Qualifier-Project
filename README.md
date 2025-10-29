# Preset-Qualifier-Project

This project is made to generate and qualify based on defined criteria.

***

## Installation

This project relies on **Python** for data processing and **REAPER** for interacting with VST presets and rendering audio.

1.  **Install Python:**
    * It's highly recommended to use a Python version manager like `pyenv` to install a compatible version (e.g., **Python 3.11** or **3.12**, as newer versions may have compatibility issues with audio libraries).
    * **On macOS:** Use Homebrew: `brew install pyenv`, then `pyenv install 3.12.4` (or similar).
2.  **Install REAPER:**
    * Download and install REAPER from [reaper.fm](https://www.reaper.fm).
    * **On macOS (Apple Silicon):** Ensure you download the **native ARM64 version**.
3.  **Configure REAPER for Python:**
    * Open REAPER > Options > Preferences > Plug-ins > ReaScript.
    * Enable Python.
    * You must *manually paste* the full path to your Python installation's dynamic library (`.dylib` on macOS, `.dll` on Windows) into the "Custom path..." field. Browsing for the file usually doesn't work.
        * **macOS Example Path:** `/Library/Frameworks/Python.framework/Versions/3.12/lib/libpython3.12.dylib`
        * You may need to remove the macOS quarantine attribute from this file using the Terminal: `sudo xattr -d com.apple.quarantine /path/to/your/libpython....dylib`
    * Restart REAPER after setting the path.
4.  **Install Python Libraries:**
    * Open your Terminal or Command Prompt.
    * Navigate to this project's directory.
    * If using `pyenv`, set the local version: `pyenv local 3.12.4`
    * Install the required libraries:
        ```bash
        pip install librosa numpy
        ```

***

## Usage

This project uses a semi-automated workflow involving Python scripts and manual steps within REAPER.

**Workflow Overview:**

1.  **Clean & Prepare Data:** Run a Python script to standardize preset filenames and generate initial metadata.
2.  **Setup REAPER Project:** Run a ReaScript inside REAPER to create tracks, load the VST, and add MIDI notes based on the metadata.
3.  **Manual Preset Loading:** Manually step through the REAPER tracks and load the corresponding presets into the VST.
4.  **Render Audio:** Use REAPER's batch rendering (stems) to generate audio previews.
5.  **Analyze Audio:** Run a Python script to analyze the rendered audio previews and generate detailed scores and suggested categories.
6.  **Sort & Rename Files:** Run a final Python script to copy the cleaned presets and audio previews into folders based on their score, renaming them based on specified attributes.

**Step-by-Step:**

1.  **Place Presets:** Put your raw, unsorted VST presets (e.g., `.fxp`, `.serumpreset`) into the `source_folder`.
2.  **Run Cleaning Script:**
    * Open your Terminal.
    * Navigate to the project directory.
    * Run: `python3 file_and_metadata_cleaning.py`
    * This creates the `clean_preset_folder` (with renamed, ASCII-safe preset files) and the initial `metadata.csv`.
3.  **Run REAPER Setup Script:**
    * Open REAPER.
    * Go to Actions > Show action list... > ReaScript: Load...
    * Select and run the `project_setup.py` script.
    * This builds the REAPER project: creates tracks (alphabetically sorted), names them, loads Serum (specified by `VST_NAME` in the script), and adds the correct 4-bar MIDI note (C1 for BASS, C3 otherwise).
4.  **Manually Load Presets in REAPER:**
    * Go to Track 1, open Serum, load the first preset corresponding to the track name.
    * Go to Track 2, open Serum, click the "next preset" arrow/button.
    * Repeat for all tracks.
5.  **Render Stems in REAPER:**
    * Select all the preset tracks (Track 1 to the last preset track).
    * Go to File > Render...
    * Set **Source** to **"Selected tracks (stems)"**.
    * Set **Directory** to the `preview_folder`.
    * Ensure **"Mute master"** and **"Create subdirectory for render"** are **UNCHECKED**.
    * Click **"Render X files"**.
6.  **Run Analysis Script:**
    * Open your Terminal.
    * Navigate to the project directory.
    * Run: `python3 analyze_previews.py`
    * This reads the `.wav` files in `preview_folder`, analyzes them, and creates the `preset_analysis_results.csv` file with detailed scores.
7.  **Run Sorting & Renaming Script:**
    * Edit the `sort_and_rename.py` script to ensure the `COLUMN_INDICES` dictionary correctly maps to the attribute columns (O, P, Q, R, S, T, etc.) in your `final_analysis.csv`.
    * Open your Terminal.
    * Navigate to the project directory.
    * Run: `python3 sort_and_rename.py`
    * This reads `final_analysis.csv`, finds the score (Column N) and attributes (Columns O-T), then copies the corresponding `.wav` from `preview_folder` and `.fxp`/`.serumpreset` from `clean_preset_folder` into the appropriate subfolder (1-5) within `alignment_score_attrs_only_v2`, renaming the files using only the attributes (e.g., `BASS_Sub_Dark_Short_Punchy_Mono.wav`). **Warning:** Files with identical scores and attributes will overwrite each other.

***

## Contributing

Contributions are welcome! Whether you're fixing bugs, improving documentation, suggesting new features, or submitting code, your help is appreciated.

Here are a few ways you can contribute:

Reporting Issues: If you find a bug or have a suggestion, please open an issue on the GitHub repository. Provide as much detail as possible, including steps to reproduce the bug or a clear description of the feature request.

Submitting Code Changes:

Fork the repository to your own GitHub account.

Create a new branch for your changes (e.g., git checkout -b feature/add-new-analysis or bugfix/fix-midi-note).

Make your changes and commit them with clear messages.

Push your branch to your fork (git push origin feature/your-feature).

Open a Pull Request (PR) from your branch to the main repository's main branch.

Clearly describe the changes you've made in the PR description.

Improving Documentation: If you find parts of the README or code comments unclear, feel free to suggest improvements by opening an issue or submitting a PR.

When submitting code, please try to follow the existing code style and ensure your changes work as expected. Thank you for helping improve this project!

***

## License

This project is licensed under the MIT License.
Copyright (c) 2025 znzl.live.

See the [LICENSE](LICENSE) file for full details.
