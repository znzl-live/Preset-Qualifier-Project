"""Audio analysis module for preset qualification."""

import librosa
import numpy as np
import os
import csv
import glob
from pathlib import Path
from scipy.signal import butter, lfilter
from typing import Dict, List, Optional, Tuple

from ..config import config
from ..utils import get_logger


class AudioAnalyzer:
    """Analyzes audio files and extracts features for preset qualification."""

    def __init__(self):
        """Initialize the audio analyzer."""
        self.logger = get_logger('audio_analyzer')
        self.sample_rate = config.get('audio.sample_rate', 44100)

    def butter_lowpass_filter(self, data: np.ndarray, cutoff: float, sr: int, order: int = 5) -> np.ndarray:
        """Apply low-pass Butterworth filter.

        Args:
            data: Audio data
            cutoff: Cutoff frequency
            sr: Sample rate
            order: Filter order

        Returns:
            Filtered audio data
        """
        nyq = 0.5 * sr
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, data)

    def extract_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract audio features from signal.

        Args:
            y: Audio signal
            sr: Sample rate

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Basic audio properties
        duration_s = librosa.get_duration(y=y, sr=sr)
        features['audiolength'] = duration_s

        # 1. Tonalness & Fundamental Pitch (pyin)
        f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        voiced_f0 = f0[voiced_flag]
        voiced_harm = voiced_prob[voiced_flag]
        features['harmonicity'] = np.mean(voiced_harm) if voiced_harm.size > 0 else 0
        features['fundamental_pitch'] = np.mean(voiced_f0) if voiced_f0.size > 0 else 0

        # 2. Attack Speed (ms)
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='frames', hop_length=128)
        if onsets.size > 0:
            onset_frame = onsets[0]
            env = librosa.feature.rms(y=y, frame_length=256, hop_length=128)[0]
            peak_frame = np.argmax(env[onset_frame:]) + onset_frame
            attack_time_s = librosa.frames_to_time(peak_frame - onset_frame, sr=sr, hop_length=128)
            features['attack_ms'] = attack_time_s * 1000
        else:
            features['attack_ms'] = 0

        # 3. Effective Duration (s)
        intervals = librosa.effects.split(y, top_db=40)
        features['effective_duration_s'] = sum(librosa.frames_to_time(interval[1] - interval[0], sr=sr) for interval in intervals)

        # 4. Brightness (Centroid)
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

        # 5. Bass Presence (Ratio)
        try:
            y_low = self.butter_lowpass_filter(y, 150, sr)
            rms_low = np.mean(librosa.feature.rms(y=y_low))
            rms_total = np.mean(librosa.feature.rms(y=y))
            features['bass_presence_ratio'] = (rms_low / rms_total) if rms_total > 0 else 0
        except Exception:
            features['bass_presence_ratio'] = 0

        # 6. Rhythmic Density (Onsets per Second)
        onsets_sec = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        features['rhythmic_density_ops'] = len(onsets_sec) / duration_s if duration_s > 0 else 0

        # 7. Dynamic Range (Crest Factor in dB)
        peak_amp = np.max(np.abs(y))
        rms_amp = np.mean(librosa.feature.rms(y=y))
        features['dynamic_range_db'] = 20 * np.log10(peak_amp / rms_amp) if rms_amp > 0 else 0

        # 8. Perceived Loudness (RMS in dBFS)
        features['loudness_dbfs'] = librosa.amplitude_to_db(np.mean(librosa.feature.rms(y=y)), ref=1.0)

        # 9. Timbral Complexity (Bandwidth)
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))

        # Additional features
        features['spectral_flatness'] = np.mean(librosa.feature.spectral_flatness(y=y))
        features['rms_energy'] = rms_amp
        features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y=y))
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

        return features

    def diagnose_features(self, features: Dict[str, float]) -> Dict[str, str]:
        """Convert raw features to human-readable diagnoses.

        Args:
            features: Raw feature values

        Returns:
            Dictionary of diagnoses
        """
        diagnoses = {}

        # Tonalness
        h = features.get('harmonicity', 0)
        if h < 0.2:
            diagnoses['diag_tonalness'] = 'Noisy'
        elif h < 0.4:
            diagnoses['diag_tonalness'] = 'Atonal'
        elif h < 0.6:
            diagnoses['diag_tonalness'] = 'Weakly Tonal'
        elif h < 0.8:
            diagnoses['diag_tonalness'] = 'Tonal'
        else:
            diagnoses['diag_tonalness'] = 'Clear Pitch'

        # Fundamental Pitch
        f0 = features.get('fundamental_pitch', 0)
        if f0 > 0:
            diagnoses['diag_pitch'] = librosa.hz_to_note(f0)
        else:
            diagnoses['diag_pitch'] = 'N/A'

        # Attack Speed
        atk = features.get('attack_ms', 0)
        if atk < 5:
            diagnoses['diag_attack'] = 'Click'
        elif atk < 20:
            diagnoses['diag_attack'] = 'Transient'
        elif atk < 50:
            diagnoses['diag_attack'] = 'Pluck'
        elif atk < 200:
            diagnoses['diag_attack'] = 'Soft'
        elif atk < 1000:
            diagnoses['diag_attack'] = 'Pad'
        else:
            diagnoses['diag_attack'] = 'Swell'

        # Effective Duration
        dur = features.get('effective_duration_s', 0)
        if dur < 0.15:
            diagnoses['diag_duration'] = 'Stab'
        elif dur < 0.5:
            diagnoses['diag_duration'] = 'Short'
        elif dur < 2.0:
            diagnoses['diag_duration'] = 'Medium'
        elif dur < 5.0:
            diagnoses['diag_duration'] = 'Long'
        else:
            diagnoses['diag_duration'] = 'Pad/Tail'

        # Brightness
        c = features.get('spectral_centroid', 0)
        if c < 500:
            diagnoses['diag_brightness'] = 'Dark'
        elif c < 1500:
            diagnoses['diag_brightness'] = 'Mellow'
        elif c < 3000:
            diagnoses['diag_brightness'] = 'Present'
        elif c < 5000:
            diagnoses['diag_brightness'] = 'Bright'
        else:
            diagnoses['diag_brightness'] = 'Airy'

        # Bass Presence
        b = features.get('bass_presence_ratio', 0)
        if b < 0.01:
            diagnoses['diag_bass_presence'] = 'No Lows'
        elif b < 0.1:
            diagnoses['diag_bass_presence'] = 'Thin'
        elif b < 0.2:
            diagnoses['diag_bass_presence'] = 'Balanced'
        elif b < 0.35:
            diagnoses['diag_bass_presence'] = 'Full'
        else:
            diagnoses['diag_bass_presence'] = 'Sub-Heavy'

        # Rhythmic Density
        r = features.get('rhythmic_density_ops', 0)
        if r < 0.2:
            diagnoses['diag_rhythm_density'] = 'Sparse'
        elif r < 1.5:
            diagnoses['diag_rhythm_density'] = 'One-Shot'
        elif r < 3.5:
            diagnoses['diag_rhythm_density'] = 'Groove'
        elif r < 7.0:
            diagnoses['diag_rhythm_density'] = 'Roll'
        else:
            diagnoses['diag_rhythm_density'] = 'Dense'

        # Dynamic Range
        dr = features.get('dynamic_range_db', 0)
        if dr < 4:
            diagnoses['diag_dynamic_range'] = 'Sausage'
        elif dr < 8:
            diagnoses['diag_dynamic_range'] = 'Compressed'
        elif dr < 14:
            diagnoses['diag_dynamic_range'] = 'Dynamic'
        elif dr < 20:
            diagnoses['diag_dynamic_range'] = 'Punchy'
        else:
            diagnoses['diag_dynamic_range'] = 'Spiky'

        # Perceived Loudness
        l = features.get('loudness_dbfs', -60)
        if l < -40:
            diagnoses['diag_loudness'] = 'Silent'
        elif l < -25:
            diagnoses['diag_loudness'] = 'Quiet'
        elif l < -12:
            diagnoses['diag_loudness'] = 'Medium'
        elif l < -3:
            diagnoses['diag_loudness'] = 'Loud'
        else:
            diagnoses['diag_loudness'] = 'Clipped'

        # Timbral Complexity
        bw = features.get('spectral_bandwidth', 0)
        if bw < 100:
            diagnoses['diag_timbre'] = 'Pure Tone'
        elif bw < 500:
            diagnoses['diag_timbre'] = 'Simple'
        elif bw < 1500:
            diagnoses['diag_timbre'] = 'Rich'
        elif bw < 3500:
            diagnoses['diag_timbre'] = 'Complex'
        else:
            diagnoses['diag_timbre'] = 'Noisy'

        return diagnoses

    def analyze_folder(self, audio_folder: Path, output_csv: Path) -> None:
        """Analyze all audio files in a folder and save results to CSV.

        Args:
            audio_folder: Path to folder containing audio files
            output_csv: Path to output CSV file
        """
        extensions = ('*.wav', '*.mp3', '*.flac', '*.aif', '*.aiff')
        audio_files = []
        for ext in extensions:
            audio_files.extend(glob.glob(str(audio_folder / ext)))

        if not audio_files:
            self.logger.warning(f"No audio files found in '{audio_folder}'")
            return

        self.logger.info(f"Found {len(audio_files)} audio files. Starting analysis...")

        # Define CSV columns
        header = [
            'filename', 'audiolength',
            # Diagnosis columns
            'diag_tonalness', 'diag_pitch', 'diag_attack', 'diag_duration',
            'diag_brightness', 'diag_bass_presence', 'diag_rhythm_density',
            'diag_dynamic_range', 'diag_loudness', 'diag_timbre',
            # Raw score columns
            'harmonicity', 'fundamental_pitch', 'attack_ms', 'effective_duration_s',
            'spectral_centroid', 'bass_presence_ratio', 'rhythmic_density_ops',
            'dynamic_range_db', 'loudness_dbfs', 'spectral_bandwidth',
            # Other features
            'spectral_flatness', 'rms_energy', 'zero_crossing_rate', 'spectral_rolloff'
        ]

        all_rows_data = []

        for file_path in audio_files:
            filename = Path(file_path).name
            self.logger.info(f"Processing: {filename}")

            try:
                y, sr = librosa.load(file_path, sr=self.sample_rate)

                if y.size == 0:
                    self.logger.warning(f"Skipping empty file: {filename}")
                    continue

                # Extract features
                features_dict = self.extract_features(y, sr)

                # Get diagnoses
                diagnosis_dict = self.diagnose_features(features_dict)

                # Combine data
                row_data = {'filename': filename}
                row_data.update(features_dict)
                row_data.update(diagnosis_dict)

                # Round values for cleaner CSV
                for key, value in row_data.items():
                    if isinstance(value, (float, np.floating)):
                        row_data[key] = round(value, 4)

                all_rows_data.append(row_data)

            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}")
                continue

        # Save to CSV
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows_data)

        self.logger.info(f"Analysis complete! Data saved to {output_csv}")


def analyze_audio():
    """Main function to analyze audio files."""
    analyzer = AudioAnalyzer()
    preview_folder = config.get_path('paths.preview_folder')
    analysis_file = config.get_path('paths.analysis_results')

    analyzer.analyze_folder(preview_folder, analysis_file)


if __name__ == "__main__":
    analyze_audio()