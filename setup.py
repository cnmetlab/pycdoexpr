import os
from setuptools import find_packages, setup

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(FILE_PATH, "README.md"), "r") as f:
    description = f.read()

with open(os.path.join(FILE_PATH, "requirements.txt")) as f:
    required = f.read().splitlines()

setup(
    name="pycdoexpr",
    version="0.0.1",
    author="blizhan",
    author_email="blizhan@icloud.com",
    description="A Python package helps to generate complicated cdo expr(computing expression) in pythonic way",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/blizhan/pycdoexpr",
    package_dir={"pycdoexpr": "pycdoexpr", ".": "./"},
    package_data={
        "": ["*.toml", "*.txt"],
    },
    include_package_data=True,
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
