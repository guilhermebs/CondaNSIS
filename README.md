CondaNSIS
==========

[![Test and Release](https://github.com/guilhermebs/CondaNSIS/actions/workflows/main.yml/badge.svg)](https://github.com/guilhermebs/CondaNSIS/actions/workflows/main.yml)

[CondaNSIS](https://guilhermebs.github.io/CondaNSIS/) packages Python applications into self-extracting installers for **Windows** by leveraging both [conda-pack](https://conda.github.io/conda-pack/) and [NSIS](https://nsis.sourceforge.io/Main_Page).

This project is inspired by [PyNSIST](https://pynsist.readthedocs.io/en/latest/).

Why?
----
Bundlers such as [PyInstaller](https://www.pyinstaller.org/) are great for small apps, but often have problems packaging complex projects with many dependencies.
Alternativelly, deployment with [Conda](https://docs.conda.io/en/latest/) can be difficult as as it requires an Anaconda or a Miniconda installation.

CondaNSIS solves this problem by packaging your Python app together with a **local** and **isolated** Python environment, such that the target computer does not need neither Python nor a Conda already installed.

Installation
------------
CondaNSIS is avaliable through conda-forge

```
conda install -c conda-forge condansis
```

Usage
------
Please see the [documentation page](http://guilhermebs.github.io/CondaNSIS)

Developers
-----------
Guilherme Bicalho Saturnino (guisa@orsted.dk)
