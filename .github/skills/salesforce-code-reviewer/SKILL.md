---
name: salesforce-code-reviewer
description: >
  Performs comprehensive code reviews of Salesforce platform code including Apex classes,
  triggers, SOQL/SOSL queries, LWC/Aura components, Flows, validation rules, formulas,
  and API integrations. Reviews for security, performance, governor limits compliance,
  design patterns, test coverage, error handling, and deployment readiness.
license: MIT
metadata:
  author: salesforce-code-review-team/Soofiya
  version: "2.0"
compatibility: Designed for VS Code, Claude Code, Cursor, and GitHub Copilot code review
---

# Salesforce Code Reviewer Skill

## Overview

The **Salesforce Code Reviewer** skill provides AI-powered code review capabilities for Salesforce platform code. This skill enables comprehensive, multi-dimensional reviews that evaluate code quality, security, performance, maintainability, and adherence to best practices.

### Key Capabilities

✅ **Security Review** — CRUD/FLS validation, SOQL injection, sensitive data exposure, sharing enforcement  
✅ **Performance & Governor Limits** — SOQL/DML optimization, bulkification, governor limit analysis  
✅ **Design Pattern Review** — Architecture compliance, layer separation, naming conventions  
✅ **Test Coverage & Quality** — Test case evaluation, coverage validation, edge case detection  
✅ **Error Handling** — Exception handling patterns, logging, recovery mechanisms  
✅ **Deployment Readiness** — Metadata completeness, CI/CD compliance, validation rules  
✅ **LWC Best Practices** — Template syntax, event handling, accessibility, Jest tests  
✅ **Apex Best Practices** — Modern Apex features, type safety, recursion prevention  

---

## How to Use This Skill

### When to Load This Skill

Use **Salesforce Code Reviewer** when you need to:
- Review pull requests (Apex, LWC, Aura, Flows)
- Identify security vulnerabilities in code
- Optimize for governor limits and performance
- Evaluate test coverage and quality
- Check deployment readiness
- Ensure compliance with Salesforce best practices
- Spot technical debt and architecture violations
- Improve code maintainability and consistency

### Step 1: Understand the Review Framework

The code reviewer uses a **layered evaluation model** across 8 key dimensions:

1. **Security & Compliance** — Data access, sharing, CRUD/FLS, encryption, API security
2. **Performance & Governor Limits** — Query optimization, bulkification, DML efficiency
3. **Architecture & Design Patterns** — Layer separation, naming conventions, SOLID principles
4. **Maintainability & Code Quality** — Readability, technical debt, complexity, documentation
5. **Error Handling & Logging** — Exception handling, error recovery, audit trails
6. **Testing & Coverage** — Unit tests, integration tests, edge cases, coverage percentage
7. **Deployment & DevOps** — Metadata completeness, CI/CD compliance, rollback strategy
8. **Modern Best Practices** — Latest Apex/LWC features, safe navigation, enhanced collections

### Step 2: Read the Relevant Review Checklists

Before performing a code review, read the **checklist files** matching the code type(s) being reviewed:

| Code Type | Review Checklist |
|---|---|
| Apex Classes & Triggers | [references/apex-review-checklist.md](references/apex-review-checklist.md) |
| Security & CRUD/FLS | [references/security-compliance-review-checklist.md](references/security-compliance-review-checklist.md) |
| Performance & Governor Limits | [references/performance-governorlimits-review-checklist.md](references/performance-governorlimits-review-checklist.md) |
| Error Handling & Logging | [references/error-handling-review-checklist.md](references/error-handling-review-checklist.md) |
| Test Coverage & Quality | [references/testcoverage-quality-review-checklist.md](references/testcoverage-quality-review-checklist.md) |
| Design Patterns & Architecture | [references/sf-design-pattern-review-checklist.md](references/sf-design-pattern-review-checklist.md) |
| LWC & Aura Components | [references/lwc-review-checklist.md](references/lwc-review-checklist.md) |
| Aura Components | [references/aura-review-checklist.md](references/aura-review-checklist.md) |
| Deployment Readiness | [references/deployment-readiness.md](references/deployment-readiness.md) |

### Step 3: Cross-Reference the Developer Skill

Use the **Salesforce Developer Skill** rulesets to understand the correct patterns:

| Reference Topic | File Location |
|---|---|
| Apex Coding Standards | [../salesforce-developer/Blogs/salesforce-apex-coding-rules.md](../salesforce-developer/Blogs/salesforce-apex-coding-rules.md) |
| LWC Coding Standards | [../salesforce-developer/Blogs/salesforce-lwc-coding-rules.md](../salesforce-developer/Blogs/salesforce-lwc-coding-rules.md) |
| Apex Patterns (Triggers, Async, DML, Collections) | [../salesforce-developer/references/apex-patterns.md](../salesforce-developer/references/apex-patterns.md) |
| Security & Sharing | [../salesforce-developer/references/security-sharing.md](../salesforce-developer/references/security-sharing.md) |
| SOQL Optimization | [../salesforce-developer/references/soql-optimization.md](../salesforce-developer/references/soql-optimization.md) |
| LWC Guide | [../salesforce-developer/references/lwc-guide.md](../salesforce-developer/references/lwc-guide.md) |
| Deployment & DevOps | [../salesforce-developer/references/deployment-devops.md](../salesforce-developer/references/deployment-devops.md) |

---

## Code Review Process

### 1. Initial Assessment

Quickly identify:
- **Code Type** — Apex, LWC, Aura, Flow, Formula, Validation Rule
- **Scope** — Single class, trigger, component, or complex feature
- **Context** — New feature, bug fix, refactor, performance optimization
- **Risk Level** — Critical path (integration, security), standard business logic, utility code

### 2. Dimensional Review

Conduct systematic reviews across each dimension using the appropriate checklist:

#### Security & Compliance
- [ ] Sharing keywords (`with sharing`, `without sharing`, `inherited sharing`)
- [ ] CRUD/FLS validation (`Security.stripInaccessible()`, `WITH SECURITY_ENFORCED`)
- [ ] SOQL injection prevention (bind variables, no concatenation)
- [ ] Sensitive data handling (PII, encryption, field-level security)
- [ ] API authentication and authorization

#### Performance & Governor Limits
- [ ] No SOQL/DML in loops
- [ ] Query consolidation and selectivity
- [ ] Bulkification for 200+ record batches
- [ ] CPU time and heap size compliance
- [ ] Query row limits and batch processing

#### Architecture & Design
- [ ] Layer separation (Trigger → Handler → Service → Selector)
- [ ] Naming conventions consistency
- [ ] SOLID principles adherence
- [ ] Code reusability and DRY principle
- [ ] Dependency management and isolation

#### Maintainability & Quality
- [ ] Code clarity and readability
- [ ] Comment quality (complex logic only)
- [ ] Method/class size and complexity
- [ ] Hardcoded values and magic numbers
- [ ] Documentation completeness

#### Error Handling
- [ ] try-catch-finally patterns
- [ ] Error logging and audit trails
- [ ] Exception types and specificity
- [ ] User error messaging
- [ ] Recovery strategies

#### Testing
- [ ] Test case variety (positive, negative, edge)
- [ ] Coverage percentage (75% minimum, 90%+ goal)
- [ ] Bulk operations testing (200+ records)
- [ ] Async operations (`Test.startTest()`/`Test.stopTest()`)
- [ ] Mock and stub usage

#### Deployment Readiness
- [ ] Metadata completeness (-meta.xml files)
- [ ] API version consistency (66.0 minimum)
- [ ] Permission set updates
- [ ] CI/CD pipeline compatibility
- [ ] Rollback strategy

#### Modern Best Practices
- [ ] Safe Navigation Operator (`?.`)
- [ ] Enhanced switch statements
- [ ] Assert class usage
- [ ] Queueable over `@future`
- [ ] Latest API features

### 3. Severity Classification

Rate findings using standard severity levels:

| Severity | Definition | Action |
|---|---|---|
| 🔴 **CRITICAL** | Security vulnerability, data loss risk, deployment blocker | **MUST FIX** before merge |
| 🟠 **HIGH** | Governor limits violation, major performance issue, sharing bypass | **SHOULD FIX** before merge |
| 🟡 **MEDIUM** | Code smell, technical debt, maintainability issue | Fix in next sprint |
| ⚪ **LOW** | Style inconsistency, minor optimization, documentation | Fix when convenient |
| 📝 **ENHANCEMENT** | Suggestion for improvement, future optimization | Consider for v2 |

### 4. Reporting

Document findings in a structured format:

```markdown
# Code Review Summary

**Reviewer:** [AI Reviewer Name]  
**Reviewed:** [Files/Classes]  
**Risk Level:** [Critical/High/Medium/Low]  

## Security Review
- [Findings and recommendations]

## Performance Review
- [Governor limit analysis]

## Architecture Review
- [Design pattern evaluation]

## Test Coverage
- [Coverage analysis and gaps]

## Deployment Readiness
- [Metadata and CI/CD checks]

## Summary
[Overall assessment, risk score, merge recommendation]
```

---

## Common Patterns to Flag

### Critical Issues (MUST FIX)

1. **SOQL Injection** — Dynamic SOQL with string concatenation
   ```apex
   // ❌ CRITICAL: SOQL Injection vulnerability
   String name = userInput;
   List<Account> accounts = Database.query('SELECT Id FROM Account WHERE Name = \'' + name + '\'');
   
   // ✅ Correct: Bind variable
   List<Account> accounts = [SELECT Id FROM Account WHERE Name = :name];
   ```

2. **No Sharing Enforcement** — Missing `with sharing` keyword
   ```apex
   // ❌ CRITICAL: No sharing enforcement
   public class AccountService {
       public List<Account> getAll() { return [SELECT Id FROM Account]; }
   }
   
   // ✅ Correct: Enforce sharing
   public with sharing class AccountService {
       public List<Account> getAll() { return [SELECT Id FROM Account]; }
   }
   ```

3. **CRUD/FLS Bypass** — No `Security.stripInaccessible()`
   ```apex
   // ❌ CRITICAL: FLS bypass
   Account acc = [SELECT Id, Name, Sensitive_Field__c FROM Account WHERE Id = :id];
   
   // ✅ Correct: Enforce FLS
   Account acc = [SELECT Id, Name FROM Account WHERE Id = :id WITH SECURITY_ENFORCED];
   ```

4. **SOQL in Loop** — Causes governor limit violation
   ```apex
   // ❌ CRITICAL: SOQL in loop (up to 200 queries)
   for (Id accountId : accountIds) {
       List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :accountId];
   }
   
   // ✅ Correct: Bulkified query
   Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
   for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
       List<Contact> contacts = contactsByAccount.get(c.AccountId);
       if (contacts == null) {
           contacts = new List<Contact>();
           contactsByAccount.put(c.AccountId, contacts);
       }
       contacts.add(c);
   }
   ```

### High Issues (SHOULD FIX)

1. **DML in Loop** — Wastes DML limit
   ```apex
   // ❌ HIGH: DML in loop
   for (Account acc : accounts) {
       update acc;  // Up to 150 DML statements
   }
   
   // ✅ Correct: Bulk DML
   update accounts;
   ```

2. **Hardcoded Record Type IDs** — Breaks in different orgs
   ```apex
   // ❌ HIGH: Hardcoded Id
   if (acc.RecordTypeId == '0121A000000IRFfQAW') { }
   
   // ✅ Correct: Query by name
   Map<String, Id> rtByName = new Map<String, Id>();
   for (RecordType rt : [SELECT Id, Name FROM RecordType WHERE SObjectType = 'Account']) {
       rtByName.put(rt.Name, rt.Id);
   }
   ```

3. **Recursive Trigger without Prevention** — Causes infinite loops
   ```apex
   // ❌ HIGH: No recursion prevention
   trigger AccountTrigger on Account (after update) {
       update Trigger.new;  // Infinite loop!
   }
   
   // ✅ Correct: Track processed records
   public class AccountTriggerHandler {
       private static Set<Id> processedIds = new Set<Id>();
       // ... recursion prevention logic ...
   }
   ```

4. **Empty Catch Blocks** — Silently swallows errors
   ```apex
   // ❌ HIGH: Silent error
   try {
       update records;
   } catch (Exception e) {
       // Error hidden!
   }
   
   // ✅ Correct: Log or handle error
   try {
       update records;
   } catch (Exception e) {
       System.debug(LoggingLevel.ERROR, 'Update failed: ' + e.getMessage());
       throw new ApplicationException('Update failed', e);
   }
   ```

---

## Review Output Template

### Executive Summary
- **Risk Level**: High/Medium/Low
- **Critical Issues**: [Count]
- **Recommendations**: [Priority order]
- **Merge Decision**: Approve / Request Changes / Needs Rework

### Detailed Findings

| # | Severity | File | Line(s) | Finding | Recommendation |
|---|----------|------|---------|---------|-----------------|
| 1 | 🔴 CRITICAL | AccountService.cls | 42-45 | SOQL Injection — dynamic query concatenation | Use bind variables instead |
| 2 | 🟠 HIGH | AccountService.cls | 50 | Missing `with sharing` keyword | Add `with sharing` to class declaration |
| 3 | 🟡 MEDIUM | AccountService.cls | 78-90 | Class exceeds 1000 lines — split into multiple classes | Refactor into logical units |
| 4 | ⚪ LOW | AccountService.cls | 15 | Missing JSDoc comment | Add class documentation |

### Positive Findings

- ✅ Excellent bulkification strategy
- ✅ Comprehensive error handling
- ✅ 92% test coverage with edge cases
- ✅ Modern Apex patterns (safe navigation, enhanced switch)

---

## Review Checklist Quick Links

### By File Type

- **Apex Classes** → [apex-review-checklist.md](references/apex-review-checklist.md)
- **Triggers** → [apex-review-checklist.md](references/apex-review-checklist.md) + [error-handling-review-checklist.md](references/error-handling-review-checklist.md)
- **LWC Components** → [lwc-review-checklist.md](references/lwc-review-checklist.md)
- **Aura Components** → [aura-review-checklist.md](references/aura-review-checklist.md)
- **Flows** → [sf-design-pattern-review-checklist.md](references/sf-design-pattern-review-checklist.md)
- **Deployment** → [deployment-readiness.md](references/deployment-readiness.md)

### By Dimension

- **Security** → [security-compliance-review-checklist.md](references/security-compliance-review-checklist.md)
- **Performance** → [performance-governorlimits-review-checklist.md](references/performance-governorlimits-review-checklist.md)
- **Architecture** → [sf-design-pattern-review-checklist.md](references/sf-design-pattern-review-checklist.md)
- **Testing** → [testcoverage-quality-review-checklist.md](references/testcoverage-quality-review-checklist.md)
- **Errors** → [error-handling-review-checklist.md](references/error-handling-review-checklist.md)

---

## Key Review Principles

1. **Assume positive intent** — Treat the developer as a peer, not an adversary
2. **Explain the why** — Don't just flag issues; explain business/technical reason
3. **Suggest solutions** — Provide code examples when possible
4. **Focus on impact** — Prioritize security, performance, maintainability
5. **Be consistent** — Apply same standards across all code
6. **Educate** — Reviews are opportunities to share knowledge
7. **Encourage growth** — Praise good patterns alongside constructive feedback
8. **Respect context** — Understand deadlines, complexity, and business priorities

---

## What This Skill Does NOT Do

❌ **Does not auto-approve or auto-merge code** — All findings require human validation  
❌ **Does not replace human review** — Use as a first pass before peer review  
❌ **Does not guarantee 100% security** — Some vulnerabilities require manual analysis  
❌ **Does not enforce style** — Focuses on substance over formatting  
❌ **Does not require exact fixes** — Suggestions; developers make final decisions  

---

## Integration with Development Workflow

### Typical Code Review Workflow

```
Developer creates Pull Request
        ↓
Automated CI/CD checks (linting, syntax, unit tests)
        ↓
AI Code Review → Generates findings report
        ↓
Developer reviews findings + peer code review
        ↓
Developer makes updates based on feedback
        ↓
AI Code Review (second pass) → Validates fixes
        ↓
Peer approval
        ↓
Merge to main/release branch
```

### Pre-Commit Local Review

Developers can use this skill locally before pushing:

```bash
# Review a file before commit
copilot code-review force-app/main/default/classes/AccountService.cls

# Review changed files in branch
copilot code-review --changed-files

# Generate detailed security review
copilot code-review --security-only AccountService.cls
```

---

## Performance Expectations

- **Small changes** (1-5 files, <500 lines): 30-60 seconds
- **Medium changes** (5-15 files, 500-2000 lines): 1-2 minutes
- **Large changes** (15+ files, 2000+ lines): 3-5 minutes
- **Full codebase review** (1000+ files): Batch processing (multiple passes)

---

## Related Documentation

- [Salesforce Developer Skill](../salesforce-developer/SKILL.md) — Code generation and patterns
- [Salesforce Architect Skill](../salesforce-architect-skill/SKILL.md) — Solution design and architecture
- [Apex Coding Rules](../Blogs/salesforce-apex-coding-rules.md) — Comprehensive Apex standards
- [LWC Coding Rules](../Blogs/salesforce-lwc-coding-rules.md) — Comprehensive LWC standards

---

## Version History

**v2.0** (2026-11) — Enhanced multi-dimensional review framework, expanded checklists, improved severity classification  
**v1.0** (2026-06) — Initial release with basic Apex and LWC review capabilities
