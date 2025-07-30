from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))
# Załaduj zawartość README.md
with open(path.join(working_directory,'README.md'), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='RdLib',
    version='0.9',
    description='Simple library to communicate with Rd03D and HLK-LD2450 radar via serial on Raspberry Pi',
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    author='G20Michu',
    author_email='G20Michu@proton.me',
    url='https://github.com/G20Michu/RdLib',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
