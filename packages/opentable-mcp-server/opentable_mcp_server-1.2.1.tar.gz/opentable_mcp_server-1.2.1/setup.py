#!/usr/bin/env python3
"""
Setup script for OpenTable MCP Server
"""

from setuptools import setup, find_packages

with open("opentable_mcp_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opentable-mcp-server",
    version="1.2.1",
    author="wheelis",
    author_email="noreply@github.com",
    description="An MCP server for OpenTable restaurant reservations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wheelis/opentable_mcp",
    py_modules=["opentable_mcp_server"],
    install_requires=[
        "mcp>=1.2.0",
        "opentable-rest-client>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "opentable-mcp-server=opentable_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    keywords=["mcp", "opentable", "restaurant", "reservations", "model-context-protocol"],
) 