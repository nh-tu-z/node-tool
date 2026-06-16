"""Setup configuration for combiner package."""


from setuptools import setup, find_packages
import os


# Read the README file for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()


# Read version from __init__.py
def get_version():
    with open(os.path.join('combiner', '__init__.py'), 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'


setup(
    name='combiner',
    version=get_version(),
    author='Combiner Contributors',
    author_email='',
    description='A tool to combine and spread files across directories',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/combiner',  # Update with your repo URL
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
    install_requires=[
        'pathspec>=0.12.1',
        'termcolor>=2.4.0',
    ],
    entry_points={
        'console_scripts': [
            'combiner=combiner.cli:main',
        ],
    },
    keywords='file combiner spread encode decode utility',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/combiner/issues',
        'Source': 'https://github.com/yourusername/combiner',
    },
)





