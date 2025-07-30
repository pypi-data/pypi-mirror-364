from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#with open("requirements.txt", "r", encoding="utf-8") as fh:
 #   requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="weighted_pod",
    version="0.0.22",
    author="Hakan Demir",
    author_email="muhammet.demir@ruhr-uni-bochum.de",
    description="Proper Orthogonal Decomposition with weighted inner products for CFD analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XXXXXXXXXX/weighted-pod",
    packages=find_packages(),
    classifiers=[ 
        "Topic :: Scientific/Engineering", 
    ]
    
)
