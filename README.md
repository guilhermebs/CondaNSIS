CondaNSIS
==========

CondaNSIS is a solution to package Python applications into self-extracting installers by leveraging both [conda-pack](https://conda.github.io/conda-pack/) and [NSIS](https://nsis.sourceforge.io/Main_Page).
This project is inspired by [PyNSIST](https://pynsist.readthedocs.io/en/latest/).

Why?
----
PyInstaller is great for small apps, but it has problems packaging complex projects with many dependencies.
However, deployment with conda can be difficult as environments are managed globally and [things can get very confusing](https://xkcd.com/1987/), especially if the application is deployed to users' computers and they have the added responsibility of managing their own environments.
CondaNSIS solves this problem by providing a way to package your Python app together with a **local** and **isolated** Python environment, such that the target computer does not even need conda to run it!

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