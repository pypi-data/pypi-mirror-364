#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", encoding="utf-8") as history_file:
    history = history_file.read()

requirements = []

test_requirements = []

setup(
    author="Yasser Alemán-Gómez",
    author_email="yasseraleman@protonmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="This package contains a set of useful tools for image processing",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="clabtoolkit",
    name="clabtoolkit",
    packages=find_packages(include=["clabtoolkit", "clabtoolkit.*"]),
    package_data={"clabtoolkit": ["config/*"]},  # FIXED LINE
    exclude_package_data={"clabtoolkit": ["test3.py", "test_2.py", "test_file.py"]},
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/connectomicslab/clabtoolkit",
    version="0.3.2a1",
    zip_safe=False,
)
