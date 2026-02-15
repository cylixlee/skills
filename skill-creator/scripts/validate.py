#!/usr/bin/env python3
"""
Skill Validator - Checks skill structure and frontmatter

Usage:
    uv run scripts/validate.py <skill-directory>
"""

import re
import sys
import yaml
from pathlib import Path

ALLOWED_PROPS = {"name", "description", "license", "allowed-tools", "metadata"}


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """Validate a skill directory."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    unexpected = set(frontmatter.keys()) - ALLOWED_PROPS
    if unexpected:
        return False, f"Unexpected keys: {', '.join(sorted(unexpected))}"

    name = frontmatter.get("name", "")
    if not isinstance(name, str) or not name:
        return False, "Missing or invalid 'name' in frontmatter"

    if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$", name):
        return False, "Name must be hyphen-case (lowercase, digits, hyphens)"
    if "--" in name or name.startswith("-") or name.endswith("-"):
        return False, "Name cannot contain consecutive hyphens or start/end with hyphen"
    if len(name) > 64:
        return False, "Name exceeds 64 characters"

    desc = frontmatter.get("description", "")
    if not isinstance(desc, str):
        return False, "Description must be a string"
    if not desc.strip():
        return False, "Description is empty"
    if len(desc) > 1024:
        return False, "Description exceeds 1024 characters"
    if "<" in desc or ">" in desc:
        return False, "Description cannot contain angle brackets"

    if len(list(skill_path.iterdir())) == 1:
        return True, "Valid (minimal skill)"

    for d in ["scripts", "references", "assets"]:
        dir_path = skill_path / d
        if dir_path.exists() and not dir_path.is_dir():
            return False, f"'{d}' exists but is not a directory"

    return True, "Valid"


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run scripts/validate.py <skill-directory>")
        sys.exit(1)

    valid, msg = validate_skill(Path(sys.argv[1]))
    print(msg)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
