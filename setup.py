# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, find_namespace_packages

import os
from os.path import join
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np


DESCRIPTION = 'Impulse responses creation for room reverberation'
LONG_DESCRIPTION = """
    This package contains methods for room impulse responses creation
    """


# directory_path = os.path.dirname(
#     os.path.abspath(__file__)
#     )


# ext_data = {
#     'pynoverb.reverbs': {
#         'sources': [join('pynoverb', 'reverbs.pyx')],
#         'include': [np.get_include()]}
# }


extensions = []

# for name, data in ext_data.items():

#     sources = data['sources']
#     include = data.get('include', [])

#     obj = Extension(
#         name,
#         sources=sources,
#         include_dirs=include
#     )
    
#     extensions.append(obj)

extensions.append(Extension(name='pynoverb.reverbs',sources=['pynoverb/reverbs.pyx'],include_dirs=np.get_include()))

# Setting up
setup(
    name="pynoverb",
    version='0.0.0',
    author="Olivier Doaré",
    author_email="<olivier.doare@ensta-paris.fr>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    package_data={'pynoverb': ['hrtf/mit_kemar/*.wav']},
    include_package_data=True,
    install_requires=['numpy','scipy'],
    keywords=['Python', 'Binaural processing', 'Signal processing', 'Artificial reverberation'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3"
        ]
)
