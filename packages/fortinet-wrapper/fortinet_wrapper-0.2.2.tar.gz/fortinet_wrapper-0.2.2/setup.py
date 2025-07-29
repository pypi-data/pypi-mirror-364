"""Setup script for the Fortinet wrapper package."""

from setuptools import find_packages, setup

setup(
    name="fortinet_wrapper",
    version="0.2.2",
    description="A Python wrapper for Fortinet API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="HBNet Networks",
    author_email="dev@hbnet.tech",
    url="https://github.com/HBNetNetworks/fortinet-wrapper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.4",
        # Add other runtime dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    license="GPLv3",
)
