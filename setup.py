from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

# and version from the _version.py file
version=open(os.path.join(here,"condansis", "_version.py")).readlines()[-1].split()[-1].strip("\"'")

setup(
    name="condansis",
    version=version,
    description="Create installers for Python packages using NSIS and Conda",
    long_description=open(os.path.join(here, 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="http://guilhermebs.github.io/condansis",
    author="Guilherme Saturnino",
    author_email="GUISA@orsted.dk",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="packaging, installer, windows",
    packages=find_packages(),
    python_requires=">=3.5, <4",
    install_requires=["conda-pack>=0.5", "jinja2"],
    extras_require={
        "test": ["pytest"],
    },
    package_data={
        "condansis": ["*.nsi", "test_files/*"],
    },
)
