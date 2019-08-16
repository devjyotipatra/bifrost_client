import os
import versioneer
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

with open('requirements.txt') as f:
    required = f.read().splitlines()


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name="bifrost",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url = "https://bitbucket.org/qubole/bifrost.git",
    author="Qubole",
    author_email="devjyotip@qubole.com",
    description="Project for  operating the Qubole's data intelligence platform",
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': ['bifrost=command_line:main'],
    },
    install_requires=required,
    test_suite='nose.collector',
    tests_require=['nose~=1.3.7', 'mock~=1.0.1'],
    long_description=read('README.md'),
    extras_require={
        'docs': ['sphinx==1.5.1',
                 'sphinx-rtd-theme==0.1.9']
    }
)
