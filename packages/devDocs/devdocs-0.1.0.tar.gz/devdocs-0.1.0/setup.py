# setup.py
from setuptools import setup, find_packages

setup(
    name="devDocs",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",  # ensure version compatibility
    ],
    entry_points={
        'console_scripts': [
            'devDocs=devDocs.cli:x'
        ]
    },
    author="Gantavya Bansal",
    description="Auto-generate Project's markdown documentation using Gemini AI for Internal teams.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
