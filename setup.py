"""
WTForms-Alchemy
---------------

Generates WTForms forms from SQLAlchemy models.
"""

import os
import re
import sys

from setuptools import setup

HERE = os.path.dirname(os.path.abspath(__file__))
PY3 = sys.version_info[0] == 3


def get_version():
    filename = os.path.join(HERE, "wtforms_alchemy", "__init__.py")
    with open(filename) as f:
        contents = f.read()
    pattern = r'^__version__ = "(.*?)"$'
    return re.search(pattern, contents, re.MULTILINE).group(1)


extras_require = {
    "test": [
        "enum34",
        "pytest>=2.3",
        "Pygments>=1.2",
        "Jinja2>=2.3",
        "docutils>=0.10",
        "flexmock>=0.9.7",
        "ruff==0.7.4",
        "WTForms-Test>=0.1.1",
    ],
    "babel": ["Babel>=1.3"],
    "arrow": ["arrow>=0.3.4"],
    "phone": ["phonenumbers>=5.9.2"],
    "intervals": ["intervals>=0.2.0"],
    "password": ["passlib >= 1.6, < 2.0"],
    "color": ["colour>=0.0.4"],
    "i18n": ["SQLAlchemy-i18n >= 0.8.2"],
    "ipaddress": ["ipaddr"] if not PY3 else [],
    "timezone": ["python-dateutil"],
}


# Add all optional dependencies to testing requirements.
for name, requirements in extras_require.items():
    if name != "test":
        extras_require["test"] += requirements


setup(
    name="WTForms-Alchemy",
    version=get_version(),
    url="https://github.com/kvesteri/wtforms-alchemy",
    license="BSD",
    author="Konsta Vesterinen",
    author_email="konsta@fastmonkeys.com",
    description="Generates WTForms forms from SQLAlchemy models.",
    long_description=__doc__,
    packages=["wtforms_alchemy"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "SQLAlchemy>=1.4",
        "WTForms>=3.1.0",
        "WTForms-Components>=0.11.0",
        "SQLAlchemy-Utils>=0.40.0",
    ],
    extras_require=extras_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
