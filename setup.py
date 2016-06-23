from setuptools import setup

setup(
    name='gemac',
    version='0.1',
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
