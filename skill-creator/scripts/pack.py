#!/usr/bin/env python3
"""
Skill Packager - Creates a .skill file from a skill directory

Usage:
    uv run scripts/pack.py <skill-name> --output <dir>

Examples:
    uv run scripts/pack.py my-skill --output ./dist
"""

import argparse
import sys
import zipfile
from pathlib import Path
import validate

SKILLS_DIR = Path(__file__).parent.parent.parent


def package_skill(skill_name: str, output_dir: Path) -> Path | None:
    """Package a skill directory into a .skill file."""
    skill_path = SKILLS_DIR / skill_name

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"Skill not found: {skill_path}")
        return None

    valid, msg = validate.validate_skill(skill_path)
    if not valid:
        print(f"Validation failed: {msg}")
        return None
    print(f"Validated: {msg}")

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{skill_name}.skill"

    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path.parent)
                    zf.write(file_path, arcname)
        print(f"Created: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error creating package: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Package a skill")
    parser.add_argument("skill_name", help="Name of the skill to package")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")

    args = parser.parse_args()

    result = package_skill(args.skill_name, args.output)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
