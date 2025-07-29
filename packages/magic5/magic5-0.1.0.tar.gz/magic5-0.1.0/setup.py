from setuptools import setup, find_packages

setup(
    name='magic5',
    version='0.1.0',
    packages=find_packages(),
    description='Utility package importing numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns, and scikit-learn with common aliases',
    author='Francesco Scolz',
    author_email='francesco.scolz@gmail.com',
    url='https://github.com/FreyFly/magic5',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scikit-learn',
    ],
)
