"""Stack Setup installer CLI.

Author: Vivek
"""

from pathlib import Path
from enum import Enum
from typing import Optional
import subprocess
import sys


def _ensure_dependencies() -> None:
    """Keep the one-command setup friction-free on a clean machine.

    Typer is the only third-party dependency. On a fresh Python install it
    will be missing, which would crash with ModuleNotFoundError before setup
    even begins. To honor the "install once, start coding" promise, install
    it automatically the first time the CLI runs.
    """
    try:
        import typer  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    print("First run: installing the CLI dependency (typer)...", flush=True)
    requirements = Path(__file__).resolve().parent.parent / "requirements.txt"
    target = ["-r", str(requirements)] if requirements.exists() else ["typer>=0.9.0"]
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", *target], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "Could not install 'typer' automatically.\n"
            "Please run:  python -m pip install -r requirements.txt\n"
            "then run this command again."
        )
        raise SystemExit(1)


_ensure_dependencies()

import typer

from utils import (
    build_install_command,
    command_exists,
    detect_os,
    detect_package_manager,
    get_vscode_settings_path,
    merge_json_file,
    run_command,
    write_file,
)

app = typer.Typer(help="Cross-platform dev environment enabler CLI")


class Profile(str, Enum):
    base = "base"
    python = "python"
    web = "web"
    java = "java"
    cpp = "cpp"
    fullstack = "fullstack"

PROFILE_TO_COMPONENTS: dict[str, list[str]] = {
    "base": ["vscode", "python", "node", "java", "cpp"],
    "python": ["vscode", "python"],
    "web": ["vscode", "node"],
    "java": ["vscode", "java"],
    "cpp": ["vscode", "cpp"],
    "fullstack": ["vscode", "python", "node", "java", "cpp"],
}

# Version policy: target the most stable, well-supported release of each tool so
# beginners and students never have to think about versions.
#   - Python : a recent stable release (3.13); skipped entirely if Python is
#              already installed (it has to be, to run this CLI)
#   - Node   : the active LTS line (most stable)
#   - Java   : the current LTS (21), the version most tutorials assume
#   - C/C++  : the platform's current stable toolchain (LLVM/Clang or GCC)
# On Windows the IDs below pin these exact lines. On macOS/Linux the package
# manager supplies its current stable equivalent.
COMPONENT_VERSION_LABELS: dict[str, str] = {
    "vscode": "VS Code (latest stable)",
    "python": "Python (latest stable)",
    "node": "Node.js (LTS)",
    "java": "Java (21 LTS)",
    "cpp": "C/C++ toolchain (stable)",
    "cmake": "CMake (latest stable)",
}

# Commands that indicate a component is already installed. If any is found, the
# component is skipped so re-running setup is safe and no second copy is added.
COMPONENT_PROBES: dict[str, list[str]] = {
    "vscode": ["code"],
    "python": ["python", "python3", "py"],
    "node": ["node"],
    "java": ["javac"],
    "cpp": ["clang++", "g++", "cl"],
    "cmake": ["cmake"],
}

PACKAGE_MAP: dict[str, dict[str, str]] = {
    "vscode": {
        "winget": "Microsoft.VisualStudioCode",
        "choco": "vscode",
        "scoop": "vscode",
        "brew": "visual-studio-code",
        "apt": "code",
        "dnf": "code",
        "yum": "code",
        "pacman": "code",
        "zypper": "code",
    },
    "python": {
        "winget": "Python.Python.3.13",
        "choco": "python",
        "scoop": "python",
        "brew": "python",
        "apt": "python3",
        "dnf": "python3",
        "yum": "python3",
        "pacman": "python",
        "zypper": "python3",
    },
    "java": {
        "winget": "EclipseAdoptium.Temurin.21.JDK",
        "choco": "temurin21",
        "scoop": "temurin-lts-jdk",
        "brew": "openjdk@21",
        "apt": "openjdk-21-jdk",
        "dnf": "java-21-openjdk-devel",
        "yum": "java-21-openjdk-devel",
        "pacman": "jdk-openjdk",
        "zypper": "java-21-openjdk-devel",
    },
    "cpp": {
        "winget": "LLVM.LLVM",
        "choco": "llvm",
        "scoop": "llvm",
        "brew": "llvm",
        "apt": "build-essential",
        "dnf": "gcc-c++",
        "yum": "gcc-c++",
        "pacman": "base-devel",
        "zypper": "gcc-c++",
    },
    "cmake": {
        "winget": "Kitware.CMake",
        "choco": "cmake",
        "scoop": "cmake",
        "brew": "cmake",
        "apt": "cmake",
        "dnf": "cmake",
        "yum": "cmake",
        "pacman": "cmake",
        "zypper": "cmake",
    },
    "node": {
        "winget": "OpenJS.NodeJS.LTS",
        "choco": "nodejs-lts",
        "scoop": "nodejs-lts",
        "brew": "node",
        "apt": "nodejs",
        "dnf": "nodejs",
        "yum": "nodejs",
        "pacman": "nodejs",
        "zypper": "nodejs20",
    },
}

PROFILE_EXTENSIONS: dict[str, list[str]] = {
    "base": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "vscjava.vscode-java-pack",
        "ms-vscode.cpptools",
        "ms-vscode.cmake-tools",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
    ],
    "python": ["ms-python.python", "ms-python.vscode-pylance", "ms-toolsai.jupyter"],
    "web": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"],
    "java": ["vscjava.vscode-java-pack"],
    "cpp": ["ms-vscode.cpptools", "ms-vscode.cmake-tools"],
    "fullstack": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "vscjava.vscode-java-pack",
        "ms-vscode.cpptools",
        "ms-vscode.cmake-tools",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-azuretools.vscode-docker",
    ],
}

DEFAULT_SETTINGS = {
    "editor.formatOnSave": True,
    "files.autoSave": "onFocusChange",
    "python.defaultInterpreterPath": "python",
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit",
    },
}


# Friendly language menu shown by the interactive setup flow. Each entry maps a
# human language name to an internal profile.
LANGUAGE_MENU: list[tuple[str, str]] = [
    ("python", "Python"),
    ("web", "JavaScript / Node.js"),
    ("java", "Java"),
    ("cpp", "C / C++"),
    ("fullstack", "Everything (all of the above)"),
]

_LANGUAGE_ALIASES = {
    "javascript": "web",
    "js": "web",
    "node": "web",
    "nodejs": "web",
    "c": "cpp",
    "c++": "cpp",
    "all": "fullstack",
}


def _prompt_for_profile() -> str:
    """Ask the user which language to set up and return the chosen profile."""
    typer.echo("Which language do you want to set up?")
    for index, (_, label) in enumerate(LANGUAGE_MENU, start=1):
        typer.echo(f"  {index}. {label}")

    while True:
        answer = typer.prompt("Enter a number or language name", default="1").strip().lower()
        if answer.isdigit():
            position = int(answer)
            if 1 <= position <= len(LANGUAGE_MENU):
                return LANGUAGE_MENU[position - 1][0]
        else:
            for profile_name, _ in LANGUAGE_MENU:
                if answer == profile_name:
                    return profile_name
            if answer in _LANGUAGE_ALIASES:
                return _LANGUAGE_ALIASES[answer]
        typer.echo("Please choose one of the listed numbers or language names.")


def _resolve_profile(profile: Optional[Profile]) -> str:
    """Use the explicit profile if given, otherwise prompt (or default safely)."""
    if profile is not None:
        return profile.value
    if sys.stdin.isatty():
        return _prompt_for_profile()
    typer.echo("No language specified; defaulting to Python. Use --profile to choose another.")
    return Profile.python.value


def _profile_components(profile: str) -> list[str]:
    if profile not in PROFILE_TO_COMPONENTS:
        raise typer.BadParameter(
            f"Unknown profile '{profile}'. Choose one of: {', '.join(PROFILE_TO_COMPONENTS.keys())}"
        )
    components = PROFILE_TO_COMPONENTS[profile][:]
    if "cpp" in components and "cmake" not in components:
        components.append("cmake")
    return components


def _already_installed(component: str) -> bool:
    """True if the component is already available, so it can be skipped."""
    return any(command_exists(probe) for probe in COMPONENT_PROBES.get(component, []))


def _install_components(profile: str, dry_run: bool = False) -> None:
    os_name = detect_os()
    package_manager = detect_package_manager(os_name)
    if package_manager is None:
        typer.echo("No supported package manager found on this machine.")
        raise typer.Exit(code=1)

    typer.echo(f"Detected OS: {os_name}")
    typer.echo(f"Using package manager: {package_manager}")

    for component in _profile_components(profile):
        label = COMPONENT_VERSION_LABELS.get(component, component)

        if _already_installed(component):
            typer.echo(f"Skipping {label}: already installed.")
            continue

        package_name = PACKAGE_MAP.get(component, {}).get(package_manager)
        if not package_name:
            typer.echo(f"Skipping {component}: no package mapping for {package_manager}")
            continue

        install_command = build_install_command(package_manager, package_name)
        typer.echo(f"Installing {label}: {' '.join(install_command)}")
        run_command(install_command, dry_run=dry_run)


def _install_vscode_extensions(profile: str, dry_run: bool = False) -> None:
    if not command_exists("code"):
        typer.echo("VS Code CLI not found. Ensure 'code' is in PATH before extension setup.")
        return

    extensions = PROFILE_EXTENSIONS.get(profile, [])
    for extension in extensions:
        command = ["code", "--install-extension", extension, "--force"]
        typer.echo(f"Installing VS Code extension: {extension}")
        run_command(command, dry_run=dry_run)


def _configure_vscode_settings() -> None:
    settings_path = get_vscode_settings_path()
    merge_json_file(settings_path, DEFAULT_SETTINGS)
    typer.echo(f"Updated VS Code settings: {settings_path}")


def _create_python_sample(project_root: Path) -> None:
    app_dir = project_root / "python-app"
    write_file(
        app_dir / "app.py",
        "def main():\n    print(\"Hello from Python starter\")\n\n\nif __name__ == '__main__':\n    main()\n",
    )
    write_file(app_dir / "requirements.txt", "pytest\n")
    write_file(
        app_dir / ".vscode" / "launch.json",
        """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run / Debug app.py",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/app.py",
      "console": "integratedTerminal"
    }
  ]
}
""",
    )
    write_file(
        app_dir / "README.md",
        "# Python Starter\n\n"
        "Open this folder in VS Code and press **F5** to run and debug.\n\n"
        "Or run it from a terminal:\n\n```bash\npython app.py\n```\n",
    )


def _create_node_sample(project_root: Path) -> None:
    app_dir = project_root / "node-app"
    write_file(
        app_dir / "package.json",
        '{\n  "name": "node-starter",\n  "version": "1.0.0",\n  "private": true,\n  "type": "module",\n  "scripts": {\n    "start": "node src/index.js"\n  }\n}\n',
    )
    write_file(
        app_dir / "src" / "index.js",
        "console.log('Hello from Node.js starter');\n",
    )
    write_file(
        app_dir / ".vscode" / "launch.json",
        """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run / Debug index.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/src/index.js",
      "console": "integratedTerminal"
    }
  ]
}
""",
    )
    write_file(
        app_dir / "README.md",
        "# Node.js Starter\n\n"
        "Open this folder in VS Code and press **F5** to run and debug.\n\n"
        "Or run it from a terminal:\n\n```bash\nnpm start\n```\n",
    )


def _create_java_sample(project_root: Path) -> None:
    write_file(
        project_root / "java-app" / "pom.xml",
        """<project xmlns=\"http://maven.apache.org/POM/4.0.0\"\n         xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd\">\n  <modelVersion>4.0.0</modelVersion>\n  <groupId>dev.enabler</groupId>\n  <artifactId>java-starter</artifactId>\n  <version>1.0.0</version>\n  <properties>\n    <maven.compiler.source>21</maven.compiler.source>\n    <maven.compiler.target>21</maven.compiler.target>\n  </properties>\n</project>\n""",
    )
    write_file(
        project_root / "java-app" / "src" / "main" / "java" / "App.java",
        "public class App {\n    public static void main(String[] args) {\n        System.out.println(\"Hello from Java starter\");\n    }\n}\n",
    )
    write_file(
        project_root / "java-app" / ".vscode" / "launch.json",
        """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run / Debug App",
      "type": "java",
      "request": "launch",
      "mainClass": "App"
    }
  ]
}
""",
    )
    write_file(
        project_root / "java-app" / "README.md",
        "# Java Starter\n\n"
        "Open this folder in VS Code (with the Java extension pack) and press "
        "**F5** to run and debug, or use the **Run** lens above `main`.\n",
    )


def _create_cpp_sample(project_root: Path) -> None:
    write_file(
        project_root / "cpp-app" / "main.cpp",
        "#include <iostream>\n\nint main() {\n    std::cout << \"Hello from C++ starter\\n\";\n    return 0;\n}\n",
    )
    write_file(
        project_root / "cpp-app" / "CMakeLists.txt",
        "cmake_minimum_required(VERSION 3.16)\nproject(cpp_starter)\nset(CMAKE_CXX_STANDARD 17)\nadd_executable(cpp_starter main.cpp)\n",
    )
    write_file(
        project_root / "cpp-app" / ".vscode" / "tasks.json",
        """{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "cmake-configure",
      "type": "shell",
      "command": "cmake",
      "args": ["-S", ".", "-B", "build"]
    },
    {
      "label": "build",
      "type": "shell",
      "command": "cmake",
      "args": ["--build", "build"],
      "dependsOn": "cmake-configure",
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}
""",
    )
    write_file(
        project_root / "cpp-app" / ".vscode" / "launch.json",
        """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run / Debug (build first)",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/build/cpp_starter",
      "args": [],
      "cwd": "${workspaceFolder}",
      "preLaunchTask": "build",
      "externalConsole": false
    }
  ]
}
""",
    )
    write_file(
        project_root / "cpp-app" / "README.md",
        "# C/C++ Starter\n\n"
        "Open this folder in VS Code (with the C/C++ extension) and press "
        "**F5** to build and debug.\n\n"
        "Or build and run from a terminal:\n\n"
        "```bash\ncmake -S . -B build\ncmake --build build\n./build/cpp_starter\n```\n\n"
        "Note: on Windows the binary is `build\\\\cpp_starter.exe` (or "
        "`build\\\\Debug\\\\cpp_starter.exe`). If the debug config doesn't match "
        "your compiler, run **Run > Add Configuration** and pick C/C++.\n",
    )


def _generate_samples(target_dir: Path, profile: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    components = _profile_components(profile)

    if "python" in components:
        _create_python_sample(target_dir)
    if "node" in components:
        _create_node_sample(target_dir)
    if "java" in components:
        _create_java_sample(target_dir)
    if "cpp" in components:
        _create_cpp_sample(target_dir)

    typer.echo(f"Sample projects generated under: {target_dir}")


@app.command("profiles")
def list_profiles() -> None:
    typer.echo("Available profiles:")
    for profile_name, components in PROFILE_TO_COMPONENTS.items():
        typer.echo(f"- {profile_name}: {', '.join(components)}")


@app.command("install")
def install(
    profile: Profile = typer.Option(Profile.fullstack, help="Environment profile to install"),
    dry_run: bool = typer.Option(False, help="Print commands without executing"),
) -> None:
    _install_components(profile.value, dry_run=dry_run)


@app.command("configure-vscode")
def configure_vscode(
    profile: Profile = typer.Option(Profile.fullstack, help="Profile to select extension set"),
    dry_run: bool = typer.Option(False, help="Print extension commands without executing"),
) -> None:
    _install_vscode_extensions(profile.value, dry_run=dry_run)
    if not dry_run:
        _configure_vscode_settings()


@app.command("init-samples")
def init_samples(
    profile: Profile = typer.Option(Profile.fullstack, help="Profile that determines sample projects"),
    output_dir: str = typer.Option("sample-projects", help="Directory to create sample projects in"),
) -> None:
    _generate_samples(Path(output_dir), profile.value)


@app.command("setup")
def setup(
    profile: Optional[Profile] = typer.Option(None, help="Language to set up; prompts if omitted"),
    output_dir: str = typer.Option("sample-projects", help="Directory to create sample projects in"),
    dry_run: bool = typer.Option(False, help="Print commands without executing install/configure steps"),
    skip_install: bool = typer.Option(False, help="Skip package installations"),
    skip_vscode: bool = typer.Option(False, help="Skip VS Code setup"),
    skip_samples: bool = typer.Option(False, help="Skip sample project generation"),
) -> None:
    profile_name = _resolve_profile(profile)
    typer.echo(f"Setting up: {profile_name}")

    if not skip_install:
        _install_components(profile_name, dry_run=dry_run)

    if not skip_vscode:
        _install_vscode_extensions(profile_name, dry_run=dry_run)
        if not dry_run:
            _configure_vscode_settings()

    if not skip_samples:
        _generate_samples(Path(output_dir), profile_name)

    typer.echo("Setup complete.")


if __name__ == "__main__":
    app()