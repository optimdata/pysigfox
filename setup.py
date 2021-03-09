#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = [req.strip("\n") for req in requirements_file.readlines()]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]
setup(
    author="Othman Moumni Abdou",
    author_email="othman.moumniabdou@inuse.eu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Unofficial client for the Sigfox V2 API",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="sigfox",
    name="pysigfox-client",
    packages=find_packages(include=["pysigfox"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/optimdata/pysigfox",
    version="0.1.1",
    zip_safe=False,
)
