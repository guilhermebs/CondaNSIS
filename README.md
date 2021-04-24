CondaNSIS
==========

CondaNSIS packages Python applications into self-extracting installers by leveraging both [conda-pack](https://conda.github.io/conda-pack/) and [NSIS](https://nsis.sourceforge.io/Main_Page).

This project is inspired by [PyNSIST](https://pynsist.readthedocs.io/en/latest/).

Why?
----
Bundlers such as [PyInstaller](https://www.pyinstaller.org/) are great for small apps, but often have problems packaging complex projects with many dependencies.
Alternativelly, deployment with [Conda](https://docs.conda.io/en/latest/) can be difficult as as it requires an Anaconda or a Miniconda installation.

CondaNSIS solves this problem by packaging your Python app together with a **local** and **isolated** Python environment, such that the target computer does not need neither Python nor a Conda already installed.

Installation
------------
TODO

Usage
------
TODO: Link to docs

How it works
------------
CondaNSIS will:

1. Create the conda environment described in the package's environment.yml in a temporary directory
2. Isolate the environment using conda-pack
3. Package the isolated environment together with any extra files in a self-extracting executable using NSIS


FAQ
----
* Can I execute the installer silently without the GUI?
    
    Yes, just use the `/S` switch. Please refer to the [NSIS documentation](https://nsis.sourceforge.io/Docs/Chapter3.html) for more options


Developers
-----------
Guilherme Bicalho Saturnino (guisa@orsted.dk)
