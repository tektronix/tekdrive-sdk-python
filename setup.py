import re
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = "tekdrive"
here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), "r", encoding="utf-8") as readme:
    README = readme.read()

with open(path.join(here, PACKAGE_NAME, "settings.py"), encoding="utf-8") as settings:
    VERSION = re.search('__version__ = "([^"]+)"', settings.read()).group(1)

extras = {
    "lint": [
        "black ==20.8b1",
        "flake8 >=3.8.4",
    ],
    "test": [
        "pytest >=6.2.2",
        "vcrpy >=4.1.1",
    ],
    "release": [
        "twine ==3.4.2",
    ]
}
extras["dev"] = extras["lint"] + extras["test"]

setup(
    name=PACKAGE_NAME,
    author="Initial State",
    author_email="thomas@initialstate.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
    description=("Package to interact with the TekDrive API."),
    install_requires=["requests >=2.25.0, <3.0"],
    extras_require=extras,
    keywords="tektronix tekdrive tekcloud",
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["tests", "tests.*"]),
    version=VERSION,
)
