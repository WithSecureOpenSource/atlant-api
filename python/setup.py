#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="atlant-api-examples",
    version="1.0",
    description="F-Secure Atlant API examples.",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "atlant-token=atlant.tools.token:main",
            "atlant-get=atlant.tools.get:main",
            "atlant-set=atlant.tools.set:main",
            "atlant-scan=atlant.tools.scan:main",
            "atlant-web=atlant.tools.web:main",
            "atlant-icap=atlant.tools.icap:main",
            "atlant-dirscan=atlant.tools.dirscan:main",
        ]
    },
    install_requires=["requests==2.28.0", "flask==2.1.2"],
    keywords=["Topic :: Security"],
)
