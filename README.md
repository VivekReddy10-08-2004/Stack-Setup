# Stack Setup

Simple CLI that sets up a dev stack in a few commands.

## What it does

- Installs tools (VS Code, Python, Java, C/C++, Node.js)
- Installs VS Code extensions
- Applies a few safe VS Code settings
- Creates ready-to-run sample projects

## Quick start

From the `src` folder:

```bash
python installer.py --help
python installer.py profiles
python installer.py setup --profile fullstack --dry-run
```

Remove `--dry-run` when you are ready to install for real.

## Profiles

Pick a profile based on what you want to build:

- `base` (all core tools)
- `python`
- `web`
- `java`
- `cpp`
- `fullstack`

## Common commands

```bash
# Install tools only
python installer.py install --profile python

# Configure VS Code only
python installer.py configure-vscode --profile python

# Create starter projects only
python installer.py init-samples --profile fullstack --output-dir "..\\sample-projects"

# Do everything
python installer.py setup --profile fullstack
```

## What gets created

Sample projects are created inside the output folder you pass in. Example:

```
sample-projects/
  python-app/
  node-app/
  java-app/
  cpp-app/
```

## Notes

- VS Code extension install needs `code` in your PATH.
- Linux installs may need `sudo`.
- Package names can vary between distros.

## Project layout

- `src/installer.py` contains the CLI commands
- `src/utils.py` contains OS and install helpers
