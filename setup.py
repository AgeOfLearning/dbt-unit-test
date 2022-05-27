#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

PACKAGE_NAME = "dbt-unit-test"

__version__ = "0.1.0"

setup_args = dict(
    # Description
    name=PACKAGE_NAME,
    version=__version__,
    description="A framework for dbt macro testing",
    python_requires=">=3.6",
    # Credentials
    author="Youcef Kadri",
    author_email="youcef.kadri@octoenergy.com",
    url="https://github.com/octo-youcef/dbt-unit-test",
    classifiers=[
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    license="MIT",
    # Package data
    package_dir={"": "src"},
    packages=find_packages(
        "src",
    ),
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["dut=dbt_unit_test.app:dut"]},
)

if __name__ == "__main__":
    setup(**setup_args)
