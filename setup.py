"""Python packaging for PDBx/mmCIF utilities."""
import setuptools
import versioneer

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="mmcif_pdbx",
    version=versioneer.get_version(),
    author="John Westbrook",
    author_email="jwest@rcsb.rutgers.edu",
    maintainer="Nathan Baker",
    maintainer_email="nathanandrewbaker@gmail.com",
    description="Python utilities for PDBx/mmCIF storage model",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/Electrostatics/mmcif_pdbx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.6",
    tests_require=["pytest"],
    test_suite="tests",
    zip_safe=True,
)
