#!/usr/bin/env python3

"""Setup for adcc-testdata"""
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [
        ("pytest-args=", "a", "Arguments to pass to pytest"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


#
# Main setup code
#

setup(
    name='adcc-testdata',
    description="Package to aid the generation of test data for adcc.",
    #
    url='https://github.com/adc-connect/adcc-testdata',
    author='Michael F. Herbst',
    author_email="info@michael-herbst.com",
    license="GPL v3",
    #
    packages=find_packages(exclude=["*.test*", "test"]),
    version='0.1.0',
    #
    python_requires='>=3.5',
    install_requires=[
        'pyscf', 'numpy', 'h5py',
    ],
    tests_require=["pytest"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Science/Research',
        "Topic :: Scientific/Engineering :: Chemistry",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
    ],
    #
    cmdclass={"pytest": PyTest},
)
