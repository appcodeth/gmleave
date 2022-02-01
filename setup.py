#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from os.path import join, dirname


exec(open(join(dirname(__file__), 'odoo', 'release.py'), 'rb').read())  # Load release variables
lib_name = 'odoo'

setup(
    name='odoo',
    version=version,
    description=description,
    long_description=long_desc,
    url=url,
    author=author,
    author_email=author_email,
    classifiers=[c for c in classifiers.split('\n') if c],
    license=license,
    scripts=['setup/odoo'],
    packages=find_packages(),
    package_dir={'%s' % lib_name: 'odoo'},
    include_package_data=True,
    install_requires=[
        'babel >= 1.0',
        'decorator',
        'docutils',
        'gevent',
        'Jinja2',
        'lxml',
        'libsass',
        'mako',
        'mock',
        'ofxparse',
        'passlib',
        'pillow',
        'polib',
        'psutil',
        'psycopg2 >= 2.2',
        'pydot',
        'pyparsing',
        'pypdf2',
        'pyserial',
        'python-dateutil',
        'pytz',
        'pyusb >= 1.0.0b1',
        'qrcode',
        'reportlab',
        'requests',
        'zeep',
        'vatnumber',
        'vobject',
        'werkzeug',
        'xlsxwriter',
        'xlwt',
    ],
    python_requires='>=3.6',
    extras_require={
        'ldap': ['python-ldap'],
        'SSL': ['pyopenssl'],
    },
    tests_require=[
        'mock',
    ],
)
