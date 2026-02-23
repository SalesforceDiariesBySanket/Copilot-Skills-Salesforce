#!/usr/bin/env python3
"""
validate-skill.py — Validates Agent Skills SKILL.md files against the specification.

Usage:
  python scripts/validate-skill.py <path-to-skill-directory>

Checks:
  - SKILL.md exists
  - Frontmatter has required 'name' and 'description' fields
  - 'name' matches directory name, is lowercase alphanumeric + hyphens, <= 64 chars
  - 'description' is non-empty and <= 1024 characters
  - SKILL.md body is <= 500 lines
  - Reference files over 100 lines have a Table of Contents
"""

import sys
import os
import re
import yaml


def validate_skill(skill_dir):
    errors = []
    warnings = []

    # 1. Check SKILL.md exists
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("SKILL.md not found in " + skill_dir)
        return errors, warnings

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Parse frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        errors.append("SKILL.md missing YAML frontmatter (--- delimiters)")
        return errors, warnings

    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML frontmatter: {e}")
        return errors, warnings

    # 3. Validate 'name'
    name = frontmatter.get("name")
    if not name:
        errors.append("Missing required 'name' field in frontmatter")
    else:
        if len(name) > 64:
            errors.append(f"'name' exceeds 64 characters ({len(name)} chars)")
        if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", name):
            errors.append(f"'name' must be lowercase alphanumeric + hyphens, not start/end with hyphen: '{name}'")
        if "--" in name:
            errors.append(f"'name' must not contain consecutive hyphens: '{name}'")
        dir_name = os.path.basename(os.path.normpath(skill_dir))
        if name != dir_name:
            errors.append(f"'name' ({name}) does not match directory name ({dir_name})")

    # 4. Validate 'description'
    desc = frontmatter.get("description", "")
    if not desc or not str(desc).strip():
        errors.append("Missing or empty 'description' field in frontmatter")
    else:
        desc_str = str(desc).strip()
        # Collapse whitespace for accurate char count (YAML multiline adds newlines)
        desc_collapsed = re.sub(r"\s+", " ", desc_str)
        if len(desc_collapsed) > 1024:
            errors.append(f"'description' exceeds 1024 characters ({len(desc_collapsed)} chars)")

    # 5. Check optional 'license'
    if "license" not in frontmatter:
        warnings.append("No 'license' field in frontmatter (recommended)")

    # 6. Body line count
    body = content[fm_match.end():]
    body_lines = body.strip().splitlines()
    if len(body_lines) > 500:
        warnings.append(f"SKILL.md body is {len(body_lines)} lines (recommended max: 500)")

    # 7. Check reference files for TOC
    refs_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(refs_dir):
        for fname in sorted(os.listdir(refs_dir)):
            fpath = os.path.join(refs_dir, fname)
            if not fname.endswith(".md") or not os.path.isfile(fpath):
                continue
            with open(fpath, "r", encoding="utf-8") as rf:
                ref_lines = rf.readlines()
            if len(ref_lines) > 100:
                # Check first 30 lines for TOC
                header = "".join(ref_lines[:30]).lower()
                if "table of contents" not in header and "## contents" not in header:
                    warnings.append(f"references/{fname} ({len(ref_lines)} lines) has no Table of Contents (recommended for files > 100 lines)")

    # 8. Check for deeply nested references (reference files linking to other reference files)
    if os.path.isdir(refs_dir):
        for fname in sorted(os.listdir(refs_dir)):
            fpath = os.path.join(refs_dir, fname)
            if not fname.endswith(".md") or not os.path.isfile(fpath):
                continue
            with open(fpath, "r", encoding="utf-8") as rf:
                ref_content = rf.read()
            nested = re.findall(r"\[.*?\]\((?:references/|\./).*?\.md\)", ref_content)
            if nested:
                warnings.append(f"references/{fname} has nested reference links (should be one level deep): {nested[:3]}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-skill.py <path-to-skill-directory>")
        print("Example: python validate-skill.py .github/skills/salesforce-developer")
        sys.exit(1)

    skill_dir = sys.argv[1]
    if not os.path.isdir(skill_dir):
        print(f"ERROR: '{skill_dir}' is not a directory")
        sys.exit(1)

    print(f"Validating skill: {skill_dir}")
    print("=" * 60)

    errors, warnings = validate_skill(skill_dir)

    if errors:
        print(f"\n ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n All checks passed!")

    print()
    if errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
