#!/usr/bin/env python3
"""
Setup script for Cogzia Alpha v1.5.
This provides better control over the installation process.
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Run post-install setup
        os.system(f"{sys.executable} post_install.py")

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # Run post-install setup
        os.system(f"{sys.executable} post_install.py")

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cogzia",
    version="1.5.0",
    author="Cogzia Team",
    author_email="team@cogzia.com",
    description="Cogzia Alpha v1.5 - Cloud-native AI Agent Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://app.cogzia.com",
    project_urls={
        "Bug Tracker": "https://github.com/cogzia/agent_builder/issues",
        "Documentation": "https://app.cogzia.com/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.5.0",
        "openai>=1.0.0",
        "httpx>=0.25.0",
        "aiohttp>=3.9.0", 
        "websockets>=11.0.0",
        "rich>=13.0.0",
        "click>=8.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
        "typing-extensions>=4.0.0",
        "jsonschema>=4.0.0",
        "msgpack>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cogzia=cogzia_alpha_v1_5.main:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "cogzia_alpha_v1_5": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt", "MANIFEST.yaml"],
    },
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
)