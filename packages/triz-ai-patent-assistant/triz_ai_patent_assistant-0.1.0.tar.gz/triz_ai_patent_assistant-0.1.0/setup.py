from setuptools import setup, find_packages

setup(
    name="triz_ai_patent_assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "openai",
        "pymystem3",
        "pytest"
    ],
    author="Voronin Sergei",
    description="AI + TRIZ system for patent formula generation and analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)