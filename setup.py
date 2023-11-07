# -*- coding: utf-8 -*-
# setup.py
#
# -------------------------------------------------
# Python functions to create room impulse responses
# -------------------------------------------------
#
# Part of pynoverb package
# (c) OD - 2023
# https://github.com/odoare/pynoverb

from setuptools import setup, find_packages

DESCRIPTION = 'Impulse responses creation for room reverberation'
LONG_DESCRIPTION = """
    This package contains methods for room impulse responses creation
    """

# Setting up
setup(
    name="pynoverb",
    version='0.0.1',
    author="Olivier Doaré",
    url='https://github.com/odoare/pynoverb'
    author_email="<olivier.doare@ensta-paris.fr>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'pynoverb': ['hrtf/mit_kemar/*.wav']},
    include_package_data=True,
    install_requires=['numpy','numba'],
    keywords=['Python', 'Binaural processing', 'Signal processing', 'Artificial reverberation'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3"
        ]
)
