#!/usr/bin/env python3
import os
import re
from setuptools import setup, find_packages

def get_version():
    """Get version from __init__.py or increment if publishing"""
    version_file = os.path.join('jobmon_pkg', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            content = f.read()
            match = re.search(r'__version__ = [\'"]([^\'"]*)[\'"]', content)
            if match:
                return match.group(1)
    return "2.0.0"  # Default version

def read_readme():
    """Read README for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Enhanced Universal SLURM Job Monitor"

setup(
    name="jobmon-slurm",
    version=get_version(),
    author="Shafeeq Ibraheem",
    author_email="omonidat@example.com",  # Update with your email
    description="Enhanced Universal SLURM Job Monitor with smart pattern matching",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/omonidat/jobmon-slurm",  # Update with your repo
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'jobmon_pkg': ['scripts/*'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'jobmon=jobmon_pkg.cli:main',
            'jm=jobmon_pkg.cli:main',
            'jq=jobmon_pkg.cli:quiet_main',
        ],
    },
    install_requires=[
        # No external Python dependencies - uses system SLURM commands
    ],
    extras_require={
        'dev': [
            'wheel',
            'twine',
            'pytest',
            'black',
        ],
    },
    keywords="slurm hpc job monitoring cluster computing batch scheduler",
    project_urls={
        "Bug Reports": "https://github.com/omonidat/jobmon-slurm/issues",
        "Source": "https://github.com/omonidat/jobmon-slurm/",
        "Documentation": "https://github.com/omonidat/jobmon-slurm/blob/main/README.md",
    },
)
