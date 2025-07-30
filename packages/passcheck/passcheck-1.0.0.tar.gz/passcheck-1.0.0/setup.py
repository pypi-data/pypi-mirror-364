from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="passcheck",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Утилита для проверки стойкости паролей",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "zxcvbn-python",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "passcheck=passcheck.main:main",
        ],
    },
)
