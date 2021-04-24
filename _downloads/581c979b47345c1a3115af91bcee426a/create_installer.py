from pathlib import Path
import condansis

if __name__ == "__main__":
    this_dir = Path(__file__).parent

    # instantiate Installer
    installer = condansis.Installer(
        package_name="snake-simulator",
        package_root=this_dir,
        package_version="1.0",
        include=["resources"],
        icon=Path("resources", "snake.ico"),
    )

    # Create a shortcut in the snake.exe entrypoint
    # In the target computer, entrypoints can be found at
    # $INSTDIR\$ENV\Scripts
    installer.add_shortcut(
        shortcut_name=Path("$INSTDIR", "snake.lnk"),
        target_file=Path("$INSTDIR", "$ENV", "Scripts", "snake.exe"),
        icon_file=Path("$INSTDIR", "resources", "snake.ico"),
    )

    # Create the installer
    installer.create()
