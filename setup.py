#!/usr/bin/env python
# coding=utf-8

"""
Set penelope package up
"""

from setuptools import setup, Extension

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

setup(
    name="penelope",
    packages=["penelope"],
    package_data={"penelope": ["res/*"]},
    version="3.0.1.10",
    description="Penelope is a multi-tool for creating, editing and converting dictionaries, especially for eReader devices",
    author="Alberto Pettarin",
    author_email="alberto@albertopettarin.it",
    url="https://github.com/pettarin/penelope",
    license="MIT License",
    long_description=open("README.rst", "r").read(),
    install_requires=["lxml>=3.0", "marisa-trie>=0.7.2"],
    scripts=["bin/penelope"],
    keywords=[
        "Dictionary",
        "Dictionaries",
        "Index",
        "Merge",
        "Flatten",
        "eReader",
        "eReaders",
        "Bookeen",
        "CSV",
        "EPUB",
        "MOBI",
        "Kindle",
        "Kobo",
        "StarDict",
        "XML",
        "MARISA",
        "kindlegen",
        "dictzip",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Desktop Environment",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Localization",
        "Topic :: Text Editors",
        "Topic :: Text Editors :: Text Processing",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Utilities"
    ],
)
