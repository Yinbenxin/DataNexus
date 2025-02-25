from setuptools import setup, find_packages

setup(
    name="modapp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pytest",
        "pytest-asyncio",
        "httpx",
    ],
)