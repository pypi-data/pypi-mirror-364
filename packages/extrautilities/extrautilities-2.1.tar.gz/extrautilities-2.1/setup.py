from setuptools import setup, find_packages

setup(
    name='extrautilities',
    version='2.1',
    packages=find_packages(),
    description='This package provides a few extra utilities for Python, like Asyncronus Encryption/Decryption.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='RandomTimeTV',
    author_email='dergepanzerte1@gmail.com',
    license='Unlicensed',
    url='https://github.com/RandomTimeLP/ExtraUtils',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='RateLimit, timeBasedToken, getFileContent, callbackVoid, validate_dict',
    install_requires=["extradecorators", "cryptography","pycryptodome"],
)