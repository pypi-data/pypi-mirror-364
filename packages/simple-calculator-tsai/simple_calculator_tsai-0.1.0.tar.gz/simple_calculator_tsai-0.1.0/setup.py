from setuptools import setup, find_packages

setup(
    name="simple-calculator-tsai",
    version="0.1.0",
    description="A simple calculator package with basic arithmetic operations.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=["simple_calculator_tsai"],
    install_requires=[],
    python_requires=">=3.6",
    url="https://pypi.org/project/simple-calculator-tsai/",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 