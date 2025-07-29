"""Setup script for KG Engine v2"""
from setuptools import setup, find_packages

setup(
    name="kg-engine-v2",
    version="2.1.3",
    description="Advanced Knowledge Graph Engine with semantic search and temporal tracking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="KG Engine Team",
    author_email="team@kg-engine.dev",
    url="https://github.com/kg-engine/kg-engine-v2",
    project_urls={
        "Bug Tracker": "https://github.com/kg-engine/kg-engine-v2/issues",
        "Documentation": "https://github.com/kg-engine/kg-engine-v2/docs",
    },
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai>=1.0.0",
        "sentence-transformers>=2.2.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "dateparser>=1.1.0",
        "neo4j>=5.0.0",
        "llama-index>=0.10.0",
        "llama-index-vector-stores-neo4jvector>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)