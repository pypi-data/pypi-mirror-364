from setuptools import setup, find_packages

setup(
    name='devremind1',
    version='0.1.2', 
    description='A Python package that reminds developers to take breaks',
    author='Anil Thapa',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'plyer',
        'playsound',
        'importlib_resources; python_version<"3.9"'
    ],
    entry_points={
        'console_scripts': [
            'devremind1 = devremind1.__main__:main',
        ],
    },
    package_data={
        'devremind1': ['alarm.mp3'],
    },
)
