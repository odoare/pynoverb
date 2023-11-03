# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

DESCRIPTION = 'Impulse responses creation for room reverberation'
LONG_DESCRIPTION = """
    This package contains methods for room impulse responses creation
    """

# Setting up
setup(
    name="pynoverb",
    version='0.0.0',
    author="Olivier Doaré",
    author_email="<olivier.doare@ensta-paris.fr>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'pynoverb': ['hrtf/mit_kemar/*.wav']},
    include_package_data=True,
    install_requires=['numpy','scipy','numba'],
    keywords=['Python', 'Binaural processing', 'Signal processing', 'Artificial reverberation'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3"
        ]
)
