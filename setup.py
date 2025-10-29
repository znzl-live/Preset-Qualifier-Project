"""Setup script for Preset Qualifier Project."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="preset-qualifier",
    version="1.0.0",
    author="znzl.live",
    description="A modular Python application for processing, analyzing, and qualifying VST presets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/znzl/preset-qualifier",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "librosa>=0.10.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pyyaml>=6.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "clean-presets=scripts.clean_presets:main",
            "analyze-audio=scripts.analyze_audio:main",
            "sort-presets=scripts.sort_presets:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)