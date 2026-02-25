# Copilot Skills — Salesforce

**Custom GitHub Copilot Agent Skills & Coding Rulesets for Salesforce Development & Architecture**

> Turn GitHub Copilot into a Salesforce-aware coding assistant that follows platform best practices, governor limits, security rules, and the Well-Architected Framework — out of the box.

---

## What Is This Repo?

This repository contains two **GitHub Copilot Agent Skills** and two **comprehensive coding rulesets** that supercharge Copilot with deep Salesforce platform knowledge:

### Skills

| Skill | Purpose |
|---|---|
| **salesforce-developer** | Generates, reviews, and debugs Apex, LWC, SOQL, Flows, triggers, integrations, and Agentforce actions |
| **salesforce-architect-skill** | Designs scalable Salesforce solutions using the Well-Architected Framework, Architect Decision Guides, and integration patterns |

### Coding Rulesets (NEW)

| Ruleset | Purpose |
|---|---|
| **[salesforce-apex-coding-rules.md](/.github/Blogs/salesforce-apex-coding-rules.md)** | 1,000+ lines of Apex coding standards: bulkification, SOQL/DML, triggers, async, security, testing, PMD rules, anti-patterns, and common runtime errors |
| **[salesforce-lwc-coding-rules.md](/.github/Blogs/salesforce-lwc-coding-rules.md)** | 1,500+ lines of LWC coding standards: templates, JS, wire service, events, navigation, security, performance, accessibility, Jest, ESLint, LWS, and common errors |

These rulesets are **tool-agnostic** — they work with GitHub Copilot, Cursor, Claude Code, Windsurf, Cline, Roo Code, or any AI coding tool that supports custom instructions.

When added to a repository, the skills and rulesets teach Copilot to:

- **Write bulkified, governor-limit-safe Apex** with proper trigger frameworks, error handling, and test patterns
- **Generate LWC components** with correct decorators, wire adapters, and event communication
- **Optimize SOQL/SOSL queries** with selective filters, indexing strategies, and cursor-based pagination
- **Design integration architectures** using the right API pattern (REST, Bulk, Platform Events, CDC, Data 360)
- **Apply security by default** — `WITH SECURITY_ENFORCED`, `with sharing`, CRUD/FLS checks, OAuth flows
- **Avoid common AI anti-patterns** — 30+ documented mistakes that LLMs typically make in Salesforce code
- **Follow the Well-Architected Framework** — Trusted > Easy > Adaptable, in that priority order
- **Produce architecture deliverables** — solution design docs, ERDs (Mermaid), integration diagrams, decision matrices
- **Pass PMD and ESLint** — rulesets include comprehensive PMD rule mapping for Apex and ESLint config for LWC

---

## Repository Structure

```
.github/
├── copilot-instructions.md                          # Entry point — tells Copilot which skills & rulesets to load
├── Blogs/
│   ├── salesforce-apex-coding-rules.md              # Comprehensive Apex coding ruleset (1,000+ lines)
│   └── salesforce-lwc-coding-rules.md               # Comprehensive LWC coding ruleset (1,500+ lines)
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
    │       └── well-architected-checklist.md        # Trusted/Easy/Adaptable validation checklist
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

### 2. Use the Coding Rulesets with Other AI Tools

The rulesets in `Blogs/` are tool-agnostic. Drop them into your AI coding tool's instruction layer:

| Tool | Where to Place |
|------|---------------|
| **GitHub Copilot (VS Code)** | `.github/copilot-instructions.md` or `.instructions.md` in target folders |
| **Cursor** | `.cursor/rules/apex.md` and `.cursor/rules/lwc.md` |
| **Claude Code** | `CLAUDE.md` in project root |
| **Windsurf** | `.windsurfrules` in project root |
| **Cline / Roo Code** | `.clinerules` or `.roo/rules/` |
| **Universal** | `AGENTS.md` in project root |

### 3. Use with GitHub Copilot

Once the `.github/` folder is in your project, **GitHub Copilot Chat** (in VS Code, Cursor, or GitHub.com) will automatically pick up the skills and apply Salesforce best practices to every response.

Try prompts like:

- *"Write an Apex trigger on Account that syncs BillingCity to related Contacts"*
- *"Create an LWC component for searching Accounts with a datatable"*
- *"Design the integration architecture for connecting Salesforce to SAP"*
- *"Review this data model for anti-patterns"*
- *"Build a Batch Apex class to flag Contacts without email addresses"*

### 4. Validate Skills

```bash
python .github/skills/scripts/validate-skill.py .github/skills/salesforce-developer
python .github/skills/scripts/validate-skill.py .github/skills/salesforce-architect-skill
```

---

## What's Inside the Coding Rulesets?

### Apex Coding Rules (`Blogs/salesforce-apex-coding-rules.md`)

| Section | What It Covers |
|---------|---------------|
| General Standards | API version, sharing, access modifiers, formatting |
| Naming Conventions | Classes, methods, variables, constants, triggers, booleans, maps |
| Modern Apex Features | Safe navigation (`?.`), `switch on`, Assert class, User Mode |
| Bulkification Rules | No SOQL/DML in loops, collection patterns, Map-based lookups |
| SOQL & SOSL Rules | Bind variables, selective queries, SOQL for-loops, USER_MODE |
| DML Rules | Partial success, SaveResult handling, Mixed DML prevention |
| Trigger Rules | One trigger per object, handler pattern, recursion prevention |
| Class Design | Service/Selector layers, method complexity, single responsibility |
| Error Handling | Custom exceptions, addError(), centralized logging |
| Security Rules | FLS, CRUD, SOQL injection, Named Credentials, HTTPS endpoints |
| Governor Limits | Complete limit table, Limits class monitoring |
| Test Class Rules | 95%+ coverage, TestDataFactory, naming conventions, Assert class |
| Async Apex | Queueable vs @future, Batch, Schedulable, Finalizers |
| Agentforce / Invocable | @InvocableMethod patterns for agents and flows |
| PMD Rules | Complete PMD rule map (50+ rules across all categories) |
| Anti-Patterns | 15 documented "never do this" patterns with fixes |
| Common Errors | 16 StackExchange top issues with causes and fixes |

### LWC Coding Rules (`Blogs/salesforce-lwc-coding-rules.md`)

| Section | What It Covers |
|---------|---------------|
| General Standards | API version, self-contained components, ESLint |
| Component Structure | File organization, folder naming, shared utilities |
| Naming Conventions | Folders, HTML tags, events, handlers, CSS classes |
| HTML Templates | `lwc:if`/`lwc:elseif`/`lwc:else`, `for:each`, key directive |
| JavaScript Rules | Lifecycle hooks, ES6+, getters, cleanup patterns |
| Reactive Properties | `@api`, `@track`, immutable patterns, proxy behavior |
| Wire Service | Wire to property/function, reactive params, refreshApex |
| Imperative Apex | async/await, loading state, @AuraEnabled patterns |
| Lightning Data Service | Record forms, createRecord, notifyRecordUpdateAvailable |
| Event Handling | CustomEvent, event naming, LMS, bubbles/composed |
| CSS Styling | Shadow DOM, SLDS tokens, :host, custom properties |
| Navigation | NavigationMixin, record/list/web page navigation |
| Error Handling | Toast (lightning/toast), reduceErrors, loading/empty/error states |
| Security | Custom Permissions, LWS compatibility, CSP |
| Performance | Debounce, pagination, lazy loading, caching getters |
| Accessibility | ARIA attributes, keyboard navigation, screen readers |
| Jest Testing | Mock wire, mock Apex, mock navigation, flushPromises |
| Component Communication | @api, CustomEvent, LMS pattern selection table |
| Metadata Configuration | .js-meta.xml, targets, targetConfigs, property types |
| Base Components | 25+ lightning-* components with use cases |
| Flow & Agentforce | FlowNavigationNextEvent, @api validate(), agent action UI |
| Light DOM & Directives | lwc:render-mode, lwc:spread, lwc:ref, lwc:is |
| Lightning Web Security | LWS rules, Locker comparison, distortion handlers |
| ESLint Rules | @salesforce/eslint-config-lwc rules, CI/CD integration |
| Anti-Patterns | 15 documented "never do this" LWC patterns with fixes |
| Common Errors | 15 StackExchange top LWC issues with causes and fixes |

---

## How Skills & Rulesets Work Together

The **copilot-instructions.md** orchestrates everything with a mandatory workflow:

```
1. Read the relevant SKILL file(s) → architecture & developer patterns
2. Read the relevant RULESET file(s) → detailed coding standards from Blogs/
3. Read the matching REFERENCE file(s) → deep-dive guides for the specific task
4. Generate code that follows ALL rules from skills, rulesets, and references
```

This layered approach ensures Copilot always has the right level of detail — from high-level architecture decisions down to specific PMD rule compliance.

---

## What Makes These Skills Different?

| Feature | Without Skills | With Skills + Rulesets |
|---|---|---|
| SOQL in loops | Copilot may generate it | Blocked by Rule CP1 — always bulkified |
| `without sharing` | Often used by default | `with sharing` enforced, `WITH SECURITY_ENFORCED` in SOQL |
| Process Builder | May be recommended | Flagged as deprecated — Flow recommended |
| Hardcoded IDs | Common in AI output | Blocked — uses `Schema.describe` or Custom Metadata |
| Test coverage | Basic tests | 200-record bulk tests with `@TestSetup` and Arrange-Act-Assert |
| API version | Often outdated | Always latest GA (currently 66.0) |
| Boolean recursion guard | Common AI mistake | `Set<Id>` pattern enforced |
| Architecture advice | Generic | Grounded in Well-Architected Framework + Decision Guides |
| PMD compliance | Not considered | 50+ PMD rules mapped and enforced |
| ESLint compliance | Not considered | @salesforce/eslint-config-lwc/recommended enforced |
| LWC event naming | Often wrong (hyphens, camelCase) | Lowercase-only enforced |
| `if:true`/`if:false` | May use deprecated syntax | `lwc:if`/`lwc:elseif`/`lwc:else` enforced |
| Error handling | Often missing | try/catch/finally with loading state, toast, and reduceErrors |

---

## Compatibility

These skills and rulesets are designed for:

| Tool | How It Works |
|------|-------------|
| **GitHub Copilot Chat** (VS Code, JetBrains, GitHub.com) | Auto-reads `.github/copilot-instructions.md` |
| **Cursor** | Copy rulesets to `.cursor/rules/` with glob frontmatter |
| **Claude Code** | Copy to `CLAUDE.md` in project root |
| **Windsurf** | Copy to `.windsurfrules` in project root |
| **Cline / Roo Code** | Copy to `.clinerules` or `.roo/rules/` |
| **Any AI tool** | Copy to `AGENTS.md` in project root |

---

## Validated As Of

**February 2026** — Salesforce API v66.0 (Spring '26). Reference files are tagged with validation dates and should be reviewed against current release notes.

---

## License

MIT
