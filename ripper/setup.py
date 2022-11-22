from setuptools import setup

setup(
    name='ripper',
    packages=['ripper'],
    include_package_data=True,
    install_requires=[
        'morecontext',
        'bs4',
        'requests',
    ],
)
