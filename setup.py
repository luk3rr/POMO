# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('readme.org') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='py_skeleton',
    version='0.1.0',
    description='py_skeleton package.',
    long_description=readme,
    author='Lucas Araújo',
    author_email='araujolucas@dcc.ufmg.br',
    url='https://github.com/luk3rr/$REPO_NAME$',
    license=license,
    packages=find_packages(exclude=('test', 'docs'))
)
