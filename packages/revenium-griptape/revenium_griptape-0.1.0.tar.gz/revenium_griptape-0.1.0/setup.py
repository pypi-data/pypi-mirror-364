import os
from setuptools import setup

setup(
    name="revenium-griptape",
    version="0.1.0",
    description="Universal Revenium middleware for Griptape framework - transparent AI usage metering across all providers",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Revenium",
    author_email="support@revenium.io",
    license="MIT",
    url="https://github.com/revenium/revenium-griptape",
    packages=["revenium_griptape", "revenium_griptape.drivers"],
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "griptape>=1.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.25.0",
        "wrapt>=1.14.0",
    ],
    extras_require={
        "openai": ["revenium-middleware-openai>=0.1.0", "openai>=1.0.0"],
        "anthropic": ["revenium-middleware-anthropic>=0.1.0", "anthropic>=0.8.0"],
        "ollama": ["revenium-middleware-ollama>=0.1.0"],
        "litellm": ["revenium-middleware-litellm>=0.1.0", "litellm>=1.0.0"],
        "all": [
            "revenium-middleware-openai>=0.1.0", "openai>=1.0.0",
            "revenium-middleware-anthropic>=0.1.0", "anthropic>=0.8.0", 
            "revenium-middleware-ollama>=0.1.0",
            "revenium-middleware-litellm>=0.1.0", "litellm>=1.0.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
        "Framework :: Griptape",
    ],
) 