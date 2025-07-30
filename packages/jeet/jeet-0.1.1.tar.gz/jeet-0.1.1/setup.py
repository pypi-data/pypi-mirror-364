# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        print("\n\nJeet here — thanks for installing me!\n")
        install.run(self)

setup(
    name='jeet',
    version='0.1.1',
    description='A prank pip package',
    author='Sangramjeet Ghosh',
    packages=['Prank'],
    cmdclass={'install': CustomInstall},
    zip_safe=False
)
