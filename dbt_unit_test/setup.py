"""dbt_unit_test module."""

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

# Runtime Requirements.
inst_reqs = ["click"]

# Dev Requirements
extra_reqs = {
    "test": ["pytest", "pytest-cov"],
    "dev": ["pytest", "pytest-cov", "pre-commit"],
}


setup(
    name="dbt_unit_test",
    version="0.0.1",
    description=u"Unit tests for DBT macros.",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="Unit tests for DBT macros.",
    author=u"Benjamin Ryon",
    author_email="benjamin.ryon@aofl.com",
    url="",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    entry_points={"console_scripts": ["dbt_unit_test = dbt_unit_test.app:run"]},
)
