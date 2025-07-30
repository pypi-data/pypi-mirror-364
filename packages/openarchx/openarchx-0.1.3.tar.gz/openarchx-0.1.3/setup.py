from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Explicitly list all packages
packages = [
    'openarchx',
    'openarchx.core',
    'openarchx.cuda',
    'openarchx.layers',
    'openarchx.nn',
    'openarchx.optimizers',
    'openarchx.quantum',
    'openarchx.utils',
    'tests',
]

setup(
    name="openarchx",
    version="0.1.0",
    description="A lightweight and extensible deep learning framework with native model serialization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenArchX Team",
    author_email="info@openarchx.org",
    url="https://github.com/openarchx/openarchx",
    packages=packages,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
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