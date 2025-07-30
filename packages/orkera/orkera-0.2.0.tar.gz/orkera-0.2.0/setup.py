from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orkera",
    version="0.2.0",
    description="Simple HTTP client for Orkera distributed task runner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0"
    ],
    python_requires=">=3.7",
    author="Orkera Team",
    author_email="contact@orkera.com",
    url="https://github.com/orkera/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/orkera/python-sdk/issues",
        "Documentation": "https://github.com/orkera/python-sdk",
        "Source Code": "https://github.com/orkera/python-sdk",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords="orkera, task, distributed, scheduler, async",
    license="MIT",
) 