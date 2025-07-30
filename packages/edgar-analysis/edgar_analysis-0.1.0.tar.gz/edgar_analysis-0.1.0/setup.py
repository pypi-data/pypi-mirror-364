"""setup.py"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='edgar_analysis',
    version='0.1.0',
    author='Jonas Bergstrom',
    author_email='gafzan@gmail.com',
    description='A package for analyzing EDGAR financial statements for companies',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gafzan/edgar_analysis',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    python_requires='>=3.8',
    install_requires=[
        'pandas==2.3.0',
        'numpy==2.3.1',
        'dateparser==1.2.2',
        'edgartools==4.3.1',
        'yfinance==0.2.64',
        'tqdm>=4.0,<5.0',
        'pydantic==2.11.7'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)