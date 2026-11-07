# Error Handling & Logging Review Checklist

> **Review Category**: Exception Handling, Error Logging, Recovery Mechanisms  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Exception Handling Patterns

### Try-Catch Best Practices

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No empty catch blocks | ☐ Pass ☐ Fail | 🔴 CRITICAL | `catch(Exception e) {}` silently hides errors; always log/handle |
| Catch specific exception types (not generic Exception) | ☐ Pass ☐ Fail | 🟠 HIGH | `catch(DmlException e)` vs `catch(Exception e)` enables targeted handling |
| Try-catch only for recoverable errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't catch if you can't handle; let exception propagate |
| Finally block used to reset state | ☐ Pass ☐ Fail | 🟡 MEDIUM | `finally { stopRecursionFlag = false; }` guarantees cleanup |
| Multiple catch blocks ordered specific → general | ☐ Pass ☐ Fail | ⚪ LOW | Specific exceptions first; general catch last |

### Custom Exceptions

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Custom exception classes created for domain logic | ☐ Pass ☐ Fail | 🟡 MEDIUM | `public class AccountException extends Exception {}` |
| Custom exceptions include message context | ☐ Pass ☐ Fail | 🟡 MEDIUM | `throw new AccountException('Account ' + accId + ' exceeds credit limit: ' + limit)` |
| Custom exceptions extend appropriate base class | ☐ Pass ☐ Fail | ⚪ LOW | Extend `Exception`, not unrelated classes |
| Custom exception constructors support various inputs | ☐ Pass ☐ Fail | ⚪ LOW | Support `new AccountException(msg)`, `new AccountException(msg, cause)` |

---

## 2. DML Error Handling

### Insert/Update/Delete Operations

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `Database.insert/update/delete()` with `allOrNone=false` | ☐ Pass ☐ Fail | 🟠 HIGH | Continues on error; allows partial success |
| SaveResult array checked for success/failure | ☐ Pass ☐ Fail | 🟠 HIGH | `for (SaveResult sr : results) { if (!sr.isSuccess()) { /* handle */ } }` |
| Error messages from SaveResult logged | ☐ Pass ☐ Fail | 🟡 MEDIUM | `sr.getErrors()[0].getMessage()` extracted and logged |
| Partial success communicated to user | ☐ Pass ☐ Fail | 🟡 MEDIUM | "500 inserted, 50 failed" better than silent half-failure |
| Trigger addError() used for validation failures | ☐ Pass ☐ Fail | 🟠 HIGH | `record.addError('Credit limit exceeded')` rolls back transaction |

### Bulk DML Exception Handling

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Each record's errors individually assessed | ☐ Pass ☐ Fail | 🟡 MEDIUM | One failed record shouldn't invalidate entire batch |
| Failed record IDs collected for logging | ☐ Pass ☐ Fail | 🟡 MEDIUM | Track which records failed for support investigation |
| Retry logic for transient failures (UNABLE_TO_LOCK) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Lock contention = temporary; retry after delay |
| Error consolidation for reporting | ☐ Pass ☐ Fail | 🟡 MEDIUM | Group errors by type (validation, CRUD, lock, etc.) |

---

## 3. Callout Error Handling

### HTTP Callout Patterns

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| HTTP response status checked (not assuming success) | ☐ Pass ☐ Fail | 🟠 HIGH | `if (response.getStatusCode() == 200) { /* success */ }` |
| Non-2xx status codes handled gracefully | ☐ Pass ☐ Fail | 🟠 HIGH | 4xx = client error (bad request), 5xx = server error (retry) |
| Response body parsed safely (malformed JSON protection) | ☐ Pass ☐ Fail | 🟠 HIGH | Wrap JSON.deserialize() in try-catch |
| Timeout exceptions caught and handled | ☐ Pass ☐ Fail | 🟡 MEDIUM | `catch(CalloutException e)` for timeout scenarios |
| Retry logic with exponential backoff | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't retry immediately; wait 1s, 2s, 4s, 8s |
| Max retry attempts enforced | ☐ Pass ☐ Fail | 🟡 MEDIUM | Prevent infinite retry loops (typical: 3-5 retries) |

### Resilience Patterns

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Circuit breaker pattern implemented | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Stop calling failed external service; resume after interval |
| Fallback data/behavior for failed callouts | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use cached data, default values, or async queue |
| Callout timeouts configured appropriately | ☐ Pass ☐ Fail | 🟡 MEDIUM | Match external API SLA (default 120s) |

---

## 4. Logging & Audit Trails

### Apex Logging

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| System.debug() statements removed before deploy | ☐ Pass ☐ Fail | 🟡 MEDIUM | Production should not have verbose debug logs |
| If debug logs needed, LoggingLevel specified | ☐ Pass ☐ Fail | 🟡 MEDIUM | `System.debug(LoggingLevel.ERROR, msg)` for error context only |
| Error logging includes stack trace | ☐ Pass ☐ Fail | 🟡 MEDIUM | `e.getStackTraceString()` for support debugging |
| Logging includes record IDs and relevant field values | ☐ Pass ☐ Fail | 🟡 MEDIUM | Example: "Update failed for Account 001xx Name: Acme, Credit: 5000" |
| No sensitive data in logs (SSN, card numbers, tokens) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Debug logs visible to admins; never log credentials/PII |

### Custom Error Logging

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Integration failures logged to custom Error Log object | ☐ Pass ☐ Fail | 🟡 MEDIUM | Persistent logging for compliance/audit |
| Error severity levels assigned (CRITICAL, ERROR, WARNING, INFO) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Enable filtering by severity during troubleshooting |
| Error timestamp recorded | ☐ Pass ☐ Fail | 🟡 MEDIUM | `DateTime.now()` for correlation with other logs |
| User context recorded (who triggered the error) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `UserInfo.getUserId()` for audit trail |
| Source system identified (which integration/class logged error) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `'AccountService'`, `'JitterBitIntegration'`, etc. |

### Audit Logging

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Sensitive operations logged (create, update, delete) | ☐ Pass ☐ Fail | 🟠 HIGH | Compliance requirement for SOX, HIPAA, GDPR |
| Field-level history tracked (Field History Tracking) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Who changed what field from X to Y at what time |
| External integration calls logged | ☐ Pass ☐ Fail | 🟡 MEDIUM | Request/response payloads logged (without credentials) |
| Batch job execution logged | ☐ Pass ☐ Fail | 🟡 MEDIUM | Batch start, completion, errors, record counts |

---

## 5. User Error Messages

### Error Communication

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| User-facing errors are non-technical and actionable | ☐ Pass ☐ Fail | 🟡 MEDIUM | ❌ "DmlException: REQUIRED_FIELD_MISSING on field Name" |
| | | | ✅ "Please enter an Account Name to proceed" |
| Error messages don't expose internal system details | ☐ Pass ☐ Fail | 🟠 HIGH | Hide stack traces, SQL, integration endpoints from users |
| Error messages include remediation steps | ☐ Pass ☐ Fail | 🟡 MEDIUM | "Contact your Salesforce admin to add Sales profile" better than "Access denied" |
| Validation errors clear and specific | ☐ Pass ☐ Fail | 🟡 MEDIUM | "Amount must be > 0" vs "Invalid amount" |
| Timeout messages inform user of retry | ☐ Pass ☐ Fail | 🟡 MEDIUM | "Service temporarily unavailable. Please try again in 5 minutes." |

### Error UI Components

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| LWC uses lightning-alert, lightning-confirm for errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | Built-in components; native UX |
| Toast messages used for transient errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | ShowToastEvent for quick notifications |
| Modal dialogs for critical/blocking errors | ☐ Pass ☐ Fail | 🟡 MEDIUM | Require user acknowledgment for severe issues |
| Error state visually distinct | ☐ Pass ☐ Fail | ⚪ LOW | Red icons, highlighted fields, error badges |

---

## 6. Exception Types & Best Practices

### Common Apex Exceptions

| Exception Type | When Thrown | Handling Strategy |
|---|---|---|
| `DmlException` | Insert/update/delete fails | Check SaveResult; user-facing error message |
| `QueryException` | Query syntax/access error | Log; wrap in try-catch if user-triggered |
| `CalloutException` | HTTP callout timeout/error | Retry with backoff; fallback behavior |
| `JsonException` | JSON parsing error | Log response body; user-facing error |
| `IllegalArgumentException` | Invalid argument to method | Validate inputs before calling; prevent in tests |
| `ListException` | Index out of bounds | Check list size before accessing; use safe index |
| `MapException` | Key not found in map | Use `containsKey()` before `get()` |
| `StringException` | String method error | Use String.isBlank() for null/empty checks |

### Exception Propagation

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Exceptions not swallowed by generic catch | ☐ Pass ☐ Fail | 🟠 HIGH | If you catch, you must handle; else rethrow |
| Exception cause chain preserved | ☐ Pass ☐ Fail | 🟡 MEDIUM | `throw new AccountException(msg, ex)` preserves stack |
| Trigger exceptions surface to user (addError vs throw) | ☐ Pass ☐ Fail | 🟡 MEDIUM | addError() shows validation message; throw propagates |
| Async exceptions logged (no exception propagation) | ☐ Pass ☐ Fail | 🟠 HIGH | @future/@InvocableMethod can't throw to caller; log to Error object |

---

## 7. Testing Error Scenarios

### Error Path Testing

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Tests verify exception messages | ☐ Pass ☐ Fail | 🟡 MEDIUM | `Assert.isTrue(e.getMessage().contains('Credit limit'))` |
| Negative tests trigger all exception paths | ☐ Pass ☐ Fail | 🟡 MEDIUM | Force errors: invalid IDs, permission violations, DML failures |
| Tests verify error logging | ☐ Pass ☐ Fail | 🟡 MEDIUM | Query error log records after error; verify content |
| Tests verify partial success handling | ☐ Pass ☐ Fail | 🟡 MEDIUM | Some records succeed, some fail; verify all handled correctly |
| Tests verify database rollback on error | ☐ Pass ☐ Fail | 🟡 MEDIUM | When transaction fails, no partial data persists |
| Tests verify retry logic | ☐ Pass ☐ Fail | 🟡 MEDIUM | Mock failure, verify retry counts, exponential backoff |

---

## Review Output Template

### Error Handling Assessment
- **Risk Level**: Critical / High / Medium / Low
- **Error Handling Quality**: Comprehensive / Good / Adequate / Insufficient
- **Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Improvement

### Findings Table

| # | Category | Severity | Issue | Impact | Remediation |
|---|----------|----------|-------|--------|------------|
| 1 | Exception | 🔴 CRITICAL | Empty catch block (line 42) | Errors silently ignored | Add error logging: `System.debug(LoggingLevel.ERROR, e.getMessage())` |
| 2 | DML | 🟠 HIGH | allOrNone=true used (line 58) | All records fail if one fails | Change to `allOrNone=false`; check SaveResult |
| 3 | Logging | 🔴 CRITICAL | SSN logged in error message | Data exposure risk | Sanitize: exclude sensitive fields from logs |
| 4 | Callout | 🟠 HIGH | No timeout exception handling | Unhandled timeout crash | Add `catch(CalloutException e)` with retry logic |

### Positive Findings
- ✅ Comprehensive error logging to custom Error_Log object
- ✅ Custom exception classes for domain-specific errors
- ✅ 100% exception path test coverage

### Overall Assessment
[Pass/Fail with recommendations for error handling improvements]
