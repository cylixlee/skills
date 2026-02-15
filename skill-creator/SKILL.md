---
name: skill-creator
description: Tool for creating and managing Agent Skills. Supports initialization, validation, packaging, and unpacking workflows.
---

# Skill Creator

Tools for creating, validating, packaging, and unpacking Agent Skills.

## Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown body (required)
├── scripts/ (optional)
├── references/ (optional)
└── assets/ (optional)
```

## Resource Directories

| Directory     | When to include                                       |
| ------------- | ----------------------------------------------------- |
| `scripts/`    | Skills requiring Python scripts                       |
| `references/` | Detailed documentation for agent reference            |
| `assets/`     | Templates, boilerplate, or files for output           |

## Commands

All scripts use uv. If uv is not installed, ask the user to install it first.

### Initialize a New Skill

```bash
# Run from project root
uv run scripts/init.py <skill-name>

# Enter skill directory
cd skills/<skill-name>

# Initialize uv project (required for scripts)
uv init --bare
```

### Validate a Skill

```bash
uv run scripts/validate.py <skill-directory>
```

### Package a Skill

```bash
uv run scripts/pack.py <skill-name> --output <output-directory>
```

### Unpack a Skill

```bash
uv run scripts/unpack.py <skill-name>.skill
```

## Git Ignore

When creating a skill with Python scripts:

```bash
cp .gitignore <skill-name>/.gitignore
```

This excludes `__pycache__/`, `*.pyc`, and `.venv/` from packages.

## uv Commands

```bash
uv init --bare                          # Initialize project
uv add <package-name>                   # Add dependency
uv remove <package-name>                # Remove dependency
uv run --frozen scripts/<name>.py <args>  # Run script
```
