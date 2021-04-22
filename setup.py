import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cubix",
    version="1.0.4",
    author="Martin Campos",
    author_email="tinotinocampos@gmail.com",
    description="Persistent homology for data clouds using KDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doctorfields/Cubix",
    packages=["cubix"],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
