"""Setup file for the RubyMarshal project.
"""

import os.path
import re

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fd:
    long_description = fd.read()
version = None
for line in open(os.path.join("rubymarshal", "__init__.py")):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

setup(
    name="rubymarshal",
    version=version,
    description="Read and write Ruby-marshalled data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthieu Gallet",
    author_email="github@19pouces.net",
    license="WTFPL",
    url="https://github.com/d9pouces/RubyMarshal",
    packages=["rubymarshal"],
    include_package_data=True,
    zip_safe=True,
    test_suite="tests",
    install_requires=[],
    setup_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
)
