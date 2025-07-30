# """
# to create pip package
# install twine
# pip install twine
# python setup.py sdist bdist_wheel
# twine upload dist/*
# """
# import setuptools
# import os
#
# # Define the path to the directory containing setup.py
# lib_folder = os.path.dirname(os.path.realpath(__file__))
#
# # Read the contents of your README file
# with open(os.path.join(lib_folder, 'digitalarzengine', 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()
#
# # Path to the requirements file
# requirement_path = os.path.join(lib_folder, 'digitalarzengine/requirements.txt')
# install_requires = []  # List to store requirements
#
# # Read the requirements file and populate the install_requires list
# if os.path.isfile(requirement_path):
#     with open(requirement_path) as f:
#         install_requires = f.read().splitlines()
#
# # Version of the package`
# VERSION = '0.2.0'
# # Short description of the package
# DESCRIPTION = 'DigitalArzEngine for GEE, raster and vector data processing'
#
# # Configuration of package setup
# setuptools.setup(
#     name="digitalarzengine",
#     version=VERSION,
#     author="Ather Ashraf",
#     author_email="atherashraf@gmail.com",
#     description=DESCRIPTION,
#     long_description=long_description,
#     long_description_content_type='text/markdown',
#     python_requires='>=3',
#     install_requires=install_requires,
#     packages=setuptools.find_packages(),
#     include_package_data=True,  # Include package data
#     package_data={},
#     keywords=['raster', 'vector', 'digitalarz'],
#     classifiers=[
#         "Development Status :: 1 - Planning",
#         "Intended Audience :: Education",
#         "Programming Language :: Python :: 3",
#         "Operating System :: MacOS :: MacOS X",
#         "Operating System :: Microsoft :: Windows",
#     ]
# )
#

import setuptools
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(lib_folder, 'digitalarzengine', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Prefer listing install_requires directly for better control
requirement_path = os.path.join(lib_folder, 'digitalarzengine/requirements.txt')
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = [line.strip() for line in f if line and not line.startswith("#")]

setuptools.setup(
    name="digitalarzengine",
    version='0.2.2.1',
    author="Ather Ashraf",
    author_email="atherashraf@gmail.com",
    description="DigitalArzEngine for GEE, raster and vector data processing",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=install_requires,
packages=setuptools.find_packages(exclude=["digitalarzengine.tests", "digitalarzengine.tests.*"]),
    include_package_data=True,
    keywords=['raster', 'vector', 'digitalarz'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
