# Stack Setup

Install your dev environment with sensible defaults so you can start coding immediately.

Stack Setup is a cross-platform CLI that installs your core tools (VS Code, Python,
Node.js, Java, C/C++), configures VS Code, and generates ready-to-run starter
projects — all from a single command.

## Prerequisite (Required)

Install Python first — Stack Setup is a Python program, so it needs Python to
run itself:

- https://www.python.org/downloads/

Then verify Python is available:

```bash
python --version
```

If `python` is not recognized on Windows, try:

```bash
py --version
```

That is the only thing you install by hand. Everything else is handled for you.
Stack Setup detects tools you already have (including this Python) and **skips
them**, so it never installs a second copy and is always safe to re-run.

## Fast Path (Recommended)

From the `Stack Setup` folder, run:

```bash
python src/installer.py setup
```

Stack Setup asks which language you want:

```text
Which language do you want to set up?
  1. Python
  2. JavaScript / Node.js
  3. Java
  4. C / C++
  5. Everything (all of the above)
```

Pick one, and that single command will:

- Install that language's tools (and VS Code)
- Install the matching VS Code extensions
- Apply safe VS Code settings
- Generate a ready-to-run, debuggable starter project in `sample-projects`

Open the generated project folder in VS Code and press **F5** to run and debug.

The first run also installs the CLI's only dependency (Typer) automatically, so
there is no extra setup step. To skip the prompt (for scripts), pass the
language directly:

```bash
python src/installer.py setup --profile python
```

## Safe Preview Before Installing

To preview commands without making changes:

```bash
python src/installer.py setup --dry-run
```

## What You Get

After setup, a starter app for your chosen language is created under
`sample-projects/`. Each starter includes a `.vscode/` debug config so you can
press **F5** to run and debug immediately. For example, choosing Python creates:

```text
sample-projects/
  python-app/
    app.py
    requirements.txt
    .vscode/launch.json
```

Choosing "Everything" creates `python-app/`, `node-app/`, `java-app/`, and
`cpp-app/`.

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

## Dependencies

The CLI needs Python plus one small library, **Typer**. You do not have to
install it manually — the first command installs it for you. To install it
ahead of time instead:

```bash
python -m pip install -r requirements.txt
```

## Versions Stack Setup Installs

The goal is a stable, well-supported setup you don't have to think about — the
versions most tutorials and courses assume:

| Tool | Version it targets |
| --- | --- |
| Python | Latest stable (3.13 on Windows; your package manager's current Python elsewhere) |
| Node.js | Active **LTS** line (the most stable choice) |
| Java | **21 LTS** (Eclipse Temurin) |
| C/C++ | Current stable toolchain (LLVM/Clang on Windows/macOS, GCC on Linux) |
| VS Code | Latest stable |

On Windows these versions are pinned exactly. On macOS and Linux the package
manager provides its current stable equivalent. Anything already installed is
detected and skipped, so re-running is safe.

## Platform Notes

- Windows: uses `winget`, `choco`, or `scoop`
- macOS: uses `brew`
- Linux: uses `apt`, `dnf`, `yum`, `pacman`, or `zypper`
- VS Code extension install requires `code` in PATH
- Linux installs may require `sudo`

## Troubleshooting

- `python` command not found: install Python and restart your terminal
- `code` command not found: enable "Shell Command: Install 'code' command in PATH" from VS Code
- Unsupported package manager detected: install one of the supported package managers for your OS

## Project Files

- `src/installer.py`: CLI entry point (profiles, install, VS Code config, samples)
- `src/utils.py`: OS detection, package manager detection, and helper functions
- `index.html`: landing page (deployed via Vercel)
