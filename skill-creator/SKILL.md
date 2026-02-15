---
name: skill-creator
description: Tool for creating and managing Agent Skills. Use when users want to create a new skill, update an existing skill, package a skill for distribution, or extract contents from a .skill file. Supports initialization, validation, packaging, and unpacking workflows.
---

# Skill Creator

This skill provides tools for creating, validating, packaging, and unpacking Agent Skills.

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else the agent needs.

**Default assumption: The agent is already very smart.** Only add context it doesn't already have.

### Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

- **High freedom**: Text-based instructions for flexible approaches
- **Medium freedom**: Pseudocode/scripts with parameters for preferred patterns
- **Low freedom**: Specific scripts for fragile, error-prone operations

### Resource Directory Philosophy

**Only create directories you actually need:**

| Directory     | When to include                                       | When to skip                         |
| ------------- | ----------------------------------------------------- | ------------------------------------ |
| `scripts/`    | Repeatedly rewritten code or deterministic operations | No executable utilities needed       |
| `references/` | The agent needs to load detailed documentation        | Information fits in SKILL.md         |
| `assets/`     | Templates, boilerplate, or files for output           | No templates or static assets needed |

If you're unsure, start without them. You can always add later.

## Skill Structure

A skill consists of:

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

## Commands

All scripts use uv for dependency management. Remind user to install uv first if not present.

### Initialize a New Skill

```bash
uv run scripts/init.py <skill-name>
```

Creates a new skill in `skills/<skill-name>/`. Reference/script/asset directories are created on-demand.

### Validate a Skill

```bash
uv run scripts/validate.py <skill-directory>
```

Checks SKILL.md frontmatter, naming conventions, and directory structure.

### Package a Skill

```bash
uv run scripts/pack.py <skill-name> --output <output-directory>
```

Creates a `.skill` file from `skills/<skill-name>/`.

### Unpack a Skill

```bash
uv run scripts/unpack.py <skill-name>.skill
```

Extracts a `.skill` file to `skills/<skill-name>/`. Useful for installing or modifying existing skills.

## Git Ignore

When creating a skill with Python scripts, copy or append the project's `.gitignore` to the skill directory:

```bash
# Copy if skill has no .gitignore
cp .gitignore <skill-name>/.gitignore

# Append if skill already has one
cat .gitignore >> <skill-name>/.gitignore
```

This ensures the skill package excludes Python-specific files like `__pycache__/`, `*.pyc`, and `.venv/.

## Workflow Decision Tree

1. **Creating a new skill?**
   - Run `init` → Edit SKILL.md → Validate → Pack

2. **Modifying an existing skill?**
   - If .skill file: Unpack first → Edit → Pack

3. **Just need to validate?**
   - Run `validate` directly

## Development

Initialize a new project:

```bash
uv init --bare
# or with specific version: uv init --bare --python <version>
```

Add dependencies:

```bash
uv add <package-name>
```

Remove dependencies:

```bash
uv remove <package-name>
```

Run scripts:

```bash
uv run --frozen scripts/<name>.py <args>
```
