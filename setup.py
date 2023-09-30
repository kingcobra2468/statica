#!/usr/bin/python3
from setuptools import setup, Extension
import os

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources

    return extensions


extensions = [
    Extension("statica.file.encoder", ["src/statica/file/encoder.pyx"]),
    Extension("statica.file.decoder", ["src/statica/file/decoder.pyx"]),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None


if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")


setup(
    ext_modules=extensions,
    install_requires=install_requires,
    extras_require={
        'test': [
            'pytest==7.0.1',
            'pytest-parallel==0.1.1'    
        ],
    }
)
