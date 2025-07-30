from setuptools import setup, find_packages

setup(
    name="promptvc",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "typer",
        "ruamel.yaml",
        "sentence-transformers",
        "openai",
        "anthropic",
    ],
    entry_points={
        "console_scripts": [
            "promptvc = promptvc.cli:app",
        ]
    },
    author="oha",
    author_email="aaronoh2015@gmail.com",
    description="A Git-like version controller for LLM prompts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/duriantaco/promptvc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
    ],
)