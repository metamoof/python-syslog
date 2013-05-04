#! /usr/bin/env python
from setuptools import setup, find_packages

try:
    with file('README.rst') as f:
        long_desc = f.read()
except:
    long_desc = ''

setup(
    name = "Python-Syslog",
    version = "1.0.dev",
    packages = find_packages(),
    author = "Giles Antonio Radford",
    author_email = "moof@metamoof.net",
    description = "An RFC5424-Compliant Syslog Handler for the Python Logging Framework",
    license = "MIT",
    keywords = ["syslog", "logging",],
    url = "https://github.com/metamoof/python-syslog",
    test_suite = "syslog.test_syslog",
    long_description = long_desc,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Logging",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ]

)