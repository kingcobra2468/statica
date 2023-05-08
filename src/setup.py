from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='statica',
    packages=find_packages(),
    ext_modules=cythonize(
        ['./**/file/*.py', './**/file/*.pxd'], language_level='3')
)
