"""Setup script for langchain-semantic-cache."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-semantic-cache",
    version="0.1.1",
    author="Chris Olande",
    author_email="olandechris@gmail.com",
    description="A semantic caching extension for LangChain with FAISS vector similarity search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chrisolande/langchain-semantic-cache",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-huggingface>=0.0.1",
        "faiss-cpu>=1.7.0",
        "numpy>=1.20.0",
        "sentence-transformers>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.20.0",
        ],
        "quantization": [
            "faiss-gpu>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
           
        ],
    },
    keywords="langchain, semantic, cache, faiss, vector, similarity, llm",
    project_urls={
        "Bug Reports": "https://github.com/Chrisolande/langchain-semantic-cache/issues",
        "Source": "https://github.com/Chrisolande/langchain-semantic-cache",
        "Documentation": "https://github.com/Chrisolande/langchain-semantic-cache#readme",
    },
)