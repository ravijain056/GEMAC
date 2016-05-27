from setuptools import setup

setup(
    name='gemac',
    author='Ravi Jain',
    author_email='ravijain056@gmail.com',
    url='http://github.com/ravijain056/GEMAC',
    packages=['gemac'],
    description='GEMAC implementation and tools',
    install_requires = ['myhdl >= 1.0.dev0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
