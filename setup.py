#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2020-03-31 22:03
#
# This source code is licensed under the Apache-2.0 license found in the
# LICENSE file in the root directory of this source tree.


import os
import sys
import shutil
import setuptools


# ------------------Package Meta-Data------------------
PACKAGE_INFO = {}

with open(os.path.join("youngs", "version")) as version_file:
    PACKAGE_INFO['Version'] = version_file.read().strip()

PACKAGE_INFO['Name'] = 'YoungS'
PACKAGE_INFO['Author'] = 'Jason-Young-AI'
PACKAGE_INFO['EMail'] = 'AI.Jason.Young@gmail.com'
PACKAGE_INFO['Source_URL'] = 'https://github.com/Jason-Young-AI/YoungS.git'
PACKAGE_INFO['Description'] = 'A Young Sequence Modeling System'

# This Package's directory absolute path is set here.
PACKAGE_DIR_ABSOLUTE_PATH = os.path.abspath(os.path.dirname(__file__))

# Long-Description file 'README.md' path is set here
README_ABSOLUTE_PATH = os.path.join(PACKAGE_DIR_ABSOLUTE_PATH, 'README.md')

# Distribution directory 'dist' path is set here.
PACKAGE_DIST_DIR_ABSOLUTE_PATH = os.path.join(PACKAGE_DIR_ABSOLUTE_PATH, 'dist')

# Building directory 'build' path is set here.
PACKAGE_BUILD_DIR_ABSOLUTE_PATH = os.path.join(PACKAGE_DIR_ABSOLUTE_PATH, 'build')

# EggInfo directory 'PACKAGE_NAME.egg-info' path is set here.
PACKAGE_EGGINFO_DIR_ABSOLUTE_PATH = os.path.join(PACKAGE_DIR_ABSOLUTE_PATH, '{}.egg-info'.format(PACKAGE_INFO['Name']))

#[Long Description]
try:
    with open(README_ABSOLUTE_PATH, 'r', encoding='utf-8') as readme_file:
        PACKAGE_INFO['Long_Description'] = '\n' + readme_file.read()
except FileNotFoundError:
    PACKAGE_INFO['Long_Description'] = PACKAGE_INFO['Description']

# Required Packages and Optional Packages
# Required
REQUIRED = [
        'torch',
        'YoungToolkit>=0.1.3',
        ]

# Optional
SERVER_EXTRAS = set(['waitress', 'flask', 'flask_wtf', 'wtforms'])
FULL = SERVER_EXTRAS

EXTRAS = {
        'full': FULL,
        'server': SERVER_EXTRAS,
        }


# Upload command class of the setup.py.
class UploadCommand(setuptools.Command):
    """Let setup.py support the command \'upload\'."""

    description = 'Building and Publishing this Package: {}'.format(PACKAGE_INFO['Name'])
    user_options = []

    @staticmethod
    def status(str):
        """Printing things in bold."""
        print('\033[1m{}\033[0m'.format(str))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous dists ...')
            shutil.rmtree(PACKAGE_DIST_DIR_ABSOLUTE_PATH)
            self.status('Removing previous builds ...')
            shutil.rmtree(PACKAGE_BUILD_DIR_ABSOLUTE_PATH)
            self.status('Removing previous egg-infos ...')
            shutil.rmtree(PACKAGE_EGGINFO_DIR_ABSOLUTE_PATH)
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution ...')
        os.system('{} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine ...')
        os.system('twine upload --repository-url https://upload.pypi.org/legacy/ dist/*')

        self.status('Pushing git tags ...')
        os.system('git tag v{}'.format(PACKAGE_INFO['Version']))
        os.system('git push --tags')
        os.system('git push -u origin master')

        sys.exit()


def setup_my_package():
    setuptools.setup(
        name=PACKAGE_INFO['Name'],
        version=PACKAGE_INFO['Version'],
        author=PACKAGE_INFO['Author'],
        author_email=PACKAGE_INFO['EMail'],
        url=PACKAGE_INFO['Source_URL'],
        description=PACKAGE_INFO['Description'],
        long_description=PACKAGE_INFO['Long_Description'],
        long_description_content_type='text/markdown',
        packages=setuptools.find_packages(exclude=('tests',)),
        install_requires=REQUIRED,
        extras_require=EXTRAS,
        include_package_data=True,
        classifiers=[
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
        cmdclass={
            'upload': UploadCommand,
        },
        entry_points={
            'console_scripts': [
                'youngs = youngs_cli.main:main',
                'youngs-preprocess = youngs_cli.preprocess:main',
                'youngs-train = youngs_cli.train:main',
                'youngs-test = youngs_cli.test:main',
                'youngs-serve = youngs_cli.serve:main',
                'youngs-inspect = youngs_cli.inspect:main',
            ],
        },
    )


if __name__ == '__main__':
    setup_my_package()
