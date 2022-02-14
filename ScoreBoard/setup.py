from setuptools import setup, Extension

sfc_module = Extension('ScoreBoard', sources = ['module.cpp'])

setup(
    name='ScoreBoard',
    version='1.0',
    description='C++ extension',
    ext_modules=[sfc_module]
)