from setuptools import setup, find_packages

# Read dependencies from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gamedev-feedback-agent",  # Package name
    version="0.1.0a4",  # Initial version
    packages=find_packages(include=["cli", "cli.*", 
                                    "scheduler", "scheduler.*",
                                    "crawlers", "crawlers.*",
                                    "database", "database.*",
                                    "intelligence", "intelligence.*"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gdcfa=cli.main:main",  # CLI command
        ]
    },
    author="VChahaha",
    description="Game Developer Community Feedback Agent CLI Tool",
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
