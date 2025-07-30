from setuptools import setup, find_packages

setup(
    name='devremind1',
    version='0.1.1',  
    description='A Python package that reminds developers to take breaks',
    author='Anil Thapa',
    packages=find_packages(),
    include_package_data=True,  
    install_requires=[
        'plyer',
        'playsound',
    ],
    entry_points={
        'console_scripts': [
            'devremind1 = devremind1.__main__:main',
        ],
    },
    package_data={
        'devremind1': ['alarm.mp3'],  # ✅ Include MP3 in the package
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',
)
