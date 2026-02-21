from pathlib import Path
from enum import Enum

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
        "winget": "Python.Python.3.12",
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


def _profile_components(profile: str) -> list[str]:
    if profile not in PROFILE_TO_COMPONENTS:
        raise typer.BadParameter(
            f"Unknown profile '{profile}'. Choose one of: {', '.join(PROFILE_TO_COMPONENTS.keys())}"
        )
    components = PROFILE_TO_COMPONENTS[profile][:]
    if "cpp" in components and "cmake" not in components:
        components.append("cmake")
    return components


def _install_components(profile: str, dry_run: bool = False) -> None:
    os_name = detect_os()
    package_manager = detect_package_manager(os_name)
    if package_manager is None:
        typer.echo("No supported package manager found on this machine.")
        raise typer.Exit(code=1)

    typer.echo(f"Detected OS: {os_name}")
    typer.echo(f"Using package manager: {package_manager}")

    for component in _profile_components(profile):
        package_name = PACKAGE_MAP.get(component, {}).get(package_manager)
        if not package_name:
            typer.echo(f"Skipping {component}: no package mapping for {package_manager}")
            continue

        install_command = build_install_command(package_manager, package_name)
        typer.echo(f"Installing {component}: {' '.join(install_command)}")
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
    write_file(
        project_root / "python-app" / "app.py",
        "def main():\n    print(\"Hello from Python starter\")\n\n\nif __name__ == '__main__':\n    main()\n",
    )
    write_file(project_root / "python-app" / "requirements.txt", "pytest\n")
    write_file(project_root / "python-app" / "README.md", "# Python Starter\n\nRun: `python app.py`\n")


def _create_node_sample(project_root: Path) -> None:
    write_file(
        project_root / "node-app" / "package.json",
        '{\n  "name": "node-starter",\n  "version": "1.0.0",\n  "private": true,\n  "type": "module",\n  "scripts": {\n    "start": "node src/index.js"\n  }\n}\n',
    )
    write_file(
        project_root / "node-app" / "src" / "index.js",
        "console.log('Hello from Node.js starter');\n",
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


def _create_cpp_sample(project_root: Path) -> None:
    write_file(
        project_root / "cpp-app" / "main.cpp",
        "#include <iostream>\n\nint main() {\n    std::cout << \"Hello from C++ starter\\n\";\n    return 0;\n}\n",
    )
    write_file(
        project_root / "cpp-app" / "CMakeLists.txt",
        "cmake_minimum_required(VERSION 3.16)\nproject(cpp_starter)\nset(CMAKE_CXX_STANDARD 17)\nadd_executable(cpp_starter main.cpp)\n",
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
    profile: Profile = typer.Option(Profile.fullstack, help="Environment profile to apply"),
    output_dir: str = typer.Option("sample-projects", help="Directory to create sample projects in"),
    dry_run: bool = typer.Option(False, help="Print commands without executing install/configure steps"),
    skip_install: bool = typer.Option(False, help="Skip package installations"),
    skip_vscode: bool = typer.Option(False, help="Skip VS Code setup"),
    skip_samples: bool = typer.Option(False, help="Skip sample project generation"),
) -> None:
    profile_name = profile.value
    typer.echo(f"Applying profile: {profile_name}")

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