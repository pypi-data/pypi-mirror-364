from setuptools import setup, find_packages

setup(
    name='generatorappmaya',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'generatorappmaya': ['templates/*', 'templates/static/*', 'templates/templates/*'],
    },
    install_requires=[
        'Django>=3.0',
    ],
    entry_points={
        'console_scripts': [
            'generatorappmaya=generatorappmaya.cli:main',
        ],
    },
)