.. CondaNSIS documentation master file, created by
   sphinx-quickstart on Tue Feb 23 11:52:35 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CondaNSIS
=====================================

CondaNSIS is a flexible and reliable way to deploy Python apps to **Windows** computers without any Python interpreters or environment managers.

It packages your Python applications together with its conda environment into a self-extracting installer by using `conda-pack <https://conda.github.io/conda-pack/>`_ to package a conda environment and `NSIS <https://nsis.sourceforge.io/Main_Page>`_ to build a self-extracting installer.
This project is inspired by `PyNSIST <https://pynsist.readthedocs.io/en/latest/>`_, with an added conda twist.

Why?
----
Bundlers such as `PyInstaller <https://www.pyinstaller.org/>`_ are great for small apps, but often have problems packaging complex projects with many dependencies.
Alternativelly, deployments with `Conda <https://docs.conda.io/en/latest/>`_ can be difficult as as it requires an Anaconda or a Miniconda installation.

CondaNSIS solves this problem by packaging your Python app together with a **local** and **isolated** Python environment, such that the target computer does not need neither Python nor a Conda already installed.


Installation
-------------
To install CondaNSIS with all required dependencies, get it from the `conda-forge` channel

.. code::

   conda install -c conda-forge condansis


Documentation
---------------

.. toctree::
   :maxdepth: 1
   
   tutorial
   api
   limitations
   changelog