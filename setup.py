#!/usr/bin/env python
#
# Copyright (c) 2011 Geisha Tokyo Entertainment, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='lightning_core',
    version='1.0.0',
    description='swf to svg parser',
    author='Takashi Aoki, Masahiro Yamauchi, Ryoko Kato',
    author_email='info@geishatokyo.com',
    url='http://www.geishatokyo.com/',
    license='MIT',
    install_requires=[
      "lxml>=2.3.1",
      "simplejson>=2.2.1",
    ],
    test_suite='lightning_core.test',
    packages=['lightning_core'] + find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
)
