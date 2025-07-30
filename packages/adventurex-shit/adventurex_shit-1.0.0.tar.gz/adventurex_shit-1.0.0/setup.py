from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adventurex-shit",
    version="1.0.0",
    author="Anonymous Hackathon Participant",
    author_email="mystery@adventurex.com",
    description="A humorous Python module commemorating the legendary AdventureX 2025 bathroom incident",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adventurex/shit-incident",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.7",
    keywords="adventurex hackathon bathroom humor toilet incident",
    project_urls={
        "Bug Reports": "https://github.com/adventurex/shit-incident/issues",
        "Source": "https://github.com/adventurex/shit-incident",
        "Bounty Hunter": "https://adventurex.com/bounty/5000",
    },
)