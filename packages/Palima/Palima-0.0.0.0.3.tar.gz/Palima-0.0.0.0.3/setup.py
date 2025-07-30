from setuptools import setup, find_packages

with open("readme.md", "r") as f:
    description = f.read()

setup(
    name="Palima",
    version="0.0.0.0.3",
    packages=find_packages(),
    install_requires=[],
    long_description=description,
    long_description_content_type="text/markdown",
    license="FELLOS-STUDIOS Official Python Programming Group",
    Author="FELLOS-STUDIOS®",
    Author_email="fellos.studios@gmail.com"
)
