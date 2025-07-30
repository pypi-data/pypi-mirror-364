from setuptools import setup, find_packages

setup(
    name='devremind1',
    version='0.1.0',
    description='A Python package that reminds developers to take breaks',
    author='Anil Thapa',
    packages=find_packages(),
    install_requires=['plyer'],
    entry_points={
        'console_scripts': [
            'devremind1 = devremind1.__main__:main',
        ],
    },
)
