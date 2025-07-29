#!/usr/bin/env python3
"""
Grim Reaper Python Package
The Ultimate Backup, Monitoring, and Security System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("py_grim/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#") and not line.startswith(" ")]

setup(
    name="grim-reaper",
    version="1.0.0",
    author="Bernie Gengel and his beagle Buddy",
    author_email="packages@tuskt.sk",
    description="The Ultimate Backup, Monitoring, and Security System - Unified CLI for sh_grim, scythe, py_grim, and go_grim",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://grim.so",
    project_urls={
        "Bug Reports": "https://github.com/grim-reaper/grim/issues",
        "Source": "https://github.com/cyber-boost/grim",
        "Documentation": "https://grim.so/docs",
    },
    packages=find_packages(include=["py_grim*", "scythe*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "full": [
            "flask>=2.0",
            "fastapi>=0.68",
            "uvicorn>=0.15",
            "websockets>=10.0",
            "aiofiles>=0.7",
            "psycopg2-binary>=2.9",
            "pymongo>=4.0",
            "redis>=4.0",
            "celery>=5.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "grim=py_grim.grim_gateway:main",
            "grim-backup=py_grim.backup:main",
            "grim-monitor=py_grim.monitor:main",
            "grim-scan=py_grim.scanner:main",
            "grim-health=py_grim.health:main",
            "scythe=scythe.scythe:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.conf", "*.yaml", "*.yml"],
        "py_grim": ["*.py", "grim_*/*.py"],
        "scythe": ["*.py", "core/*.py", "config/*.yaml"],
    },
    data_files=[
        ("share/grim-reaper", [
            "grim_throne.sh",
            "README.md",
            "LICENSE",
        ]),
        ("share/grim-reaper/config", [
            "config/blacksmith.conf",
            "config/credentials.tsk",
            "config/healer.conf",
            "config/notify.conf",
        ]),
        ("share/grim-reaper/ascii", [
            "ascii/ascii/commands.txt",
            "ascii/ascii/grim-1.txt",
            "ascii/ascii/grim-2.txt",
            "ascii/ascii/grim-3.txt",
            "ascii/ascii/grim-4.txt",
            "ascii/ascii/grim-5.txt",
            "ascii/ascii/init.txt",
            "ascii/ascii/scythe-alt.txt",
            "ascii/ascii/skull-1.txt",
            "ascii/ascii/sycthe.txt",
            "ascii/ascii/terd.txt",
        ]),
    ],
    zip_safe=False,
    keywords=[
        "grim",
        "backup",
        "monitoring", 
        "security",
        "cli",
        "orchestration",
        "system-management",
        "compression",
        "encryption",
        "ai",
        "machine-learning",
        "grim-reaper",
    ],
    license="BBL",
    platforms=["any"],
) 