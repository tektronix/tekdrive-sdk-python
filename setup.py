import re
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = "tekdrive"
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, "README.rst"), encoding="utf-8") as fp:
    README = fp.read()
with open(path.join(HERE, PACKAGE_NAME, "settings.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

extras = {
    "lint": [
        "black",
        "flake8",
    ],
    "test": [
        "pytest >=6.2.2",
        "vcrpy >=4.1.1",
    ],
}
extras["dev"] = extras["lint"] + extras["test"]

setup(
    name=PACKAGE_NAME,
    author="Thomas Buida",
    author_email="thomas@initialstate.com",
    python_requires="~=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
    description=("A Python package that allows for simple access to the TekDrive API."),
    install_requires=["requests >=2.25.0, <3.0"],
    extras_require=extras,
    keywords="tektronix tekdrive api sdk",
    long_description=README,
    packages=find_packages(exclude=["tests", "tests.*"]),
    version=VERSION,
)
