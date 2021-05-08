Known Issues and Limitations
============================

CondaNSIS does **not** support:

* `Environment variable settings <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#setting-environment-variables>`_.
* Bundling files outside the package root.
* Copying files to outside the installation directory (can be done in a post-processing step).
* Conda `activate scripts <https://docs.conda.io/projects/conda-build/en/latest/resources/activate-scripts.html>`_.