# Security, Sharing & Access Control Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes for sharing model and security changes.

## Table of Contents
1. [Sharing Keywords in Apex](#sharing-keywords-in-apex)
2. [CRUD & FLS Enforcement](#crud-and-fls-enforcement)
3. [Sharing Model Architecture](#sharing-model-architecture)
4. [Security Best Practices](#security-best-practices)
5. [SOQL Injection Prevention](#soql-injection-prevention)
6. [XSS Prevention](#xss-prevention)
7. [Custom Permissions](#custom-permissions)
8. [Permission Sets & Permission Set Groups](#permission-sets)
9. [Shield Platform Encryption](#shield-platform-encryption)

---

## Sharing Keywords in Apex

Apex runs in **system context** by default — it has access to all records and fields regardless of
the current user's permissions. Use sharing keywords to enforce or bypass record-level security.

### `with sharing`

Enforces the running user's sharing rules. Use this by default for all user-facing code.

```apex
public with sharing class AccountService {
    // SOQL respects sharing rules — user sees only records they have access to
    public List<Account> getMyAccounts() {
        return [SELECT Id, Name FROM Account ORDER BY Name LIMIT 100];
    }
}
```

### `without sharing`

Ignores sharing rules — runs as if the user has "View All Data." Use sparingly.

```apex
public without sharing class AccountAdminService {
    // Use only when the business logic REQUIRES access to all records
    // Example: Calculating org-wide metrics, system integrations
    public Integer getTotalAccountCount() {
        return [SELECT COUNT() FROM Account];
    }
}
```

### `inherited sharing`

Inherits the sharing context of the caller. Use for utility/library classes.

```apex
public inherited sharing class UtilityService {
    // If called from a `with sharing` class → sharing enforced
    // If called from a `without sharing` class → sharing not enforced
    // If called without an explicit sharing context (e.g., trigger, anonymous Apex,
    //   or another class with no sharing keyword) → defaults to `without sharing`
    //   (Salesforce docs: "the default is without sharing" in the absence of an inherited context)
    public List<Account> queryAccounts(Set<Id> accountIds) {
        return [SELECT Id, Name FROM Account WHERE Id IN :accountIds];
    }
}
```

### Sharing Keyword Decision Matrix

| Scenario | Keyword | Reason |
|---|---|---|
| LWC/Aura controller | `with sharing` | User context — respect their access |
| REST API endpoint | `with sharing` | External caller should see only permitted data |
| Trigger handler | `without sharing` (carefully) or `with sharing` | Triggers need to process all records in the batch |
| Batch Apex | `without sharing` (often) | Usually processes org-wide data |
| Utility/helper class | `inherited sharing` | Let the caller decide the sharing context |
| System integration service | `without sharing` | Integration needs full data access |
| Scheduled Apex | `without sharing` (often) | Runs as the scheduling user |

### Inner Class Sharing Behavior

```apex
public with sharing class OuterClass {
    // Inner classes do NOT inherit the outer class sharing keyword
    // They run in the sharing context of their caller
    public class InnerHelper {
        // Sharing context determined by whoever instantiates this class
    }

    // To enforce sharing on an inner class, declare it explicitly
    public with sharing class SecureInner {
        // Always enforces sharing
    }
}
```

---

## CRUD and FLS Enforcement

### WITH SECURITY_ENFORCED (SOQL — Recommended)

The simplest way to enforce CRUD and FLS in SOQL. Throws an exception if the user lacks
access to any field or object in the query.

```apex
// Throws System.QueryException if user can't read Account.Name, Account.AnnualRevenue,
// or the Account object itself
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WHERE Industry = 'Technology'
    WITH SECURITY_ENFORCED
];
```

**Pros:** Simple, declarative, covers the entire query
**Cons:** All-or-nothing — fails if ANY field is inaccessible (no graceful degradation)

### WITH USER_MODE / SYSTEM_MODE (API v56.0+)

More granular control introduced in API v56.0 (Winter '23). DML support via `AccessLevel` added in v57.0.

```apex
// USER_MODE — enforces CRUD, FLS, AND sharing rules
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WITH USER_MODE
];

// SYSTEM_MODE — bypasses all security (explicit opt-in)
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WITH SYSTEM_MODE
];

// Also works with Database methods
List<Account> accounts = Database.query(
    'SELECT Id, Name FROM Account',
    AccessLevel.USER_MODE
);

// DML with user mode
Database.insert(records, AccessLevel.USER_MODE);
Database.update(records, AccessLevel.USER_MODE);
```

### Security.stripInaccessible()

Gracefully removes fields the user can't access instead of throwing an exception.

```apex
List<Account> accounts = [SELECT Id, Name, AnnualRevenue, Phone FROM Account];

// Strip fields the user can't read
SObjectAccessDecision decision = Security.stripInaccessible(
    AccessType.READABLE,
    accounts
);

// Get sanitized records — inaccessible fields are removed (null)
List<Account> sanitized = decision.getRecords();

// Check which fields were removed
Set<String> removedFields = decision.getRemovedFields().get('Account');
if (removedFields != null && !removedFields.isEmpty()) {
    System.debug('Stripped fields: ' + removedFields);
}
```

**Access types:**
- `AccessType.READABLE` — Check read access
- `AccessType.CREATABLE` — Check create access
- `AccessType.UPDATABLE` — Check update access
- `AccessType.UPSERTABLE` — Check upsert access

### Manual CRUD/FLS Checks (Legacy Pattern)

```apex
// Check object-level access (CRUD)
if (!Schema.sObjectType.Account.isAccessible()) {
    throw new AuraHandledException('You do not have access to Account records.');
}

// Check field-level access (FLS)
if (!Schema.sObjectType.Account.fields.AnnualRevenue.isAccessible()) {
    throw new AuraHandledException('You do not have access to the Annual Revenue field.');
}

// Check create access
if (!Schema.sObjectType.Account.isCreateable()) {
    throw new AuraHandledException('You cannot create Account records.');
}

// Check specific field create access
if (!Schema.sObjectType.Account.fields.Name.isCreateable()) {
    throw new AuraHandledException('You cannot set the Name field.');
}

// Check update access
Schema.sObjectType.Account.isUpdateable();
Schema.sObjectType.Account.isDeletable();
```

### FLS Best Practices

| Method | When to Use |
|---|---|
| `WITH SECURITY_ENFORCED` | Default for SOQL in user-facing code |
| `WITH USER_MODE` | When you also want sharing enforced in the query itself |
| `Security.stripInaccessible()` | When you want graceful degradation instead of exceptions |
| Manual `isAccessible()` | When you need fine-grained control or custom error messages |
| `WITH SYSTEM_MODE` | Only for system-level operations that explicitly need full access |

---

## Sharing Model Architecture

### Record Access Hierarchy

Record access is cumulative — it can only be opened up, never restricted below the OWD.

```
Organization-Wide Defaults (OWD)         ← Most restrictive baseline
    ↓
Role Hierarchy                           ← Managers see subordinates' records
    ↓
Sharing Rules (criteria-based or owner)  ← Open access to groups/roles
    ↓
Manual Sharing                           ← Ad hoc record-by-record sharing
    ↓
Apex Managed Sharing                     ← Programmatic sharing
    ↓
Implicit Sharing                         ← Built-in (parent-child, portal)
```

### Organization-Wide Defaults (OWD)

| Setting | Description |
|---|---|
| **Private** | Only the owner and users above them in the role hierarchy can see the record |
| **Public Read Only** | All users can see all records, but only the owner can edit |
| **Public Read/Write** | All users can see and edit all records |
| **Controlled by Parent** | Access to child record determined by access to parent (detail in master-detail) |
| **Public Full Access** | All users can read, edit, transfer, and delete (used for Campaigns) |

### Apex Managed Sharing

Create sharing records programmatically for complex sharing requirements.

```apex
public without sharing class AccountSharingService {
    public static void shareAccountsWithTeam(List<Account> accounts, Id groupId) {
        List<AccountShare> shares = new List<AccountShare>();

        for (Account acc : accounts) {
            AccountShare share = new AccountShare();
            share.AccountId = acc.Id;
            share.UserOrGroupId = groupId;
            share.AccountAccessLevel = 'Edit';       // 'Read' or 'Edit'
            share.OpportunityAccessLevel = 'Read';    // Required for Account shares
            share.CaseAccessLevel = 'None';           // 'None', 'Read', or 'Edit'
            share.RowCause = Schema.AccountShare.RowCause.Manual;
            // For custom row cause: share.RowCause = 'My_Custom_Reason__c';
            shares.add(share);
        }

        Database.SaveResult[] results = Database.insert(shares, false);
        for (Integer i = 0; i < results.size(); i++) {
            if (!results[i].isSuccess()) {
                System.debug(LoggingLevel.ERROR,
                    'Share failed for ' + accounts[i].Name + ': ' + results[i].getErrors());
            }
        }
    }

    // Remove sharing
    public static void removeSharing(Id accountId, Id userOrGroupId) {
        List<AccountShare> shares = [
            SELECT Id FROM AccountShare
            WHERE AccountId = :accountId
            AND UserOrGroupId = :userOrGroupId
            AND RowCause = 'Manual'
        ];
        if (!shares.isEmpty()) {
            delete shares;
        }
    }
}
```

### Share Object Naming Convention

| Standard Object | Share Object |
|---|---|
| Account | `AccountShare` |
| Contact | `ContactShare` |
| Opportunity | `OpportunityShare` |
| Case | `CaseShare` |
| Lead | `LeadShare` |
| Custom Object (MyObj__c) | `MyObj__Share` |

### Share Object Fields

| Field | Description |
|---|---|
| `ParentId` or `[Object]Id` | The record being shared |
| `UserOrGroupId` | User or public group receiving access |
| `AccessLevel` or `[Object]AccessLevel` | `Read` or `Edit` |
| `RowCause` | Why the share exists (`Manual`, `Rule`, custom RowCause) |

---

## Security Best Practices

### Apex Security Checklist

1. **Always use `with sharing`** on classes called from user context (LWC, Aura, VF)
2. **Use `WITH SECURITY_ENFORCED`** or `WITH USER_MODE` on SOQL queries
3. **Use `Security.stripInaccessible()`** before DML if you need graceful handling
4. **Never hardcode credentials** — use Named Credentials or Custom Metadata
5. **Escape user input** in dynamic SOQL with `String.escapeSingleQuotes()`
6. **Use bind variables** in SOQL instead of string concatenation
7. **Don't expose sensitive data** in debug logs, error messages, or exceptions
8. **Validate input data** — check for null, length, format before processing
9. **Use `AuraHandledException`** for user-facing errors (hides internal details)
10. **Apply Custom Permissions** for feature gating instead of profile checks

### Secure Coding in LWC

```javascript
// GOOD — Use Lightning Data Service (respects CRUD/FLS automatically)
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';

// GOOD — Schema imports provide compile-time validation
import NAME_FIELD from '@salesforce/schema/Account.Name';

// BAD — Do not construct dynamic API calls with user input
// const endpoint = '/services/data/v66.0/sobjects/' + userInput; ❌

// GOOD — Always sanitize user input for display
// LWC templates auto-escape by default ({expression} is safe)
// BUT: lwc:dom="manual" and innerHTML bypass escaping — avoid when possible
```

---

## SOQL Injection Prevention

### Bind Variables (Best Protection)

```apex
// SAFE — bind variable, no injection possible
String userInput = ApexPages.currentPage().getParameters().get('name');
List<Account> accounts = [SELECT Id, Name FROM Account WHERE Name = :userInput];
```

### Dynamic SOQL — Escape User Input

```apex
// When bind variables aren't possible (dynamic field names, etc.)
String safeName = String.escapeSingleQuotes(userInput);
String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + safeName + '\'';
List<Account> results = Database.query(query);
```

### Dynamic SOQL — Allowlist Pattern (Best for Dynamic Fields/Objects)

```apex
// SAFE — Validate against known safe values
private static final Set<String> ALLOWED_FIELDS = new Set<String>{
    'Name', 'Industry', 'AnnualRevenue', 'Rating'
};

public static List<Account> dynamicQuery(String fieldName, String sortOrder) {
    if (!ALLOWED_FIELDS.contains(fieldName)) {
        throw new AuraHandledException('Invalid field: ' + fieldName);
    }
    if (sortOrder != 'ASC' && sortOrder != 'DESC') {
        sortOrder = 'ASC';
    }

    String query = 'SELECT Id, Name FROM Account ORDER BY '
                 + fieldName + ' ' + sortOrder + ' LIMIT 100';
    return Database.query(query);
}
```

---

## XSS Prevention

### In Visualforce

```html
<!-- SAFE — auto-escaped by default -->
<apex:outputText value="{!account.Name}" />

<!-- UNSAFE — escape="false" disables escaping -->
<apex:outputText value="{!account.Name}" escape="false" />  <!-- ❌ -->

<!-- SAFE — Use JSENCODE for JavaScript contexts -->
<script>
    var name = '{!JSENCODE(account.Name)}';
</script>

<!-- SAFE — Use HTMLENCODE for HTML contexts -->
<div>{!HTMLENCODE(account.Description)}</div>

<!-- SAFE — Use URLENCODE for URL parameters -->
<a href="/search?q={!URLENCODE(searchTerm)}">Search</a>
```

### In LWC

```javascript
// LWC templates auto-escape {expressions} — this is SAFE:
// <p>{accountName}</p>

// AVOID lwc:dom="manual" with user-generated content
// If you must use innerHTML, sanitize first:
renderedCallback() {
    // ❌ DANGEROUS — never do this with user input
    // this.template.querySelector('.container').innerHTML = userInput;

    // ✅ SAFE — use template expressions instead
    // <p>{sanitizedContent}</p>
}
```

---

## Custom Permissions

### Creating & Checking Custom Permissions

Custom Permissions let you gate features without relying on profiles.

```apex
// Check a custom permission in Apex
if (FeatureManagement.checkPermission('Bypass_Validation_Rules')) {
    // User has the custom permission — skip validation
} else {
    // Enforce validation
}
```

```javascript
// Check custom permission in LWC
import hasPermission from '@salesforce/customPermission/Bypass_Validation_Rules';

export default class MyComponent extends LightningElement {
    get canBypass() {
        return hasPermission;
    }
}
```

```
// Check in Validation Rules / Formulas
$Permission.Bypass_Validation_Rules
```

### Custom Permission Best Practices

- Use for feature flags (show/hide UI, enable/disable features)
- Assign via Permission Sets or Permission Set Groups
- Prefer over Profile checks (`$Profile.Name = 'Admin'` → `$Permission.Admin_Feature`)
- Namespaced in managed packages: `namespace__Permission_Name`

---

## Permission Sets and Permission Set Groups

### Permission Set Assignments in Apex

```apex
// Assign a permission set to a user (requires @future or Queueable for mixed DML)
@future
public static void assignPermissionSet(Id userId, String permSetName) {
    PermissionSet ps = [
        SELECT Id FROM PermissionSet
        WHERE Name = :permSetName
        LIMIT 1
    ];
    insert new PermissionSetAssignment(
        AssigneeId = userId,
        PermissionSetId = ps.Id
    );
}
```

### Permission Set Groups

Permission Set Groups bundle multiple Permission Sets for role-based access.

```
Permission Set Group: "Sales Manager Access"
├── Permission Set: "Account Management"
├── Permission Set: "Opportunity Management"
├── Permission Set: "Report Builder"
└── Permission Set: "Dashboard Viewer"
```

- **Muting Permission Sets** can remove specific permissions within a group
- Permission Set Groups support **session-based activation** for time-limited access

---

## Shield Platform Encryption

### Key Concepts

| Feature | Description |
|---|---|
| **Classic Encryption** | Encrypts individual text fields (128-bit AES), visible as `EncryptedString` field type |
| **Shield Platform Encryption** | Encrypts data at rest with 256-bit AES, transparent to most code |
| **Deterministic Encryption** | Allows filtering on encrypted fields (with reduced security) |
| **Probabilistic Encryption** | Stronger encryption, but encrypted fields can't be filtered |

### Apex Considerations with Shield Encryption

```apex
// Encrypted fields can't be used in:
// - WHERE clauses (unless deterministic encryption)
// - ORDER BY
// - GROUP BY
// - LIKE operator
// - Aggregate functions (SUM, AVG, etc.)

// Check if a field is encrypted at runtime
if (Schema.sObjectType.Account.fields.SSN__c.isEncrypted()) {
    // Handle encrypted field differently
}
```
