from setuptools import setup, find_packages

setup(
    name="plasmidhub",
    version="1.0.0",
    author="Dr. Balint Timmer",
    author_email="timmer.balint@med.unideb.hu",
    description="Plasmidhub: Bioinformatic Tool for Plasmid Network Analysis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/Plasmidhub",  # Replace with actual URL when ready
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "biopython>=1.80",
        "pandas>=1.3",
        "networkx>=3.0",
        "matplotlib>=3.5",
        "python-louvain>=0.16",
        "numpy>=1.20"
    ],
    entry_points={
        "console_scripts": [
            "plasmidhub=plasmidhub.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update if you use another license
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    python_requires='>=3.8',
)