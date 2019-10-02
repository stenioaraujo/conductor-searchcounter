import setuptools
from os import path

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = [x.strip() for x in f.readlines()]

setuptools.setup(
    name='conductor_searchcounter',
    version='0.0.1',
    keywords='conductor searchcounter challenge',
    author='Stenio Araujo',
    author_email='stenioalt@hiaraujo.com',
    description=(
        'conductor_searchcounter is a module that contains the class '
        'SearchCounter. It is an implementation of a sliding window counter '
        'for the conductor challenge.'),
    long_description=long_description,
    url='https://github.com/stenioaraujo/conductor-searchcounter',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_requires,
    python_requires=">=3.7",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'conductor-searchcounter=conductor_searchcounter.cli:main']}
)
