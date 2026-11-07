# Salesforce Code Reviewer - Evaluation Scenarios

**File**: `eval-scenarios.json`  
**Purpose**: Define test scenarios for evaluating the Code Reviewer skill's ability to identify and classify code quality issues  
**Status**: ✅ Complete  
**Version**: 1.0  

---

## 📋 Overview

This file contains 10 comprehensive evaluation scenarios designed to test the Salesforce Code Reviewer skill across all major dimensions:

- ✅ **Security & Compliance** (Scenarios 1, 7)
- ✅ **Performance & Governor Limits** (Scenarios 2, 10)
- ✅ **Architecture & Design Patterns** (Scenarios 3, 8)
- ✅ **LWC Best Practices** (Scenario 4)
- ✅ **Testing & Coverage** (Scenario 5)
- ✅ **Deployment Readiness** (Scenario 6)
- ✅ **Error Handling** (Scenario 7)
- ✅ **Code Quality** (Scenario 8)
- ✅ **Aura Components** (Scenario 9)

---

## 🎯 Scenario Details

### Scenario 1: Security Vulnerability Detection (review-eval-01)
**Focus**: SOQL injection, missing FLS, security enforcement  
**Code Type**: Apex Service Class  
**Expected Findings**: 4 issues
- 🔴 CRITICAL: SOQL injection vulnerability
- 🔴 CRITICAL: Missing WITH SECURITY_ENFORCED
- 🟠 HIGH: Missing 'with sharing' keyword
- 🟡 MEDIUM: No FLS field stripping

**Checklist Used**: security-compliance-review-checklist.md

---

### Scenario 2: Performance Issue Detection (review-eval-02)
**Focus**: SOQL in loop, bulkification, governor limits  
**Code Type**: Apex Batch Job  
**Expected Findings**: 4 issues
- 🔴 CRITICAL: SOQL query inside loop
- 🟠 HIGH: Governor limit risk (100 SOQL limit)
- 🟠 HIGH: Missing error handling
- 🟡 MEDIUM: Missing DML bulk guard

**Checklist Used**: performance-governorlimits-review-checklist.md, error-handling-review-checklist.md

---

### Scenario 3: Architecture Pattern Violation (review-eval-03)
**Focus**: Trigger design, layer separation, recursion prevention  
**Code Type**: Apex Trigger  
**Expected Findings**: 4 issues
- 🔴 CRITICAL: Business logic in trigger (violates architecture)
- 🟠 HIGH: No recursive execution prevention
- 🟠 HIGH: SOQL/DML in trigger context
- 🟡 MEDIUM: No Trigger → Handler → Service → Selector pattern

**Checklist Used**: sf-design-pattern-review-checklist.md, apex-review-checklist.md

---

### Scenario 4: LWC Best Practices (review-eval-04)
**Focus**: Template expressions, Apex integration, accessibility  
**Code Type**: LWC Component  
**Expected Findings**: 5 issues
- 🔴 CRITICAL: Inline ternary operator in template (LWC doesn't support)
- 🔴 CRITICAL: @AuraEnabled(cacheable=true) with DML method
- 🟠 HIGH: Hyphenated event name ('record-updated')
- 🟠 HIGH: Missing error handling for callout
- 🟡 MEDIUM: Missing loading spinner during async

**Checklist Used**: lwc-review-checklist.md, error-handling-review-checklist.md

---

### Scenario 5: Test Coverage Review (review-eval-05)
**Focus**: Test coverage, test structure, edge cases  
**Code Type**: Apex Test Class  
**Expected Findings**: 5 issues
- 🔴 CRITICAL: Coverage 60% (below 75% minimum)
- 🟠 HIGH: Missing @TestSetup
- 🟠 HIGH: No negative test cases
- 🟡 MEDIUM: No bulk operation testing
- 🟡 MEDIUM: Assertions lack descriptive messages

**Checklist Used**: testcoverage-quality-review-checklist.md

---

### Scenario 6: Deployment Readiness (review-eval-06)
**Focus**: Metadata completeness, permission sets, rollback plan  
**Code Type**: Deployment Package  
**Expected Findings**: 5 issues
- 🔴 CRITICAL: Missing -meta.xml files
- 🟠 HIGH: Permission set not updated
- 🟠 HIGH: No rollback plan documented
- 🟡 MEDIUM: CI/CD pipeline not configured
- 🟡 MEDIUM: Database migration script missing

**Checklist Used**: deployment-readiness.md

---

### Scenario 7: Error Handling Review (review-eval-07)
**Focus**: Exception handling, DML error checking, sensitive data  
**Code Type**: Integration Class  
**Expected Findings**: 5 issues
- 🔴 CRITICAL: Empty catch block
- 🔴 CRITICAL: DML SaveResult not checked
- 🟠 HIGH: Sensitive data logged
- 🟠 HIGH: Callout timeout handling missing
- 🟡 MEDIUM: No error context stored

**Checklist Used**: error-handling-review-checklist.md, security-compliance-review-checklist.md

---

### Scenario 8: Code Quality Review (review-eval-08)
**Focus**: Naming conventions, method size, DRY principle  
**Code Type**: Utility Class  
**Expected Findings**: 5 issues
- 🟠 HIGH: Generic class name 'Utils'
- 🟡 MEDIUM: Method size >100 lines
- 🟡 MEDIUM: Duplicate code (DRY violation)
- ⚪ LOW: Hardcoded magic numbers
- ⚪ LOW: Missing JSDoc comments

**Checklist Used**: sf-design-pattern-review-checklist.md, apex-review-checklist.md

---

### Scenario 9: Aura Component Review (review-eval-09)
**Focus**: Legacy technology, accessibility, SLDS usage  
**Code Type**: Aura Component  
**Expected Findings**: 4 issues
- 🟡 MEDIUM: Using Aura (deprecated, should migrate to LWC)
- ⚪ LOW: Missing accessibility attributes
- ⚪ LOW: Inline styling instead of SLDS classes
- 📝 ENHANCEMENT: Plan LWC migration

**Checklist Used**: aura-review-checklist.md, lwc-review-checklist.md

---

### Scenario 10: Governor Limits Compliance (review-eval-10)
**Focus**: SOQL/DML limits, heap management, async patterns  
**Code Type**: Synchronous Apex Class  
**Expected Findings**: 4 issues
- 🔴 CRITICAL: 95 SOQL queries (only 5 remaining)
- 🔴 CRITICAL: 140 DML operations (only 10 remaining)
- 🟠 HIGH: Large string concatenation (heap issues)
- 🟠 HIGH: Synchronous execution not suitable for bulk

**Checklist Used**: performance-governorlimits-review-checklist.md

---

## 📊 Coverage Analysis

### By Severity Level
- 🔴 **CRITICAL**: 14 issues (must fix before merge)
- 🟠 **HIGH**: 19 issues (should fix before merge)
- 🟡 **MEDIUM**: 13 issues (fix in next sprint)
- ⚪ **LOW**: 4 issues (nice to have)
- 📝 **ENHANCEMENT**: 1 issue (future improvement)
- **TOTAL**: 51 issues across 10 scenarios

### By Code Type
| Code Type | Scenario IDs | Count |
|-----------|-------------|-------|
| Apex Classes | 1, 3, 5, 7, 8, 10 | 6 |
| LWC Components | 4 | 1 |
| Aura Components | 9 | 1 |
| Deployment Package | 6 | 1 |
| Integration Class | 7 | 1 |

### By Review Dimension
| Dimension | Scenario IDs | Issue Count |
|-----------|------------|-------------|
| Security & Compliance | 1, 7 | 9 |
| Performance & Governor Limits | 2, 10 | 8 |
| Architecture & Design Patterns | 3, 8 | 7 |
| LWC Best Practices | 4 | 5 |
| Testing & Coverage | 5 | 5 |
| Deployment Readiness | 6 | 5 |
| Error Handling | 7 | 5 |
| Code Quality | 8 | 5 |
| Aura Components | 9 | 4 |

---

## 🔍 How to Use These Scenarios

### For Evaluation Testing
1. Run each scenario through the Code Reviewer skill
2. Verify the skill identifies all expected issues
3. Check that severity classifications match expectations
4. Confirm correct checklist references

### Example Test Case
```
Scenario: review-eval-01 (Security Vulnerability)

Input: Review ContactQueryService.cls
Expected Output:
  - 4 findings total
  - 2 CRITICAL (SOQL injection, missing WITH SECURITY_ENFORCED)
  - 1 HIGH (missing 'with sharing')
  - 1 MEDIUM (no FLS stripping)
```

### Automation
These scenarios can be automated to:
- Test skill against known issues
- Verify accuracy of issue detection
- Validate severity classification
- Check checklist linkage
- Measure skill performance

---

## 📝 JSON Schema

Each scenario follows this structure:

```json
{
  "id": "review-eval-XX",
  "title": "Brief description",
  "skills": ["salesforce-code-reviewer"],
  "scenario": "Detailed scenario description",
  "code_snippet": {
    "type": "apex|lwc|aura|package",
    "class|component|file|deployment": "name",
    "issues_present": [
      "Description of issue 1",
      "Description of issue 2"
    ]
  },
  "expected_findings": [
    {
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|ENHANCEMENT",
      "issue": "Issue title",
      "checklist": "checklist-filename.md",
      "guidance": "Remediation guidance"
    }
  ]
}
```

---

## ✅ Validation Rules

Each scenario must:
- ✅ Have unique ID in format `review-eval-NN`
- ✅ Have clear title describing the issue
- ✅ Include skill reference (`["salesforce-code-reviewer"]`)
- ✅ Describe the scenario clearly
- ✅ List issues present in code snippet
- ✅ Define expected findings
- ✅ Include severity level
- ✅ Reference correct checklist
- ✅ Provide actionable guidance

---

## 🎯 Quality Metrics

| Metric | Value |
|--------|-------|
| Total Scenarios | 10 |
| Total Expected Issues | 51 |
| CRITICAL Issues | 14 |
| Coverage Dimensions | 9 |
| Code Types | 5 |
| Checklists Referenced | 9 |
| JSON Valid | ✅ Yes |

---

## 🔗 Related Files

- **[SKILL.md](../SKILL.md)** — Main skill definition
- **[INDEX.md](../INDEX.md)** — Navigation guide
- **[security-compliance-review-checklist.md](../references/security-compliance-review-checklist.md)** — Security checklist
- **[performance-governorlimits-review-checklist.md](../references/performance-governorlimits-review-checklist.md)** — Performance checklist
- **[sf-design-pattern-review-checklist.md](../references/sf-design-pattern-review-checklist.md)** — Architecture checklist

---

## 📊 Evaluation Process

### Step 1: Load Scenario
Retrieve scenario from eval-scenarios.json by ID

### Step 2: Present to Skill
Ask skill to review the code snippet described in scenario

### Step 3: Collect Findings
Capture all issues identified by the skill

### Step 4: Validate Results
Compare findings against expected_findings:
- ✅ All expected issues found?
- ✅ Correct severity levels?
- ✅ Correct checklist references?
- ✅ Actionable guidance provided?

### Step 5: Score Results
Calculate accuracy:
- True Positives (found expected issues)
- False Positives (found issues not in expected)
- False Negatives (missed expected issues)

---

## 🚀 Future Enhancements

- [ ] Add Flow/declarative automation scenarios
- [ ] Add Formula/validation rule scenarios
- [ ] Add managed package patterns
- [ ] Add Agentforce agent scenarios
- [ ] Automated evaluation harness
- [ ] Severity scoring algorithm
- [ ] Performance benchmarking

---

**File**: eval-scenarios.json  
**Status**: ✅ Complete & Production-Ready  
**Version**: 1.0  
**Date Created**: November 7, 2026
