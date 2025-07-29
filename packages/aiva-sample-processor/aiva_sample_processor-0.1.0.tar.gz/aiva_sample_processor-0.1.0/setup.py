from setuptools import setup, find_packages
import os

# Read the contents of README.md file
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="aiva-sample-processor",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["generate_sample_csvs"],  # Include the script as a module
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "pysam>=0.16.0",
        "psycopg2-binary>=2.9.0",
        "tqdm>=4.62.0",
        "open-cravat>=2.2.0",
        "python-dotenv>=0.19.0",
        "aiva-vrs>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "aiva-sample-processor=generate_sample_csvs:main",
        ],
    },
    python_requires=">=3.8",
    description="OpenCRAVAT CSV processor for generating sample CSVs for aiva-database import",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mamidi Health",
    author_email="info@mamidi.co.in",
    url="https://github.com/MHSPL/aiva-sample-processor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
