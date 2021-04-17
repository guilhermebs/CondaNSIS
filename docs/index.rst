.. CondaNSIS documentation master file, created by
   sphinx-quickstart on Tue Feb 23 11:52:35 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CondaNSIS
=====================================

CondaNSIS packages your Python applications together with its conda environment into a self-extracting installer.
It aims to be a reliable and flexible way to deploy Python apps to Windows computers without any Python interpreters or environment managers.


Use cases
----------
* Creating an installer for a local Python application 
* Deploying Python applications in a highly reproducible fashion
* Archiving applications for full reproducibility

Installation
-------------
TODO

How does it work?
-------------------
CondaNSIS uses `conda-pack <https://conda.github.io/conda-pack/>`_ to package a conda environment, and `NSIS <https://nsis.sourceforge.io/Main_Page>`_ to build a self-extracting installer with the environment, any additional files and post-install operations.
This project is inspired by `PyNSIST <https://pynsist.readthedocs.io/en/latest/>`_, with an added conda twist.


Requirements
-------------

* Conda
* Python 3


Documentation
---------------

.. toctree::
   :maxdepth: 1
   
   tutorial
   api
