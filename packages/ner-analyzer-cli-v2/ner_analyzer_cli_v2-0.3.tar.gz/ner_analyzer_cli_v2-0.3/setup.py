from setuptools import setup, find_packages
import os

# Get the current directory
this_dir = os.path.abspath(os.path.dirname(__file__))

# Read the README.md for long_description
readme_path = os.path.join(this_dir, "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name='ner_analyzer_cli_v2',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'spacy>=3.0.0',
    ],
    entry_points={
        'console_scripts': [
            'ner-analyze=ner_analyzer.cli:main',
        ],
    },
    author='Your Name',
    description='NER analyzer package with CLI and export options',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Linguistic',
    ],
    python_requires='>=3.7',
)
