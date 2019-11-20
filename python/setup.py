#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="atlant-api-examples",
    version="1.0",
    description="F-Secure Atlant API examples.",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "atlant-token=authentication.token:main",
            "atlant-get=configuration.get:main",
            "atlant-set=configuration.set:main",
            "atlant-scan=scanning.scan:main",
            "atlant-web=web.web:main",
            "atlant-icap=icap.icap:main",
        ]
    },
    install_requires=["requests2==2.16.0", "click==7.0", "flask==1.1.1"],
    keywords=["Topic :: Security"],
)
