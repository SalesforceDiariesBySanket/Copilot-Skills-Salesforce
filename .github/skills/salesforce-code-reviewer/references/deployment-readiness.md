# Deployment Readiness Review Checklist

> **Review Category**: Metadata Completeness, CI/CD Compliance, Production Readiness  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Metadata Completeness

### File Structure

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| All Apex classes have `-meta.xml` files | ☐ Pass ☐ Fail | 🟠 HIGH | Example: `AccountService.cls-meta.xml` |
| All LWC components have `-meta.xml` files | ☐ Pass ☐ Fail | 🟠 HIGH | Standard LWC metadata configuration |
| All Aura components have `-meta.xml` files | ☐ Pass ☐ Fail | 🟠 HIGH | `component-meta.xml` in component bundle |
| All Apex tests have `-meta.xml` files | ☐ Pass ☐ Fail | 🟠 HIGH | Test classes need metadata |
| Metadata files not manually edited | ☐ Pass ☐ Fail | 🟡 MEDIUM | Generate via IDE; don't hand-edit |

### Apex Class Metadata

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `apiVersion` set to 66.0 (current or later) | ☐ Pass ☐ Fail | 🟠 HIGH | Use latest GA version |
| `status` set to `Active` | ☐ Pass ☐ Fail | 🟠 HIGH | Inactive = class not available |
| Custom settings/objects have correct metadata | ☐ Pass ☐ Fail | 🟡 MEDIUM | Entity visibility, sharing settings |

---

## 2. Test Coverage & Validation

### Coverage Requirements

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Overall code coverage ≥75% | ☐ Pass ☐ Fail | 🟠 HIGH | Org-wide minimum for deployment |
| Critical business logic ≥95% coverage | ☐ Pass ☐ Fail | 🔴 CRITICAL | Security, integrations, financial |
| No classes with 0% coverage | ☐ Pass ☐ Fail | 🟠 HIGH | Every class needs at least one test |
| All test classes pass | ☐ Pass ☐ Fail | 🔴 CRITICAL | Tests must pass before deploy |

### Deployment Test Modes

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Code tested with RunAllTestsInOrg (if deploying to prod) | ☐ Pass ☐ Fail | 🟠 HIGH | All org tests run; must pass |
| Specific test classes identified for CI/CD | ☐ Pass ☐ Fail | 🟡 MEDIUM | Package should run specific test suites |
| Test data doesn't interfere with production data | ☐ Pass ☐ Fail | 🟠 HIGH | Tests isolated; prod data not modified |

---

## 3. Code Quality & Standards

### Linting & Formatting

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Apex code passes PMD linting | ☐ Pass ☐ Fail | 🟡 MEDIUM | Run `sf scanner run -t apex` |
| LWC code passes ESLint | ☐ Pass ☐ Fail | 🟡 MEDIUM | Run `npm run lint` |
| Code formatted consistently | ☐ Pass ☐ Fail | 🟡 MEDIUM | Run Prettier: `npm run prettier` |
| No console.log or System.debug in production code | ☐ Pass ☐ Fail | 🟡 MEDIUM | Remove debug statements before deploy |

### Documentation

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| README updated with feature documentation | ☐ Pass ☐ Fail | 🟡 MEDIUM | Describe functionality, dependencies, configuration |
| CHANGELOG entry added | ☐ Pass ☐ Fail | 🟡 MEDIUM | What changed? Why? When? |
| API documentation for public methods | ☐ Pass ☐ Fail | 🟡 MEDIUM | JSDoc or Markdown file |
| Configuration steps documented | ☐ Pass ☐ Fail | 🟡 MEDIUM | Setup guide for deploying team |
| Known issues/limitations listed | ☐ Pass ☐ Fail | 🟡 MEDIUM | Transparency prevents surprises |

---

## 4. Permission Set Updates

### Field-Level Security

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| New fields added to permission sets | ☐ Pass ☐ Fail | 🟠 HIGH | Update FLS for new custom fields |
| Standard fields not included in FLS | ☐ Pass ☐ Fail | ⚪ LOW | Standard Name, Id, CreatedDate don't need FLS |
| Correct access levels assigned (Read/Edit) | ☐ Pass ☐ Fail | 🟠 HIGH | Match business requirements |
| Permission sets by role identified | ☐ Pass ☐ Fail | 🟡 MEDIUM | Document which profiles/psets need access |

### Apex Class Access

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| New Apex classes added to permission sets | ☐ Pass ☐ Fail | 🟠 HIGH | LWC calls Apex via `@AuraEnabled`; pset needs access |
| Custom permissions created if needed | ☐ Pass ☐ Fail | 🟡 MEDIUM | Sensitive operations protected by custom perms |
| Custom permission assignments in psets | ☐ Pass ☐ Fail | 🟡 MEDIUM | Assign custom perms to appropriate roles |

### Flow/Custom Settings Access

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Flows accessible to required profiles | ☐ Pass ☐ Fail | 🟡 MEDIUM | Set flow visibility appropriately |
| Custom settings readable by required users | ☐ Pass ☐ Fail | 🟡 MEDIUM | Org-level settings vs User-level |

---

## 5. Configuration & Custom Metadata

### Custom Metadata Types

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Custom Metadata Type records created | ☐ Pass ☐ Fail | 🟠 HIGH | Integration endpoints, feature toggles, etc. |
| Metadata records deployed with code | ☐ Pass ☐ Fail | 🟠 HIGH | Include in package.xml for deployment |
| Metadata values match target environment | ☐ Pass ☐ Fail | 🟠 HIGH | URLs, endpoints, timeouts correct for prod |

### Custom Settings

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Organization/User-level settings created | ☐ Pass ☐ Fail | 🟡 MEDIUM | Org-level for global; User-level for per-user |
| Default values set appropriately | ☐ Pass ☐ Fail | 🟡 MEDIUM | Sensible defaults prevent null reference errors |
| Settings not containing secrets | ☐ Pass ☐ Fail | 🔴 CRITICAL | Use Named Credentials for credentials |

---

## 6. Static Resources & Assets

### Static Resources

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Static resources minified (if applicable) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reduce size for faster loading |
| Third-party libraries included with license | ☐ Pass ☐ Fail | 🟠 HIGH | Document licenses for compliance |
| Resource caching configured | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cache-Control headers set appropriately |

---

## 7. Rollback & Disaster Recovery

### Rollback Plan

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Rollback procedure documented | ☐ Pass ☐ Fail | 🟠 HIGH | How to revert if deployment fails? |
| Data migration steps documented (if applicable) | ☐ Pass ☐ Fail | 🟠 HIGH | Before/after data handling |
| Rollback tested in sandbox | ☐ Pass ☐ Fail | 🟡 MEDIUM | Ensure rollback procedure actually works |
| Communication plan for outages | ☐ Pass ☐ Fail | 🟡 MEDIUM | Who to notify if something goes wrong? |

### Backup Strategy

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Data backup taken before deployment | ☐ Pass ☐ Fail | 🟡 MEDIUM | Sandbox refresh after testing |
| Configuration backup maintained | ☐ Pass ☐ Fail | 🟡 MEDIUM | Version control holds all metadata |
| Recovery time objective (RTO) defined | ☐ Pass ☐ Fail | 🟡 MEDIUM | How long can system be down? |
| Recovery point objective (RPO) defined | ☐ Pass ☐ Fail | 🟡 MEDIUM | How much data loss acceptable? |

---

## 8. CI/CD & Automation

### Build Pipeline

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Package.xml includes all changes | ☐ Pass ☐ Fail | 🟠 HIGH | All metadata to be deployed listed |
| Destructive changes documented | ☐ Pass ☐ Fail | 🟠 HIGH | Separate destructiveChanges.xml if deleting metadata |
| Build pipeline runs automated tests | ☐ Pass ☐ Fail | 🟠 HIGH | CI/CD fails if tests don't pass |
| Linting runs in pipeline | ☐ Pass ☐ Fail | 🟡 MEDIUM | Code quality checked automatically |
| Code coverage enforced in pipeline | ☐ Pass ☐ Fail | 🟡 MEDIUM | Fail if coverage drops below threshold |

### Deployment Strategy

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Deployment method chosen (Change Set vs sf CLI) | ☐ Pass ☐ Fail | 🟡 MEDIUM | sf CLI recommended for modern workflows |
| Deployment validation run first | ☐ Pass ☐ Fail | 🟠 HIGH | Test deploy before actual deploy |
| Run tests specification correct | ☐ Pass ☐ Fail | 🟠 HIGH | Which tests to run? All? Specific classes? |
| Rollback tests included | ☐ Pass ☐ Fail | 🟡 MEDIUM | Verify rollback works before production deploy |

---

## 9. Production Readiness Checklist

### Pre-Deployment Tasks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| ☐ Code reviewed and approved | Approval | 🟠 HIGH | At least 2 reviewers for production |
| ☐ All tests passing | Tests | 🟠 HIGH | 75%+ coverage, all tests green |
| ☐ Performance testing completed | Performance | 🟡 MEDIUM | Load testing, query optimization verified |
| ☐ Security review passed | Security | 🔴 CRITICAL | SOQL injection, FLS, sharing checks |
| ☐ UAT testing completed | UAT | 🟡 MEDIUM | Business stakeholders validated functionality |
| ☐ Documentation completed | Docs | 🟡 MEDIUM | README, CHANGELOG, API docs updated |
| ☐ Rollback plan tested | Rollback | 🟠 HIGH | Verified ability to revert if needed |
| ☐ Stakeholders notified | Communication | 🟡 MEDIUM | Users informed of changes, downtime if any |

### Deployment Tasks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| ☐ Validation deployment passes | Validation | 🟠 HIGH | Run deployment in test mode first |
| ☐ Final backup taken | Backup | 🟠 HIGH | Data backed up before actual deploy |
| ☐ Deployment executed | Deploy | 🟠 HIGH | Run actual deployment during maintenance window |
| ☐ All tests re-run | Tests | 🟠 HIGH | Verify tests pass in production environment |
| ☐ Smoke tests passed | Smoke Tests | 🟠 HIGH | Quick validation that critical features work |
| ☐ Monitoring enabled | Monitoring | 🟡 MEDIUM | Error logs, performance metrics watched |

### Post-Deployment Tasks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| ☐ UAT validation in production | UAT | 🟡 MEDIUM | Business confirms functionality works |
| ☐ Error logs monitored | Monitoring | 🟡 MEDIUM | Watch for errors in first 24 hours |
| ☐ Performance monitored | Monitoring | 🟡 MEDIUM | Query performance, CPU usage normal? |
| ☐ Stakeholders notified of completion | Communication | 🟡 MEDIUM | Confirm deployment successful |

---

## Review Output Template

### Deployment Readiness Assessment
- **Overall Readiness**: Production-Ready / Ready with Minor Issues / Needs Work / Not Ready
- **Blocker Issues**: [Count of critical issues]
- **Ready to Deploy**: ✅ Yes | ⚠️ With Cautions | ❌ No

### Deployment Checklist Status

| Item | Status | Notes |
|------|--------|-------|
| Metadata Complete | ✅ Pass | All -meta.xml files present |
| Code Coverage | ✅ Pass | 78% overall coverage |
| Tests Passing | ✅ Pass | All 547 tests pass |
| Linting | ⚠️ Warnings | 3 minor ESLint warnings (non-blocking) |
| Permission Sets | ✅ Pass | Updated for new Apex classes |
| Documentation | ✅ Pass | README and CHANGELOG updated |
| Rollback Plan | ✅ Pass | Tested in sandbox |
| CI/CD Pipeline | ✅ Pass | All automation checks pass |

### Critical Issues

| # | Issue | Resolution | Status |
|---|-------|-----------|--------|
| 1 | 25% code coverage (below 75%) | Add missing tests for error paths | ❌ Blocking |
| 2 | FeatureToggle class not in permission set | Add to Finance_Analyst pset | ⚠️ High Priority |

### Recommendations

- Add 50+ lines of test code to reach 75% minimum coverage
- Schedule deployment during maintenance window (2 AM weekend)
- Have rollback team on standby for first 4 hours

### Final Assessment
**Status**: ⚠️ **Needs Rework** — Address code coverage gap before production deployment

---

## Deployment Validation Commands

```bash
# Validate without deploying
sf project deploy validate --source-dir force-app --target-org prod

# Run specific test classes
sf apex test run --class-names AccountServiceTest,ContactTriggerHandlerTest --target-org prod

# Check code coverage
sf apex test run --code-coverage --target-org prod

# Deploy with rollback
sf project deploy start --source-dir force-app --target-org prod --test-level RunSpecifiedTests --tests AccountServiceTest ContactTriggerHandlerTest
```
