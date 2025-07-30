# setup.py
from setuptools import setup, find_packages

setup(
    name="ergou",  # 包名，必须是PyPI上唯一的
    version="0.1.3",         # 版本号
    author="nigulasi_ergou",
    author_email="ergou@email.com",

    description="A simple package with my custom functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)



