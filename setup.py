"""dbt-unit-test module."""

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

# Runtime Requirements.
inst_reqs = ["click", "jinja2"]

# Dev Requirements
extra_reqs = {
    "test": ["pytest", "pytest-cov"],
    "dev": ["pytest", "pytest-cov", "pre-commit"],
}


setup(
    name="dbt-unit-test",
    version="0.0.5",
    description=u"A tiny framework for testing reusable code inside of dbt models",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="sql dbt test unittest",
    author="Benjamin Ryon",
    author_email="benjamin.ryon@aofl.com",
    url="https://github.com/AgeOfLearning/dbt-unit-test",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    entry_points={"console_scripts": ["dut = dbt_unit_test.app:dut"]},
)
