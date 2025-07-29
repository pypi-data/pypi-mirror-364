from setuptools import setup, find_packages

setup(
    name="tensor-schema",
    version="0.1.0",
    description="A lightweight shape validation system for multimodal tensors",
    author="Benji Beck",
    author_email="",
    url="https://github.com/bbeckca/tensor-schema",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "torch>=1.13",
        "typing_extensions>=4.5.0",  # for Annotated on older Python versions
    ],
)