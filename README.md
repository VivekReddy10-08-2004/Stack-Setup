# Stack Setup

Install your dev environment with sensible defaults so you can start coding immediately.

## Prerequisite (Required)

Install the latest Python first:

- https://www.python.org/downloads/

Then verify Python is available:

```bash
python --version
```

If `python` is not recognized on Windows, try:

```bash
py --version
```

## Fast Path (Recommended)

From the `Stack Setup` folder, run:

```bash
python src/installer.py setup
```

That single command will, by default:

- Install core tools (VS Code, Python, Node.js, Java, C/C++)
- Install VS Code extensions for the stack
- Apply safe VS Code settings
- Generate starter projects in `sample-projects`

## Safe Preview Before Installing

To preview commands without making changes:

```bash
python src/installer.py setup --dry-run
```

## What You Get

After setup, starter apps are created under:

```text
sample-projects/
  python-app/
  node-app/
  java-app/
  cpp-app/
```

## Common Commands

```bash
# Show CLI help
python src/installer.py --help

# Show available profiles
python src/installer.py profiles

# Install packages only
python src/installer.py install --profile fullstack

# Configure VS Code only
python src/installer.py configure-vscode --profile fullstack

# Generate sample projects only
python src/installer.py init-samples --profile fullstack --output-dir "sample-projects"
```

## Optional Profiles

If you want a smaller setup, use `--profile`:

- `base`
- `python`
- `web`
- `java`
- `cpp`
- `fullstack` (default)

Example:

```bash
python src/installer.py setup --profile python
```

## Platform Notes

- Windows: uses `winget`, `choco`, or `scoop`
- macOS: uses `brew`
- Linux: uses `apt`, `dnf`, `yum`, `pacman`, or `zypper`
- VS Code extension install requires `code` in PATH
- Linux installs may require `sudo`

## Troubleshooting

- `python` command not found: install Python and restart terminal
- `code` command not found: enable "Shell Command: Install 'code' command in PATH" from VS Code
- Unsupported package manager detected: install one of the supported package managers for your OS

## Project Files

- `src/installer.py`: CLI entry point
- `src/utils.py`: OS detection, package manager, and helper functions
