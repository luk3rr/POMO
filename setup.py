# -*- coding: utf-8 -*-

# Filename: setup.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>


from setuptools import setup, find_packages


with open('readme.org') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pomo',
    version='0.1.0',
    description='Pomo package.',
    long_description=readme,
    author='Lucas Araújo',
    author_email='araujolucas@dcc.ufmg.br',
    url='https://github.com/luk3rr/POMO',
    license=license,
    packages=find_packages(exclude=('test', 'docs'))
)
