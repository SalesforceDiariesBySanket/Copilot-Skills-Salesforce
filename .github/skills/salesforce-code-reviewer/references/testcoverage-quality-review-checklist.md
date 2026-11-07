# Test Coverage & Quality Review Checklist

> **Review Category**: Unit Tests, Integration Tests, Coverage, Code Quality  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Test Coverage Requirements

### Coverage Thresholds

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Overall code coverage ≥75% (org-wide minimum) | ☐ Pass ☐ Fail | 🟠 HIGH | Deploy requirement; higher for critical code |
| Critical business logic ≥95% coverage | ☐ Pass ☐ Fail | 🟠 HIGH | Security, integrations, financial calculations |
| Trigger handlers 100% coverage | ☐ Pass ☐ Fail | 🟠 HIGH | Triggers must be fully exercised |
| Controllers/API endpoints ≥90% coverage | ☐ Pass ☐ Fail | 🟠 HIGH | All user-facing code paths tested |
| Utility classes ≥80% coverage | ☐ Pass ☐ Fail | 🟡 MEDIUM | Helper/utility code covered but lower priority |

### Coverage by Code Type

| Code Type | Min Coverage | Best Practice |
|---|---|---|
| Apex Classes | 75% | 90%+ for critical |
| Apex Triggers | 100% | 100% required |
| LWC Components | 80%+ | 90%+ for critical paths |
| Aura Components | 70%+ | 85%+ for critical paths |
| Batch Apex | 80%+ | 90%+ for final data |
| Queueable Async | 80%+ | 90%+ for business logic |

---

## 2. Test Structure & Organization

### Test Class Organization

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Test class matches source class naming: `[ClassName]Test` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `AccountServiceTest` for `AccountService` |
| Test class in same folder as source code | ☐ Pass ☐ Fail | ⚪ LOW | Co-location improves discoverability |
| `@isTest` annotation on all test classes | ☐ Pass ☐ Fail | 🟡 MEDIUM | Marks class as test-only; not deployed to production |
| `@TestSetup` method creates baseline data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reused across multiple test methods; reduces redundancy |
| Test data factory classes created for complex data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reusable test data builders |

### Test Method Naming

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Naming: `test[Method][Scenario][Expected]` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `testGetAccounts_FilterByIndustry_ReturnsMatching` |
| Each test method tests ONE feature | ☐ Pass ☐ Fail | 🟡 MEDIUM | Easier to debug when one assertion fails |
| Test names describe scenario and expectation | ☐ Pass ☐ Fail | 🟡 MEDIUM | Name should explain what's being tested and result |
| `@isTest` methods are private or public test methods | ☐ Pass ☐ Fail | ⚪ LOW | Standard convention for test methods |

---

## 3. Test Cases & Scenarios

### Positive Test Cases (Happy Path)

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Normal/valid input tested | ☐ Pass ☐ Fail | 🟠 HIGH | Verify code works with expected data |
| Success path fully exercised | ☐ Pass ☐ Fail | 🟠 HIGH | All branches of success logic tested |
| Side effects verified (DML, callouts, logging) | ☐ Pass ☐ Fail | 🟠 HIGH | When account created, verify email sent |
| Return values validated | ☐ Pass ☐ Fail | 🟠 HIGH | `Assert.areEqual(expected, actual)` |

### Negative Test Cases (Error Conditions)

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Invalid input rejected | ☐ Pass ☐ Fail | 🟠 HIGH | Null, empty, out-of-range values handled |
| Exception thrown with correct message | ☐ Pass ☐ Fail | 🟠 HIGH | `try { method(); Assert.fail(); } catch (Exception e) { Assert.isTrue(e.getMessage().contains(...)) }` |
| Error handling verified | ☐ Pass ☐ Fail | 🟠 HIGH | When query fails, does code log error gracefully? |
| Permission errors tested | ☐ Pass ☐ Fail | 🟠 HIGH | User without access = error message, not exception |

### Edge Cases & Boundary Conditions

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Empty lists tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | `getAccounts([])` returns empty result, not error |
| Null values handled | ☐ Pass ☐ Fail | 🟡 MEDIUM | Null account name, null opportunity amount |
| Maximum/minimum values tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Large numbers, long strings, many records |
| Duplicate records handled | ☐ Pass ☐ Fail | 🟡 MEDIUM | Inserting same account twice = error or merge? |
| Zero/single/bulk record counts tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Test with 0, 1, 100, 200 records |

---

## 4. Bulk Operation Testing

### Trigger Bulk Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Bulk insert tested (200 records minimum) | ☐ Pass ☐ Fail | 🟠 HIGH | Triggers must handle full batch size |
| Bulk update tested (200 records minimum) | ☐ Pass ☐ Fail | 🟠 HIGH | Verify governor limits not exceeded |
| Bulk delete tested (200 records minimum) | ☐ Pass ☐ Fail | 🟠 HIGH | Cleanup logic exercised with full batch |
| Recursion prevention tested with bulk | ☐ Pass ☐ Fail | 🟠 HIGH | Recursion flags must allow 200-record batch |
| Governor limit consumption measured | ☐ Pass ☐ Fail | 🟡 MEDIUM | Assert: `Limits.getQueries() < 100` |

### Batch Apex Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Batch with max scope size tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Scope 1-2000; test with realistic chunk |
| Batch error handling for partial failure | ☐ Pass ☐ Fail | 🟡 MEDIUM | One failed record doesn't stop batch |
| Batch finish() method with aggregate results | ☐ Pass ☐ Fail | 🟡 MEDIUM | Verify final cleanup and notifications |
| Multiple batch job chaining tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | If batch chains to next job, verify flow |

---

## 5. Async Apex Testing

### Queueable Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `Test.startTest()` / `Test.stopTest()` used | ☐ Pass ☐ Fail | 🟠 HIGH | Executes async jobs synchronously in test |
| Assertions AFTER `Test.stopTest()` | ☐ Pass ☐ Fail | 🟠 HIGH | Before stopTest = job hasn't executed yet |
| Queueable error handling tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Mock callout timeout; verify exception handling |
| Queueable chaining tested (if applicable) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Verify next job enqueued correctly |

### Scheduled Apex Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Scheduled job execution tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | `System.schedule()` and verify job runs |
| Schedule timing verified | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cron expression creates job at expected time |
| Job completion and results verified | ☐ Pass ☐ Fail | 🟡 MEDIUM | After execution, assert expected data changes |

### Future Method Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| @future method outcome verified | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use `Test.startTest()` / `Test.stopTest()` |
| Future method errors caught | ☐ Pass ☐ Fail | 🟡 MEDIUM | No exception propagation; must log errors |

---

## 6. Mock & Stub Testing

### HTTP Callout Mocking

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| HttpCalloutMock implemented for external calls | ☐ Pass ☐ Fail | 🟠 HIGH | Never call real external services in tests |
| Success response mocked | ☐ Pass ☐ Fail | 🟠 HIGH | Test happy path with 200 status, valid JSON |
| Error responses mocked (4xx, 5xx) | ☐ Pass ☐ Fail | 🟠 HIGH | Test error handling with error status codes |
| Timeout responses mocked | ☐ Pass ☐ Fail | 🟡 MEDIUM | Throw CalloutException to test timeout retry |
| Response payload variations tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Partial data, malformed JSON, unexpected fields |

### Data Mocking

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Test data fixtures created (not querying production data) | ☐ Pass ☐ Fail | 🟠 HIGH | Use `@testSetup` or testdata factories |
| Custom field values set appropriately | ☐ Pass ☐ Fail | 🟡 MEDIUM | Test with realistic values, not placeholders |
| Record Type assignments in test data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use `Schema.SObjectType.Account.getRecordTypeInfosByName()` |
| Field history/audit not relied upon in tests | ☐ Pass ☐ Fail | 🟡 MEDIUM | Field history not populated until after insert |

---

## 7. Test Quality & Assertions

### Assertion Best Practices

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Every test has assertions | ☐ Pass ☐ Fail | 🟠 HIGH | No test should pass without verifying outcome |
| Assertions include descriptive messages | ☐ Pass ☐ Fail | 🟡 MEDIUM | `Assert.areEqual(expected, actual, 'Account name should match')` |
| `Assert` class used (not `System.assertEquals`) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Assert class is modern Apex standard |
| Meaningful assertions (not just `Assert.isTrue(true)`) | ☐ Pass ☐ Fail | 🟠 HIGH | Test should fail if logic is removed |
| Multiple assertions per test (related to same feature) | ☐ Pass ☐ Fail | 🟡 MEDIUM | One concept, multiple validation points |

### Test Efficiency

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@TestSetup` data reused across methods | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reduces test execution time |
| No unnecessary queries in test data setup | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use direct inserts, not queries |
| Test isolation (one test doesn't affect another) | ☐ Pass ☐ Fail | 🟠 HIGH | Tests should run in any order, independently |
| Mock data cleanup not required (@testSetup handles it) | ☐ Pass ☐ Fail | ⚪ LOW | Test data auto-rolled back after test |

---

## 8. Code Quality Metrics

### Code Complexity

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Cyclomatic complexity <10 per method | ☐ Pass ☐ Fail | 🟡 MEDIUM | Too many if/switch = hard to test |
| No duplicate code (DRY principle) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract common patterns to reduce duplication |
| Methods <50 lines | ☐ Pass ☐ Fail | 🟡 MEDIUM | Long methods = complex logic = hard to test |
| Classes <1000 lines | ☐ Pass ☐ Fail | 🟡 MEDIUM | Large classes = multiple responsibilities |

### Code Maintainability

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Clear variable/method names | ☐ Pass ☐ Fail | 🟡 MEDIUM | `getUnpaidInvoices()` better than `getInv()` |
| Comments for complex logic | ☐ Pass ☐ Fail | 🟡 MEDIUM | Comment WHY, not WHAT |
| Dead code removed | ☐ Pass ☐ Fail | ⚪ LOW | Remove commented-out code |
| Magic numbers extracted to constants | ☐ Pass ☐ Fail | 🟡 MEDIUM | `MAX_BATCH_SIZE = 200` instead of bare `200` |

---

## 9. LWC Jest Testing

### Jest Test Coverage

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Jest tests present for all LWC components | ☐ Pass ☐ Fail | 🟡 MEDIUM | `__tests__/[componentName].test.js` |
| Jest coverage ≥80% for LWC | ☐ Pass ☐ Fail | 🟡 MEDIUM | Run `npm test -- --coverage` |
| Component lifecycle tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | connectedCallback, disconnectedCallback, renderedCallback |
| Wire decorators mocked | ☐ Pass ☐ Fail | 🟠 HIGH | Mock Apex methods called via @wire |
| User interactions tested (clicks, input events) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Simulate user actions; verify results |

### Jest Best Practices

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| DOM cleanup in afterEach() | ☐ Pass ☐ Fail | 🟡 MEDIUM | `while (document.body.firstChild) document.body.removeChild(...)` |
| Test names descriptive | ☐ Pass ☐ Fail | 🟡 MEDIUM | `it('should display error message on validation failure')` |
| Async tests use done() or async/await | ☐ Pass ☐ Fail | 🟡 MEDIUM | Mock promises properly |

---

## Review Output Template

### Test Quality Assessment
- **Overall Coverage**: [Percentage]
- **Coverage By Category**: Apex [%] | LWC [%] | Batch [%]
- **Test Quality**: Excellent / Good / Adequate / Insufficient
- **Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Improvement

### Findings Table

| # | Category | Severity | Issue | Coverage Gap | Remediation |
|---|----------|----------|-------|--------------|------------|
| 1 | Coverage | 🟠 HIGH | 68% overall (below 75% minimum) | Missing 7% | Add negative test cases, edge cases |
| 2 | Bulk Test | 🟠 HIGH | No 200-record bulk insert test | Trigger not validated | Add bulk insert test with 200 records |
| 3 | Error Path | 🟡 MEDIUM | No exception path tests | Error handling untested | Add try/catch tests; verify error messages |
| 4 | Mock Data | 🟡 MEDIUM | Test data queried from org | Fragile tests | Use @testSetup or testdata factory |

### Coverage Analysis
- **Well-Tested Areas**: Security logic (100%), Core business rules (95%)
- **Coverage Gaps**: Error handling (40%), Edge cases (50%)
- **Recommendation**: Add error path and edge case tests to reach 80%+ coverage

### Overall Assessment
[Pass/Fail with recommendations for test improvements]
