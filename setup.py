#!/usr/bin/env python3

from setuptools import setup, find_packages

def get_reqs():
    with open("requirements.txt", "r") as req_file:
        return [r.strip() for r in req_file]

setup(name="Circular Cropper",
        version="1.0",
        description="GUI to crop images as a circle",
        author="John Rizkalla",
        url="",
        packages=find_packages(),
        install_requires=get_reqs(),
        license="MIT")
