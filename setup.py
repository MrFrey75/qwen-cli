# setup.py
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="qwen-cli",
    version="0.1.0",
    description="A secure, local-first AI assistant built on Qwen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MrFrey75",
    author_email="mr.frey@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dashscope>=1.14.0",
        "cryptography>=38.0.0",
        "spacy>=3.0.0",
        "python-dateutil>=2.8.0",
        "vosk>=0.3.30",
        "whisper.cpp>=0.1.0",
        "silero>=0.1.0",
        "pyttsx3>=2.90",
        "opencv-python>=4.0.0",
        "ultralytics>=8.0.0",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "qwen-cli=qwen_cli.__main__:main",
        ],
    },
    python_requires=">=3.9",
    include_package_data=True,
)