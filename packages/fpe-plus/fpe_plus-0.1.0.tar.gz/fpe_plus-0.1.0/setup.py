from setuptools import setup, find_packages

setup(
    name="fpe_plus",
    version="0.1.0",
    author="Vasudev Jaiswal",
    author_email="vasudevjaiswal786@gmail.com",
    description="Format Preserving Encryption with support for dates, numbers, floats, and strings with any character",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vasudevjaiswal/fpe_plus",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)