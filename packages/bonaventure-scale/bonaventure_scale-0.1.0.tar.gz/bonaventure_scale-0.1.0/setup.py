import os
from setuptools import setup, find_packages

setup(
    name="bonaventure_scale",
    version="0.1.0",
    author="Bonaventure",
    author_email="niyibizibonaventure33@gmail.com",  
    description="Python module for Bonaventure temperature scale conversions",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/whapoproject/bonaventure_scale",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
