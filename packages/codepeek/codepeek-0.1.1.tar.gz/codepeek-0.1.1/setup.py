from setuptools import setup, find_packages

setup(
    name='codepeek',
    version='1.0.0',
    description='Extract and visualize code structure from GitHub repositories.',
    author='Ahmed Abd Alzeez',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'codepeek=codepeek.cli:main',
        ],
    },
    python_requires='>=3.7',
)
