#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

# Get common version number (https://stackoverflow.com/a/7071358)
import re
VERSIONFILE="histpy/__version__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='histpy',
      version=verstr,
      author='Israel Martinez',
      author_email='imc@umd.edu',
      install_requires = ['scipy>=1.11',
                          'matplotlib',
                          'h5py',
                          'sparse',
                          'astropy',
                          'mhealpy',
                         ],
      url='https://gitlab.com/burstcube/histpy',
      packages = find_packages(include=["histpy","histpy.*"]),
      long_description = long_description,
      long_description_content_type="text/markdown",
      )
