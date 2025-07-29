from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="remote-detector",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Detects remote access tools and logs ERP login to MongoDB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/remote-detector",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "click",
        "python-json-logger",
        "requests",
        "beautifulsoup4",
        "pymongo"
    ],
    entry_points={
        "console_scripts": [
            "remote-detector = remote_detector.cli:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "Topic :: Utilities"
    ],
    python_requires='>=3.7',
) 