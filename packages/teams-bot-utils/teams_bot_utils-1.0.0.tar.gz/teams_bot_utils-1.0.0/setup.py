from setuptools import setup, find_packages
import os


def get_version():
    """Get version from __init__.py"""
    init_file = os.path.join(
        os.path.dirname(__file__), "teams_bot_utils", "__init__.py"
    )
    if os.path.exists(init_file):
        with open(init_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"


def get_long_description():
    """Get long description from README.md"""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return ""


def get_requirements():
    """Get requirements from requirements.txt"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as fh:
            return [
                line.strip() for line in fh if line.strip() and not line.startswith("#")
            ]
    return [
        "mixpanel>=2.2.0",
        "httpx>=0.24.0",
        "botbuilder-core>=4.14.0",
        "pydantic>=1.8.0",
    ]


setup(
    name="teams-bot-utils",
    version=get_version(),
    author="Shubham Shinde",
    author_email="shubhamshinde7995@gmail.com",
    description="A comprehensive Python library for Microsoft Teams bot development with utilities for message processing, image handling, telemetry tracking, and HTTP client management",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/shubhamshinde7995/teams-bot-utils",
    project_urls={
        "Bug Tracker": "https://github.com/shubhamshinde7995/teams-bot-utils/issues",
        "Documentation": "https://github.com/shubhamshinde7995/teams-bot-utils#readme",
        "Source": "https://github.com/shubhamshinde7995/teams-bot-utils",
        "Download": "https://pypi.org/project/teams-bot-utils/",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Conferencing",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
        "Environment :: Console",
        "Natural Language :: English",
        "Framework :: AsyncIO",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "black>=22.0",
            "mypy>=0.950",
            "flake8>=4.0",
            "pre-commit>=2.15.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.17.0",
        ],
    },
    keywords=[
        "microsoft teams",
        "bot framework",
        "telemetry",
        "image processing",
        "http client",
        "connection pooling",
        "mixpanel",
        "async",
        "bot development",
        "teams bot",
        "analytics",
        "monitoring",
        "chatbot",
        "conversation",
        "azure",
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        # Add console scripts if needed in the future
    },
)
