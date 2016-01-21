# -*- coding: utf-8 -*-
"""Setup file for the RubyMarshal project.
"""

import codecs
import os.path
import re

from setuptools import setup, find_packages


with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()
version = None
for line in codecs.open(os.path.join('rubymarshal', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

setup(
    name='rubymarshal',
    version=version,
    description='Read and write Ruby-marshalled data.',
    long_description=long_description,
    author='Matthieu Gallet',
    author_email='python-dev@19pouces.net',
    license='WTFPL',
    url='https://github.com/d9pouces/RubyMarshal',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    test_suite='rubymarshal.tests',
    install_requires=[],
    setup_requires=[],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Utilities',
                 ],
)
