# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="SyncLink",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="A Modern way to sync files",
)
