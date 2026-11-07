# Salesforce Design Patterns & Architecture Review Checklist

> **Review Category**: Architecture, Design Patterns, SOLID Principles, Naming Conventions  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Layer Separation & Architecture

### Trigger-Handler-Service-Selector Pattern

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| One trigger per object | ☐ Pass ☐ Fail | 🟠 HIGH | Multiple triggers cause execution order issues |
| Trigger delegates to handler (no business logic in trigger) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Trigger is thin wrapper; all logic in Handler/Service |
| Handler extends framework (e.g., TriggerHandler) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Consistent patterns improve testability |
| Service class contains business logic | ☐ Pass ☐ Fail | 🟠 HIGH | Logic reusable across triggers, controllers, flows |
| Selector class contains all SOQL queries | ☐ Pass ☐ Fail | 🟡 MEDIUM | Centralized queries simplify optimization and sharing |
| Layer dependencies are one-way: Trigger → Handler → Service → Selector | ☐ Pass ☐ Fail | 🟠 HIGH | No circular dependencies; Service doesn't call Trigger |

### Separation of Concerns

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Controllers handle HTTP/UI concerns only | ☐ Pass ☐ Fail | 🟡 MEDIUM | Request parsing, response formatting; not business logic |
| Service classes handle business logic | ☐ Pass ☐ Fail | 🟠 HIGH | Rules, calculations, external integrations |
| Selector classes handle data access | ☐ Pass ☐ Fail | 🟡 MEDIUM | All SOQL, data filtering, record retrieval |
| Utility classes handle cross-cutting concerns | ☐ Pass ☐ Fail | 🟡 MEDIUM | String formatting, date manipulation, logging |
| No business logic in controllers | ☐ Pass ☐ Fail | 🟠 HIGH | Controllers should be thin wrappers |

---

## 2. Naming Conventions

### Class Naming

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Classes use PascalCase | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountService`, `ContactTriggerHandler` |
| Service classes end with `Service` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountService`, `InvoiceCalculationService` |
| Handler classes end with `Handler` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountTriggerHandler`, `OpportunitySyncHandler` |
| Selector classes end with `Selector` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountSelector`, `ContactSelector` |
| Controller classes end with `Controller` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountPageController`, `InvoiceListController` |
| Test classes end with `Test` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountServiceTest`, `AccountTriggerHandlerTest` |
| Trigger classes named `[Object]Trigger` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountTrigger`, `OpportunityStageTrigger` |

### Variable & Method Naming

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Methods use camelCase | ☐ Pass ☐ Fail | 🟡 MEDIUM | `getAccounts()`, `calculateTotal()` |
| Variables use camelCase | ☐ Pass ☐ Fail | 🟡 MEDIUM | `accountList`, `totalAmount` |
| Constants use UPPER_SNAKE_CASE | ☐ Pass ☐ Fail | 🟡 MEDIUM | `MAX_BATCH_SIZE`, `DEFAULT_TIMEOUT` |
| Boolean variables prefixed with `is`, `has`, `can`, `should` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `isActive`, `hasEmail`, `canDelete` |
| Map names follow `[value]By[Key]` pattern | ☐ Pass ☐ Fail | ⚪ LOW | `accountsByIds`, `contactsByEmail` |
| Collection names plural | ☐ Pass ☐ Fail | ⚪ LOW | `accounts`, `contacts` (not `accountList`) |

---

## 3. SOLID Principles

### Single Responsibility Principle

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Each class has one reason to change | ☐ Pass ☐ Fail | 🟡 MEDIUM | `AccountService` handles account logic; not contact logic |
| Methods have single, well-defined purpose | ☐ Pass ☐ Fail | 🟡 MEDIUM | `getActiveAccounts()` gets active accounts; doesn't also send emails |
| No mixed concerns (data access + business logic) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Separate Selector from Service |
| Classes <1000 lines (split large classes) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract methods/classes to maintain focus |

### Open/Closed Principle

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Classes open for extension (interfaces, abstract classes) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Use interfaces for behavior contracts |
| Classes closed for modification (change behavior via config) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Custom Metadata Types enable feature toggles without code |
| Inheritance used appropriately (is-a relationship) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Extend base classes for shared behavior |

### Liskov Substitution Principle

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Subclasses compatible with base class | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Interface contracts honored in implementations |
| Method signatures match or extend base class | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Override methods must accept parent's parameters |
| No type casting required in polymorphic code | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | If you need to cast, design violated LSP |

### Interface Segregation Principle

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Interfaces focused and specific | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Many specific interfaces > one fat interface |
| Clients implement only needed interfaces | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Don't force unused method implementations |
| No unused method implementations | ☐ Pass ☐ Fail | 🟡 MEDIUM | If implementing but not using, interface too fat |

### Dependency Inversion Principle

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| High-level modules don't depend on low-level modules | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Both depend on abstractions (interfaces) |
| Dependencies injected (constructor, method parameter) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Don't instantiate dependencies within class |
| No hardcoded dependencies | ☐ Pass ☐ Fail | 🟡 MEDIUM | Inject; enable testing with mocks |

---

## 4. Naming Conventions (Continued)

### Object & Field Naming

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Custom objects descriptive and singular | ☐ Pass ☐ Fail | 🟡 MEDIUM | `Service_Work_Order__c` (not `ServiceOrders`) |
| Custom fields descriptive and lowercase with underscores | ☐ Pass ☐ Fail | 🟡 MEDIUM | `is_active__c`, `last_modified_date__c` |
| Lookup/Master-Detail fields end with `__c` | ☐ Pass ☐ Fail | ⚪ LOW | `account__c`, `parent_invoice__c` |
| Formula/Rollup fields clearly marked | ☐ Pass ☐ Fail | ⚪ LOW | `total_amount_formula__c`, `contact_count_rollup__c` |

---

## 5. DRY Principle & Code Reuse

### Duplicate Code

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No significant code duplication | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract common logic to utility methods |
| Repeated SOQL queries consolidated | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cache results or move to Selector class |
| Repeated business rules extracted to Service | ☐ Pass ☐ Fail | 🟡 MEDIUM | Reuse same validation across flows/LWC/API |
| Utility methods for common string/date operations | ☐ Pass ☐ Fail | ⚪ LOW | `formatCurrency()`, `addBusinessDays()` in utility class |

---

## 6. API Versioning & Backward Compatibility

### Apex API Changes

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Public method signatures stable across versions | ☐ Pass ☐ Fail | 🟡 MEDIUM | Changing parameter types breaks consumers |
| New parameters added as optional (default values) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `updateAccount(Account acc, Boolean sendNotification = true)` |
| Deprecated methods marked with `@Deprecated` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `@Deprecated public void oldMethod() {}` |
| Migration path documented for deprecated APIs | ☐ Pass ☐ Fail | 🟡 MEDIUM | "Use newMethod() instead" in Javadoc |

---

## 7. Configuration Over Customization

### Metadata-Driven Design

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Integration endpoints stored in Custom Metadata (not hardcoded) | ☐ Pass ☐ Fail | 🟠 HIGH | Change URLs/credentials without code redeploy |
| Feature toggles via Custom Settings/Metadata | ☐ Pass ☐ Fail | 🟡 MEDIUM | Enable/disable features without code |
| Business rules stored in Custom Metadata (not hardcoded) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Tax rates, shipping rules, approval thresholds |
| No org-specific IDs hardcoded | ☐ Pass ☐ Fail | 🟠 HIGH | Query by name instead of hardcoding org-specific Ids |
| Custom Labels used for user-facing text | ☐ Pass ☐ Fail | 🟡 MEDIUM | Enable localization without code changes |

---

## 8. Consistency & Standards

### Code Style

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Consistent indentation (4 spaces, no tabs) | ☐ Pass ☐ Fail | ⚪ LOW | Configure IDE to use 4-space tabs |
| Braces on same line (same-line brace style) | ☐ Pass ☐ Fail | ⚪ LOW | `if (condition) { } else { }` |
| Space after keywords (if, for, while) | ☐ Pass ☐ Fail | ⚪ LOW | `if (x > 0)` (not `if(x > 0)`) |
| Max line length 120 characters | ☐ Pass ☐ Fail | ⚪ LOW | Readability; most screens support 120 chars |

### Comment Standards

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Class-level JSDoc comments | ☐ Pass ☐ Fail | 🟡 MEDIUM | Purpose, usage, dependencies |
| Public method JSDoc comments | ☐ Pass ☐ Fail | 🟡 MEDIUM | Parameters, return value, exceptions |
| Complex logic commented (WHY not WHAT) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Code explains WHAT; comments explain WHY |
| No over-commenting obvious code | ☐ Pass ☐ Fail | ⚪ LOW | Don't comment every line |
| TODO comments tracked as issues | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't leave TODOs in production code |

---

## 9. Common Design Patterns

### Recursive Trigger Prevention

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `static Set<Id>` tracking (not `static Boolean`) | ☐ Pass ☐ Fail | 🟠 HIGH | Boolean blocks all records; Set allows bulk |
| Tracks processed records during execution | ☐ Pass ☐ Fail | 🟠 HIGH | Prevents infinite loops |

### Map-Based Bulk Processing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses Map<Id, Collections> for bulk lookups | ☐ Pass ☐ Fail | 🟡 MEDIUM | O(1) lookup; replaces nested loop O(n²) |
| Map populated once outside loop | ☐ Pass ☐ Fail | 🟠 HIGH | Single query, reused across loop iterations |

---

## Review Output Template

### Architecture Assessment
- **Design Maturity**: Excellent / Good / Adequate / Needs Improvement
- **Pattern Adherence**: [Pattern compliance %, common patterns used]
- **Consistency**: Consistent across codebase / Some inconsistencies / Inconsistent
- **Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Redesign

### Findings Table

| # | Category | Severity | Issue | Impact | Remediation |
|---|----------|----------|-------|--------|------------|
| 1 | Architecture | 🟠 HIGH | Business logic in trigger | Hard to test, slow | Move to Service class |
| 2 | Naming | 🟡 MEDIUM | Service class too generic | Unclear purpose | Rename: `AccountCalculationService` |
| 3 | DRY | 🟡 MEDIUM | Account validation logic duplicated | Maintenance burden | Extract to single `validateAccount()` method |
| 4 | Config | 🟠 HIGH | Hardcoded integration URL | Can't change without redeploy | Move to Custom Metadata Type |

### Positive Findings
- ✅ Clean Trigger → Handler → Service → Selector architecture
- ✅ Consistent naming conventions throughout
- ✅ Good separation of concerns
- ✅ Configuration-driven instead of hardcoded

### Overall Assessment
[Architecture evaluation and recommendations]
