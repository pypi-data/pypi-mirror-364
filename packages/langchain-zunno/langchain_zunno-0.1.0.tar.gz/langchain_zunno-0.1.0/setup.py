from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-zunno",
    version="0.1.0",
    author="Amit Kumar",
    author_email="amit@zunno.ai",
    description="LangChain integration for Zunno LLM and Embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zunno/langchain-zunno",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "requests>=2.25.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords="langchain, llm, embeddings, zunno, ai, machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/zunno/langchain-zunno/issues",
        "Source": "https://github.com/zunno/langchain-zunno",
        "Documentation": "https://github.com/zunno/langchain-zunno#readme",
    },
) 