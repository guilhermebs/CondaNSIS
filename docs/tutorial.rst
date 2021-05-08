Tutorial
=========

In this tutorial, we will show how to package a simple script with CondaNSIS to make it available on computers without conda installed.


Creating an installer for a script
-----------------------------------

We want to distribute a script called :download:`snake.py <../example/script/snake.py>`, that prints a snake in the terminal for 10 seconds.

.. literalinclude:: ../example/script/snake.py

We also define the environment for our script in the `conda environment file <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment>`_ :download:`environment.yml <../example/script/environment.yml>` file below.

.. literalinclude:: ../example/script/environment.yml

Finally, we write a small :download:`script <../example/script/create_installer.py>` to tell CondaNSIS how to put together the installer.

.. literalinclude:: ../example/script/create_installer.py

In this example, we are using 2 special variables:

* :code:`$INSTDIR` will be resolved to the full path to the installation directory. This and many other variables are standard in `NSIS <https://nsis.sourceforge.io/Docs/Chapter4.html#variables>`_ and can be used to setup installers in CondaNSIS.
* :code:`$PYTHON` will be resolved the full path to the python interpreter in the target machine. This is a special variable provided by CondaNSIS.

Additionally, CondaNSIS also provides the variables:

* :code:`$PYTHONW`: local :file:`pythonw.exe` interpreter in target machine.
* :code:`$ENV`: Name of conda environment folder in target machine.

The :ref:`API <api>` documentation gives a complete description of the :meth:`Installer <condansis.Installer>` class and :meth:`add_shortcut <condansis.Installer.add_shortcut>` method.


Creating an installer for a package
-----------------------------------

Development of our snake simulator package is coming along and we have now created a nice `Python package <https://github.com/guilhermebs/CondaNSIS/tree/main/example/package>`_, sourced an icon, and structured it such as:

::

  package
  ├── snake
  │ ├── __init__.py
  │ └── snake.py
  ├── resources
  │ └── snake.ico
  ├── setup.py
  └── environment.yml



When installed using :code:`pip` or :code:`python setup.py`, this package creates an entrypoint called :file:`snake.exe`. We now want to create an installer for our package which will give easy access to this entrypoint.
For that, we write the :download:`Python script <../example/package/create_installer.py>` below

.. literalinclude:: ../example/package/create_installer.py