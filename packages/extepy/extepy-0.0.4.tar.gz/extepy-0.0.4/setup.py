#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

tagname = "v0.0.4"

setup(
    name='extepy',
    version=tagname[1:],
    description='Extension of Python Language',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zhiqing Xiao',
    author_email='zhiqingxiaophd@gmail.com',
    url='http://github.com/extepy/extepy',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
    ],
)
