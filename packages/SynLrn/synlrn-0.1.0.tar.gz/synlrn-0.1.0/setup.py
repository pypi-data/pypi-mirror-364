# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="SynLrn",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rapidfuzz",
        "google-genai",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="A modern way to allow your AI to learn from every interaction",
)
