from setuptools import setup, find_packages

setup(
    name='collection-fc',
    version='0.1.0',
    description='A flexible, easy-to-use Python library for collection forecasting.',
    author='Monish Gosar',
    packages=find_packages(),
    install_requires=[
        'pandas',
        # Add other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'collection_fc=collection_fc.cli:main',
        ],
    },
) 