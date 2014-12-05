#!/usr/bin/env python

"""
    Quickpaypy

   :copyright: (c) 2014 Walter Vargas <walter@exds.co>
   :license: AGPLv3, see LICENSE for more details

"""

import os
from setuptools import setup
import quickpaypy

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    # Basic package information.
    name = 'quickpaypy',
    version = quickpaypy.quickpaypy.__version__,

    # Packaging options.
    include_package_data = True,

    # Package dependencies.
    install_requires = ['httplib2',],

    # Metadata for PyPI.
    author = 'Walter Vargas',
    license = 'GNU AGPL-3',
    url = 'https://github.com/waltervargas/quickpaypy',
    packages=['quickpaypy'],
    keywords = 'quickpay merchant api client rest',
    description = 'A library to access QuickPay merchant from Python.',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet'
        ]
)
