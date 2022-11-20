from setuptools import setup, Extension

sfc_module = Extension('OldScoreBoard', sources=['module.cpp'])

setup(
    name='OldScoreBoard',
    version='1.0',
    description='Provides a fast score board function',
    ext_modules=[sfc_module]
)
