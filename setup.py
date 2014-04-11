#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import blatt

setup(
    name='blatt',
    version=blatt.__version__,
    description='',
    long_description=blatt.__doc__,
    author=u'Alvaro Mouriño',
    author_email='alvaro@mourino.net',
    url=blatt.__url__,
    download_url='https://codeload.github.com/tooxie/blatt/zip/master',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Multimedia',
    ],
    license='MIT',
    platforms=['OS-independent', 'Any'],
    package_dir={'': '.'},
    packages=find_packages('.'),
    install_requires=[
        'markdownify==0.4.0',
        'scrapy==0.22.2',
        'slugify==0.0.1',
        'sqlalchemy==0.9.4',
    ],
    entry_points={
        'console_scripts': [
            'blatt = blatt.bin.blatt:main',
        ]
    }
)
