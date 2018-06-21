"""
Setup file for the disk temperature package.
"""
from setuptools import setup, find_packages
import os

setup(
    name='widget',
    version='0.1.0',
    description='widget to scroll throught multi-dimensional data with contour or line plots',
    long_description=open(os.path.join(
        os.path.dirname(__file__), 'README.md')).read(),
    url='http://www.til-birnstiel.de',
    author='Til Birnstiel',
    author_email='birnstiel@me.com',
    packages=find_packages(),
    license='GPLv3',
    include_package_data=True,
    install_requires=[
        'scipy',
        'numpy',
        'matplotlib'],
    zip_safe=False)
