from setuptools import find_packages, setup

setup(
    name='bot-core',
    packages=find_packages(include=['botcore']),
    version='0.1.0',
    description='Bot-Core provides the core functionality and utilities for the bots of the Python Discord community',
    author='Python Discord',
    license='MIT',
    install_requires=["discord.py=^1.7.2"],
    tests_require=['pytest~=6.2.4'],
    test_suite='tests',
)
