# Salesforce Developer — GitHub Copilot Instructions

This project uses two Agent Skills:

1. **salesforce-developer** at `.github/skills/salesforce-developer/`
   Read that skill's `SKILL.md` and `references/` files for all Salesforce development patterns.

2. **salesforce-architect-skill** at `.github/skills/salesforce-architect-skill/`
   Read that skill's `SKILL.md` and `references/` files for architecture, data model, integration, and Well-Architected guidance.

## Mandatory Rules

All mandatory development rules (bulkification, governor limits, security, testing, etc.) are
maintained in a single source of truth:
**[salesforce-developer/SKILL.md](.github/skills/salesforce-developer/SKILL.md) → "Mandatory Rules" section.**

Do not duplicate those rules here. Read SKILL.md before generating any Salesforce code.
