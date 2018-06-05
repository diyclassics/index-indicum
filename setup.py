import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "index_indicum",
    version = "0.0.1",
    author = "Patrick J. Burns",
    author_email = "patrick.j.burns@nyu.edu",
    description = ("Build indices from journal data"),
    # license = "MIT",
    # keywords = "example documentation tutorial",
    # url = "",
    # packages=['an_example_pypi_project', 'tests'],
    long_description=read('README.md'),
    classifiers=[
    ],
)
