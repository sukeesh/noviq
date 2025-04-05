from setuptools import setup, find_packages

setup(
    name="noviq",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dspy",
        "inquirer",
        "ollama",
    ],
    author="Sukeesh",
    description="A research assistant powered by LLMs",
    python_requires=">=3.6",
) 