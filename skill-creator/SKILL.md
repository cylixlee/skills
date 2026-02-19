---
name: skill-creator
description: Tool for creating, validating, packaging, and unpacking Agent Skills. Use when users want to create a new skill or manage existing skills. Supports initialization, validation, packaging, unpacking, and iterative development workflows.
license: Complete terms in LICENSE.txt
---

# Skill Creator

Tools for creating, validating, packaging, and unpacking Agent Skills.

## About Skills

Skills are modular, self-contained packages that extend an Agent's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform an Agent from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else the Agent needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: The Agent is already very smart.** Only add context the Agent doesn't already have. Challenge each piece of information: "Does the Agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of an Agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

## Skill Structure

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

## Resource Directories

| Directory     | When to include                             | Examples                                      |
| ------------- | ------------------------------------------- | --------------------------------------------- |
| `scripts/`    | Skills requiring Python scripts             | `scripts/rotate_pdf.py`, `scripts/extract.py` |
| `references/` | Detailed documentation for agent reference  | `references/api.md`, `references/schema.md`   |
| `assets/`     | Templates, boilerplate, or files for output | `assets/template.html`, `assets/config.yaml`  |

### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Agent for patching or environment-specific adjustments

### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Agent's process and thinking.

- **When to include**: For documentation that Agent should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/policies.md` for company policies
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Agent determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window.

### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Agent produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/frontend-template/` for HTML/React boilerplate
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Agent to use files without loading them into context

### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

## Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Agent (Unlimited because scripts can be executed without reading into context window)

### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

The Agent loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    └── product.md (API usage, features)
```

When a user asks about sales metrics, the Agent only reads sales.md.

**Pattern 3: Conditional details**

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

The Agent reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so the Agent can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Initialize the skill
2. Edit the skill (implement resources and write SKILL.md)
3. Validate the skill
4. Package the skill
5. Iterate based on real usage

### Step 1: Initialize the Skill

```bash
# Run from project root
uv run scripts/init.py <skill-name>

# Enter skill directory
cd skills/<skill-name>

# Initialize uv project (required for scripts)
uv init --bare
```

The initialization script creates:
- Skill directory structure
- SKILL.md template with YAML frontmatter
- Resource directories: `scripts/`, `references/`, `assets/`
- Example files (can be customized or deleted)

### Step 2: Edit the Skill

Implement reusable resources and update SKILL.md with skill-specific instructions.

#### Add Scripts

Create Python scripts in `scripts/` directory for tasks requiring deterministic reliability. Scripts should be idempotent and handle errors gracefully.

```bash
# Add dependencies if needed
uv add <package-name>

# Run and test the script
uv run --frozen scripts/<script-name>.py <args>
```

#### Add References

Add documentation files in `references/` for domain knowledge, schemas, API specs, or policies.

#### Add Assets

Add templates, boilerplate, or output files in `assets/`.

#### Update SKILL.md

Write the YAML frontmatter and Markdown body for the skill. See SKILL.md Writing Guidelines below.

### Step 3: Validate the Skill

```bash
uv run scripts/validate.py <skill-directory>
```

Validation checks:
- YAML frontmatter format and required fields
- Skill naming conventions and directory structure
- Description completeness and quality
- File organization and resource references

### Step 4: Package the Skill

```bash
uv run scripts/pack.py <skill-name> --output <output-directory>
```

Packaging automatically validates the skill first, then creates a `.skill` file (zip archive) for distribution.

### Step 5: Unpack a Skill

```bash
uv run scripts/unpack.py <skill-name>.skill
```

Extracts a packaged skill into the current directory.

### Step 6: Iterate

After testing the skill, iterate based on real usage:

1. Use the skill on actual tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes, validate, and repackage

## SKILL.md Writing Guidelines

### YAML Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps the Agent understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here—not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to the Agent.
  - Example: "Tool for creating and managing Agent Skills. Use when users want to create a new skill or manage existing skills. Supports initialization, validation, packaging, unpacking, and iterative development workflows."

Do not include any other fields in YAML frontmatter.

### Markdown Body

Write instructions for using the skill and its bundled resources. Use imperative/infinitive form.

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
uv run scripts/<script-name>.py <args>   # Run skill scripts
```

All skill-creator scripts use uv. If uv is not installed, ask the user to install it first.
