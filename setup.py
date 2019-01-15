from setuptools import setup, find_namespace_packages

setup(
    name="weatherapp.core",
    version="0.1.0",
    author="Taras Melnychuk",
    description="A simple cli weather aggregator",
    long_descriptoin="",
    packages=find_namespace_packages(),
    entry_points={
        'console_scripts': 'wfapp=weatherapp.core.app:main'
    },
    install_requires=[
        'requests',
        'bs4',
    ]
)
