"""
Setup script for fetch-fundamental-data package.
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="fetch-fundamental-data",
    version="0.1.0",
    author="Carl Viggo Gravenhorst-Lövenstierne",
    author_email="",
    description="A Python package for fetching and analyzing fundamental financial data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/fetch-fundamental-data",  # Update with actual repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "fetch-fundamentals=fetch_fundamental_data.cli:main",
        ],
    },
    keywords="finance, stocks, fundamental analysis, financial data, EODHD",
    project_urls={
        "Bug Reports": "https://github.com/username/fetch-fundamental-data/issues",
        "Source": "https://github.com/username/fetch-fundamental-data",
        "Documentation": "https://github.com/username/fetch-fundamental-data/blob/main/README.md",
    },
) 