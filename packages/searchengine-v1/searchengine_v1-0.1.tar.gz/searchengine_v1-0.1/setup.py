# setup.py
from setuptools import setup, find_packages

setup(
    name="searchengine_v1",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch>=1.7.0",
        "transformers>=4.0.0",
        "scikit-learn>=0.24.0"
    ],
    author="Your Name",
    description="A lightweight semantic search engine using transformer embeddings.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Falgit1/searchengine",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7'
)
