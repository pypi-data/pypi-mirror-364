# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="updatepkgs",
    version="1.0.1",
    author="Dishani William",
    author_email="dishaniwilliam@outlook.com",
    description="Update or install Python packages interactively from terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dnettz/updatepkgs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'updatepkgs=updatepkgs.__main__:main',
        ],
    },
)
