# Security & Compliance Review Checklist

> **Review Category**: Salesforce Security, Data Protection, Compliance  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Data Access & Sharing Enforcement

### Sharing Keywords

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| All classes explicitly declare a sharing keyword | ☐ Pass ☐ Fail | 🔴 CRITICAL | Use `with sharing`, `without sharing`, or `inherited sharing` — never implicit |
| User-facing code (controllers, services) uses `with sharing` | ☐ Pass ☐ Fail | 🟠 HIGH | Respects user's record-level sharing rules and field accessibility |
| Integration/system services justified with `without sharing` comment | ☐ Pass ☐ Fail | 🟠 HIGH | Example: "without sharing // Admin integration needs full data access" |
| Helper/utility classes use `inherited sharing` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Inherits caller's sharing context; flexible for reuse |
| Inner classes inherit outer class sharing context | ☐ Pass ☐ Fail | 🟡 MEDIUM | Verify behavior matches intent (inner class inherits parent's sharing keyword) |

### CRUD & FLS

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SOQL uses `WITH SECURITY_ENFORCED` or WITH USER_MODE | ☐ Pass ☐ Fail | 🔴 CRITICAL | Fails query if user lacks FLS read access; prevents data leakage |
| DML uses `Security.stripInaccessible(AccessType.CREATABLE/UPDATABLE)` | ☐ Pass ☐ Fail | 🔴 CRITICAL | Removes inaccessible fields before insert/update; prevents CRUD bypass |
| SOQL Injection prevention (bind variables only) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Never: `'WHERE Name = ' + userInput`; Always: `WHERE Name = :nameVar` |
| No exposure of sensitive fields (SSN, credit card, API keys) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Never log, return in API, or persist unencrypted sensitive data |
| No storing credentials in code/custom settings | ☐ Pass ☐ Fail | 🔴 CRITICAL | Use Named Credentials, Custom Labels, or Key Management Service |

---

## 2. External Integrations & APIs

### HTTP Callouts

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| HTTPS (TLS 1.2+) enforced for all external calls | ☐ Pass ☐ Fail | 🔴 CRITICAL | HTTP traffic interceptable; never send credentials over HTTP |
| Certificate validation enabled (default in Salesforce) | ☐ Pass ☐ Fail | 🟠 HIGH | Verify server certificate prevents MITM attacks |
| Timeout configured for callouts | ☐ Pass ☐ Fail | 🟡 MEDIUM | Prevent hanging connections; default 120s |
| Request payload validated and sanitized | ☐ Pass ☐ Fail | 🟠 HIGH | Prevent XML/JSON injection |
| Response validation (not trusting external service) | ☐ Pass ☐ Fail | 🟠 HIGH | Parse carefully; don't assume server is trustworthy |

### Named Credentials & Secrets

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Named Credentials used for all external authentication | ☐ Pass ☐ Fail | 🔴 CRITICAL | Never hardcode credentials in Apex |
| OAuth flow used instead of basic auth | ☐ Pass ☐ Fail | 🟡 MEDIUM | OAuth more secure; credentials have expiry |
| Secrets stored in Salesforce Secrets | ☐ Pass ☐ Fail | 🟠 HIGH | Encrypted storage with audit trail |

---

## 3. Sensitive Data Handling

### PII & Confidential Data

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SSN, credit card, password never logged | ☐ Pass ☐ Fail | 🔴 CRITICAL | Debug logs accessible to admins; never expose sensitive values |
| Sensitive fields excluded from error messages | ☐ Pass ☐ Fail | 🔴 CRITICAL | Don't log full credit card numbers, SSN, tokens in errors |
| PII fields displayed only to users with explicit need | ☐ Pass ☐ Fail | 🟠 HIGH | Minimize exposure via FLS or custom permission |
| Email/phone used only where necessary | ☐ Pass ☐ Fail | 🟠 HIGH | PII has regulatory implications (GDPR, CCPA) |

### Encryption at Rest

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Shield Platform Encryption for sensitive custom fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | Required for compliance (HIPAA, PCI-DSS) |
| Encrypted fields tested for searchability | ☐ Pass ☐ Fail | 🟡 MEDIUM | Encrypted fields not queryable; plan alternative lookup |

---

## 4. Authentication & Authorization

### Security Context

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Code in system context has explicit access checks | ☐ Pass ☐ Fail | 🟠 HIGH | @AuraEnabled, batch run in system context; manually validate access |
| `@AuraEnabled(cacheable=false)` for user-specific data | ☐ Pass ☐ Fail | 🟠 HIGH | cacheable=true caches across users; cacheable=false recalculates per user |
| Custom permissions for sensitive operations | ☐ Pass ☐ Fail | 🟠 HIGH | Check `Perm.SensitiveOp__c` before high-risk actions |
| Permission sets updated with new custom permissions | ☐ Pass ☐ Fail | 🟡 MEDIUM | New permissions should be pre-assigned to relevant sets |

---

## 5. Audit & Compliance

### Audit Trails

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Sensitive data changes logged to audit object | ☐ Pass ☐ Fail | 🟠 HIGH | Record who/what/when for regulatory compliance |
| Field history tracked for important objects | ☐ Pass ☐ Fail | 🟡 MEDIUM | Enable Field History for sensitive data |
| Setup audit trail enabled for config changes | ☐ Pass ☐ Fail | 🟡 MEDIUM | Monitor who modified custom fields, rules, code |
| Regular audit log export configured | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Archive for long-term compliance (7 years typical) |

### Compliance Frameworks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| GDPR compliance considered (if EU data) | ☐ Pass ☐ Fail | 🟠 HIGH | Data retention, right to erasure, consent, breach notification |
| CCPA compliance (if California data) | ☐ Pass ☐ Fail | 🟠 HIGH | Privacy policy, opt-out, no discrimination |
| HIPAA compliance (if healthcare data) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Encryption, BAA, access logs, breach notification |
| PCI-DSS compliance (if handling cards) | ☐ Pass ☐ Fail | 🔴 CRITICAL | Tokenize cards, encrypt, no full card storage |
| SOX compliance (if public company) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Financial data integrity, controls, audit |

---

## Review Output Template

### Security Risk Assessment
- **Risk Level**: Critical / High / Medium / Low
- **Compliance Frameworks**: [GDPR, HIPAA, PCI-DSS, SOX]
- **Security Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Rework

### Findings Table

| # | Category | Severity | Issue | Remediation |
|---|----------|----------|-------|------------|
| 1 | Data Access | 🔴 CRITICAL | Missing `with sharing` keyword | Add `with sharing` to class |
| 2 | SOQL Safety | 🔴 CRITICAL | String concatenation in SOQL | Use bind variables |
| 3 | Credentials | 🔴 CRITICAL | API key hardcoded in code | Move to Named Credentials |

### Positive Findings
- ✅ HTTPS enforced for all external integrations
- ✅ Comprehensive audit logging

### Compliance Status
[Assessment of frameworks and remediation plan]
