#!/usr/bin/env python3
"""
YICA-Mirage: High-Performance AI Computing Optimization Framework
Supporting In-Memory Computing Architecture (Python-only version)
"""

from setuptools import setup, find_packages
import os

# Version information
VERSION = "1.0.0"
DESCRIPTION = "YICA-Mirage: AI Computing Optimization Framework for In-Memory Computing Architecture"
LONG_DESCRIPTION = """
YICA-Mirage is a high-performance AI computing optimization framework designed for in-memory computing architectures.

Core Features:
- 🚀 Mirage-based universal code optimization
- 🧠 YICA in-memory computing architecture specific optimizations
- ⚡ Automatic Triton code generation
- 🔧 Multi-backend support (CPU/GPU/YICA)
- 📊 Intelligent performance tuning

Supported Platforms:
- Linux (x86_64, aarch64)
- macOS (x86_64, arm64)
- Windows (x86_64)

Installation:
```bash
pip install yica-mirage
```
"""

# Dependencies
REQUIREMENTS = [
    "numpy>=1.19.0",
    "torch>=1.12.0",
    # "triton>=2.0.0",  # Optional for now
    # "z3-solver>=4.8.0",  # Optional for now
]

EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=6.0",
        "black>=21.0",
        "flake8>=3.8",
        "mypy>=0.900",
        "sphinx>=4.0",
        "sphinx-rtd-theme>=1.0",
    ],
    "cuda": [
        "cupy>=9.0.0",
        "nvidia-ml-py>=11.0.0",
    ],
    "rocm": [
        "torch-rocm>=1.12.0",
    ],
    "full": [
        "triton>=2.0.0",
        "z3-solver>=4.8.0",
    ],
}

# Read README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return LONG_DESCRIPTION

# Main configuration
setup(
    name="yica-mirage",
    version=VERSION,
    author="YICA Team",
    author_email="contact@yica.ai",
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yica-ai/yica-mirage",
    project_urls={
        "Bug Tracker": "https://github.com/yica-ai/yica-mirage/issues",
        "Documentation": "https://yica-mirage.readthedocs.io/",
        "Source Code": "https://github.com/yica-ai/yica-mirage",
    },
    
    # Package configuration
    packages=find_packages(where="mirage/python"),
    package_dir={"": "mirage/python"},
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    
    # Classifications
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Compilers",
        "Topic :: System :: Hardware",
    ],
    
    # Keywords
    keywords="ai, optimization, compiler, triton, yica, mirage, deep-learning, in-memory-computing",
    
    # Entry points
    entry_points={
        "console_scripts": [
            "yica-optimizer=mirage.yica_optimizer:main",
            "yica-benchmark=mirage.yica_performance_monitor:main",
            "yica-analyze=mirage.yica_auto_tuner:main",
        ],
    },
    
    # Include data files
    include_package_data=True,
    package_data={
        "mirage": [
            "*.py",
            "*.yaml",
            "*.json",
        ],
    },
    
    zip_safe=False,
) 