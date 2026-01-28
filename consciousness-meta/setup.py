#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="consciousness-meta",
    version="0.1.0",
    author="Clawdbot Assistant",
    author_email="none",
    description="Meta-observation layer for computational consciousness",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/consciousness-meta",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Cognitive Science",
    ],
    python_requires=">=3.6",
    keywords="consciousness meta-observation strange-loops qualia ai",
)