from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Explicitly list all packages
packages = [
    'openarchx',
    'openarchx.algorithms',
    'openarchx.bayesian',
    'openarchx.core',
    'openarchx.cuda',
    'openarchx.data',
    'openarchx.layers',
    'openarchx.nn',
    'openarchx.optimizers',
    'openarchx.quantum',
    'openarchx.training',
    'openarchx.utils',
    'tests',
]

setup(
    name="openarchx",
    version="0.1.4",
    description="Revolutionary deep learning framework with quantum-inspired computing, O(n) attention, 90% data compression, and 70% gradient reduction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenArchX Team",
    author_email="info@openarchx.org",
    url="https://github.com/openarchx/openarchx",
    packages=packages,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "pytorch": ["torch>=1.7.0"],
        "tensorflow": ["tensorflow>=2.4.0"],
        "huggingface": ["transformers>=4.0.0", "datasets>=1.0.0"],
        "all": [
            "torch>=1.7.0",
            "tensorflow>=2.4.0",
            "transformers>=4.0.0",
            "datasets>=1.0.0",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/openarchx/openarchx/issues",
    },
)