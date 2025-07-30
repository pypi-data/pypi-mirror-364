from setuptools import setup, Command
from codecs import open
from os import path

currPath = path.abspath(path.dirname(__file__))

# Parse README
with open(path.join(currPath, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Parse version
with open(path.join(currPath, 'survivaldnn', '__init__.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('"')[1]

setup(
    name='SurvivalDNN',
    description='Survival Analysis using Deep Learning for Prediction',
    version=version,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adamvvu/SurvivalDNN',
    author='Adam Wu',
    author_email='adamwu1@outlook.com',
    packages=['survivaldnn'],
    classifiers=[
	'Intended Audience :: Science/Research',
	'Topic :: Scientific/Engineering :: Information Analysis',
	'Programming Language :: Python',
	'Operating System :: OS Independent',
	'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'pandas',
        "tensorflow >= 2.10",
        "tf-compactprogbar",
        "matplotlib"
    ],
    license_files = ('LICENSE',),
)