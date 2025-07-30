from setuptools import setup, find_packages

setup(
    name='devremind1',  # <-- Changed here
    version='0.1.3',
    description='A Python package that reminds developers to take breaks',
    author='Anil Thapa',
    author_email='anilthapa4200@gmail.com',
    packages=find_packages(),  # Automatically finds 'devremind1'
    include_package_data=True,
    install_requires=[
        'plyer',
        'playsound',
        'importlib_resources; python_version<"3.9"'
    ],
    entry_points={
        'console_scripts': [
            'devremind1=devremind1.__main__:main',  # CLI command
        ],
    },
    package_data={
        'devremind1': ['alarm.mp3'],
    },
)
