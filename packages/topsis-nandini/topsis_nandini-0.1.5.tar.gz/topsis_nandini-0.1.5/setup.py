
from setuptools import setup, find_packages

setup(
    name='topsis-nandini',
    version='0.1.5',
    description='TOPSIS implementation for multi-criteria decision making',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Nandini Shekhar',
    author_email='nandiniii.2404@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'topsis = topsis.__main__:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
