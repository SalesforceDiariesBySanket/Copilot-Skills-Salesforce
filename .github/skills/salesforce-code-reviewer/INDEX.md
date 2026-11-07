# Salesforce Code Reviewer Skill - Index & Navigation

**Status**: ✅ Production-Ready  
**Version**: 2.0  
**Last Updated**: November 7, 2026  

---

## 🎯 Quick Navigation

### Start Here
1. **[SKILL.md](./SKILL.md)** — Main skill definition (15 min read)
   - How to use the skill
   - Review process flow
   - Severity classification
   - Common patterns to flag

2. **[SKILL_QUICK_START.md](../../SKILL_QUICK_START.md)** — Quick start guide (5 min read)
   - Getting started
   - Common scenarios
   - Severity reference
   - Tips for best results

---

## 📚 Review Checklists by Scenario

### "Review My Apex Code"
Use: [apex-review-checklist.md](./references/apex-review-checklist.md)
- Trigger design & architecture
- Bulkification & governor limits
- Security & access control
- Error handling & logging
- Code quality & maintainability
- Modern Apex patterns
- Testing & coverage
- Performance considerations

---

### "Secure My Code - Security Audit"
Use: [security-compliance-review-checklist.md](./references/security-compliance-review-checklist.md)
- Data access & sharing enforcement
- CRUD/FLS enforcement
- SOQL injection prevention
- Sensitive data handling
- External integration security
- Authentication & authorization
- Compliance frameworks (GDPR, HIPAA, PCI-DSS, SOX, CCPA)

---

### "Optimize Performance"
Use: [performance-governorlimits-review-checklist.md](./references/performance-governorlimits-review-checklist.md)
- Bulkification patterns
- Governor limits compliance
- Async Apex patterns
- Query optimization
- Memory management
- Performance testing

---

### "Fix Error Handling"
Use: [error-handling-review-checklist.md](./references/error-handling-review-checklist.md)
- Exception handling patterns
- DML error handling
- Callout error handling
- Error logging
- User error messages
- Audit & compliance

---

### "Improve Test Coverage"
Use: [testcoverage-quality-review-checklist.md](./references/testcoverage-quality-review-checklist.md)
- Coverage requirements
- Test structure
- Positive/negative/edge case testing
- Bulk testing patterns
- Async testing patterns
- Mock/stub usage
- Jest testing for LWC

---

### "Review Architecture & Design"
Use: [sf-design-pattern-review-checklist.md](./references/sf-design-pattern-review-checklist.md)
- Layer separation (Trigger → Handler → Service → Selector)
- SOLID principles
- Naming conventions
- DRY principle
- Configuration over customization
- API versioning

---

### "Review LWC Component"
Use: [lwc-review-checklist.md](./references/lwc-review-checklist.md)
- Template best practices
- JavaScript patterns
- Apex integration
- Event communication
- Data handling
- Navigation
- Jest testing

---

### "Review Aura Component"
Use: [aura-review-checklist.md](./references/aura-review-checklist.md)
- Component basics
- Markup & styling
- Controller & logic
- Data handling
- Event communication
- Migration path to LWC

---

### "Pre-Deployment Review"
Use: [deployment-readiness.md](./references/deployment-readiness.md)
- Metadata completeness
- Code quality
- Test coverage
- Permission sets
- CI/CD pipeline
- Rollback strategy
- Pre/post-deployment tasks

---

## 📊 Checklist Quick Reference

| File | Size | Items | Best For |
|------|------|-------|----------|
| [apex-review-checklist.md](./references/apex-review-checklist.md) | 26 KB | 121 | Apex classes & triggers |
| [security-compliance-review-checklist.md](./references/security-compliance-review-checklist.md) | 12 KB | 63 | Security audits |
| [performance-governorlimits-review-checklist.md](./references/performance-governorlimits-review-checklist.md) | 14 KB | 80 | Performance optimization |
| [error-handling-review-checklist.md](./references/error-handling-review-checklist.md) | 14 KB | 60 | Error handling patterns |
| [testcoverage-quality-review-checklist.md](./references/testcoverage-quality-review-checklist.md) | 16 KB | 73 | Test coverage & quality |
| [sf-design-pattern-review-checklist.md](./references/sf-design-pattern-review-checklist.md) | 15 KB | 58 | Architecture & design |
| [lwc-review-checklist.md](./references/lwc-review-checklist.md) | 14 KB | 72 | LWC components |
| [aura-review-checklist.md](./references/aura-review-checklist.md) | 10 KB | 47 | Aura components |
| [deployment-readiness.md](./references/deployment-readiness.md) | 15 KB | 70 | Pre-deployment validation |

---

## 🔍 Finding What You Need

### By Code Type
- **Apex Class**: apex-review-checklist.md
- **Apex Trigger**: apex-review-checklist.md
- **LWC Component**: lwc-review-checklist.md
- **Aura Component**: aura-review-checklist.md
- **Integration/API**: security-compliance-review-checklist.md + performance-governorlimits-review-checklist.md
- **Flow**: sf-design-pattern-review-checklist.md
- **Deployment Package**: deployment-readiness.md

### By Review Dimension
- **Security**: security-compliance-review-checklist.md
- **Performance**: performance-governorlimits-review-checklist.md
- **Architecture**: sf-design-pattern-review-checklist.md
- **Quality**: apex-review-checklist.md
- **Error Handling**: error-handling-review-checklist.md
- **Testing**: testcoverage-quality-review-checklist.md
- **Deployment**: deployment-readiness.md

### By Severity
- **🔴 CRITICAL issues**: All checklists (search for "CRITICAL")
- **🟠 HIGH issues**: All checklists (search for "HIGH")
- **🟡 MEDIUM issues**: All checklists (search for "MEDIUM")
- **⚪ LOW issues**: All checklists (search for "LOW")
- **📝 ENHANCEMENT**: All checklists (search for "ENHANCEMENT")

---

## 🎓 How to Use This Skill

### Step 1: Load the Skill
```
/skill salesforce-code-reviewer
```

### Step 2: Request a Code Review
```
Please review my Apex class for:
- Security issues
- Performance problems
- Code quality concerns
- Test coverage gaps
```

### Step 3: Get Structured Feedback
The skill will:
1. Analyze your code against all relevant checklists
2. Identify issues by severity
3. Provide actionable remediation guidance
4. Generate a structured findings report

### Step 4: Address Findings
Use the guidance in the relevant checklist to fix issues:
- 🔴 CRITICAL: Must fix before merge
- 🟠 HIGH: Should fix before merge
- 🟡 MEDIUM: Fix in next sprint
- ⚪ LOW: Nice to have
- 📝 ENHANCEMENT: Consider for backlog

---

## 📋 Common Review Scenarios

### Scenario 1: Code Review in PR
```
/skill salesforce-code-reviewer

Please review this PR for:
1. Security vulnerabilities
2. Governor limit violations
3. Code quality issues
4. Test coverage gaps
5. Architecture compliance

Provide: Severity-classified findings + go/no-go recommendation
```

### Scenario 2: Security Audit
```
/skill salesforce-code-reviewer

Perform security audit:
- SOQL injection risks
- FLS/CRUD enforcement
- Sharing enforcement
- Hardcoded credentials
- Compliance framework (GDPR, HIPAA, etc.)

Highlight: All security risks by severity
```

### Scenario 3: Performance Optimization
```
/skill salesforce-code-reviewer

Performance review:
- SOQL/DML in loops
- Governor limit compliance
- Bulkification patterns
- Query optimization
- Async pattern selection

Recommend: Performance improvements
```

### Scenario 4: Pre-Deployment
```
/skill salesforce-code-reviewer

Deployment readiness check:
- Code coverage
- Metadata completeness
- Test results
- Security review passed
- Rollback plan ready

Recommend: Go/no-go for production
```

---

## 🔗 Related Skills

**Salesforce Developer Skill**
- Location: `../../salesforce-developer/SKILL.md`
- Use for: Learning how to write correct Salesforce code
- Includes: Best practices, patterns, do's and don'ts

**Salesforce Architect Skill**
- Location: `../../salesforce-architect-skill/SKILL.md`
- Use for: Solution design and architecture guidance
- Includes: Design patterns, Well-Architected Framework

---

## 📊 Coverage Summary

✅ **8 Review Dimensions**
- Security & Compliance
- Performance & Governor Limits
- Architecture & Design Patterns
- Maintainability & Code Quality
- Error Handling & Logging
- Testing & Coverage
- Deployment & DevOps
- Modern Best Practices

✅ **8 Major Code Types**
- Apex Classes
- Apex Triggers
- LWC Components
- Aura Components
- API/Integration Code
- Flows
- Deployment Packages
- Batch/Queueable Code

✅ **5 Compliance Frameworks**
- GDPR
- HIPAA
- PCI-DSS
- SOX
- CCPA

---

## 📞 Support & FAQ

### Q: Where do I start?
A: Read [SKILL.md](./SKILL.md) first (15 min), then use specific checklists as needed.

### Q: How do I know which checklist to use?
A: Use the "By Code Type" table above, or load the skill and describe your code.

### Q: What if I have multiple issues?
A: Use the severity classification to prioritize:
- 🔴 CRITICAL → Fix before merge
- 🟠 HIGH → Should fix before merge
- 🟡 MEDIUM → Fix in next sprint

### Q: Can I use this for PR reviews?
A: Yes! The skill includes structured reporting templates for PR reviews.

### Q: Is this for production code only?
A: No, use it for any Salesforce code review (dev, test, production).

### Q: Does this include Flow/automation patterns?
A: Partially. See [sf-design-pattern-review-checklist.md](./references/sf-design-pattern-review-checklist.md) for basic patterns. Detailed Flow checklist coming soon.

---

## 🎯 Key Files

**Must-Read**:
- [SKILL.md](./SKILL.md) — Main skill definition
- [../../SKILL_QUICK_START.md](../../SKILL_QUICK_START.md) — Quick start guide

**Reference**:
- [../../CODE_REVIEWER_SKILL_SUMMARY.md](../../CODE_REVIEWER_SKILL_SUMMARY.md) — Full documentation
- [../../BUILD_REPORT.md](../../BUILD_REPORT.md) — Build report & statistics

**Checklists**:
- All files in [./references/](./references/) directory

---

## ✅ Quality Standards

This skill meets these quality standards:
✅ Production-ready  
✅ Comprehensive coverage  
✅ Real-world examples  
✅ Actionable guidance  
✅ Consistent formatting  
✅ Cross-validated references  

---

## 🚀 Ready to Review Code?

Load the skill and start reviewing:

```
/skill salesforce-code-reviewer

Review my [code type] for:
- [dimension 1]
- [dimension 2]
- [dimension 3]
```

---

**Version**: 2.0 (Production-Ready)  
**Status**: ✅ Complete  
**Last Updated**: November 7, 2026
