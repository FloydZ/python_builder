#!/usr/bin/env python3
""" install script """
import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from python_builder import __version__, __author__, __email__


def read_text_file(path):
    """ read a test file and returns its content"""
    with open(os.path.join(os.path.dirname(__file__), path)) as file:
        return file.read()

class CustomInstallCommand(install):
    """ install script """
    def run(self):
        install.run(self)


class CustomDevelopCommand(develop):
    """ develop script """
    def run(self):
        develop.run(self)


class CustomEggInfoCommand(egg_info):
    """ custom script """
    def run(self):
        egg_info.run(self)


setup(
    name="AssemblyLinePython",
    long_description="parse all build systems and control the via python",
    author=__author__,
    author_email=__email__,
    version=__version__,
    description="parse all build systems",
    url="https://github.com/FloydZ/python_builder",
    package_dir={"": "python_builder"},
    keywords=["build systems"],
    install_requires=["setuptools", "py-make", "parse_cmake"],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
    package_data={'': ['deps/', 'python_builder/']},
    requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
	    "Programming Language :: Python",
	    "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ]
)
