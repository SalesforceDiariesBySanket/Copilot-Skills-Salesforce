# SOQL/SOSL Optimization & Governor Limits Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes before relying on limits or query behavior.

## Table of Contents
1. [SOQL Best Practices](#soql-best-practices)
2. [Dynamic SOQL](#dynamic-soql)
3. [Query Selectivity & Indexing](#query-selectivity-and-indexing)
4. [Relationship Queries](#relationship-queries)
5. [SOSL Patterns](#sosl-patterns)
6. [Governor Limits Quick Reference](#governor-limits-quick-reference)
7. [Large Data Volume Strategies](#large-data-volume-strategies)
8. [SOQL Cursors](#soql-cursors)
9. [Big Objects](#big-objects)

---

## SOQL Best Practices

### Query Only What You Need
```apex
// BAD — SELECT * equivalent, fetches all fields
// (Salesforce doesn't support SELECT *, but querying too many fields is wasteful)

// GOOD — Only fetch fields you use
List<Account> accounts = [
    SELECT Id, Name, Industry
    FROM Account
    WHERE Industry = 'Technology'
    WITH SECURITY_ENFORCED
    LIMIT 200
];
```

### Always Use Bind Variables
```apex
// BAD — Vulnerable to SOQL injection
String userInput = 'Technology';
String query = 'SELECT Id FROM Account WHERE Industry = \'' + userInput + '\'';

// GOOD — Bind variable (inline SOQL)
List<Account> accs = [SELECT Id FROM Account WHERE Industry = :userInput];

// GOOD — Bind variable (dynamic SOQL)
String query = 'SELECT Id FROM Account WHERE Industry = :userInput';
List<Account> accs = Database.query(query);

// For dynamic SOQL with user input in non-bind positions, escape:
String safeName = String.escapeSingleQuotes(userInput);
```

---

## Dynamic SOQL — Comprehensive Guide

Dynamic SOQL lets you build query strings at runtime. Use it when the object, fields, or filters
are not known at compile time (e.g., admin-configurable reports, generic utilities).

### Database.query() — Basic Dynamic SOQL
```apex
// Simple dynamic query
String objectName = 'Account';
String query = 'SELECT Id, Name FROM ' + String.escapeSingleQuotes(objectName) +
               ' WHERE Industry = :industryFilter LIMIT 100';
String industryFilter = 'Technology';
List<sObject> results = Database.query(query);
```

### Database.queryWithBinds() — Safe Bind Variables (API v57.0+)
Preferred over string concatenation for filter values — prevents SOQL injection automatically.

```apex
// Pass bind variables as a Map — the SAFEST way to build dynamic SOQL
String query = 'SELECT Id, Name FROM Account WHERE Industry = :industry AND AnnualRevenue > :minRev';
Map<String, Object> binds = new Map<String, Object>{
    'industry' => 'Technology',
    'minRev' => 1000000
};
List<Account> results = Database.queryWithBinds(
    query, binds, AccessLevel.USER_MODE   // Enforces sharing + CRUD/FLS
);
```

### Database.countQuery() — Dynamic COUNT
```apex
String countQuery = 'SELECT COUNT() FROM Account WHERE Industry = :ind';
String ind = 'Technology';
Integer total = Database.countQuery(countQuery);
```

### Database.getQueryLocator() — Dynamic Batch Queries
```apex
// Use in Batch Apex start() method for queries returning > 50k rows
public Database.QueryLocator start(Database.BatchableContext bc) {
    String query = 'SELECT Id, Name FROM Account WHERE LastModifiedDate < :cutoff';
    return Database.getQueryLocator(query);
}
```

### Building Dynamic Queries Safely
```apex
public with sharing class DynamicQueryBuilder {
    // Build a query with optional filters — SAFE pattern
    public static List<sObject> queryWithFilters(
        String objectName, List<String> fields, Map<String, Object> filters
    ) {
        // Validate object name against Schema to prevent injection
        if (!Schema.getGlobalDescribe().containsKey(objectName.toLowerCase())) {
            throw new AuraHandledException('Invalid object: ' + objectName);
        }

        // Validate field names against Schema
        DescribeSObjectResult objDesc = Schema.getGlobalDescribe()
            .get(objectName.toLowerCase()).getDescribe();
        Map<String, SObjectField> fieldMap = objDesc.fields.getMap();
        List<String> safeFields = new List<String>();
        for (String f : fields) {
            if (fieldMap.containsKey(f.toLowerCase())) {
                safeFields.add(f);
            }
        }
        if (safeFields.isEmpty()) {
            safeFields.add('Id');
        }

        // Build query
        String query = 'SELECT ' + String.join(safeFields, ', ') +
                       ' FROM ' + objectName;

        // Add filters using bind map
        List<String> conditions = new List<String>();
        Map<String, Object> binds = new Map<String, Object>();
        Integer i = 0;
        for (String field : filters.keySet()) {
            if (fieldMap.containsKey(field.toLowerCase())) {
                String bindKey = 'bind' + i;
                conditions.add(field + ' = :' + bindKey);
                binds.put(bindKey, filters.get(field));
                i++;
            }
        }
        if (!conditions.isEmpty()) {
            query += ' WHERE ' + String.join(conditions, ' AND ');
        }
        query += ' WITH USER_MODE LIMIT 2000';

        return Database.queryWithBinds(query, binds, AccessLevel.USER_MODE);
    }
}
```

### Dynamic SOQL Anti-Patterns
```apex
// ❌ BAD — String concatenation with user input (SOQL injection risk)
String query = 'SELECT Id FROM Account WHERE Name = \'' + userInput + '\'';

// ❌ BAD — Dynamic field names without validation (can expose unauthorized fields)
String query = 'SELECT ' + userProvidedField + ' FROM Account';

// ❌ BAD — Using escapeSingleQuotes alone without schema validation
String safeName = String.escapeSingleQuotes(userInput);
// This only prevents injection via quotes — doesn't protect against
// object/field name manipulation

// ✅ GOOD — Always validate against Schema.getGlobalDescribe() + field maps
// ✅ GOOD — Use Database.queryWithBinds() for filter values
// ✅ GOOD — Use AccessLevel.USER_MODE for automatic security enforcement
```

---

### Aggregate Queries
```apex
// COUNT
Integer count = [SELECT COUNT() FROM Account WHERE Industry = 'Technology'];

// GROUP BY with aggregate functions
List<AggregateResult> results = [
    SELECT Industry, COUNT(Id) cnt, AVG(AnnualRevenue) avgRev, SUM(AnnualRevenue) totalRev
    FROM Account
    GROUP BY Industry
    HAVING COUNT(Id) > 5
    ORDER BY COUNT(Id) DESC
];
for (AggregateResult ar : results) {
    String industry = (String) ar.get('Industry');
    Integer cnt = (Integer) ar.get('cnt');
    Decimal avgRev = (Decimal) ar.get('avgRev');
}
```

### Date Literals (No Hardcoded Dates)
```apex
// Use SOQL date literals for relative dates
SELECT Id, Name FROM Opportunity WHERE CloseDate = THIS_QUARTER
SELECT Id FROM Case WHERE CreatedDate = LAST_N_DAYS:30
SELECT Id FROM Lead WHERE ConvertedDate = THIS_FISCAL_YEAR
SELECT Id FROM Task WHERE ActivityDate = NEXT_N_MONTHS:3

// Common date literals:
// TODAY, YESTERDAY, TOMORROW
// THIS_WEEK, LAST_WEEK, NEXT_WEEK
// THIS_MONTH, LAST_MONTH, NEXT_MONTH
// THIS_QUARTER, LAST_QUARTER, NEXT_QUARTER
// THIS_YEAR, LAST_YEAR, NEXT_YEAR
// THIS_FISCAL_QUARTER, THIS_FISCAL_YEAR
// LAST_N_DAYS:n, NEXT_N_DAYS:n
// LAST_N_MONTHS:n, NEXT_N_MONTHS:n
```

### FOR UPDATE (Record Locking)
```apex
// Lock records to prevent concurrent modifications
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WHERE Id IN :accountIds
    FOR UPDATE
];
// Records are locked until the transaction completes
```

---

## Query Selectivity and Indexing

### Standard Indexed Fields (Always Indexed)
- `Id`
- `Name`
- `OwnerId`
- `CreatedDate`
- `SystemModstamp` / `LastModifiedDate`
- `RecordTypeId`
- Lookup / Master-Detail relationship fields
- `External ID` fields (auto-indexed when marked as External ID)
- Unique fields

### Selectivity Thresholds

For a query to be "selective" and use an index, the filter must match fewer records than the threshold.

**Standard Index thresholds:**
| Total Records | Threshold |
|---|---|
| ≤ 1 million | 30% of total |
| > 1 million | Scales down, caps at ~1 million rows |

**Custom Index thresholds (request from Salesforce Support):**
| Total Records | Threshold |
|---|---|
| ≤ 1 million | 10% of total |
| > 1 million | Scales down, caps at ~333,333 rows |

### Non-Selective Filter Conditions (Cannot Use Index)
- Negative operators: `!=`, `NOT LIKE`, `EXCLUDES`, `NOT IN`
- Leading wildcard: `LIKE '%search%'` (trailing wildcard `LIKE 'search%'` IS selective)
- Comparison operators on text fields: `>`, `<`, `>=`, `<=`
- Non-deterministic formula fields
- Null comparisons on non-indexed fields

### Compound Filters & Selectivity
```apex
// AND — both conditions evaluated, most selective wins
WHERE Industry = 'Tech' AND State = 'CA'  // Selective if EITHER is selective

// OR — ALL conditions must be selective individually
WHERE Industry = 'Tech' OR State = 'CA'   // Selective only if BOTH are selective

// Best practice: put most selective filter first
```

### Custom Indexes

Salesforce maintains standard indexes on certain fields (Id, Name, OwnerId, CreatedDate,
SystemModstamp, RecordTypeId, lookups, External IDs, unique fields). For other fields,
request a **custom index** from Salesforce Support.

**Types of custom indexes:**

| Index Type | Description | When to Request |
|---|---|---|
| **Single-column** | Index on one field | Filter on a single non-indexed field on large-volume object |
| **Two-column** | Composite index on two fields | Frequently filter on a specific pair (e.g., `Status__c` + `Region__c`) |
| **Picklist index** | Index on picklist field | Picklist used as primary filter on tables > 100K |
| **Skinny table** | Denormalized read-only table with subset of fields | Wide objects (100+ fields) queried on narrow set |
| **External ID** | Automatically indexed when field is marked External ID | Upsert keys, integration matching |

**How to request:**
1. Open a case with Salesforce Support → Category: "Custom Index Request"
2. Provide object API name, field API name(s), estimated record count
3. Salesforce evaluates and creates the index (no downtime)
4. Custom indexes are org-specific and survive sandboxes refreshes from production

**Custom index rules:**
- Custom index threshold: **10%** of total records (vs 30% for standard indexes)
- Cannot index formula fields, long text, rich text, or encrypted fields
- Cannot index fields with > 30% null values (nulls are not indexed)
- Two-column indexes: both fields must meet individual selectivity thresholds

### Query Plan Tool (Developer Console)

Use the Query Plan tool to see how Salesforce will execute your SOQL:

**How to enable:**
1. Developer Console → Help → Preferences → Enable Query Plan ✓
2. Query Editor tab → paste SOQL → click **Query Plan** button
3. Review the plan output

**Query Plan output fields:**

| Field | Meaning |
|---|---|
| **Cardinality** | Estimated number of records returned |
| **Fields** | Index fields being considered |
| **Leading Operation Type** | `Index` (good), `TableScan` (bad for large tables) |
| **Cost** | Relative cost — lower is better. < 1.0 generally means selective |
| **sObject Cardinality** | Total records in the object |
| **sObject Type** | Object being queried |
| **Notes** | Why an index was/wasn't used |

**Reading the plan:**
```
// Example output for: SELECT Id FROM Account WHERE Custom_Field__c = 'ABC'
Plan 1: Index on Account.Custom_Field__c
  Cardinality: 150
  Cost: 0.003
  Leading Operation Type: Index
  
Plan 2: TableScan
  Cardinality: 50000
  Cost: 1.0
  Leading Operation Type: TableScan

// Salesforce picks Plan 1 (lowest cost)
// If only TableScan appears → add an index or rewrite the query
```

### Data Skew

Data skew causes record locking, sharing recalculation bottlenecks, and query performance issues.

**Types of data skew:**

| Skew Type | Description | Mitigation |
|---|---|---|
| **Account skew** | One parent Account owns millions of child records (Contacts, Opps, Cases) | Break large accounts into sub-accounts or territory accounts |
| **Ownership skew** | One user owns > 10,000 records | Redistribute to queue or role-based owners; use exempt "integration user" |
| **Lookup skew** | Millions of records point to the same lookup target | Add lookup filter to spread distribution; use formula instead of lookup |

**Detection queries:**
```apex
// Find ownership skew — users owning too many records
List<AggregateResult> ownerSkew = [
    SELECT OwnerId, COUNT(Id) cnt
    FROM Account
    GROUP BY OwnerId
    HAVING COUNT(Id) > 10000
    ORDER BY COUNT(Id) DESC
];

// Find lookup skew — single parent with too many children
List<AggregateResult> parentSkew = [
    SELECT AccountId, COUNT(Id) cnt
    FROM Contact
    GROUP BY AccountId
    HAVING COUNT(Id) > 10000
    ORDER BY COUNT(Id) DESC
];
```

**Impact of data skew on operations:**
- **Lock contention**: DML on child records locks the parent → serializes concurrent updates
- **Sharing recalculation**: Moving a record from/to a skewed owner triggers massive sharing recalc
- **Query timeouts**: Queries that resolve to a skewed parent may scan millions of rows

### Skinny Tables (Large Data Volumes)

For objects with millions of records, request Salesforce Support to create a "skinny table" containing
only the fields you frequently query. This bypasses the standard wide-table overhead.

**Skinny table details:**
- Contains a **read-only** copy of a subset of fields (max ~100 fields)
- Automatically kept in sync by the platform (no user maintenance)
- Significantly faster for queries that only need a few fields from a wide object
- Does NOT include soft-deleted records (IsDeleted = true)
- Does NOT support polymorphic relationships
- Survives sandbox refresh from production
- Cannot include formula fields, long text, or encrypted fields
- Available only for custom objects and some standard objects (Contact, Account, Opportunity, Case, Lead)

**When to request a skinny table:**
- Object has > 100 custom fields but queries typically use < 20
- Queries on the object regularly approach or exceed timeout limits
- Object has millions of records AND reports/dashboards are slow

---

## Relationship Queries

### Parent-to-Child (Subquery)
```apex
// Up to 20 subqueries per SOQL statement
// Child relationship names use plural (e.g., Contacts, Opportunities)
List<Account> accounts = [
    SELECT Id, Name,
        (SELECT Id, LastName, Email FROM Contacts WHERE IsActive__c = true),
        (SELECT Id, Name, Amount FROM Opportunities WHERE StageName != 'Closed Lost')
    FROM Account
    WHERE Id IN :accountIds
];

for (Account acc : accounts) {
    for (Contact c : acc.Contacts) {
        System.debug(c.LastName);
    }
}
```

### Child-to-Parent (Dot Notation)
```apex
// Up to 5 levels of parent traversal (55 max relationship hops per query)
List<Contact> contacts = [
    SELECT Id, LastName,
           Account.Name,
           Account.Owner.Name,
           Account.Parent.Name
    FROM Contact
    WHERE Account.Industry = 'Technology'
];
```

### Custom Relationship Names
```apex
// Custom child relationships: use __r suffix
// Parent object: Invoice__c, Child: Line_Item__c (lookup to Invoice__c)
SELECT Id, Name,
    (SELECT Id, Product__c, Quantity__c FROM Line_Items__r)
FROM Invoice__c

// Child to custom parent
SELECT Id, Invoice__r.Name, Invoice__r.Total__c
FROM Line_Item__c
```

### Polymorphic Relationships (What/Who)
```apex
// TYPEOF for polymorphic fields (API v46.0+)
SELECT Id, Subject,
    TYPEOF What
        WHEN Account THEN Name, Industry
        WHEN Opportunity THEN Name, StageName
    END
FROM Task
WHERE What.Type IN ('Account', 'Opportunity')
```

---

## SOSL Patterns

### Basic SOSL
```apex
List<List<sObject>> searchResults = [
    FIND 'Acme*' IN ALL FIELDS
    RETURNING Account(Id, Name WHERE Industry = 'Technology'),
              Contact(Id, FirstName, LastName, Email),
              Opportunity(Id, Name, Amount)
    LIMIT 20
];

List<Account> accounts = (List<Account>) searchResults[0];
List<Contact> contacts = (List<Contact>) searchResults[1];
List<Opportunity> opps = (List<Opportunity>) searchResults[2];
```

### SOQL vs SOSL Decision Guide
| Use SOQL When... | Use SOSL When... |
|---|---|
| You know which object to query | Searching across multiple objects |
| Querying by exact field values | Full-text search / fuzzy matching |
| Need relationship traversal | User-driven keyword search |
| Need aggregate functions | Need results from many objects fast |
| Need ORDER BY / GROUP BY | Searching in ALL FIELDS |

---

## Governor Limits Quick Reference

### Per-Transaction Limits

| Resource | Synchronous | Asynchronous |
|---|---|---|
| SOQL queries issued | 100 | 200 |
| Records retrieved by SOQL | 50,000 | 50,000 |
| Records retrieved by Database.getQueryLocator | 10,000 | 10,000 |
| SOSL queries | 20 | 20 |
| Records retrieved by SOSL | 2,000 | 2,000 |
| DML statements | 150 | 150 |
| Records processed by DML | 10,000 | 10,000 |
| Callouts (HTTP + web services) | 100 | 100 |
| Callout timeout | 120 seconds | 120 seconds |
| Total callout timeout per txn | 120 seconds | 120 seconds |
| CPU time | 10,000 ms | 60,000 ms |
| Heap size | 6 MB | 12 MB |
| Maximum execution time | 10 minutes | 10 minutes |
| Sent emails (single) | 10 | 10 |
| Future method calls | 50 | 0 in future context |
| Queueable jobs added | 50 | 1 |
| Push notification methods | 10 | 10 |

### Checking Limits in Code
```apex
System.debug('SOQL queries used: ' + Limits.getQueries() + ' / ' + Limits.getLimitQueries());
System.debug('DML statements: ' + Limits.getDmlStatements() + ' / ' + Limits.getLimitDmlStatements());
System.debug('DML rows: ' + Limits.getDmlRows() + ' / ' + Limits.getLimitDmlRows());
System.debug('CPU time: ' + Limits.getCpuTime() + ' / ' + Limits.getLimitCpuTime());
System.debug('Heap size: ' + Limits.getHeapSize() + ' / ' + Limits.getLimitHeapSize());
```

### Platform-Wide Limits
| Resource | Limit |
|---|---|
| Async Apex executions / 24hr | max(250,000, licenses × 200) |
| Scheduled Apex jobs | 100 (5 in Dev Edition) |
| Batch Apex concurrent jobs | 5 |
| API requests / 24hr | Per edition (varies) |
| Bulk API batches / 24hr | 15,000 |

---

## Large Data Volume Strategies

### Use QueryLocator for Batch Processing
```apex
// Database.getQueryLocator supports up to 50 million rows
// (vs 50,000 for regular SOQL)
public Database.QueryLocator start(Database.BatchableContext bc) {
    return Database.getQueryLocator([
        SELECT Id, Name FROM Account WHERE CreatedDate > :cutoffDate
    ]);
}
```

### Offset Pagination (Simple, Limited)
```apex
// OFFSET limited to 2,000
List<Account> page = [
    SELECT Id, Name FROM Account
    ORDER BY Name
    LIMIT 50 OFFSET 100
];
```

### Cursor-Based Pagination (Preferred for Large Sets)
```apex
// Use the last record's sort field for next page
String lastSeen = 'Company ABC';
List<Account> nextPage = [
    SELECT Id, Name FROM Account
    WHERE Name > :lastSeen
    ORDER BY Name
    LIMIT 50
];
```

### Async SOQL (Big Objects)
```apex
// For extremely large datasets, use async SOQL or Big Objects
// Async SOQL runs in background, results stored in target object
// Not available in all editions — check your org
```

---

## SOQL Cursors

SOQL Cursors (API v62.0+, Winter '25) allow incremental, position-based traversal of large query
result sets without loading all records into memory at once. Cursors are the preferred alternative
to OFFSET for paginating large datasets.

### Database.getCursor()

```apex
// Create a cursor from a SOQL query
Database.Cursor cursor = Database.getCursor(
    'SELECT Id, Name, Industry FROM Account WHERE Industry != null ORDER BY Name'
);

// Get total record count (does NOT consume SOQL query limit)
Integer totalRecords = cursor.getNumRecords();
System.debug('Total matching records: ' + totalRecords);

// Fetch records in pages using fetch(position, count)
// position = 0-based start index, count = number of records to fetch
Integer pageSize = 200;
for (Integer offset = 0; offset < totalRecords; offset += pageSize) {
    List<Account> page = (List<Account>) cursor.fetch(offset, pageSize);
    // Process page...
    System.debug('Fetched ' + page.size() + ' records starting at ' + offset);
}
```

### Cursor Key Rules

| Rule | Detail |
|---|---|
| **API version** | Requires API v62.0+ on the class metadata |
| **Input** | Query string only (no inline SOQL) — same syntax as `Database.query()` |
| **getNumRecords()** | Returns total count; does NOT count against SOQL query limit |
| **fetch(position, count)** | Returns `List<sObject>`; each `fetch()` counts as **1 SOQL query** against governor limits |
| **Max fetch count** | Up to **2,000 records per fetch()** call |
| **Cursor lifetime** | Valid within the **same transaction** only — cannot be serialized or stored |
| **No DML interleave** | Avoid DML between fetch() calls on the same cursor — behavior is undefined |
| **Bind variables** | NOT supported — use string concatenation with `String.escapeSingleQuotes()` for dynamic values |
| **AccessLevel** | Use `Database.getCursor(query, AccessLevel.USER_MODE)` for CRUD/FLS enforcement |

### Cursor vs QueryLocator vs OFFSET

| Feature | Database.getCursor() | Database.getQueryLocator() | OFFSET |
|---|---|---|---|
| **API version** | v62.0+ | All | All |
| **Max records** | 50,000 (sync), subject to governor limits per fetch | 50 million (Batch Apex only) | 2,000 |
| **Random access** | ✅ `fetch(position, count)` — any position | ❌ Sequential only | ✅ Via OFFSET clause |
| **Use case** | Flexible pagination in Apex | Batch Apex start() method | Simple pagination, small sets |
| **Governor impact** | Each `fetch()` = 1 SOQL query | 1 query in start() | 1 query per page |
| **Supports USER_MODE** | ✅ | ❌ | N/A (use WITH SECURITY_ENFORCED) |

### Cursor in Batch Apex

Cursors are particularly useful in `execute()` methods when you need to cross-reference data
without loading everything into the scope:

```apex
public class AccountEnrichmentBatch implements Database.Batchable<sObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Name, Industry FROM Account WHERE NeedsEnrichment__c = true
        ]);
    }

    public void execute(Database.BatchableContext bc, List<Account> scope) {
        // Use cursor to look up related data without loading full result set
        Set<String> industries = new Set<String>();
        for (Account a : scope) {
            industries.add(a.Industry);
        }

        // Standard query for the smaller reference set
        Map<String, Industry_Config__c> configs = new Map<String, Industry_Config__c>();
        for (Industry_Config__c ic : [
            SELECT Id, Industry__c, Enrichment_Source__c
            FROM Industry_Config__c
            WHERE Industry__c IN :industries
        ]) {
            configs.put(ic.Industry__c, ic);
        }

        // Process scope with config data
        for (Account a : scope) {
            Industry_Config__c cfg = configs.get(a.Industry);
            if (cfg != null) {
                a.Enrichment_Source__c = cfg.Enrichment_Source__c;
            }
        }
        update scope;
    }

    public void finish(Database.BatchableContext bc) {
        System.debug('Enrichment complete');
    }
}
```

### Cursor Anti-Patterns

```apex
// ❌ BAD — Fetching one record at a time (wastes SOQL limits)
for (Integer i = 0; i < cursor.getNumRecords(); i++) {
    List<sObject> single = cursor.fetch(i, 1); // 1 SOQL per record!
}

// ❌ BAD — Trying to serialize cursor for later use
// Cursors are transaction-scoped and cannot survive serialization

// ❌ BAD — Using bind variables (not supported)
Database.Cursor c = Database.getCursor(
    'SELECT Id FROM Account WHERE Industry = :myVar' // Runtime error!
);

// ✅ GOOD — Batch fetch with safe string values
String safeValue = String.escapeSingleQuotes(userInput);
Database.Cursor c = Database.getCursor(
    'SELECT Id FROM Account WHERE Industry = \'' + safeValue + '\''
);
List<Account> batch = (List<Account>) c.fetch(0, 2000);
```

---

## Big Objects

Big Objects store and manage massive data volumes (billions of rows) on the Salesforce platform.
They are designed for archiving, audit trails, 360-degree customer views, and historical analytics.

### Key Characteristics

| Feature | Standard/Custom Objects | Big Objects |
|---|---|---|
| Record limit | ~tens of millions practical | Billions |
| Storage | Counts against data storage | Separate Big Object storage |
| SOQL support | Full | Limited (see below) |
| Triggers | Full | Not supported |
| Flows | Full | Not supported |
| Sharing/Security | Full OWD + sharing rules | No sharing model — all or nothing |
| DML | Standard | `Database.insertImmediate()` only |
| Suffix | `__c` | `__b` |
| Indexes | Standard + custom | Defined at creation (composite index on first N fields) |

### Defining a Big Object

Big Objects are defined via Metadata API (not the UI). The index is defined at creation and
**cannot be changed** after deployment.

```xml
<!-- Customer_Event__b.object-meta.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <deploymentStatus>Deployed</deploymentStatus>
    <label>Customer Event</label>
    <pluralLabel>Customer Events</pluralLabel>
    <fields>
        <fullName>Account_Id__c</fullName>
        <label>Account ID</label>
        <length>18</length>
        <type>Text</type>
        <required>true</required>
    </fields>
    <fields>
        <fullName>Event_Date__c</fullName>
        <label>Event Date</label>
        <type>DateTime</type>
        <required>true</required>
    </fields>
    <fields>
        <fullName>Event_Type__c</fullName>
        <label>Event Type</label>
        <length>100</length>
        <type>Text</type>
        <required>true</required>
    </fields>
    <fields>
        <fullName>Details__c</fullName>
        <label>Details</label>
        <length>10000</length>
        <type>LongTextArea</type>
        <visibleLines>5</visibleLines>
    </fields>
    <!-- Index: MUST list index fields in order. The composite key defines uniqueness. -->
    <indexes>
        <fullName>CustomerEventIndex</fullName>
        <label>Customer Event Index</label>
        <fields>
            <name>Account_Id__c</name>
            <sortDirection>ASC</sortDirection>
        </fields>
        <fields>
            <name>Event_Date__c</name>
            <sortDirection>DESC</sortDirection>
        </fields>
        <fields>
            <name>Event_Type__c</name>
            <sortDirection>ASC</sortDirection>
        </fields>
    </indexes>
</CustomObject>
```

### SOQL Limitations on Big Objects
Big Object SOQL is **heavily restricted** compared to standard objects:

```apex
// ✅ Supported: Equality filters on ALL index fields from left, range on last
List<Customer_Event__b> events = [
    SELECT Account_Id__c, Event_Date__c, Event_Type__c, Details__c
    FROM Customer_Event__b
    WHERE Account_Id__c = '001XXXXXXXXXXXX'
    AND Event_Date__c > 2024-01-01T00:00:00Z
    ORDER BY Account_Id__c ASC, Event_Date__c DESC  // Must match index order
    LIMIT 200
];

// ❌ NOT supported on Big Objects:
// - Aggregate functions (COUNT, SUM, AVG, etc.)
// - LIKE, NOT IN, != operators
// - OR conditions
// - Subqueries
// - Relationship queries (no dot notation or child subqueries)
// - OFFSET
// - GROUP BY / HAVING
// - ORDER BY on non-index fields
// - Filtering on non-index fields
// - FOR UPDATE
```

**Index query rules:**
- Filters MUST start from the first index field and proceed left-to-right without gaps
- Only the LAST index field in the filter can use a range operator (`>`, `<`, `>=`, `<=`)
- All preceding index fields must use equality (`=`)

### DML on Big Objects
```apex
// Big Objects use Database.insertImmediate() — not standard insert
List<Customer_Event__b> events = new List<Customer_Event__b>();
events.add(new Customer_Event__b(
    Account_Id__c = accountId,
    Event_Date__c = DateTime.now(),
    Event_Type__c = 'Page View',
    Details__c = 'Viewed product catalog'
));

// insertImmediate is asynchronous and does not guarantee immediate availability
Database.insertImmediate(events);

// To upsert: if a record with the same index key exists, it is overwritten
// There is NO update or delete DML — re-insert with same key to overwrite,
// and records cannot be individually deleted (use data retention policies)
```

### Big Object Use Cases

| Use Case | Description |
|---|---|
| **Audit trail** | Store billions of field history records beyond standard 24-month limit |
| **Archiving** | Move old Opportunities, Cases, or custom object data off standard storage |
| **IoT / telemetry** | Store sensor readings, device events, click-stream data |
| **360-degree customer view** | Aggregate interactions across systems into one timeline |
| **Compliance** | Retain immutable records for regulatory requirements |

### Archiving Pattern: Standard Object → Big Object
```apex
// Batch Apex to archive old Cases to a Big Object
public class CaseArchiveBatch implements Database.Batchable<sObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, CaseNumber, Subject, Status, CreatedDate, AccountId
            FROM Case
            WHERE CreatedDate < LAST_N_YEARS:3 AND Status = 'Closed'
        ]);
    }

    public void execute(Database.BatchableContext bc, List<Case> scope) {
        List<Archived_Case__b> archives = new List<Archived_Case__b>();
        for (Case c : scope) {
            archives.add(new Archived_Case__b(
                Account_Id__c = c.AccountId,
                Case_Date__c = c.CreatedDate,
                Case_Number__c = c.CaseNumber,
                Subject__c = c.Subject,
                Status__c = c.Status
            ));
        }
        Database.insertImmediate(archives);
        // Optionally delete the archived originals
        // delete scope;
    }

    public void finish(Database.BatchableContext bc) {
        System.debug('Archive batch complete');
    }
}
```
