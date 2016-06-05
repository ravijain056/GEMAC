import sys
from setuptools.command.test import test as TestCommand
from setuptools import setup


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='gemac',
    version = '0.1',
    author='Ravi Jain',
    author_email='ravijain056@gmail.com',
    url='http://github.com/ravijain056/GEMAC',
    packages=['gemac'],
    description='GEMAC implementation and tools',
    long_description=open('README.md').read() + '\n\n',
    install_requires=['myhdl >= 1.0.dev0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
