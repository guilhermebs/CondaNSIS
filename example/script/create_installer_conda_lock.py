"""
This example creates and environment based in a conda-lock file (https://github.com/conda-incubator/conda-lock)
"""

import os
import condansis

if __name__ == "__main__":
    this_dir = os.path.dirname(__file__)

    # instantiate Installer
    installer = condansis.Installer(
        package_name="snake-simulator",
        package_root=this_dir,
        package_version="0.2",
        include=["snake.py"],
        install_root_package=False,  # do not run pip install in the package root
        env_file=os.path.join(this_dir, "conda-win-64.lock"),
        conda_command="conda"  # To use a conda-lock file, we need to overwrite the default ("conda-env")
    )

    # Create a shortcut in the install directory to run
    # $PYTHON $INSTDIR\snake.py
    # where $PYTHON is the path to the interpreter after installation
    installer.add_shortcut(
        shortcut_name=os.path.join("$INSTDIR", "snake.lnk"),
        target_file="$PYTHON",
        parameters=os.path.join("$INSTDIR", "snake.py"),
    )

    # Create the installer
    installer.create()
