from setuptools import setup, find_packages

setup(
    name="research_analyzer",
    version="0.1.0",
    description="Universal, domain-agnostic research analysis toolkit for extracting insights from textual datasets.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "pyyaml",
        "nltk",
        "spacy",
        # Add more as needed for full functionality
    ],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 