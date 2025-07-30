from setuptools import setup, find_packages

setup(
    name='generatorappmaya',
    version='0.3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'generatorappmaya': ['templates/**/*'],
    },
    install_requires=[
        'Django>=5.2.4',
    ],
    entry_points={
        'console_scripts': [
            'generatorappmaya=generatorappmaya.cli:main',
        ],
    },
    author='amah',
    author_email='estherkouao9@gmail.com',
    description='Un générateur d’application Django personnalisé',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Estherkouao/generatorappmaya.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.10',
)
