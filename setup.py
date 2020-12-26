""" Setuptools configuration for project packaging """
from typing import List
from setuptools import setup, find_packages


# Extract version from main package
from botlet import __version__ as version


# Extract descriptions from README file
def _read_description() -> str:
    with open('README.md') as readme:
        readme.readline()
        return readme.readline().rstrip()

def _read_long_description() -> str:
    with open('README.md') as readme:
        return readme.read()


# Extract install dependencies from requirements file
def _read_requirements(filename: str) -> List[str]:
    with open(filename) as requirements_file:
        return [line for line in requirements_file.read().splitlines() if line and not line.lstrip().startswith('#')]


# Send setup information
setup(
    name='botlet',
    version=version,
    author='Christoph "Youka" Spanknebel',
    author_email='spanknebel.christoph@t-online.de',
    url='https://youka.io',
    description=_read_description(),
    long_description=_read_long_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Chat',
        'Topic :: Home Automation',
        'Topic :: Office/Business',
        'Topic :: System :: Monitoring'
    ],
    keywords=['bot', 'automation', 'assistant'],
    license='Apache-2.0',
    platforms=['any'],
    packages=find_packages(include=('botlet', 'botlet.*',)),
    package_data={
        'botlet.config': ['*.ini']
    },
    install_requires=_read_requirements('requirements.txt'),
    extras_require={
        'dev': _read_requirements('requirements-dev.txt')
    },
    entry_points={
        'console_scripts':[
            'botlet=botlet.cli:main'
        ]
    },
    python_requires='>=3.7.3'
)
