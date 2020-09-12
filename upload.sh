#!/usr/bin/env bash
rm -f dist/*
python3 setup.py sdist
python3 setup.py bdist_wheel
for filename in dist/*; do
    twine upload "${filename}"
done