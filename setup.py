import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding = 'utf-8', errors = 'ignore')

setup(
    name="orbital-sim",
    version="0.9.3",
    description="A simple physics engine build over a PyGame simulation to model planetary orbits in space",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jasonfyw/orbital-sim",
    author="Jason Wang",
    author_email="jasonwang0610@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pygame", "astropy", "astroquery"],
    download_url="https://github.com/jasonfyw/orbital-sim/archive/v0.9.2.tar.gz"
)