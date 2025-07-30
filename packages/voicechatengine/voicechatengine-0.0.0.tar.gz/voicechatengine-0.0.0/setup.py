from setuptools import setup, find_packages
import setuptools
import subprocess
import os

setup(
    name='voicechatengine',  # Package name
    version='0.0.0',  # Version of your package
    author='enes kuzucu',  # Your name
    
    description='A production-ready Python framework for building real-time AI voice chat applications using OpenAI s Realtime API ', 
    long_description=open('README.md').read(),  # Long description from a README file
    long_description_content_type='text/markdown',  # Type of the long description
    
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[ 'python-dotenv'],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Development status
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # License as you choose
        'Programming Language :: Python :: 3',  # Supported Python versions
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Minimum version requirement of Python
)