"""Setup configuration for ATS Scorer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="ats-scorer",
    version="0.1.0",
    author="ATS Scorer Team",
    author_email="",
    description="ATS (Applicant Tracking System) compatibility scorer for resumes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ats-scorer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.9.0",
        "python-docx>=0.8.11",
        "docx2txt>=0.8",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "nlp": [
            "spacy>=3.0.0",
            "nltk>=3.8.0",
            "textblob>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ats-score=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)