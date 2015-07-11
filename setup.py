# -*- coding: utf-8 -*-
"""Setup file for the RubyMarshal project.
"""

import codecs
import os.path
import sys
from setuptools import setup, find_packages
from rubymarshal import __version__ as version
# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()


setup(
    name='rubymarshal',
    version=version,
    description='No description yet.',
    long_description=long_description,
    author='Matthieu Gallet',
    author_email='MatthieuGallet@19pouces.net',
    license='CeCILL-B',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='rubymarshal.tests',
    install_requires=[],
    setup_requires=[],
    classifiers=[],
)