# Setup file for pip installation
# Setup file for pip installation

from setuptools import setup, find_packages

# To Load the README file to use as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sfn_blueprint",
    version="0.5.7",  # validation release version
    author="Rajesh Darak",
    author_email="rajesh@stepfuction.ai",
    description="sfn-blueprint is a modular framework that enables rapid building of AI Agents, offering both flexibility and ease of customization.",
    long_description=long_description,  # Using README.md as long description
    long_description_content_type="text/markdown",  # README file format
    url="https://github.com/iamrajeshdaraksfn/sfn_blueprint",  # Github URL
    packages=find_packages(),  # This will Automatically find and include packages
    include_package_data=True,  # To Ensure non-Python files are included
    package_data={
        "sfn_blueprint": [
            "config/prompts_config.json",
            "config/config.json"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # License
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # Required Python version
    install_requires=[
        # List of dependencies required for this package
        'numpy>=1.26.4',
        'openai>=1.54.4',
        'python-dotenv>=1.0.0',
        'streamlit>=1.39.0',
        'textblob>=0.18.0.post0',
        'scikit-learn>=1.5.2',
        'nltk>=3.9.1',
        'spacy>=3.8.2',
        'pyyaml>=6.0',
        'pytest>=8.3.4',
        'cloudpickle>=2.0.0,!=2.1.0,!=2.2.0,<=2.2.1', # to resolve dependency conflict between snowflake and dask, installing cloudpickle manually with specified version.
        'dask[dataframe]>=2024.8.0',
        'dask[delayed]>=2024.8.0',
        'openpyxl>=3.1.5',
        'snowflake-connector-python>=3.12.3',
        'snowflake-ml-python>=1.7.0',
        'snowflake-snowpark-python>=1.23.0',
        'sfn-llm-client>=0.1.2'
        ]
)