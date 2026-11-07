# Apex Code Review Checklist

> **Review Category**: Apex Classes, Apex Triggers, Test Classes  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Trigger Design & Architecture

### Single Responsibility & Layer Separation

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| One trigger per object | ☐ Pass ☐ Fail | 🟠 HIGH | Multiple triggers on same object cause race conditions and unpredictable execution order |
| Trigger contains no business logic | ☐ Pass ☐ Fail | 🔴 CRITICAL | All logic must be in Handler/Service classes; triggers are thin delegation |
| Handler class extends framework (KC_TriggerHandler or similar) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Consistent patterns improve maintainability and testability |
| Service classes contain business logic | ☐ Pass ☐ Fail | 🟠 HIGH | Logic in Service layer enables reuse and testability |
| Selector classes contain all SOQL | ☐ Pass ☐ Fail | 🟡 MEDIUM | Centralized query management simplifies optimization and sharing |

### Recursion Prevention

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `static Set<Id>` for recursion tracking (NOT `static Boolean`) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Boolean flags block all records after first batch; Set allows bulk processing |
| Tracks processed records across trigger execution | ☐ Pass ☐ Fail | 🟠 HIGH | Prevents infinite loops when trigger updates same object |
| Clears recursion state appropriately | ☐ Pass ☐ Fail | 🟡 MEDIUM | State should survive batch but be manageable in test context |
| Test validates recursion prevention | ☐ Pass ☐ Fail | 🟡 MEDIUM | Ensure protection works without breaking bulk operations |

### Event Handlers

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `switch on Trigger.operationType` for all event types | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cleaner than if-else chains; handles all 7 trigger events |
| Handles BEFORE_INSERT, BEFORE_UPDATE, AFTER_INSERT, AFTER_UPDATE, BEFORE_DELETE, AFTER_DELETE, AFTER_UNDELETE | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't leave handlers empty — comment if intentional |
| `oldMap` used in before/after update handlers | ☐ Pass ☐ Fail | 🟡 MEDIUM | Essential for detecting field changes |
| `Trigger.new` / `Trigger.newMap` available in all after event handlers | ☐ Pass ☐ Fail | ⚪ LOW | Verify expected variables are accessible for each event |

---

## 2. Bulkification & Governor Limits

### Query Optimization

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No SOQL queries inside loops | ☐ Pass ☐ Fail | 🔴 CRITICAL | Single loop with 200 records = up to 200 queries = limit exceeded |
| No DML statements inside loops | ☐ Pass ☐ Fail | 🔴 CRITICAL | Batching all DML before single operation saves limit (150 DML limit) |
| No nested loops on collections >100 items | ☐ Pass ☐ Fail | 🔴 CRITICAL | O(n²) complexity with 200 records = 40k operations on CPU |
| Queries are selective (WHERE clause with indexed fields) | ☐ Pass ☐ Fail | 🟠 HIGH | Full table scans consume query resources; use indexed fields (Id, Name, standard lookup fields) |
| Aggregate SOQL used when only count/sum needed | ☐ Pass ☐ Fail | 🟡 MEDIUM | COUNT(), SUM(), MIN(), MAX() on database is faster than client aggregation |
| Queries use minimal field selection | ☐ Pass ☐ Fail | 🟡 MEDIUM | Only SELECT needed fields; improves query performance and API bandwidth |
| LIMIT clauses prevent row limit violations | ☐ Pass ☐ Fail | 🟠 HIGH | 50k row limit across all SOQL in transaction; use pagination or LIMIT |

### Bulk Operations

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| DML operations batched (insert/update/delete all records once) | ☐ Pass ☐ Fail | 🟠 HIGH | Reduces DML governor limit pressure |
| Uses `Database.insert/update/delete(records, false)` for partial success | ☐ Pass ☐ Fail | 🟠 HIGH | Continues on error; always check SaveResult for success/failure |
| Handles governor limits near trigger context (before transaction ends) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Trigger context has baseline limits; monitor heap, CPU, DML |
| Async operations (Queueable, scheduled job) used for large batch processing | ☐ Pass ☐ Fail | 🟡 MEDIUM | Defers heavy processing outside trigger context |

### Heap & CPU Time

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No large string concatenations in loop | ☐ Pass ☐ Fail | 🟠 HIGH | String += in loop causes exponential heap growth; use List<String> + join() |
| No excessive collection cloning | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cloning 200-record list multiple times wastes heap |
| Processing logic is O(n) not O(n²) or worse | ☐ Pass ☐ Fail | 🟠 HIGH | Nested loops on 200-record trigger batches can exceed 10s CPU limit |
| Maps used for O(1) lookups instead of List.contains() | ☐ Pass ☐ Fail | 🟡 MEDIUM | List.contains() is O(n) for each call; Map is O(1) |

---

## 3. Security & Access Control

### Sharing Enforcement

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Class declares `with sharing`, `without sharing`, or `inherited sharing` | ☐ Pass ☐ Fail | 🔴 CRITICAL | Explicit sharing keyword prevents unintended access escalation |
| `with sharing` used on all user-facing code (controllers, services) | ☐ Pass ☐ Fail | 🟠 HIGH | Respects user's sharing rules and record access |
| `without sharing` justified and documented | ☐ Pass ☐ Fail | 🟠 HIGH | Include comment explaining why system context is needed |
| Trigger handlers appropriately scoped | ☐ Pass ☐ Fail | 🟡 MEDIUM | Triggers need access to all records in batch; use `without sharing` or case-by-case logic |
| Sharing recalc considered for Parent record changes | ☐ Pass ☐ Fail | 🟡 MEDIUM | Changing Account ownership/sharing requires manual recalc or platform event handling |

### CRUD & FLS

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SOQL uses `WITH SECURITY_ENFORCED` or WITH USER_MODE | ☐ Pass ☐ Fail | 🔴 CRITICAL | Fails query if user lacks FLS read access; prevents data leakage |
| DML uses `Security.stripInaccessible(AccessType.CREATABLE/UPDATABLE, records)` | ☐ Pass ☐ Fail | 🔴 CRITICAL | Removes inaccessible fields before insert/update; prevents CRUD bypass |
| Custom permissions checked before sensitive operations | ☐ Pass ☐ Fail | 🟠 HIGH | Use Salesforce's permission model instead of custom logic |
| `Database.AllowsCallouts` checked before HTTP callouts | ☐ Pass ☐ Fail | 🟠 HIGH | Callouts not allowed in before triggers, batch jobs, or some async contexts |

### Data Integrity

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SOQL injection prevention (no dynamic SOQL with concatenation) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Use bind variables `:variable` for all user input |
| No exposure of sensitive fields (SSN, credit card, API keys) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Never log, return in API, or persist unencrypted sensitive data |
| PII fields accessed only with business need | ☐ Pass ☐ Fail | 🟠 HIGH | Minimize exposure of Personally Identifiable Information |
| Encryption at rest considered for sensitive custom fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | Shield Platform Encryption available; use for high-sensitivity data |
| No storing of credentials in code/custom settings | ☐ Pass ☐ Fail | 🔴 CRITICAL | Use Named Credentials, Custom Labels, or Key Management Service |

---

## 4. Error Handling & Logging

### Exception Handling

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No empty catch blocks | ☐ Pass ☐ Fail | 🔴 CRITICAL | Catch blocks must handle, log, or rethrow — silent failures hide bugs |
| Custom exceptions thrown with meaningful messages | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `throw new AccountException('Account credit limit exceeded: ' + limit);` |
| Try-catch used only for recoverable errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use try-catch when you can handle the error; otherwise let it propagate |
| Finally blocks used to reset state (e.g., async flags) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Ensures cleanup runs even if exception occurs |
| Trigger exceptions use `addError()` instead of throw | ☐ Pass ☐ Fail | 🟠 HIGH | addError() rolls back transaction; throw propagates to outer handler |

### Logging

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| System.debug() statements removed or gated with LoggingLevel | ☐ Pass ☐ Fail | 🟡 MEDIUM | Remove before deploy; if keeping, use `System.debug(LoggingLevel.ERROR, msg)` |
| Custom error logs created for integration failures | ☐ Pass ☐ Fail | 🟡 MEDIUM | Integration errors should persist in Salesforce (custom object or external system) |
| Error context includes relevant record IDs and field values | ☐ Pass ☐ Fail | 🟡 MEDIUM | Help support troubleshoot: "Update failed for Account: 001xx | Credit Limit: 10000" |
| Error severity levels appropriate (ERROR, WARN, INFO) | ☐ Pass ☐ Fail | ⚪ LOW | Different log levels enable filtering during troubleshooting |

### Recovery Mechanisms

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Partial success handled (Database.SaveResult checked) | ☐ Pass ☐ Fail | 🟠 HIGH | Use `Database.insert(records, false)`; check SaveResult.isSuccess() and getErrors() |
| Retry logic implemented for transient failures | ☐ Pass ☐ Fail | 🟡 MEDIUM | Callouts may fail temporarily; consider retry with exponential backoff |
| Circuit breaker pattern used for external service calls | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Stop calling failed service; resume after time interval |

---

## 5. Code Quality & Maintainability

### Naming Conventions

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Classes use PascalCase: `AccountService`, `ContactTriggerHandler` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Consistent naming improves readability and searchability |
| Methods use camelCase: `getAccounts()`, `updateRating()` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Must be lowercase letter; Apex is case-insensitive but convention matters |
| Constants use UPPER_SNAKE_CASE: `MAX_BATCH_SIZE` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Distinguish constants from variables at a glance |
| Boolean variables/methods prefixed with `is`, `has`, `can`, `should` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `isActive`, `hasEmail`, `canDelete` |
| Map names use pattern: `[value]By[Key]` | ☐ Pass ☐ Fail | ⚪ LOW | Example: `accountsByIds`, `contactsByEmail` |
| Trigger names follow `[Object]Trigger` pattern | ☐ Pass ☐ Fail | ⚪ LOW | Example: `AccountTrigger`, `OpportunityTrigger` |
| Handler classes follow `[Object]TriggerHandler` pattern | ☐ Pass ☐ Fail | ⚪ LOW | Example: `AccountTriggerHandler` |

### Code Size & Complexity

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Class size <1000 lines | ☐ Pass ☐ Fail | 🟡 MEDIUM | Split large classes into focused, single-responsibility classes |
| Method size <50 lines | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract complex logic into helper methods |
| Cyclomatic complexity <10 per method | ☐ Pass ☐ Fail | 🟡 MEDIUM | Too many if/switch branches = hard to test and maintain |
| No significant code duplication | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract common patterns into utility methods (DRY principle) |
| Dead code removed | ☐ Pass ☐ Fail | ⚪ LOW | Remove commented-out or unreachable code |

### Documentation & Comments

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Class has JSDoc comment (purpose, usage, dependencies) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `// Handles account record triggers. Prevent recursion via processedIds Set.` |
| Public methods have JSDoc comments | ☐ Pass ☐ Fail | 🟡 MEDIUM | Parameter types, return value, exceptions thrown |
| Complex logic commented (WHY not WHAT) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Code explains WHAT; comments explain WHY (e.g., business rule, workaround) |
| No over-commenting obvious code | ☐ Pass ☐ Fail | ⚪ LOW | `List<Account> = new List<Account>();  // Create list` is noise |
| README or wiki updated with API changes | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Document breaking changes, new dependencies |

### Hardcoded Values & Magic Numbers

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No hardcoded Ids (org-specific Ids vary across sandboxes/prod) | ☐ Pass ☐ Fail | 🟠 HIGH | Use query by name, API name, or dynamically fetched Ids |
| No hardcoded Record Type Ids | ☐ Pass ☐ Fail | 🟠 HIGH | Query from RecordType object using SObjectType and Name |
| No hardcoded URLs or endpoints | ☐ Pass ☐ Fail | 🟠 HIGH | Use Custom Metadata Type (Integration config) or Named Credentials |
| Configuration values in Custom Metadata, Custom Settings, or Labels | ☐ Pass ☐ Fail | 🟡 MEDIUM | Enable org admin to change values without code redeploy |
| Magic numbers explained or extracted to constants | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `final Integer BATCH_SIZE = 200;` instead of bare `200` |

---

## 6. Modern Apex Patterns

### Safe Navigation & Null Checks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses safe navigation operator `?.` to prevent NPE | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `account?.Name` returns null safely instead of error |
| Null checks guard DML operations | ☐ Pass ☐ Fail | 🟡 MEDIUM | Check `!recordList.isEmpty()` before insert/update/delete |
| NOT using `?.` in boolean conditions | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use `records != null && records.isEmpty()` instead of `records?.isEmpty()` |

### Collections & Built-In Methods

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `String.isBlank()` for user input validation | ☐ Pass ☐ Fail | 🟡 MEDIUM | Handles null, empty, and whitespace-only strings |
| Uses enhanced for loops (no index-based loops when unnecessary) | ☐ Pass ☐ Fail | ⚪ LOW | `for (Account acc : accounts)` cleaner than `for (int i = 0; ...)` |
| Collections initialized with capacity where known | ☐ Pass ☐ Fail | ⚪ LOW | Example: `new List<Account>(200)` if expecting 200 items |
| Uses `Collections.sort()` or native sort for lists | ☐ Pass ☐ Fail | 🟡 MEDIUM | Prefer database-level sorting via SOQL ORDER BY |
| Map operations use `.containsKey()` before `.get()` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Prevents NPE and makes intent clear |

### Async Apex

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Queueable used instead of `@future` for new async code | ☐ Pass ☐ Fail | 🟡 MEDIUM | Queueable supports chaining, callouts, better error handling |
| Scheduled Apex properly implemented (implements Schedulable) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use for recurring jobs; Queueable for one-time deferred processing |
| Batch Apex used for 1000+ record processing | ☐ Pass ☐ Fail | 🟡 MEDIUM | Batch handles large datasets with scope chunking; not for small batches |
| Governor limits considered for async context | ☐ Pass ☐ Fail | 🟡 MEDIUM | Async has higher limits (200 SOQL, 200 DML) but still bounded |
| `@future(callout=true)` used only if callouts required | ☐ Pass ☐ Fail | 🟡 MEDIUM | Callout=true limits to 100 max callout methods; use sparingly |

### Type Safety & Interfaces

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses typed exceptions instead of generic `Exception` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `throw new AccountException('message')` enables specific catch |
| Implements appropriate interfaces (Comparable, Iterator, etc.) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Interface-based design improves testability and flexibility |
| Generics used for type-safe collections | ☐ Pass ☐ Fail | 🟡 MEDIUM | `List<Account>` safer than untyped `List` |

### Enhanced Switch & Null Coalescing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `switch on` instead of long if-else chains | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cleaner for multiple conditions; adds type safety with enums |
| Uses null coalescing operator (`??`) where appropriate | ☐ Pass ☐ Fail | ⚪ LOW | `value ?? defaultValue` replaces verbose ternary |

---

## 7. Testing & Coverage

### Test Structure

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Test class matches source class naming: `[ClassName]Test` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `AccountServiceTest` for `AccountService` |
| `@TestSetup` method creates baseline test data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reused across multiple test methods; reduces redundancy |
| Test methods follow naming convention: `test[Method][Scenario][Expected]` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: `testGetAccounts_EmptyList_ReturnsEmpty` |
| Arrange-Act-Assert pattern used in all tests | ☐ Pass ☐ Fail | 🟡 MEDIUM | Setup data, execute logic, verify results |
| Each test method tests ONE thing | ☐ Pass ☐ Fail | 🟡 MEDIUM | Easier to debug when one assertion fails |

### Coverage & Test Cases

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Overall code coverage ≥75% (deploy minimum; 90%+ goal for critical code) | ☐ Pass ☐ Fail | 🟠 HIGH | Critical paths: security, integrations, financial logic should be 95%+ |
| Positive test cases present (happy path) | ☐ Pass ☐ Fail | 🟠 HIGH | Verify code works correctly with valid input |
| Negative test cases present (error conditions) | ☐ Pass ☐ Fail | 🟠 HIGH | Verify error handling, exceptions thrown, graceful degradation |
| Edge case tests present (boundary conditions) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Empty lists, null values, max batch size, field limits |
| Bulk operation tests (200+ records) present | ☐ Pass ☐ Fail | 🟠 HIGH | Triggers must handle full batch size without governor violations |

### Async Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `Test.startTest()` / `Test.stopTest()` used for Queueable/Scheduled Apex | ☐ Pass ☐ Fail | 🟠 HIGH | Executes async jobs synchronously in test context |
| Async tests verify results AFTER `Test.stopTest()` | ☐ Pass ☐ Fail | 🟠 HIGH | Assertions before stopTest() execute before async job completes |
| `Test.isRunningTest()` used sparingly (only for critical workarounds) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Avoid test-specific code paths if possible |
| Mock/stub frameworks used for external dependencies (HTTP, APIs) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't call real external services in tests; use HttpCalloutMock |

### Negative Test Coverage

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Tests verify exception messages are meaningful | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: assert `e.getMessage().contains('Credit limit')`  |
| Tests trigger all exception paths | ☐ Pass ☐ Fail | 🟡 MEDIUM | Force errors: invalid IDs, permission violations, DML failures |
| Tests verify database rollback on errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | When transaction fails, no partial data persists |

---

## 8. Performance Considerations

### Query Performance

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SELECT clause includes only required fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reduces payload, improves parsing efficiency |
| WHERE clause uses indexed fields (Id, Name, custom index) | ☐ Pass ☐ Fail | 🟠 HIGH | Unindexed field searches full table |
| LIMIT clause prevents query timeout | ☐ Pass ☐ Fail | 🟡 MEDIUM | Set reasonable limit for human interaction; offset for pagination |
| ORDER BY used in query (not in code) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Database sorting is more efficient than client-side |
| Subqueries optimized (not nested subqueries >1 level) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Deeply nested subqueries are slow; consider separate queries |

### Memory Efficiency

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Large collections filtered before manipulation | ☐ Pass ☐ Fail | 🟡 MEDIUM | Filter in SOQL WHERE clause, not in Apex |
| Pagination implemented for large result sets | ☐ Pass ☐ Fail | 🟡 MEDIUM | Process 200 records at a time, not 50,000 |
| Temporary data cleared after use | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't hold large lists/maps longer than needed |
| No memory leaks from static collections | ☐ Pass ☐ Fail | 🟡 MEDIUM | Static data persists across transaction; can grow unbounded |

---

## Review Output Template

### Summary
- **Class Name**: [Name]
- **Risk Level**: Critical / High / Medium / Low
- **Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Rework

### Findings Table

| # | Section | Severity | Item | Finding | Recommendation |
|---|---|---|---|---------|-----------------|
| 1 | Security | 🔴 CRITICAL | Sharing Enforcement | Missing `with sharing` keyword | Add: `public with sharing class AccountService` |
| 2 | Bulkification | 🔴 CRITICAL | Query Optimization | SOQL in loop (line 42) | Move query outside loop; use bulkified collection logic |
| 3 | Error Handling | 🟠 HIGH | Exception Handling | Empty catch block (line 58) | Add logging: `System.debug(LoggingLevel.ERROR, e.getMessage());` |

### Positive Findings
- ✅ Excellent recursion prevention with Set<Id>
- ✅ Comprehensive test coverage (94%)
- ✅ Good separation of concerns (Handler/Service pattern)

### Overall Assessment
[Pass/Fail with summary recommendation]