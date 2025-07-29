from setuptools import setup, find_packages

setup(
    name='scripbox',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'scripbox = scripbox.cli:main',
        ],
    },
    author='YASHWANTH BR',
    description='A CLI tool for logging into Scripbox',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/YBR1104/scripbox',
    classifiers=[	
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)

