from setuptools import find_packages, setup

setup (
    name='DBL_API',
    packages=find_packages(include=['DBL_API', 'DBL_API.Database', 'DBL_API.Types']),
    version='0.1.0',
    description='Tools for Dragon Ball Legends API',
    author='Jamie Levitt',
    requires=['bs4']
)