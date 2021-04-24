import os
from pathlib import Path
import subprocess
import pytest
import tempfile
import shutil

import conda_pack

from .installer import Installer

TEST_FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_files"))


@pytest.fixture
def env_file(self):
    pass


class TestInstaller:
    def test_init_installer(self):
        installer = Installer(
            "package",
            TEST_FILES_DIR,
            package_version="0.1",
            installer_name=None,
            default_install_dir=None,
            include=None,
            icon=None,
            postinstall_python_scripts=None,
            preuninstall_python_scripts=None,
            env_file=None,
            env_name=None,
            nsis_template=None,
            clean_instdir=False,
            register_uninstaller=True,
            compressor="lzma",
            makensis_exe=None,
        )
        assert installer.package_name == "package"
        assert installer.package_root == Path(TEST_FILES_DIR).resolve()
        assert installer.installer_name == os.path.abspath("install_package-0.1.exe")
        assert installer.default_install_dir == Path("$PROFILE", "package")
        assert installer.include == []
        assert installer.icon is None
        assert installer.postinstall_python_scripts == []
        assert installer.preuninstall_python_scripts == []
        assert os.path.samefile(installer.env_file, os.path.join(TEST_FILES_DIR, "environment.yml"))
        assert installer.env_name == "package_env"
        assert os.path.isfile(installer.nsis_template)

    def test_create_temp_env(self, monkeypatch):
        def mock_run(args, check):
            os.makedirs(os.path.join(args[args.index("-p") + 1], "Lib", "site-packages"))

        monkeypatch.setattr(subprocess, "run", mock_run)
        installer = Installer("package", ".", install_root_package=False)
        with tempfile.TemporaryDirectory() as env_prefix:
            env_prefix = Path(env_prefix)
            installer.create_temp_env(env_prefix)
            assert (
                env_prefix / "Lib" / "site-packages" / "sitecustomize.py"
            ).is_file()

    def test_pack_temp_env(self, monkeypatch):
        class MockCondaEnv:
            @staticmethod
            def pack(packed_env):
                shutil.make_archive(
                    str(packed_env)[:-4],
                    "tar",
                    TEST_FILES_DIR,
                    TEST_FILES_DIR,
                )

        def mock_from_prefix(*args, **kwargs):
            return MockCondaEnv()

        monkeypatch.setattr(conda_pack.CondaEnv, "from_prefix", mock_from_prefix)
        installer = Installer("package", ".")
        with tempfile.TemporaryDirectory() as work_dir:
            work_dir = Path(work_dir)
            with tempfile.TemporaryDirectory() as env_prefix:
                env_prefix = Path(env_prefix)
                installer.pack_temp_env(work_dir, env_prefix)
                assert (work_dir / installer.env_name).is_dir()
                assert not env_prefix.with_suffix(".tar").exists()

    def test_create_app_dir(self):
        installer = Installer(
            "package", TEST_FILES_DIR, include=["environment.yml", "package_folder"]
        )
        with tempfile.TemporaryDirectory() as work_dir:
            installer.create_app_dir(Path(work_dir))
            assert os.path.exists(
                os.path.join(work_dir, "package_folder", "package_file.py")
            )

    def test_create_nsis_script(self):
        installer = Installer(
            "package", TEST_FILES_DIR, include=["environment.yml", "package_folder"]
        )
        with tempfile.TemporaryDirectory() as work_dir:
            script_name = installer.create_nsis_script(Path(work_dir))
            file_contents = open(script_name, "r").read()
            assert "package_folder" in file_contents
            assert "environment.yml" in file_contents
