# Copilot Skills — Salesforce

**Custom GitHub Copilot Agent Skills for Salesforce Development & Architecture**

> Turn GitHub Copilot into a Salesforce-aware coding assistant that follows platform best practices, governor limits, security rules, and the Well-Architected Framework — out of the box.

---

## What Is This Repo?

This repository contains two **GitHub Copilot Agent Skills** that supercharge Copilot with deep Salesforce platform knowledge:

| Skill | Purpose |
|---|---|
| **salesforce-developer** | Generates, reviews, and debugs Apex, LWC, SOQL, Flows, triggers, integrations, and Agentforce actions |
| **salesforce-architect-skill** | Designs scalable Salesforce solutions using the Well-Architected Framework, Architect Decision Guides, and integration patterns |

When added to a repository, these skills teach Copilot to:

- **Write bulkified, governor-limit-safe Apex** with proper trigger frameworks, error handling, and test patterns
- **Generate LWC components** with correct decorators, wire adapters, and event communication
- **Optimize SOQL/SOSL queries** with selective filters, indexing strategies, and cursor-based pagination
- **Design integration architectures** using the right API pattern (REST, Bulk, Platform Events, CDC, Data 360)
- **Apply security by default** — `WITH SECURITY_ENFORCED`, `with sharing`, CRUD/FLS checks, OAuth flows
- **Avoid common AI anti-patterns** — 30+ documented mistakes that LLMs typically make in Salesforce code
- **Follow the Well-Architected Framework** — Trusted > Easy > Adaptable, in that priority order
- **Produce architecture deliverables** — solution design docs, ERDs (Mermaid), integration diagrams, decision matrices

---

## Repository Structure

```
.github/
├── copilot-instructions.md                          # Entry point — tells Copilot which skills to load
└── skills/
    ├── salesforce-developer/
    │   ├── SKILL.md                                 # Mandatory rules, naming conventions, anti-patterns
    │   ├── evaluations/
    │   │   └── eval-scenarios.json                  # Test scenarios to validate skill quality
    │   └── references/
    │       ├── apex-patterns.md                     # Triggers, async Apex, error handling, testing, JSON, wrappers
    │       ├── soql-optimization.md                 # Query selectivity, indexing, cursors, Big Objects, LDV
    │       ├── lwc-guide.md                         # LWC fundamentals, wire service, dynamic components
    │       ├── api-integration.md                   # REST services, Bulk API, Named Credentials, OAuth
    │       ├── formulas-validation.md               # Formula fields, validation rules, date/time functions
    │       ├── flows-automation.md                  # Record-triggered flows, screen flows, invocable Apex
    │       ├── security-sharing.md                  # Sharing keywords, CRUD/FLS, permission sets, encryption
    │       ├── deployment-devops.md                 # sf CLI, scratch orgs, CI/CD pipelines, packaging
    │       └── agentforce-ai.md                     # Agent actions, Prompt Builder, Models API, Platform Events, CDC
    ├── salesforce-architect-skill/
    │   ├── SKILL.md                                 # Well-Architected Framework, decision guides, anti-patterns
    │   ├── evaluations/
    │   │   └── eval-scenarios.json                  # Architecture evaluation scenarios
    │   └── references/
    │       ├── data-model-patterns.md               # Object design, sharing model, LDV, data skew
    │       ├── integration-patterns.md              # Pattern selection, API decision tree, middleware guidance
    │       └── well-architected-checklist.md         # Trusted/Easy/Adaptable validation checklist
    └── scripts/
        └── validate-skill.py                        # Validates SKILL.md files against the specification
```

---

## How to Use

### 1. Add to Your Salesforce Project

Copy the `.github/` folder into the root of any Salesforce DX project:

```bash
# Clone this repo
git clone https://github.com/SalesforceDiariesBySanket/Copilot-Skills-Salesforce.git

# Copy the .github folder to your project
cp -r Copilot-Skills-Salesforce/.github /path/to/your-salesforce-project/
```

### 2. Use with GitHub Copilot

Once the `.github/` folder is in your project, **GitHub Copilot Chat** (in VS Code, Cursor, or GitHub.com) will automatically pick up the skills and apply Salesforce best practices to every response.

Try prompts like:

- *"Write an Apex trigger on Account that syncs BillingCity to related Contacts"*
- *"Create an LWC component for searching Accounts with a datatable"*
- *"Design the integration architecture for connecting Salesforce to SAP"*
- *"Review this data model for anti-patterns"*
- *"Build a Batch Apex class to flag Contacts without email addresses"*

### 3. Validate Skills

```bash
python .github/skills/scripts/validate-skill.py .github/skills/salesforce-developer
python .github/skills/scripts/validate-skill.py .github/skills/salesforce-architect-skill
```

---

## What Makes These Skills Different?

| Feature | Without Skills | With Skills |
|---|---|---|
| SOQL in loops | Copilot may generate it | Blocked by Rule CP1 — always bulkified |
| `without sharing` | Often used by default | `with sharing` enforced, `WITH SECURITY_ENFORCED` in SOQL |
| Process Builder | May be recommended | Flagged as deprecated — Flow recommended |
| Hardcoded IDs | Common in AI output | Blocked — uses `Schema.describe` or Custom Metadata |
| Test coverage | Basic tests | 200-record bulk tests with `@TestSetup` and Arrange-Act-Assert |
| API version | Often outdated | Always latest GA (currently 66.0) |
| Boolean recursion guard | Common AI mistake | `Set<Id>` pattern enforced |
| Architecture advice | Generic | Grounded in Well-Architected Framework + Decision Guides |

---

## Compatibility

These skills are designed for:

- **GitHub Copilot Chat** (VS Code, JetBrains, GitHub.com)
- **Claude Code**
- **Cursor**
- Any AI coding assistant that reads `.github/copilot-instructions.md`

---

## Validated As Of

**February 2026** — Salesforce API v66.0 (Spring '26). Reference files are tagged with validation dates and should be reviewed against current release notes.

---

## License

MIT
