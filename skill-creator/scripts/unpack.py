#!/usr/bin/env python3
"""
Skill Unpacker - Extracts a .skill file to skills/ directory

Usage:
    uv run scripts/unpack.py <skill-name>.skill

Examples:
    uv run scripts/unpack.py my-skill.skill
"""

import argparse
import sys
import zipfile
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent


def unpack_skill(skill_file: Path) -> Path | None:
    """Extract a .skill file to skills/ directory."""
    skill_file = skill_file.resolve()

    if not skill_file.exists() or not skill_file.is_file():
        print(f"Not a file: {skill_file}")
        return None

    if skill_file.suffix != ".skill":
        print(f"File must have .skill extension: {skill_file}")
        return None

    skill_name = skill_file.stem
    output_dir = SKILLS_DIR / skill_name

    if output_dir.exists():
        print(f"Skill already exists: {output_dir}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(skill_file, "r") as zf:
            zf.extractall(output_dir)
        print(f"Extracted to: {output_dir}")
        return output_dir
    except zipfile.BadZipFile:
        print(f"Invalid .skill file: {skill_file}")
        return None
    except Exception as e:
        print(f"Error extracting: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Unpack a skill")
    parser.add_argument("skill_file", type=Path, help=".skill file to extract")

    args = parser.parse_args()

    result = unpack_skill(args.skill_file)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
