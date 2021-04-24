from typing import List, Sequence, Union
from pathlib import Path
import os
import subprocess
import shutil
import tempfile
import logging
from dataclasses import dataclass

from jinja2 import Template
import conda_pack

SITECUSTOMIZE = (Path(__file__).parent / "sitecustomize.py").resolve()
NSIS_TEMPLATE = (Path(__file__).parent / "installer_template.nsi").resolve()

try:
    CONDA_EXE = os.environ["CONDA_EXE"]
except KeyError:
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Python\ContinuumAnalytics", winreg.KEY_READ
        ) as reg:
            conda_install_dir = winreg.QueryValue(
                reg, os.path.join(winreg.EnumKey(reg, 0), "InstallPath")
            )
            CONDA_EXE = Path(conda_install_dir, "Scripts", "conda.exe")

    except (ImportError, WindowsError):
        CONDA_EXE = "conda"

logging.basicConfig(
    format="CondaNSIS - %(levelname)s: %(message)s ", level=logging.INFO,
)


@dataclass
class _shortcut:
    """ See https://nsis.sourceforge.io/Reference/CreateShortCut """

    shortcut_name: Union[str, Path]
    target_file: Union[str, Path]
    parameters: str = ""
    icon_file: Union[str, Path] = ""


class Installer:
    r""" Defines an installer for a Python package and its environment 

    Parameters
    ------------
    package_name: str
        Name of the package

    package_root: str or Path
        Path to the package root
   
    package_version: str (optional)
        Version of the package. Default: None

    installer_name: str or Path (optional)
        Name of the installer to output. Default: install_{package_name}-{package_version}.exe
    
    default_install_dir: str or Path (optional)
        Default install directory in target computer.
        Accepts `NSIS variables <https://nsis.sourceforge.io/Docs/Chapter4.html#variables>`_
        Default: %USERPROFILE%\\package_name

    include: list of str or Path (optional)
        List of directories and files to be included in the installer. Should be relative to package_root
    
    icon: str or Path (optional)
        Path to installer icon, relative to package_root
    
    postinstall_python_scripts: list of str (optional)
        List of commands to be run in Python on the target machine after installation.
        Accepts `NSIS variables <https://nsis.sourceforge.io/Docs/Chapter4.html#variables>`_

    preuninstall_python_scripts: list of str (optional)
        List of commands to be run in Python on the target machine before uninstall
        Accepts `NSIS variables <https://nsis.sourceforge.io/Docs/Chapter4.html#variables>`_

    env_file: str or Path (optional)
        YML file with app environment. Default: :file:`package_root/environment.yml`

    install_root_package: bool (optional)
        Whether to run :code:`pip install package_root`. Default: True

    env_name: str (optional)
        Name of the python environment in the target machine. Default: {package_name}_env
   
    nsis_template: str or Path (optional)
        Path to Jinja2 NSIS template to be used. Defaults to the CondaNSIS default script

    clean_instdir: bool (optional)
        Whether to clean the install directory before installing new files. Default: False

    register_uninstaller: bool (optional)
        Whether to register the uninstaller to Windows' "add or remove programs". Default: True

    compressor: 'zlib', 'bzip2', or 'lzma' (optional)
        Compression algorithm to use. Default: lzma
        `See here for more information <https://nsis.sourceforge.io/Reference/SetCompressor>`_

    makensis_exe: str or Path (optional)
        Call to the makensis.exe executable. Defaults to "makensis"
    """

    def __init__(
        self,
        package_name: str,
        package_root: Union[str, Path],
        package_version: str = None,
        installer_name: Union[str, Path] = None,
        default_install_dir: Union[str, Path] = None,
        include: Sequence[Union[str, Path]] = None,
        icon: Union[str, Path] = None,
        postinstall_python_scripts: Sequence[str] = None,
        preuninstall_python_scripts: Sequence[str] = None,
        env_file: Union[str, Path] = None,
        env_name: str = None,
        install_root_package: bool = True,
        nsis_template: Union[str, Path] = None,
        clean_instdir: bool = False,
        register_uninstaller: bool = True,
        compressor: str = "lzma",
        makensis_exe: Union[str, Path] = "makensis",
    ) -> None:

        self.package_name = package_name
        self.package_version = package_version
        self.package_root = Path(package_root).resolve()
        self.icon = icon

        if installer_name is None:
            self.installer_name = os.path.abspath(f"install_{package_name}-{package_version}.exe")
        else:
            self.installer_name = os.path.abspath(installer_name)

        if include is None:
            self.include = []
        else:
            self.include = include

        if postinstall_python_scripts is None:
            self.postinstall_python_scripts = []
        else:
            self.postinstall_python_scripts = postinstall_python_scripts

        if preuninstall_python_scripts is None:
            self.preuninstall_python_scripts = []
        else:
            self.preuninstall_python_scripts = preuninstall_python_scripts

        if default_install_dir is None:
            self.default_install_dir = Path("$PROFILE", package_name)
        else:
            self.default_install_dir = default_install_dir

        if env_file is None:
            self.env_file = self.package_root / "environment.yml"
        else:
            self.env_file = Path(env_file)

        if not self.env_file.is_file():
            raise IOError(f"Could not find environment file at {self.env_file}")

        if env_name is None:
            self.env_name = f"{package_name}_env"
        else:
            self.env_name = env_name

        if nsis_template is None:
            self.nsis_template = NSIS_TEMPLATE
        else:
            self.nsis_template = nsis_template

        if compressor not in ["zlib", "bzip2", "lzma"]:
            raise ValueError(f"Compressor must be 'zlib', 'bzip2' or 'lzma'. Got: {compressor}")

        self.compressor = compressor
        self.install_root_package = install_root_package

        self.makensis_exe = makensis_exe

        self.clean_instdir = clean_instdir
        self.register_uninstaller = register_uninstaller

        self._shortcuts = []

    @property
    def include_dirs(self) -> List[Path]:
        return [
            Path(dir_name) for dir_name in self.include if (self.package_root / dir_name).is_dir()
        ]

    @property
    def include_files(self) -> List[Path]:
        return [
            Path(file_name)
            for file_name in self.include
            if (self.package_root / file_name).is_file()
        ]

    @property
    def shortcuts(self) -> List[_shortcut]:
        return self._shortcuts

    def create_temp_env(self, env_prefix: Path) -> None:
        """ Creates a temporary environment
        
        Parameters
        -----------
        env_prefix: Path
            Directory where the environment will be created
        """
        # Create a temporary environment in a temp folder
        subprocess.run(
            [CONDA_EXE, "env", "create", "-p", env_prefix, "-f", self.env_file, "--force"],
            check=True,
        )
        # Move sitecustomize.py
        shutil.copy(SITECUSTOMIZE, env_prefix / "Lib" / "site-packages")

        if self.install_root_package:
            # run pip install on the root package directory
            subprocess.run(
                [
                    env_prefix / "python.exe",
                    "-m",
                    "pip",
                    "install",
                    self.package_root,
                    "--no-warn-script-location",
                ],
                check=True,
            )

    def pack_temp_env(
        self, work_dir: Path, env_prefix: Path, ignore_missing_files: bool = True
    ) -> None:
        """ Runs conda-pack to create the packaged environment and unpack it in the working directory

        Parameters
        -----------
        work_dir: Path
            Working directory to create installer 

        env_prefix: Path
            Directory with the conda environment
        
        ignore_missing_files: bool
            Ignore that files are missing that should be present in the conda environment as specified by the conda metadata.
            Default: True
        """
        logging.info("Running conda-pack")
        packed_env = env_prefix.with_suffix(".tar")
        try:
            conda_env = conda_pack.CondaEnv.from_prefix(
                env_prefix, ignore_missing_files=ignore_missing_files
            )
            conda_env.pack(str(packed_env))
        finally:
            self.remove_temp_env(env_prefix)
        try:
            shutil.unpack_archive(
                packed_env, work_dir / self.env_name,
            )
        finally:
            packed_env.unlink()

    def remove_temp_env(self, env_prefix: Path) -> None:
        """ Removes the temporary environment

        Parameters
        ------------
        env_prefix: Path
            Directory with the conda environment
        

        Warnings
        ----------
        Often times this function fails to remove some dlls. Investigate further
        """
        logging.info("Cleaning temporary env")
        subprocess.run(
            [CONDA_EXE, "env", "remove", "-y", "-p", env_prefix], check=True,
        )

    def create_app_dir(self, work_dir: Path) -> None:
        """ Copies all include_files to the working directory

        Parameters
        ----------
        work_dir: Path
            Working directory to create installer 

        """
        if self.icon is None:
            include_files = self.include
        else:
            include_files = self.include + [self.icon]
        for file in include_files:
            source = self.package_root / file
            destination = work_dir / file
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            elif source.is_file():
                destination.parent.mkdir(exist_ok=True)
                shutil.copy2(source, destination)
            else:
                raise IOError(f"Coud not find {source}")

    def create_nsis_script(self, work_dir: Path) -> Path:
        """ Creates the NSIS script based on the template

        Parameters
        -----------
        work_dir: Path
            Working directory to create installer

        Returns
        --------
        script_name: path
            Path to the processed makensis script
        """
        script_name = work_dir / "installer.nsi"
        with open(self.nsis_template, "r") as f:
            install_script = Template(f.read()).render(installer=self)
        with open(script_name, "w") as f:
            f.write(install_script)
        return script_name

    def run_nsis(self, script_name: Path) -> None:
        """ Runs makensis to create the installer

        Parameters
        -----------
        script_name: Path
            Path to processed NSIS script
        """
        logging.info("Running makensis")
        subprocess.run(
            [self.makensis_exe, script_name], check=True,
        )

    def create(self) -> None:
        """ Creates the installer """
        with tempfile.TemporaryDirectory() as work_dir:
            work_dir = Path(work_dir)
            env_dir = Path(tempfile.mkdtemp())
            env_prefix = env_dir / self.env_name
            self.create_temp_env(env_prefix)
            self.pack_temp_env(work_dir, env_prefix)
            shutil.rmtree(env_dir, ignore_errors=True)
            if env_dir.is_dir():
                logging.warning(f"Could not remove temporary directory: {env_dir}")
            self.create_app_dir(work_dir)
            nsis_script = self.create_nsis_script(work_dir)
            self.run_nsis(nsis_script)
            logging.info(f"Installer created at {self.installer_name}")

    def add_shortcut(
        self,
        shortcut_name: Union[str, Path],
        target_file: Union[str, Path],
        parameters: str = "",
        icon_file: Union[str, Path] = "",
    ) -> None:
        r"""  Adds a new shortcut to be written by the installer

        For more information, please see `this link <https://nsis.sourceforge.io/Reference/CreateShortCut>`_

        Parameters
        -----------
        shortcut_name: str or Path
            Full path to the shortcut in the target computer.
            Accepts `NSIS variables <https://nsis.sourceforge.io/Docs/Chapter4.htm#variables>`_
        target_file: str or Path
            Executable target for the shortcut, in target computer.
            Accepts `NSIS variables <https://nsis.sourceforge.io/Docs/Chapter4.htm#variables>`_ and
              * $PYTHON: local python interpreter in target machine
              * $PYTHONW: local pythonw.exe interpreter in target machine
              * $ENV: Name of python environment folder in target machine
        parameters: str (optional)
            Parameters for the execution of target_file. Default: ""
        icon_file: str or Path (optional)
            path to ".ico" file in target computer 

        Examples
        ---------
        create a shortcut to the python interpreter in the installation directory

        >>> installer.add_shortcut(r"$INSTDIR\\python.lnk", "$PYTHON")

        create a shortcut to execute a run_app.py, located in the "scripts" subfolder

        >>> installer.add_shortcut(r"$INSTDIR\\app.lnk", "$PYTHON", "$INSTDIR\\scripts\\run_app.py")
        """
        self._shortcuts.append(_shortcut(shortcut_name, target_file, parameters, icon_file))

