#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 youfa <vsyfar@gmail.com>
#
# Distributed under terms of the GPLv2 license.

"""

"""

from setuptools import setup, find_packages

setup(
    name="pdf-hider",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyPDF2==3.0.1",  # Specify exact version for stability
        "reportlab==4.0.0",  # Specify exact version for stability
    ],
    entry_points={
        "console_scripts": [
            "pdf-hider=pdf_hider.main:main",
        ],
    },
    author="Youfa",  # Replace with your name
    author_email="hi@youfa.me",  # Replace with your email
    description="A tool to embed hidden, transparent text into PDF files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pdf-hidden-text-tool",  # Replace with your GitHub repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    keywords="pdf hidden text transparency ai resume",
)
