# Salesforce Apex Coding Rules — Vibe Coding Ruleset

**A comprehensive, tool-agnostic Apex coding ruleset for AI-assisted development tools (GitHub Copilot, Cursor, Claude Code, Windsurf, etc.)**

---
document_id: "RULESET_APEX_CODING_STANDARDS"
status: "Published"
classification: "Public"
last_updated: "2026-02-24"
audience: [Developers, AI_Assistants, Vibe_Coders]
usage: "Drop into .github/copilot-instructions.md, .cursor/rules/, .cursorrules, AGENTS.md, or any AI coding tool's instruction layer"
---

## How to Use This Document

This is a **copy-paste-ready** ruleset. Depending on your tool:

| Tool | Where to Place These Rules |
|------|---------------------------|
| **GitHub Copilot (VS Code)** | `.github/copilot-instructions.md` or `.instructions.md` in target folders |
| **Cursor** | `.cursor/rules/apex.md` (with frontmatter: `globs: "**/*.cls, **/*.trigger"`) |
| **Claude Code** | `CLAUDE.md` in project root |
| **Windsurf** | `.windsurfrules` in project root |
| **Cline / Roo Code** | `.clinerules` or `.roo/rules/` |
| **Universal** | `AGENTS.md` in project root |

---

## Table of Contents

1. [General Apex Standards](#1-general-apex-standards)
2. [Naming Conventions](#2-naming-conventions)
3. [Modern Apex Features](#3-modern-apex-features)
4. [Bulkification Rules](#4-bulkification-rules)
5. [SOQL & SOSL Rules](#5-soql--sosl-rules)
6. [DML Rules](#6-dml-rules)
7. [Trigger Rules](#7-trigger-rules)
8. [Class Design & Architecture](#8-class-design--architecture)
9. [Error Handling & Logging](#9-error-handling--logging)
10. [Security Rules](#10-security-rules)
11. [Governor Limits Awareness](#11-governor-limits-awareness)
12. [Test Class Rules](#12-test-class-rules)
13. [Asynchronous Apex Rules](#13-asynchronous-apex-rules)
14. [Agentforce / Invocable Rules](#14-agentforce--invocable-rules)
15. [Metadata & Deployment Rules](#15-metadata--deployment-rules)
16. [Code Documentation Rules](#16-code-documentation-rules)
17. [Performance Rules](#17-performance-rules)
18. [Approval & Sharing Rules in Code](#18-approval--sharing-rules-in-code)
19. [Platform Events & Change Data Capture](#19-platform-events--change-data-capture)
20. [Integration Rules](#20-integration-rules)
21. [PMD Static Analysis Rules](#21-pmd-static-analysis-rules)
22. [Anti-Patterns to Avoid](#22-anti-patterns-to-avoid)
23. [Common Runtime Errors & Prevention](#23-common-runtime-errors--prevention-stackexchange-top-issues)

---

## 1. General Apex Standards

```
RULES:
- Use API version 66.0 (Spring '26) or later for all new components. Keep all components on the same API version.
- Never hardcode IDs. Use Custom Metadata Types, Custom Labels, Custom Settings, or SOQL queries to resolve IDs dynamically.
- Never hardcode org-specific URLs, endpoints, or credentials. Use Named Credentials, Custom Metadata, or Remote Site Settings.
- Always use `with sharing` by default on all classes. Only use `without sharing` when explicitly required and documented with a reason.
- Use `inherited sharing` for utility/library classes that are called from varying sharing contexts.
- Explicitly declare sharing on every class — never leave it undeclared (PMD: ApexSharingViolations).
- Avoid the `global` access modifier unless building a managed package or exposing a REST/SOAP endpoint. Use `public` instead.
- Every Apex class must have a corresponding `-meta.xml` file.
- Lines should not exceed 120 characters where possible for readability.
- Use 4-space indentation (no tabs).
- One variable declaration per line — never declare multiple variables on the same line (PMD: OneDeclarationPerLine).
- Field/property declarations should appear before method declarations in a class (PMD: FieldDeclarationsShouldBeAtStart).
- Always use braces {} for if, else, for, while, and do-while blocks — even single-line bodies (PMD: IfStmtsMustUseBraces, ForLoopsMustUseBraces).
- Always include meaningful comments for complex logic.
- Remove all System.debug statements before deploying to production (or gate them behind a logging utility). Debug statements consume CPU time even when debug logs are off (PMD: AvoidDebugStatements).
- When using System.debug, always include a LoggingLevel as the first parameter: System.debug(LoggingLevel.ERROR, 'message') (PMD: DebugsShouldUseLoggingLevel).
- Never use `@SuppressWarnings` to hide legitimate issues.
- Never perform DML operations in class constructors or initializers — DML in constructors executes before CSRF token validation, and more commonly causes application errors on page load. PMD classifies this as Error Prone, not a security vulnerability (PMD: ApexCSRF).
- Remove unused local variables — they add noise and confuse maintainers (PMD: UnusedLocalVariable).
- Remove or refactor unused private methods — dead code increases maintenance cost (PMD: UnusedMethod).
- Never use annotations that don't exist on the platform — they are silently ignored today but may break in future releases (PMD: AvoidNonExistentAnnotations).
- Avoid empty if, while, try, finally, and generic statement blocks — they serve no purpose and indicate incomplete logic (PMD: EmptyIfStmt, EmptyWhileStmt, EmptyTryOrFinallyBlock, EmptyStatementBlock).
```

---

## 2. Naming Conventions

```
RULES:
- Classes: PascalCase → CaseRoutingHandler, AccountService, LeadQualificationAgent
- Methods: camelCase → routeCase(), calculateScore(), getAccountsByRegion()
- Variables: camelCase → accountList, caseCount, isProcessed
- Constants: UPPER_SNAKE_CASE → MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE, API_VERSION
- Test Classes: [ClassName]Test → CaseRoutingHandlerTest, AccountServiceTest
- Triggers: [ObjectName]Trigger → CaseTrigger, LeadTrigger, AccountTrigger
- Trigger Handlers: [ObjectName]TriggerHandler → CaseTriggerHandler, LeadTriggerHandler
- Batch Classes: [Purpose]Batch → AccountCleanupBatch, LeadScoringBatch
- Schedulable Classes: [Purpose]Scheduler or [Purpose]Schedule → DailyLeadScoringScheduler
- Queueable Classes: [Purpose]Queueable → CaseEscalationQueueable
- Custom Exceptions: [Domain]Exception → CaseRoutingException, IntegrationException
- Interfaces: I[Name] or [Name]able → ICaseRouter, Scoreable, Routable
- Wrapper/DTO Classes: [Purpose]Wrapper or [Purpose]DTO → CaseResponseWrapper, LeadScoreDTO
- Service Classes: [Object/Domain]Service → AccountService, EmailService
- Selector Classes: [Object]Selector → AccountSelector, CaseSelector
- Domain Classes: [ObjectPlural] → Accounts, Cases, Leads (if using fflib/domain layer)
- Boolean variables: prefix with is, has, should, can → isActive, hasEmail, shouldProcess
- Collections: use plural nouns → accounts, caseList, leadMap, contactsByAccountId
- Map variables: [value]By[Key] → contactsByAccountId, ownerNameByUserId
- Methods: never name a method the same as the enclosing class (reserved for constructors) (PMD: MethodWithSameNameAsEnclosingClass)
- Type names: avoid shadowing built-in Salesforce namespaces (System, Database, Schema, etc.) (PMD: TypeShadowsBuiltInNamespace)
- PMD enforces configurable naming conventions — align with your team's standards:
    - Classes: PascalCase (PMD: ClassNamingConventions)
    - Methods: camelCase (PMD: MethodNamingConventions)
    - Fields/Properties: camelCase (PMD: FieldNamingConventions, PropertyNamingConventions)
    - Local Variables: camelCase (PMD: LocalVariableNamingConventions)
    - Formal Parameters: camelCase (PMD: FormalParameterNamingConventions)
    - Annotations: PascalCase (PMD: AnnotationsNamingConventions)
```

---

## 3. Modern Apex Features

```
RULES:
- Use the Safe Navigation Operator (?.) to prevent NullPointerExceptions:
    // BAD:
    String name = account.Name.toUpperCase(); // NPE if account or Name is null
    // GOOD:
    String name = account?.Name?.toUpperCase(); // returns null safely

- Use `switch on` statements instead of long if-else chains:
    // BAD:
    if (priority == 'High') { ... }
    else if (priority == 'Medium') { ... }
    else if (priority == 'Low') { ... }
    // GOOD:
    switch on priority {
        when 'High' { /* handle high */ }
        when 'Medium' { /* handle medium */ }
        when 'Low' { /* handle low */ }
        when else { /* default */ }
    }
    - switch on also works with SObject types, enums, and Integer/Long values.

- Use the Assert class (e.g., Assert.areEqual(), Assert.isTrue()) instead of the legacy System.assert() methods.
- Use User Mode for DML and SOQL (API 60.0+):
    - Database.insert(records, AccessLevel.USER_MODE);
    - [SELECT Id FROM Account WITH USER_MODE]
    - This is the modern replacement for manual CRUD/FLS checks.
- Use null-safe comparison patterns:
    String.isBlank(value) instead of value == null || value == ''
    String.isNotBlank(value) instead of value != null && value != ''
- Avoid using the Safe Navigation Operator (?.) in boolean conditions (e.g., `if (accounts?.isEmpty())`) because it evaluates to `null` when the object is null, which throws a `NullPointerException` in Apex. Use `accounts?.isEmpty() == true` or `accounts != null && accounts.isEmpty()` instead.
- Override both equals() AND hashCode() if you override either (PMD: OverrideBothEqualsAndHashcode).
- Limit method parameters — if a method needs more than 5 parameters, refactor to use a wrapper/DTO class (PMD: ExcessiveParameterList).
- Avoid Boolean method parameters where possible — use enums or separate methods for clarity (PMD: AvoidBooleanMethodParameters).
- Use @testMethod annotation is legacy — always use @isTest annotation instead (PMD: ApexUnitTestMethodShouldHaveIsTestAnnotation).
- Prefer Queueable over @future for all new async code — @future is a legacy pattern with limited capabilities (no chaining, no complex params, no job monitoring) (PMD: AvoidFutureAnnotation).
- Attach a Finalizer to Queueable jobs via System.attachFinalizer() for error recovery when the job fails. This is a recommended practice, though PMD rates QueueableWithoutFinalizer as priority 5 (Low) (PMD: QueueableWithoutFinalizer).
```

---

## 4. Bulkification Rules

```
RULES:
- NEVER place SOQL queries inside a loop (for, while, do-while). Collect IDs/criteria first, query once outside the loop.
- NEVER place DML statements inside a loop. Collect records in a List, then perform a single DML operation outside the loop.
- NEVER place callouts (HTTP requests) inside loops.
- NEVER use SOQL inside a trigger's for loop — query in bulk before iterating.
- Always assume trigger context will contain up to 200 records. Code must handle 200+ records correctly.
- Use collections (List, Set, Map) to aggregate data before performing operations.
- When querying related records, use Maps keyed by the parent ID for O(1) lookup instead of nested loops.
- Prefer Map<Id, SObject> for lookups instead of iterating through lists.
- Use Database.query() with bind variables to handle dynamic queries at scale.

PATTERN — Correct Bulkification:
  // GOOD: Collect all AccountIds, query once, map for lookup
  Set<Id> accountIds = new Set<Id>();
  for (Contact c : contacts) {
      accountIds.add(c.AccountId);
  }
  Map<Id, Account> accountMap = new Map<Id, Account>(
      [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
  );
  for (Contact c : contacts) {
      Account a = accountMap.get(c.AccountId);
      // process...
  }

ANTI-PATTERN:
  // BAD: SOQL inside a loop
  for (Contact c : contacts) {
      Account a = [SELECT Id, Name FROM Account WHERE Id = :c.AccountId];
  }
```

---

## 5. SOQL & SOSL Rules

```
RULES:
- Always use bind variables (:variable) in SOQL. Never concatenate user input into query strings (SOQL injection risk — PMD: ApexSOQLInjection).
- Always add a LIMIT clause to queries unless you explicitly need all records and have accounted for governor limits.
- Use selective queries — filter on indexed fields (Id, Name, RecordTypeId, Foreign Key fields, External ID fields, and custom indexed fields).
- Never use SELECT * equivalent (SELECT all fields). Explicitly name only the fields you need.
- Never write SOQL with no WHERE clause on large objects (PMD: AvoidNonRestrictiveQueries).
- When using dynamic SOQL (Database.query), use String.escapeSingleQuotes() on any user input.
- Prefer SOQL for relationship queries (parent-child, child-parent) over multiple separate queries.
- Use aggregate queries (COUNT(), SUM(), AVG(), GROUP BY) when you need summaries instead of retrieving and looping all records.
- When querying in a for loop (SOQL for loop), use the batch syntax: for (List<Account> batch : [SELECT ...]) to process in chunks of 200.
- Never rely on record order unless you specify ORDER BY.
- Use `WITH USER_MODE` in SOQL to enforce CRUD and FLS automatically (preferred, API 60.0+):
    SELECT Id, Name FROM Account WITH USER_MODE
- Use `WITH SECURITY_ENFORCED` as an alternative to WITH USER_MODE (throws exception on inaccessible fields).
- Use Security.stripInaccessible() when you need to silently strip inaccessible fields rather than throw.
- Avoid SOQL in constructors of Visualforce controllers — defer to init methods or lazy loading.
- Use the Selector pattern (a dedicated class per object) for all SOQL queries in complex orgs.
- Never assign SOQL results to a single SObject variable unless you are certain exactly 1 row will return:
    // BAD — throws "List has no rows for assignment to SObject" if 0 rows:
    Account a = [SELECT Id FROM Account WHERE Name = 'Acme'];
    // GOOD — use a List and check:
    List<Account> accounts = [SELECT Id FROM Account WHERE Name = 'Acme' LIMIT 1];
    if (!accounts.isEmpty()) { Account a = accounts[0]; }

GOVERNOR LIMITS TO REMEMBER:
  - 100 SOQL queries per synchronous transaction
  - 200 SOQL queries per asynchronous transaction
  - 50,000 records retrieved per transaction
  - 20 SOSL queries per transaction
```

---

## 6. DML Rules

```
RULES:
- Prefer Database.insert/update/upsert/delete with allOrNone=false for partial success handling in batch or integration scenarios.
- Use allOrNone=true (the default) for transactional operations where all records must succeed or all must fail.
- Always handle Database.SaveResult, Database.UpsertResult, Database.DeleteResult when using partial-success DML.
- Log or collect errors from DML results — never silently ignore failures.
- Use upsert with External ID fields for idempotent integrations.
- Combine records into a single list before DML. Never perform multiple DML operations on the same SObject type in the same transaction if avoidable.
- Be aware of the 150 DML statements per transaction limit.
- Be aware of the 10,000 records per DML statement limit.
- When mixing SObject types in DML, use a single list with proper ordering (Account before Contact if Contact references Account).
- Use Database.setSavepoint() and Database.rollback() when multiple DML operations must be atomic.
- Use Security.stripInaccessible(AccessType.CREATABLE, records) before insert, AccessType.UPDATABLE before update, to enforce FLS on DML.
- MIXED DML PREVENTION: Never perform DML on setup objects (User, PermissionSet, Group) and non-setup objects (Account, Contact) in the same transaction:
    // BAD — causes MixedDmlException:
    insert new Account(Name = 'Test');
    insert new User(...);
    // GOOD — use @future or System.runAs() in tests, or separate transactions.
- User Mode DML (API 60.0+): Use Database.insert(records, AccessLevel.USER_MODE) to enforce CRUD/FLS automatically.
```

---

## 7. Trigger Rules

```
RULES:
- ONE trigger per object. No exceptions. Multiple triggers on the same object have unpredictable execution order.
- Triggers must be logic-free. The trigger body should ONLY call a handler class. No business logic in the trigger file itself.
- Use the Handler Pattern:
    trigger AccountTrigger on Account (before insert, before update, after insert, after update, before delete, after delete, after undelete) {
        AccountTriggerHandler handler = new AccountTriggerHandler();
        handler.run();
    }
- The handler class should implement a framework or at minimum dispatch by trigger context:
    - before insert → beforeInsert(List<SObject> newRecords)
    - before update → beforeUpdate(Map<Id, SObject> oldMap, Map<Id, SObject> newMap)
    - after insert → afterInsert(Map<Id, SObject> newMap)
    - after update → afterUpdate(Map<Id, SObject> oldMap, Map<Id, SObject> newMap)
    - before delete → beforeDelete(Map<Id, SObject> oldMap)
    - after delete → afterDelete(Map<Id, SObject> oldMap)
    - after undelete → afterUndelete(Map<Id, SObject> newMap)
- Always use Trigger.new, Trigger.old, Trigger.newMap, Trigger.oldMap — never re-query records that are already in context.
- Never access Trigger.old or Trigger.new by integer index (e.g., Trigger.new[0]) — iterate the list instead. Note: using Trigger.newMap.get(id) or Trigger.oldMap.get(id) is perfectly fine and idiomatic (PMD: AvoidDirectAccessTriggerMap).
- Implement recursion prevention (static Boolean flag or static Set<Id>) to avoid re-entrant trigger execution.
- Always check Trigger.isExecuting to validate context.
- Never perform callouts from triggers directly — use @future(callout=true) or Queueable with Database.AllowsCallouts.
- Triggers should be bypassable via Custom Metadata or a static utility for data migration and admin operations:
    if (TriggerConfig__mdt.getInstance('AccountTrigger')?.Is_Active__c != false) { handler.run(); }
- Always filter records that actually changed before processing: 
    for (Account a : (List<Account>)Trigger.new) {
        Account old = (Account)Trigger.oldMap.get(a.Id);
        if (a.Status__c != old.Status__c) { changedRecords.add(a); }
    }
```

---

## 8. Class Design & Architecture

```
RULES:
- Follow Separation of Concerns: Trigger → Handler → Service → Selector → Domain.
- Service classes contain business logic. They should be stateless and have static methods.
- Selector classes contain all SOQL queries for a specific SObject. Centralize queries for reuse and maintainability.
- Domain classes encapsulate behavior on a collection of records (if using fflib pattern).
- Keep Apex classes under 500 lines where possible. Extract large classes into focused, single-responsibility classes.
- Methods should do one thing. If a method name requires "and" (e.g., validateAndSave), split it.
- Maximum method length: aim for under 40 lines. Extract sub-methods for readability.
- Avoid deep nesting (more than 3 levels). Refactor using early returns or helper methods (PMD: AvoidDeeplyNestedIfStmts).
- Monitor method complexity — high Cyclomatic Complexity indicates too many decision paths. Keep methods simple and testable (PMD: CyclomaticComplexity, CognitiveComplexity).
- Monitor class size via non-commenting source statements (NCSS). Bloated classes/methods are hard to maintain (PMD: NcssCount).
- Classes with too many fields become unwieldy — consider splitting into multiple focused classes or using composition (PMD: TooManyFields).
- Classes with too many public methods/attributes suggest the class has too many responsibilities (PMD: ExcessivePublicCount).
- Use interfaces for extensibility and testability (dependency injection, strategy pattern).
- Use virtual/abstract classes when creating frameworks or shared handlers.
- Use enums instead of String constants for finite sets of values.
- Prefer composition over inheritance.
- Use custom Apex exception classes for domain-specific error types.
- Use inner classes or wrapper classes for structured data transfer between layers.
- Never instantiate a utility class — make utility methods static and the constructor private.
- Use the Singleton pattern for configuration classes (Custom Metadata Type wrappers).
- Avoid circular dependencies between classes.
```

---

## 9. Error Handling & Logging

```
RULES:
- Never use empty catch blocks. Always handle, log, or rethrow (PMD: EmptyCatchBlock).
- Never swallow exceptions silently with just System.debug().
- Use specific exception types in catch blocks before catching generic Exception:
    try {
        // logic
    } catch (DmlException e) {
        // handle DML-specific
    } catch (QueryException e) {
        // handle query-specific
    } catch (Exception e) {
        // handle everything else
    }
- Create custom exception classes for domain logic:
    public class CaseRoutingException extends Exception {}
- Use addError() on SObject records in trigger context instead of throwing exceptions:
    record.addError('Validation failed: reason');
- Implement a centralized logging utility class that writes to a custom object (e.g., Apex_Error_Log__c) or uses Platform Events for async logging.
- Log the following in every error entry: class name, method name, line number, exception message, stack trace, record ID(s) involved, user ID, timestamp.
- Use finally blocks for cleanup (e.g., releasing resources, resetting state).
- Never expose raw exception messages to end users — map to user-friendly messages.
- In batch Apex, collect errors per record in execute() and report them in finish().
- In API/integration code, always check HTTP response status codes and handle non-200 responses.
- System.LimitException CANNOT be caught by try-catch. You must prevent limit violations through proper code design — you cannot recover from them at runtime.
- addError() in trigger context: be aware that addError() with escape=false renders raw HTML — never pass user input with escape=false (PMD: ApexXSSFromEscapeFalse).
```

---

## 10. Security Rules

```
RULES:
- Always use `with sharing` unless there is a documented business reason to bypass.
- Use WITH SECURITY_ENFORCED in SOQL to enforce Field-Level Security (FLS) and Object-Level Security (CRUD).
    SELECT Id, Name FROM Account WITH SECURITY_ENFORCED
- Alternatively, use Security.stripInaccessible() to remove fields the running user cannot access:
    SObjectAccessDecision decision = Security.stripInaccessible(AccessType.READABLE, accounts);
    List<Account> safeAccounts = decision.getRecords();
- Use Security.stripInaccessible(AccessType.CREATABLE, records) before insert, AccessType.UPDATABLE before update.
- Never use String concatenation to build SOQL queries from user input. Use bind variables or String.escapeSingleQuotes().
- Validate and sanitize all external input (API parameters, Visualforce parameters, Lightning component parameters).
- Never store credentials, API keys, or secrets in Apex code. Use Named Credentials, Protected Custom Metadata, or Custom Settings (protected).
- Use Crypto class for encryption/hashing when handling sensitive data.
- In Lightning components, always validate server-side — never trust client-side validation alone.
- Use @AuraEnabled(cacheable=true) only for read operations. Never cache DML or side-effect operations.
- In Experience Cloud (Community) code, always validate the running user's permissions before data access.
- Never expose internal org structure (user IDs, org IDs, field API names) to external consumers unnecessarily.
- Always use HTTPS endpoints for callouts — never use plain HTTP (PMD: ApexInsecureEndpoint).
- Validate redirect URLs — never redirect to user-controlled URLs without validation (PMD: ApexOpenRedirect).
- Use WITH USER_MODE (preferred) or WITH SECURITY_ENFORCED for SOQL, and Security.stripInaccessible() for DML, to enforce FLS/CRUD.
- @AuraEnabled property getters must be `public` or `global` — private getters will fail at runtime (PMD: InaccessibleAuraEnabledGetter).
- @AuraEnabled methods do NOT support method overloading — two methods with the same name but different parameters will cause a runtime error. Use distinct method names.
```

---

## 11. Governor Limits Awareness

```
RULES:
- Always write code with governor limits in mind. Key limits per transaction:
    - SOQL Queries: 100 (sync) / 200 (async)
    - DML Statements: 150
    - Records Retrieved via SOQL: 50,000
    - Records processed by DML: 10,000
    - CPU Time: 10,000 ms (sync) / 60,000 ms (async)
    - Heap Size: 6 MB (sync) / 12 MB (async)
    - Callouts: 100 per transaction
    - Future Calls: 50 per transaction
    - Queueable Jobs Enqueued: 50 per transaction
    - Email Invocations: 10 per transaction
    - Describe Calls: 100 per transaction
    - SOSL Queries: 20 per transaction
    - Push Notification Calls: 10 per transaction

- Use Limits class to monitor consumption at runtime:
    System.debug('SOQL Queries used: ' + Limits.getQueries() + '/' + Limits.getLimitQueries());
- Use asynchronous processing (Batch, Queueable, Future) to break large operations into separate governor limit contexts.
- Use Platform Events to decouple operations and get their own transaction limits.
- Use Lazy Loading — don't query or process data until it's actually needed.
- Optimize SOQL with indexed fields, selective WHERE clauses, and appropriate LIMIT values.
- Use Database.Stateful in Batch Apex only when you must carry state between execute() calls — it consumes more heap.
- When using Database.Stateful, avoid storing Database.SaveResult, Database.UpsertResult, or Database.DeleteResult objects (or collections of them) as instance variables — they can cause serialization failures and excessive heap. Store only the data you need (IDs, error messages) (PMD: AvoidStatefulDatabaseResult).
```

---

## 12. Test Class Rules

```
RULES:
- Every Apex class must have a corresponding test class.
- Test classes must use the @isTest annotation at the class level.
- Target minimum 95% code coverage (not just 75% — that's the deployment minimum, not the quality bar).
- 100% coverage for all critical business logic paths.
- Use @testSetup to create test data shared across test methods. This improves test performance.
- NEVER use @SeeAllData=true. Ever. Tests must create their own data.
    - Exception: only when testing against standard objects that cannot be created in test context (e.g., some Knowledge article scenarios, ConnectApi). Document the reason.
- Test methods annotated @isTest or using testMethod keyword MUST reside in a class annotated @isTest. Test methods in non-test classes cause deployment failures (PMD: TestMethodsMustBeInTestClasses).
- Test method naming convention: test_[methodName]_[scenario]_[expectedResult]
    - Example: test_routeCase_highPriorityTechnical_assignsToTier2Queue
- Each test method should test ONE behavior/scenario.
- Always include:
    - Positive tests (happy path)
    - Negative tests (invalid input, missing data, edge cases)
    - Bulk tests (200+ records to simulate trigger batch)
    - Boundary tests (governor limit edge cases, null parameters, empty lists)
    - Permission tests (running as different user profiles where relevant)
- Use Assert class methods (NOT legacy System.assert):
    - Assert.areEqual(expected, actual, 'message')
    - Assert.areNotEqual(unexpected, actual, 'message')
    - Assert.isTrue(condition, 'message')
    - Assert.isFalse(condition, 'message')
    - Assert.isNull(value, 'message')
    - Assert.isNotNull(value, 'message')
    - Assert.fail('message')
- Every assertion MUST include a descriptive message parameter.
- Never just assert for coverage — assert for correctness.
- Use Test.startTest() and Test.stopTest() to reset governor limits and execute async operations:
    Test.startTest();
    // call the method under test
    Test.stopTest();
    // assertions go AFTER stopTest()
- Use System.runAs() to test sharing rules and profile-specific behavior.
- Use Test.isRunningTest() ONLY as a last resort (prefer dependency injection or Custom Metadata bypasses).
- Mock callouts using HttpCalloutMock and Test.setMock().
- Mock email services using standard test patterns.
- Create utility test data factory class (TestDataFactory) for reusable test record creation:
    public class TestDataFactory {
        public static Account createAccount(Boolean doInsert) { ... }
        public static List<Case> createCases(Integer count, Id accountId, Boolean doInsert) { ... }
    }
- Never hard-code record type IDs or user IDs in tests. Query them dynamically.
```

---

## 13. Asynchronous Apex Rules

```
RULES:

FUTURE METHODS (@future):
- @future is considered a legacy pattern. Prefer Queueable for all new async code (PMD: AvoidFutureAnnotation).
- Use @future only for the simplest fire-and-forget operations that need a separate transaction context.
- Use @future(callout=true) when making HTTP callouts from trigger context.
- Future methods must be static and return void.
- Parameters must be primitive types or collections of primitives (no SObjects).
- Cannot call another @future from a @future method.
- Cannot chain or guarantee execution order.
- Prefer Queueable over @future for anything needing chaining, complex parameters, or monitoring.

QUEUEABLE APEX:
- Use Queueable for complex async work that needs chaining, SObject parameters, or job ID tracking.
- Implement Database.AllowsCallouts interface for callouts.
- Limit chaining depth to avoid runaway processes — use a counter or Custom Metadata to set max chain depth.
- Consider attaching a Finalizer via System.attachFinalizer(this) in the execute() method for error recovery (PMD: QueueableWithoutFinalizer, priority 5 — Low). Finalizers provide a callback when a Queueable succeeds or fails, which is especially useful in chained jobs.
- Implement Finalizer interface for error handling in Queueable chains.
- Always check AsyncApexJob for monitoring.
- Pattern:
    public class MyQueueable implements Queueable, Database.AllowsCallouts {
        public void execute(QueueableContext context) {
            // work
            if (shouldChain) {
                System.enqueueJob(new NextQueueable());
            }
        }
    }

BATCH APEX:
- Use Batch Apex for processing large data volumes (thousands to millions of records).
- Implement Database.Batchable<SObject>.
- start() method: return Database.QueryLocator for up to 50 million records, or Iterable<SObject> for custom iteration (max 50,000).
- execute() handles chunks (default 200, configurable via Database.executeBatch(batch, scopeSize)).
- finish() is for post-processing (send emails, chain another batch, log results).
- Use Database.Stateful ONLY if you need instance variables to persist across execute() calls.
- Always handle partial failures in execute() — don't let one bad record kill the whole batch.
- Add a try-catch in execute() to capture errors per chunk.
- Set appropriate scope size for the operation type:
    - Data processing: 200 (default)
    - Callouts in batch: 1-10 (due to callout limits per execute)
    - Complex CPU operations: 50-100
- Pattern:
    public class MyBatch implements Database.Batchable<SObject>, Database.Stateful {
        public Integer errorCount = 0;
        public Database.QueryLocator start(Database.BatchableContext bc) {
            return Database.getQueryLocator('SELECT Id FROM Account WHERE ...');
        }
        public void execute(Database.BatchableContext bc, List<SObject> scope) {
            // process scope
        }
        public void finish(Database.BatchableContext bc) {
            // post-processing
        }
    }

SCHEDULABLE APEX:
- Use Schedulable for recurring time-based operations.
- Implement the Schedulable interface.
- Keep the execute() method lightweight — it should just kick off a Batch or Queueable.
- Never put heavy logic directly in a Schedulable — governor limits are strict in scheduled context.
- Use System.schedule() or the Cron expression for scheduling.
- Pattern:
    public class MyScheduler implements Schedulable {
        public void execute(SchedulableContext sc) {
            Database.executeBatch(new MyBatch(), 200);
        }
    }

PLATFORM EVENTS (Async via Event Bus):
- Use Platform Events to decouple processes and get a new governor limit context.
- Publish events with EventBus.publish().
- Subscribe with Apex Triggers on the Platform Event object.
- Use Trigger.operationType check in event triggers.
- Handle EventBus.RetryableException for transient failures.
```

---

## 14. Agentforce / Invocable Rules

```
RULES:
- Use @InvocableMethod to expose Apex actions to Agentforce, Flows, and Einstein Bots.
- Every @InvocableMethod must have a clear label and description:
    @InvocableMethod(label='Route Cases' description='Routes cases to appropriate queues based on priority and type')
- Use @InvocableVariable for input/output inner class parameters with labels and descriptions:
    public class CaseRoutingInput {
        @InvocableVariable(label='Case IDs' description='List of Case IDs to route' required=true)
        public List<Id> caseIds;
    }
- InvocableMethod must accept List<InputType> and return List<OutputType> for bulk safety.
- A class can have only ONE @InvocableMethod.
- Always validate inputs inside the InvocableMethod — Flows may send null or empty values.
- Design Invocable actions to be idempotent when possible (safe to retry).
- Keep InvocableMethod lightweight — delegate to a service class:
    @InvocableMethod(label='Route Cases' description='Routes cases to queues')
    public static List<CaseRoutingOutput> routeCases(List<CaseRoutingInput> inputs) {
        return CaseRoutingService.route(inputs);
    }
- For Agentforce Agents, ensure your Apex action descriptions are clear and natural-language friendly — the agent AI uses these descriptions to decide when to invoke your action.
- Test InvocableMethod by calling it directly in test classes with proper input lists.
```

---

## 15. Metadata & Deployment Rules

```
RULES:
- Every Apex class, trigger, LWC, Aura component, and Visualforce page must have a corresponding -meta.xml file.
- Use a consistent API version across all components in the project.
- Standard -meta.xml for Apex class:
    <?xml version="1.0" encoding="UTF-8"?>
    <ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
        <apiVersion>66.0</apiVersion>
        <status>Active</status>
    </ApexClass>
- Standard -meta.xml for Apex trigger:
    <?xml version="1.0" encoding="UTF-8"?>
    <ApexTrigger xmlns="http://soap.sforce.com/2006/04/metadata">
        <apiVersion>66.0</apiVersion>
        <status>Active</status>
    </ApexTrigger>
- Place all source code in the sfdx project structure:
    force-app/main/default/classes/ → Apex classes
    force-app/main/default/triggers/ → Triggers
    force-app/main/default/lwc/ → Lightning Web Components
    force-app/main/default/aura/ → Aura Components
    force-app/main/default/objects/ → Custom Objects/Fields
    force-app/main/default/permissionsets/ → Permission Sets
    force-app/main/default/flows/ → Flows
- Use sfdx-project.json for project configuration. Keep sourceApiVersion in sync with component versions.
- Use .forceignore to exclude unnecessary files from deployment.
- Validate deployments with: sf project deploy start --dry-run before actual deployment.
- Use scratch orgs for development and testing. Define org shape in config/ directory.
```

---

## 16. Code Documentation Rules

```
RULES:
- Every class must have a header comment block:
    /**
     * @description Service class for routing cases to appropriate queues
     * @author Developer Name
     * @date 2026-02-24
     * @group Case Management
     */
- Every public/global method must have an ApexDoc comment:
    /**
     * @description Routes a list of cases to the appropriate queue based on priority and type
     * @param cases List of Case records to route
     * @return List<Case> Updated cases with new OwnerId values
     * @throws CaseRoutingException if no valid queue is found for a routing rule
     * @example
     * List<Case> updatedCases = CaseRoutingService.routeCases(casesToRoute);
     */
- Use inline comments for complex business logic — explain WHY, not WHAT.
- Do not over-comment obvious code:
    // BAD: Increment counter by 1
    counter++;
    // GOOD: Increment retry counter — we allow 3 retries before failing the integration
    retryCount++;
- Use TODO comments for known improvements: // TODO: Refactor to use Custom Metadata for queue mapping
- Use FIXME comments for known bugs: // FIXME: Fails when Account has no contacts — null check needed
- Document all magic numbers:
    // BAD:
    if (score >= 40) { ... }
    // GOOD:
    private static final Integer QUALIFIED_THRESHOLD = 40;
    if (score >= QUALIFIED_THRESHOLD) { ... }
```

---

## 17. Performance Rules

```
RULES:
- Avoid nested loops wherever possible. Use Maps for O(1) lookups instead of O(n²) nested iteration.
- Cache SOQL query results when the same data is needed multiple times in a transaction.
- Use lazy loading — only query/compute data when it's needed.
- Use Database.QueryLocator in Batch Apex for efficient large-data processing.
- Avoid String concatenation in loops — use String.join() or List<String> with join.
- Use Set<Id> for collection membership checks instead of List — Set.contains() is O(1) vs List iteration O(n).
- Avoid unnecessary type casting and object instantiation in loops.
- Never place Schema.getGlobalDescribe(), Schema.describeSObjects(), or SObjectType.getDescribe() calls inside loops — cache the result before the loop (PMD: OperationWithHighCostInLoop).
- Never place DML, SOQL, SOSL, Approval process calls, email sends, or async scheduling (System.enqueueJob, System.schedule) inside loops (PMD: OperationWithLimitsInLoop).
- Use SObjectDescribeOptions.DEFERRED when calling SObjectType.getDescribe() to lazy-load child relationships instead of eagerly loading everything (PMD: EagerlyLoadedDescribeSObjectResult):
    // BAD — eagerly loads all child relationships:
    Schema.DescribeSObjectResult dsr = Account.SObjectType.getDescribe();
    // GOOD — deferred/lazy loading:
    Schema.DescribeSObjectResult dsr = Account.SObjectType.getDescribe(SObjectDescribeOptions.DEFERRED);
- Use SOQL for loops (for (Account a : [SELECT ...])) for read-only iterations to reduce heap:
    for (List<Account> batch : [SELECT Id, Name FROM Account WHERE Industry = 'Technology']) {
        // processes 200 at a time, reducing heap
    }
- Avoid Describe calls in loops. Cache Schema.SObjectType and Schema.DescribeFieldResult (PMD: OperationWithHighCostInLoop).
- Use SObjectDescribeOptions.DEFERRED for lazy-loading describe results (PMD: EagerlyLoadedDescribeSObjectResult).
- Use Platform Cache (Session/Org cache) for frequently accessed, rarely changing data.
- Use SOQL Cursors (Database.getCursor / Database.getQueryLocatorCursor) for traversing large result sets with forward/back navigation in chained Queueable jobs — a modern alternative to Batch Apex for high-volume processing.
- In Visualforce, use transient variables for view state optimization.
- Use selective SOQL queries — non-selective queries on large tables hit "Non-selective query" errors.
- Minimize the use of formula fields in queries — they can't be indexed and impact performance.
```

---

## 18. Approval & Sharing Rules in Code

```
RULES:
- Use Apex Managed Sharing (inserting into __Share objects) when you need programmatic sharing beyond OWD and sharing rules.
- Always set RowCause to a valid Apex sharing reason.
- Always set AccessLevel appropriately: 'Read', 'Edit', 'All'.
- Clean up manual shares when the sharing condition changes.
- For Approval Processes invoked from Apex, use Approval.ProcessSubmitRequest and Approval.process().
- Always validate that the record meets entry criteria before submitting to an approval process.
```

---

## 19. Platform Events & Change Data Capture

```
RULES:
- Use Platform Events for decoupled, event-driven architecture.
- Publish events with EventBus.publish(eventList) — it's a DML-like call (counts toward DML limits).
- Subscribe via Apex Trigger on the Platform Event:
    trigger OrderEvent on Order_Event__e (after insert) {
        // handle events
    }
- Check Trigger.operationType == System.TriggerOperation.AFTER_INSERT (only after insert is valid for events).
- Use EventBus.RetryableException to retry on transient failures — the platform will retry the batch.
- Set the Publish Behavior on the platform event definition:
    - "Publish After Commit" — event publishes only after the transaction commits (recommended for data consistency).
    - "Publish Immediately" — event publishes immediately (use for logging, notifications).
- For Change Data Capture, subscribe to ChangeEvents and handle Create, Update, Delete, Undelete event types.
- Always handle the ReplayId for event replay and durability.
```

---

## 20. Integration Rules

```
RULES:
- Always use Named Credentials for external service authentication — never hardcode tokens, passwords, or API keys (PMD: ApexSuggestUsingNamedCred).
- Use External Services where possible for declarative REST API integration.
- For custom Apex callouts, use HttpRequest/HttpResponse classes.
- Always set timeouts: req.setTimeout(120000); // 2-minute max timeout
- Always check response status codes:
    if (res.getStatusCode() != 200) {
        throw new IntegrationException('API call failed: ' + res.getStatusCode() + ' ' + res.getBody());
    }
- Implement retry logic with exponential backoff for transient failures (429, 500, 503).
- Use @future(callout=true) or Queueable with Database.AllowsCallouts for callouts from trigger context.
- Respect the callout limits: 100 callouts per transaction, 120-second total timeout, 12 MB max response size.
- Use JSON.deserialize() and JSON.serialize() with strongly typed Apex classes, not generic JSON parsing.
- Create dedicated request/response wrapper classes for each integration:
    public class PaymentGatewayRequest {
        public String orderId;
        public Decimal amount;
        public String currency_x; // 'currency' is reserved word
    }
- Use the Continuation class for long-running callouts in Lightning/Visualforce.
- Log all outbound and inbound integration calls with request/response details for debugging.
- Use Custom Metadata to store endpoint URLs, API versions, and configurable parameters.
- Design integrations to be idempotent — duplicate calls should produce the same result.
- "You have uncommitted work pending" error: Never make a callout AFTER performing DML in the same transaction. Either do the callout first, or use @future/Queueable for the callout:
    // BAD — throws CalloutException:
    insert new Account(Name = 'Test');
    HttpResponse res = new Http().send(req);  // VIOLATION
    // GOOD — callout first, then DML:
    HttpResponse res = new Http().send(req);
    insert new Account(Name = 'Test');
```

---

## 21. PMD Static Analysis Rules

```
PMD is the standard static analysis tool for Apex. Run PMD checks in CI/CD pipelines and IDE plugins.
Use the PMD quickstart ruleset (rulesets/apex/quickstart.xml) as a baseline, then customize.
Reference: https://pmd.github.io/pmd/pmd_rules_apex.html

COMPREHENSIVE PMD RULE MAP — all rules referenced throughout this document:

BEST PRACTICES (category/apex/bestpractices.xml):
- ApexAssertionsShouldIncludeMessage  → Every assertion needs a descriptive message parameter.
- ApexUnitTestClassShouldHaveAsserts  → Test classes must include at least one assertion.
- ApexUnitTestClassShouldHaveRunAs    → Test classes should include at least one System.runAs().
- ApexUnitTestMethodShouldHaveIsTestAnnotation → Use @isTest, not legacy testMethod keyword.
- ApexUnitTestShouldNotUseSeeAllDataTrue → Never use @isTest(seeAllData=true).
- AvoidFutureAnnotation               → Prefer Queueable over @future (since PMD 7.19.0).
- AvoidGlobalModifier                  → Avoid global access modifier unless necessary.
- AvoidLogicInTrigger                  → Triggers must delegate to handler classes.
- DebugsShouldUseLoggingLevel          → System.debug must include a LoggingLevel parameter.
- QueueableWithoutFinalizer            → Attach System.attachFinalizer() in Queueable execute() (since PMD 7.8.0, priority 5 — Low).
- UnusedLocalVariable                  → Remove declared-but-unused local variables.

CODE STYLE (category/apex/codestyle.xml):
- AnnotationsNamingConventions         → Annotations should follow PascalCase.
- ClassNamingConventions               → Class names should follow PascalCase.
- FieldDeclarationsShouldBeAtStart     → Fields/properties before methods in class body.
- FieldNamingConventions               → Field names should follow camelCase.
- ForLoopsMustUseBraces                → for loops must use braces.
- FormalParameterNamingConventions     → Parameters should follow camelCase.
- IfElseStmtsMustUseBraces             → if/else blocks must use braces.
- IfStmtsMustUseBraces                 → if blocks must use braces.
- LocalVariableNamingConventions       → Local variables should follow camelCase.
- MethodNamingConventions              → Method names should follow camelCase.
- OneDeclarationPerLine                → One variable declaration per line.
- PropertyNamingConventions            → Properties should follow camelCase.
- WhileLoopsMustUseBraces              → while loops must use braces.

DESIGN (category/apex/design.xml):
- AvoidBooleanMethodParameters         → Avoid boolean params; use enums or separate methods.
- AvoidDeeplyNestedIfStmts             → Max 3 levels of nesting.
- CognitiveComplexity                  → Measures human-understandable complexity; keep methods simple.
- CyclomaticComplexity                 → Counts decision paths; high values = hard to test/maintain.
- ExcessiveParameterList               → Refactor methods with >5 parameters into wrapper/DTO classes.
- ExcessivePublicCount                 → Too many public members = too many responsibilities.
- NcssCount                            → Non-commenting source statement count; monitors bloat.
- TooManyFields                        → Classes with too many fields should be refactored.
- UnusedMethod                         → Remove unused private methods (dead code).

DOCUMENTATION (category/apex/documentation.xml):
- ApexDoc                              → Public classes, methods, and properties require ApexDoc comments.

ERROR PRONE (category/apex/errorprone.xml):
- ApexCSRF                             → No DML in constructors/initializers — classified as Error Prone (not Security); causes app errors on page load.
- AvoidDirectAccessTriggerMap          → Don't access Trigger.old/Trigger.new lists by integer index (e.g., Trigger.new[0]); iterate instead. Trigger.newMap.get(id) is fine.
- AvoidHardcodingId                    → Never hardcode record IDs.
- AvoidNonExistentAnnotations          → Don't use non-existent annotations.
- AvoidStatefulDatabaseResult          → Don't store Database results in Stateful batch class fields.
- EmptyCatchBlock                      → Never swallow exceptions silently.
- EmptyIfStmt                          → Empty if blocks serve no purpose.
- EmptyStatementBlock                  → Empty blocks should be removed.
- EmptyTryOrFinallyBlock               → Empty try/finally blocks are pointless.
- EmptyWhileStmt                       → Empty while loops are errors.
- InaccessibleAuraEnabledGetter        → @AuraEnabled property getters must be public/global.
- MethodWithSameNameAsEnclosingClass   → Non-constructor methods must not match class name.
- OverrideBothEqualsAndHashcode        → Override both or neither.
- TestMethodsMustBeInTestClasses       → @isTest methods must be in @isTest classes.
- TypeShadowsBuiltInNamespace          → Don't shadow System, Database, Schema, etc.

PERFORMANCE (category/apex/performance.xml):
- AvoidDebugStatements                 → System.debug consumes CPU even without active logs.
- AvoidNonRestrictiveQueries           → SOQL/SOSL must have WHERE/LIMIT clauses.
- EagerlyLoadedDescribeSObjectResult   → Use SObjectDescribeOptions.DEFERRED for lazy loading.
- OperationWithHighCostInLoop          → No Schema.getGlobalDescribe/describeSObjects in loops.
- OperationWithLimitsInLoop            → No DML/SOQL/SOSL/email/async ops in loops.

SECURITY (category/apex/security.xml):
- ApexBadCrypto                        → Use random IVs/keys; never hardcode crypto values.
- ApexCRUDViolation                    → Check CRUD/FLS before SOQL/DML.
- ApexDangerousMethods                 → Flags calls to dangerous methods (FinancialForce, etc.).
- ApexInsecureEndpoint                 → Always use HTTPS, never HTTP.
- ApexOpenRedirect                     → Validate redirect URLs; never redirect to user-controlled URLs.
- ApexSharingViolations                → Every class must declare sharing (with/without/inherited).
- ApexSOQLInjection                    → Use bind variables; never concatenate user input into SOQL.
- ApexSuggestUsingNamedCred            → Use Named Credentials for endpoint auth; never hardcode.
- ApexXSSFromEscapeFalse               → Never use addError() with escape=false on user input.
- ApexXSSFromURLParam                  → Escape/sanitize all URL parameters.

SAMPLE PMD RULESET XML (save as pmd-apex-ruleset.xml in project root):
    <?xml version="1.0" encoding="UTF-8"?>
    <ruleset name="Salesforce Apex Rules"
        xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0 https://pmd.sourceforge.io/ruleset_2_0_0.xsd">
        <description>Comprehensive Apex ruleset for AI-assisted development</description>
        <rule ref="rulesets/apex/quickstart.xml" />
        <rule ref="category/apex/bestpractices.xml/AvoidFutureAnnotation" />
        <rule ref="category/apex/bestpractices.xml/QueueableWithoutFinalizer" />
        <rule ref="category/apex/bestpractices.xml/UnusedLocalVariable" />
        <rule ref="category/apex/design.xml/CognitiveComplexity" />
        <rule ref="category/apex/design.xml/UnusedMethod" />
        <rule ref="category/apex/performance.xml/EagerlyLoadedDescribeSObjectResult" />
        <rule ref="category/apex/performance.xml/OperationWithHighCostInLoop" />
        <rule ref="category/apex/errorprone.xml/AvoidStatefulDatabaseResult" />
    </ruleset>
```

---

## 22. Anti-Patterns to Avoid

```
NEVER DO THESE:

1. SOQL in a loop:
   for (Account a : accounts) {
       List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :a.Id]; // VIOLATION
   }

2. DML in a loop:
   for (Account a : accounts) {
       update a; // VIOLATION
   }

3. Hardcoded IDs:
   account.OwnerId = '005000000000001'; // VIOLATION — IDs differ between orgs

4. Multiple triggers on one object:
   // File 1: AccountTrigger.trigger
   // File 2: AccountTrigger2.trigger — VIOLATION

5. Logic in triggers:
   trigger CaseTrigger on Case (before insert) {
       for (Case c : Trigger.new) {
           // 50 lines of business logic here — VIOLATION
       }
   }

6. Using @SeeAllData=true in tests:
   @isTest(SeeAllData=true) // VIOLATION — tests should create their own data

7. Empty catch blocks:
   try { ... } catch (Exception e) { } // VIOLATION — silently swallowing exceptions

8. System.assert without message:
   System.assertEquals(expected, actual); // VIOLATION — use Assert.areEqual with message

9. Using without sharing for no reason:
   public without sharing class MyController { // VIOLATION unless documented

10. Infinite recursion in triggers:
    // Trigger updates record → fires trigger again → infinite loop
    // VIOLATION — use static recursion guard

11. Mixing concerns:
    // Controller class that has SOQL, DML, business logic, and callouts all in one — VIOLATION

12. Using Metadata.DeployContainer hardcoded to specific environments — VIOLATION

13. Returning null from methods that should return collections:
    return null; // VIOLATION — return empty list: return new List<Account>();

14. Not handling null values:
    String name = account.Name.toUpperCase(); // VIOLATION if Name is null → NullPointerException

15. Using SOQL queries with no WHERE clause on large objects:
    SELECT Id FROM Account // VIOLATION — will fail on orgs with 50k+ accounts
```

---

## 23. Common Runtime Errors & Prevention (StackExchange Top Issues)

```
These are the most frequently asked Salesforce StackExchange issues. Build awareness of each into your code:

1. "System.LimitException: Too many SOQL queries: 101"
   CAUSE: SOQL inside a loop, recursive triggers, or complex trigger chains.
   FIX: Bulkify all queries. Use recursion guards. Monitor with Limits.getQueries().

2. "System.QueryException: List has no rows for assignment to SObject"
   CAUSE: Assigning SOQL result to a single SObject when 0 rows return.
   FIX: Always assign to a List<SObject> and check .isEmpty() before accessing.

3. "System.CalloutException: You have uncommitted work pending"
   CAUSE: DML operation executed before a callout in the same transaction.
   FIX: Organize code so callouts happen BEFORE any DML. Or use @future(callout=true) / Queueable.

4. "System.DmlException: MIXED_DML_OPERATION"
   CAUSE: DML on a setup object (User, Group, PermissionSet) and a non-setup object (Account, Contact) in the same transaction.
   FIX: Use @future to separate the operations. In tests, use System.runAs() to create a separate execution context.

5. "System.FinalException: Record is read-only" (after trigger context)
   CAUSE: Trying to modify Trigger.new records in an after insert/update trigger.
   FIX: In after triggers, query the records and perform a separate DML update. Only modify Trigger.new in before triggers.

6. "UNABLE_TO_LOCK_ROW"
   CAUSE: Concurrent transactions trying to update the same record (e.g., parallel batch jobs, triggers + workflow rules).
   FIX: Use FOR UPDATE in SOQL for explicit locking. Reduce batch scope size. Avoid overlapping scheduled jobs. Use Queueable chaining for sequential processing.

7. "System.LimitException: Apex CPU time limit exceeded"
   CAUSE: Inefficient loops, nested iterations, excessive String concatenation, or complex formula field resolution in queries.
   FIX: Use Maps instead of nested loops. Avoid String concat in loops (use String.join). Move work to async. Simplify formulas.
   NOTE: System.LimitException CANNOT be caught — you must prevent it.

8. "System.LimitException: Apex heap size too large"
   CAUSE: Storing too much data in memory (large query results, large Strings, Collections).
   FIX: Use SOQL for-loops to process in batches. Use transient variables in VF. Move to Batch Apex. Don't store entire query results when you only need a subset.

9. "System.LimitException: Too many DML statements: 151"
   CAUSE: DML inside loops or multiple separate DML calls that should be combined.
   FIX: Combine records into a single List and perform one DML call.

10. "System.LimitException: Too many future calls: 51"
    CAUSE: Calling @future from a loop or from batch execute() with large scope.
    FIX: Use Queueable with chaining instead of @future. Never call @future from another @future or from batch Apex.

11. "System.TypeException: Invalid conversion from runtime type List<SObject> to List<Account>"
    CAUSE: Casting Trigger.new directly without proper type casting.
    FIX: Use explicit casting: List<Account> accounts = (List<Account>) Trigger.new;

12. NullPointerException (the #1 most common runtime exception)
    CAUSE: Accessing a method or property on a null reference.
    FIX: Use Safe Navigation Operator (?.). Check for null before accessing.
    Always return empty collections instead of null from methods.
    Use String.isBlank() / String.isNotBlank() for null-safe String checks.

13. "System.SObjectException: SObject row was retrieved via SOQL without querying the requested field"
    CAUSE: Accessing a field on a queried record that wasn’t included in the SELECT clause.
    FIX: Ensure all fields you access are in the SOQL SELECT. Use wrapper classes to make required fields explicit.

14. "Recursive trigger" / StackOverflowError
    CAUSE: Trigger updates a record → trigger fires again → infinite loop.
    FIX: Implement a static Set<Id> or Boolean recursion guard in the handler class. Check before re-processing.

15. "FIELD_CUSTOM_VALIDATION_EXCEPTION" not caught as expected
    CAUSE: Validation Rules throw as DmlException, not a generic Exception. Using allOrNone=true causes the entire batch to fail.
    FIX: Use Database.insert(records, false) with allOrNone=false. Check SaveResult for success/failure per record.

16. "Batch Apex: Too many queueable jobs added to the queue: 2" (from batch execute)
    CAUSE: Enqueueing more than 1 Queueable job per batch execute() invocation.
    FIX: Each batch execute() can enqueue only 1 Queueable. Collect work and enqueue once, or chain from finish().
```

---

## Quick Reference Card

| Category | Rule | Priority |
|----------|------|----------|
| Bulkification | No SOQL/DML in loops | **CRITICAL** |
| Security | Use `with sharing` by default | **CRITICAL** |
| Security | Use `WITH USER_MODE` or `WITH SECURITY_ENFORCED` in SOQL | **CRITICAL** |
| Security | No hardcoded credentials — use Named Credentials | **CRITICAL** |
| Security | Use bind variables in SOQL — no string concatenation | **CRITICAL** |
| Security | Always use HTTPS endpoints, never HTTP | **CRITICAL** |
| Modern Apex | Use Safe Navigation Operator (`?.`) to prevent NPE | **HIGH** |
| Modern Apex | Use `switch on` over long if-else chains | **HIGH** |
| Modern Apex | Use Assert class, not legacy System.assert | **HIGH** |
| Triggers | One trigger per object | **HIGH** |
| Triggers | Logic-free triggers (handler/framework pattern) | **HIGH** |
| Triggers | Recursion prevention (static guard) | **HIGH** |
| DML | Handle MixedDmlException — separate setup/non-setup DML | **HIGH** |
| DML | Callouts BEFORE DML, never after (uncommitted work error) | **HIGH** |
| SOQL | Use List<SObject> not single SObject assignment | **HIGH** |
| Testing | 95%+ coverage with meaningful assertions | **HIGH** |
| Testing | Never use @SeeAllData=true | **HIGH** |
| Testing | Include positive, negative, bulk, and permission tests | **HIGH** |
| Error Handling | No empty catch blocks | **HIGH** |
| Error Handling | System.LimitException cannot be caught — prevent, don't catch | **HIGH** |
| Governor Limits | Always consider limits in design | **HIGH** |
| Architecture | Separation of Concerns (Service/Selector layers) | **MEDIUM** |
| Design | Monitor Cyclomatic/Cognitive Complexity (PMD) | **MEDIUM** |
| Design | Remove unused methods and local variables (PMD) | **MEDIUM** |
| Design | Avoid too many fields or public members per class (PMD) | **MEDIUM** |
| Naming | Follow PascalCase/camelCase conventions (PMD naming rules) | **MEDIUM** |
| Code Style | Always use braces on if/for/while blocks | **MEDIUM** |
| Code Style | One declaration per line, fields before methods | **MEDIUM** |
| Code Style | No empty if/while/try/catch/finally blocks (PMD) | **HIGH** |
| Documentation | ApexDoc on all public methods (PMD: ApexDoc) | **MEDIUM** |
| Performance | Maps for lookups, not nested loops | **MEDIUM** |
| Performance | No Schema.describe calls in loops (PMD: OperationWithHighCostInLoop) | **HIGH** |
| Performance | Use deferred SObjectDescribeOptions (PMD: EagerlyLoadedDescribeSObjectResult) | **MEDIUM** |
| Performance | No DML/SOQL/SOSL/Email/Async in loops (PMD: OperationWithLimitsInLoop) | **CRITICAL** |
| Async | Prefer Queueable over @future (PMD: AvoidFutureAnnotation) | **HIGH** |
| Async | Consider attaching Finalizer to Queueable (PMD: QueueableWithoutFinalizer) | **LOW** |
| Async | Avoid storing Database results in Stateful batch (PMD: AvoidStatefulDatabaseResult) | **MEDIUM** |
| Metadata | Always include -meta.xml files, API version 66.0 | **HIGH** |

---

*This ruleset is tool-agnostic. It works with GitHub Copilot, Cursor, Claude Code, Windsurf, Cline, Roo Code, or any AI-assisted coding tool that supports custom instructions.*
