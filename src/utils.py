import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

def get_config_path() -> str:
    home_dir = Path.home()
    config_dir = home_dir / ".config" / "dev_environment_enabler"
    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / "config.json")


def detect_os() -> str:
    os_name = platform.system().lower()
    if os_name == "darwin":
        return "macos"
    if os_name.startswith("win"):
        return "windows"
    return "linux"


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(
    command: list[str],
    *,
    check: bool = False,
    dry_run: bool = False,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str] | None:
    if dry_run:
        return None

    return subprocess.run(
        command,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def detect_package_manager(os_name: str) -> str | None:
    if os_name == "windows":
        for manager in ["winget", "choco", "scoop"]:
            if command_exists(manager):
                return manager
        return None

    if os_name == "macos":
        return "brew" if command_exists("brew") else None

    linux_managers = ["apt", "dnf", "yum", "pacman", "zypper"]
    for manager in linux_managers:
        if command_exists(manager):
            return manager
    return None


def build_install_command(package_manager: str, package: str) -> list[str]:
    install_commands = {
        "winget": ["winget", "install", "--id", package, "--silent", "--accept-source-agreements", "--accept-package-agreements"],
        "choco": ["choco", "install", package, "-y"],
        "scoop": ["scoop", "install", package],
        "brew": ["brew", "install", package],
        "apt": ["sudo", "apt", "install", "-y", package],
        "dnf": ["sudo", "dnf", "install", "-y", package],
        "yum": ["sudo", "yum", "install", "-y", package],
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", package],
        "zypper": ["sudo", "zypper", "install", "-y", package],
    }
    if package_manager not in install_commands:
        raise ValueError(f"Unsupported package manager: {package_manager}")
    return install_commands[package_manager]


def get_vscode_settings_path() -> Path:
    os_name = detect_os()
    home = Path.home()
    if os_name == "windows":
        app_data = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        return Path(app_data) / "Code" / "User" / "settings.json"
    if os_name == "macos":
        return home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
    return home / ".config" / "Code" / "User" / "settings.json"


def merge_json_file(file_path: Path, update_payload: dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as existing_file:
            try:
                current_data = json.load(existing_file)
            except json.JSONDecodeError:
                current_data = {}
    else:
        current_data = {}

    current_data.update(update_payload)

    with file_path.open("w", encoding="utf-8") as output_file:
        json.dump(current_data, output_file, indent=2)


def write_file(file_path: Path, content: str, overwrite: bool = False) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists() and not overwrite:
        return
    file_path.write_text(content, encoding="utf-8")