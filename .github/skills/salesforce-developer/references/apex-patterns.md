# Apex Patterns & Best Practices Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes before relying on limits, method signatures, or API behavior.

## Table of Contents
1. [Trigger Patterns](#trigger-patterns)
2. [Async Apex](#async-apex)
3. [Error Handling](#error-handling)
4. [Testing Patterns](#testing-patterns)
5. [DML Best Practices](#dml-best-practices)
6. [Collections & sObjects](#collections-and-sobjects)
7. [Dynamic Apex & Schema Describe](#dynamic-apex-and-schema-describe)
8. [JSON Serialization & Deserialization](#json-serialization-and-deserialization)
9. [Wrapper Classes & Inner Classes](#wrapper-classes-and-inner-classes)
10. [Apex Interfaces Reference](#apex-interfaces-reference)
11. [Debugging & Logging](#debugging-and-logging)

---

## Trigger Patterns

### Trigger Handler with Recursion Prevention

Use a `Set<Id>` to track processed records — NOT a static `Boolean`. A Boolean flag blocks the 
trigger from processing any records after the first batch, breaking bulk operations.

```apex
public class AccountTriggerHandler {
    private static Set<Id> processedIds = new Set<Id>();

    public void run() {
        switch on Trigger.operationType {
            when BEFORE_INSERT  { beforeInsert(Trigger.new); }
            when BEFORE_UPDATE  { beforeUpdate(Trigger.new, Trigger.oldMap); }
            when AFTER_INSERT   { afterInsert(getUnprocessedRecords(Trigger.new)); }
            when AFTER_UPDATE   { afterUpdate(getUnprocessedRecords(Trigger.new), Trigger.oldMap); }
            when BEFORE_DELETE  { beforeDelete(Trigger.old); }
            when AFTER_DELETE   { afterDelete(Trigger.old); }
            when AFTER_UNDELETE { afterUndelete(Trigger.new); }
        }
    }

    private List<Account> getUnprocessedRecords(List<Account> records) {
        List<Account> unprocessed = new List<Account>();
        for (Account acc : records) {
            if (!processedIds.contains(acc.Id)) {
                unprocessed.add(acc);
                processedIds.add(acc.Id);
            }
        }
        return unprocessed;
    }

    private void beforeInsert(List<Account> newRecords) {
        // Field defaults, validations, stamp fields
    }

    private void beforeUpdate(List<Account> newRecords, Map<Id, Account> oldMap) {
        // Only process changed records
        List<Account> changed = new List<Account>();
        for (Account acc : newRecords) {
            Account old = oldMap.get(acc.Id);
            if (acc.Industry != old.Industry || acc.AnnualRevenue != old.AnnualRevenue) {
                changed.add(acc);
            }
        }
        if (!changed.isEmpty()) {
            AccountService.recalculateRatings(changed);
        }
    }

    private void afterInsert(List<Account> newRecords) {
        // Create related records, send notifications
    }

    private void afterUpdate(List<Account> newRecords, Map<Id, Account> oldMap) {
        // Cross-object updates, platform events
    }

    private void beforeDelete(List<Account> oldRecords) {
        // Prevent deletion validations
    }

    private void afterDelete(List<Account> oldRecords) {
        // Cleanup related data
    }

    private void afterUndelete(List<Account> newRecords) {
        // Restore related data
    }
}
```

### Trigger Context Variables

| Variable | Type | Description |
|---|---|---|
| `Trigger.new` | `List<sObject>` | New versions of records (insert, update, undelete) |
| `Trigger.old` | `List<sObject>` | Old versions (update, delete) |
| `Trigger.newMap` | `Map<Id, sObject>` | Map of new records by Id (available in before update, after insert, after update, after undelete — not in before insert) |
| `Trigger.oldMap` | `Map<Id, sObject>` | Map of old records by Id |
| `Trigger.operationType` | `System.TriggerOperation` | Enum: BEFORE_INSERT, AFTER_UPDATE, etc. |
| `Trigger.size` | `Integer` | Total records in trigger |

### Field Change Detection Pattern

```apex
// Check if specific fields changed
private List<Account> getChangedRecords(List<Account> newRecs, Map<Id, Account> oldMap,
                                         Set<SObjectField> fieldsToCheck) {
    List<Account> changed = new List<Account>();
    for (Account acc : newRecs) {
        Account old = oldMap.get(acc.Id);
        for (SObjectField field : fieldsToCheck) {
            if (acc.get(field) != old.get(field)) {
                changed.add(acc);
                break;
            }
        }
    }
    return changed;
}

// Usage
Set<SObjectField> watchFields = new Set<SObjectField>{
    Account.Industry, Account.AnnualRevenue, Account.Rating
};
List<Account> changed = getChangedRecords(Trigger.new, Trigger.oldMap, watchFields);
```

---

## Async Apex

### Future Methods
Best for simple callouts or mixed DML isolation. Cannot chain or monitor.

**Parameter restrictions:** `@future` methods accept ONLY primitive types and collections of
primitives (`List<Id>`, `Set<String>`, etc.). No sObjects, no custom classes.

```apex
public with sharing class AccountCalloutService {
    @future(callout=true)
    public static void syncToExternalSystem(Set<Id> accountIds) {
        List<Account> accounts = [
            SELECT Id, Name, BillingCity FROM Account
            WHERE Id IN :accountIds
            WITH SECURITY_ENFORCED
        ];
        // Make HTTP callout
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:MyNamedCredential/accounts');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(accounts));
        Http http = new Http();
        HttpResponse res = http.send(req);
    }
}
```

**@future Key Rules:**
| Rule | Detail |
|---|---|
| Parameters | Primitives and collections of primitives only — no sObjects |
| Return type | Must be `void` |
| Chaining | Cannot call a future from a future |
| Monitoring | No job ID returned — cannot track individual calls |
| Execution order | NOT guaranteed FIFO |
| Max per txn | 50 (sync context); 0 from another future context |
| Gov limits | Async limits: 200 SOQL, 60s CPU, 12MB heap |
| Testing | `Test.startTest()`/`Test.stopTest()` forces synchronous execution |

**When @future is still appropriate:**
- Simple fire-and-forget callouts triggered by DML
- MIXED_DML isolation (insert setup + non-setup objects)
- When you don't need job monitoring or chaining
- When parameter data is simple (IDs or strings)

### Queueable Apex
Preferred over @future for complex async. Supports chaining, object parameters, and monitoring.

```apex
public class AccountProcessingJob implements Queueable, Database.AllowsCallouts {
    private List<Account> accounts;
    private Integer depth;
    private static final Integer BATCH_SIZE = 50;

    public AccountProcessingJob(List<Account> accounts, Integer depth) {
        this.accounts = accounts;
        this.depth = depth;
    }

    public void execute(QueueableContext context) {
        // Get the job ID for monitoring
        Id jobId = context.getJobId();
        System.debug('Executing Queueable job: ' + jobId + ' at depth: ' + depth);

        // Process a batch of accounts
        Integer processCount = Math.min(BATCH_SIZE, accounts.size());
        List<Account> toUpdate = new List<Account>();
        for (Integer i = 0; i < processCount; i++) {
            Account acc = accounts[i];
            acc.Description = 'Processed on ' + Datetime.now().format();
            toUpdate.add(acc);
        }
        if (!toUpdate.isEmpty()) {
            update toUpdate;
        }

        // Chain another job for remaining accounts (limit: 1 child job per execution in async)
        List<Account> remainingAccounts = new List<Account>();
        for (Integer i = processCount; i < accounts.size(); i++) {
            remainingAccounts.add(accounts[i]);
        }
        if (depth < 5 && !remainingAccounts.isEmpty()) {
            System.enqueueJob(new AccountProcessingJob(remainingAccounts, depth + 1));
        }
    }
}

// Enqueue: Id jobId = System.enqueueJob(new AccountProcessingJob(accounts, 0));
```

### Transaction Finalizers (API v54.0+)
Attach a finalizer to a Queueable job to execute cleanup logic after the job completes
(whether success or failure). Essential for retry patterns.

```apex
public class RetryableJob implements Queueable {
    private Integer retryCount;
    private List<Account> records;

    public RetryableJob(List<Account> records, Integer retryCount) {
        this.records = records;
        this.retryCount = retryCount;
    }

    public void execute(QueueableContext context) {
        // Attach the finalizer FIRST
        System.attachFinalizer(new RetryFinalizer(records, retryCount));

        // Business logic that might fail
        update records;
    }
}

public class RetryFinalizer implements Finalizer {
    private List<Account> records;
    private Integer retryCount;
    private static final Integer MAX_RETRIES = 3;

    public RetryFinalizer(List<Account> records, Integer retryCount) {
        this.records = records;
        this.retryCount = retryCount;
    }

    public void execute(FinalizerContext ctx) {
        Id parentJobId = ctx.getAsyncApexJobId();
        switch on ctx.getResult() {
            when SUCCESS {
                System.debug('Job ' + parentJobId + ' succeeded');
            }
            when UNHANDLED_EXCEPTION {
                String errorMsg = ctx.getException().getMessage();
                System.debug(LoggingLevel.ERROR, 'Job ' + parentJobId +
                    ' failed: ' + errorMsg);
                // Retry if under max attempts
                if (retryCount < MAX_RETRIES) {
                    System.enqueueJob(new RetryableJob(records, retryCount + 1));
                }
            }
        }
    }
}
```

### Async Options (API v60.0+)
Delay or schedule Queueable execution with `AsyncOptions`.

```apex
// Delay execution by a minimum of 5 minutes
AsyncOptions options = new AsyncOptions();
options.minimumQueueableDelayInMinutes = 5;
System.enqueueJob(new AccountProcessingJob(accounts, 0), options);

// Set max depth for auto-chaining (avoids MAX_STACK_DEPTH errors)
options.maximumQueueableStackDepth = 10;
```

### Queueable Monitoring

```apex
// Query the status of Queueable/Batch/Future jobs
List<AsyncApexJob> jobs = [
    SELECT Id, Status, JobType, ApexClassId, ApexClass.Name,
           NumberOfErrors, MethodName, CreatedDate, CompletedDate,
           TotalJobItems, JobItemsProcessed, ExtendedStatus
    FROM AsyncApexJob
    WHERE JobType IN ('Queueable', 'BatchApex', 'Future')
    AND CreatedDate = TODAY
    ORDER BY CreatedDate DESC
    LIMIT 50
];
```

### @future vs Queueable Decision Guide

| Criteria | @future | Queueable |
|---|---|---|
| Parameter types | Primitives only | Any serializable type (sObjects, custom classes) |
| Return / monitor | No job ID | Returns `Id` from `System.enqueueJob()` |
| Chaining | Cannot chain | Can chain (1 child from async, 50 from sync) |
| Callouts | `@future(callout=true)` | Implement `Database.AllowsCallouts` |
| Retry on failure | Manual | Transaction Finalizers (`System.Finalizer`) |
| Delayed execution | Not possible | `AsyncOptions.minimumQueueableDelayInMinutes` |
| Complexity | Simple | Medium — more boilerplate but more powerful |
| **Recommendation** | Legacy; use for simple cases | **Preferred for all new async work** |

### Batch Apex
For processing large data volumes (millions of records).

```apex
public class AccountCleanupBatch implements Database.Batchable<sObject>,
        Database.Stateful, Database.AllowsCallouts, Database.RaisesPlatformEvents {
    private Integer recordsProcessed = 0;
    private List<String> errors = new List<String>();

    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, Name, LastActivityDate
            FROM Account
            WHERE LastActivityDate < LAST_N_YEARS:2
        ]);
    }

    public void execute(Database.BatchableContext bc, List<Account> scope) {
        // Each execute() gets a fresh set of governor limits
        try {
            for (Account acc : scope) {
                acc.Rating = 'Cold';
            }
            Database.SaveResult[] results = Database.update(scope, false);
            for (Integer i = 0; i < results.size(); i++) {
                if (!results[i].isSuccess()) {
                    errors.add('Record ' + scope[i].Id + ': ' +
                        results[i].getErrors()[0].getMessage());
                }
            }
            recordsProcessed += scope.size();
        } catch (Exception e) {
            // If execute() throws an unhandled exception, that batch is marked failed
            // but remaining batches CONTINUE processing (unless Database.RaisesPlatformEvents
            // is implemented, which publishes BatchApexErrorEvent)
            System.debug(LoggingLevel.ERROR, 'Batch execute error: ' + e.getMessage());
        }
    }

    public void finish(Database.BatchableContext bc) {
        // Get the job status
        AsyncApexJob job = [
            SELECT Id, Status, NumberOfErrors, TotalJobItems, JobItemsProcessed
            FROM AsyncApexJob
            WHERE Id = :bc.getJobId()
        ];
        System.debug('Processed ' + recordsProcessed + ' records. Errors: ' + errors.size());

        // Chain next batch if needed
        // Database.executeBatch(new NextBatch(), 200);

        // Or send a completion notification
        if (!errors.isEmpty()) {
            Messaging.SingleEmailMessage mail = new Messaging.SingleEmailMessage();
            mail.setToAddresses(new String[]{'admin@company.com'});
            mail.setSubject('Batch Job Complete with Errors');
            mail.setPlainTextBody('Errors:\n' + String.join(errors, '\n'));
            Messaging.sendEmail(new Messaging.SingleEmailMessage[]{mail});
        }
    }
}

// Execute with custom scope size (default 200, max 2000):
Id batchId = Database.executeBatch(new AccountCleanupBatch(), 200);
```

### QueryLocator vs Iterable in Batch Apex

| Feature | `Database.QueryLocator` | `Iterable<sObject>` |
|---|---|---|
| Max records | 50 million | 50,000 (standard SOQL limit) |
| Use when | Standard SOQL can express the query | Need complex filtering, in-memory joins, or non-SOQL data |
| Return from | `start()` returns `Database.QueryLocator` | `start()` returns `Iterable<sObject>` |
| Performance | Optimized for large datasets | Slower; loads all into memory |

```apex
// Iterable<sObject> example — use when query logic is too complex for SOQL
public class CustomIterableBatch implements Database.Batchable<sObject> {
    public Iterable<sObject> start(Database.BatchableContext bc) {
        // Custom logic to produce the list (max 50k records)
        List<Account> accounts = [SELECT Id, Name FROM Account WHERE Industry = 'Technology'];
        List<Account> filtered = new List<Account>();
        for (Account acc : accounts) {
            if (customLogicCheck(acc)) {
                filtered.add(acc);
            }
        }
        return filtered;
    }

    public void execute(Database.BatchableContext bc, List<sObject> scope) { /* ... */ }
    public void finish(Database.BatchableContext bc) { /* ... */ }
    private Boolean customLogicCheck(Account acc) { return true; }
}
```

### Batch Apex Key Facts

| Fact | Detail |
|---|---|
| Default scope | 200 records per `execute()` |
| Max scope | 2,000 (set in `Database.executeBatch(instance, scopeSize)`) |
| Concurrent limit | 5 active batch jobs per org |
| Flex Queue | Up to 100 additional jobs queued (wait for an active slot) |
| `Database.Stateful` | Required to maintain instance variable state across execute() calls |
| `Database.AllowsCallouts` | Required for HTTP callouts from execute() |
| `Database.RaisesPlatformEvents` | Publishes `BatchApexErrorEvent` on execute() failures |
| `System.scheduleBatch()` | Schedule a batch to run once at a future time (no Schedulable needed) |
| Gov limits per execute() | Each execute() gets its own transaction and fresh governor limits |
| finish() | Runs once after all execute() calls; use for chaining, email, cleanup |
| Testing | `Test.startTest()`/`Test.stopTest()` executes batch synchronously (1 execute()) |

### Scheduled Apex

```apex
public class WeeklyAccountReview implements Schedulable {
    public void execute(SchedulableContext sc) {
        Database.executeBatch(new AccountCleanupBatch(), 200);
    }
}

// Schedule: CRON expression — every Monday at 6 AM
// String cronExp = '0 0 6 ? * MON';
// Id jobId = System.schedule('Weekly Account Review', cronExp, new WeeklyAccountReview());
```

### CRON Expression Reference
CRON expressions have 7 fields: `Seconds Minutes Hours Day-of-Month Month Day-of-Week Year`

| Field | Allowed Values | Special Characters |
|---|---|---|
| Seconds | 0-59 | `, - * /` |
| Minutes | 0-59 | `, - * /` |
| Hours | 0-23 | `, - * /` |
| Day-of-Month | 1-31 | `, - * ? / L W` |
| Month | 1-12 or JAN-DEC | `, - * /` |
| Day-of-Week | 1-7 or SUN-SAT | `, - * ? / L #` |
| Year | (optional) | `, - * /` |

**Common CRON examples:**
```apex
// Daily at midnight
System.schedule('Daily Midnight', '0 0 0 * * ?', new MySchedulable());

// Every weekday at 8 AM
System.schedule('Weekday 8am', '0 0 8 ? * MON-FRI', new MySchedulable());

// First day of every month at 6 AM
System.schedule('Monthly', '0 0 6 1 * ?', new MySchedulable());

// Every 5 minutes (schedule 12 jobs, one for each 5-min slot in the hour)
for (Integer i = 0; i < 60; i += 5) {
    System.schedule('Every5min_' + i, '0 ' + i + ' * * * ?', new MySchedulable());
}

// Last day of every month at 11 PM
System.schedule('MonthEnd', '0 0 23 L * ?', new MySchedulable());

// Second Monday of every month at 9 AM
System.schedule('2ndMonday', '0 0 9 ? * MON#2', new MySchedulable());
```

### Scheduled Apex Management

```apex
// Monitor scheduled jobs
List<CronTrigger> scheduledJobs = [
    SELECT Id, CronJobDetail.Name, State, NextFireTime, PreviousFireTime,
           TimesTriggered, CronExpression
    FROM CronTrigger
    WHERE CronJobDetail.JobType = '7'  // 7 = Scheduled Apex
    ORDER BY NextFireTime
];

// Schedule a batch directly (no Schedulable class needed)
// Runs once at the specified time
Id batchJobId = System.scheduleBatch(
    new AccountCleanupBatch(),   // Batchable instance
    'One-Time Cleanup',           // Job name
    60,                           // Minutes from now
    200                           // Scope size (optional)
);

// Abort a scheduled job
System.abortJob(jobId);
```

**Scheduled Apex limits:**
- Max 100 scheduled jobs per org (5 in Developer Edition)
- Minimum interval: 1 hour via Setup UI, but CRON allows finer (using multiple jobs)
- Cannot guarantee exact execution time — runs at or after the scheduled time
- Scheduled Apex runs in async governor limits context

### Platform Events

```apex
// Publishing
List<Order_Event__e> events = new List<Order_Event__e>();
events.add(new Order_Event__e(
    Order_Id__c = order.Id,
    Status__c = 'Completed'
));
List<Database.SaveResult> results = EventBus.publish(events);

// Subscribing via trigger
trigger OrderEventTrigger on Order_Event__e (after insert) {
    List<Task> tasks = new List<Task>();
    for (Order_Event__e event : Trigger.new) {
        if (event.Status__c == 'Completed') {
            tasks.add(new Task(
                Subject = 'Follow up on order ' + event.Order_Id__c,
                Status = 'Open'
            ));
        }
    }
    insert tasks;
}
```

---

## Error Handling

### Apex Error Handling Pattern

```apex
public with sharing class AccountService {
    public static List<Database.SaveResult> safeUpdate(List<Account> accounts) {
        List<Database.SaveResult> results = Database.update(accounts, false); // allOrNone=false
        List<String> errors = new List<String>();

        for (Integer i = 0; i < results.size(); i++) {
            if (!results[i].isSuccess()) {
                for (Database.Error err : results[i].getErrors()) {
                    errors.add('Record ' + accounts[i].Name + ': ' +
                              err.getStatusCode() + ' - ' + err.getMessage());
                }
            }
        }

        if (!errors.isEmpty()) {
            System.debug(LoggingLevel.ERROR, 'Update errors: ' + String.join(errors, '\n'));
        }
        return results;
    }
}
```

### AuraHandledException for LWC/Aura

```apex
@AuraEnabled
public static Account getAccount(Id accountId) {
    try {
        List<Account> accounts = [
            SELECT Id, Name, Industry
            FROM Account
            WHERE Id = :accountId
            WITH SECURITY_ENFORCED
        ];
        if (accounts.isEmpty()) {
            throw new AuraHandledException('Account not found');
        }
        return accounts[0];
    } catch (System.QueryException e) {
        throw new AuraHandledException('Insufficient access to Account records');
    } catch (Exception e) {
        throw new AuraHandledException(e.getMessage());
    }
}
```

---

## Testing Patterns

### Test Data Factory

```apex
@IsTest
public class TestDataFactory {
    public static List<Account> createAccounts(Integer count, Boolean doInsert) {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accounts.add(new Account(
                Name = 'Test Account ' + i,
                Industry = 'Technology',
                BillingCity = 'San Francisco',
                BillingState = 'CA'
            ));
        }
        if (doInsert) insert accounts;
        return accounts;
    }

    public static List<Contact> createContacts(List<Account> accounts, Integer perAccount,
                                                Boolean doInsert) {
        List<Contact> contacts = new List<Contact>();
        for (Account acc : accounts) {
            for (Integer i = 0; i < perAccount; i++) {
                contacts.add(new Contact(
                    AccountId = acc.Id,
                    FirstName = 'Test',
                    LastName = 'Contact ' + i,
                    Email = 'test' + i + '@' + acc.Name.replaceAll(' ', '') + '.com'
                ));
            }
        }
        if (doInsert) insert contacts;
        return contacts;
    }
}
```

### Testing Callouts with Mocks

```apex
@IsTest
private class AccountCalloutServiceTest {
    private class MockHttpResponse implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setBody('{"status":"success"}');
            return res;
        }
    }

    @IsTest
    static void testCallout() {
        Test.setMock(HttpCalloutMock.class, new MockHttpResponse());
        Account acc = new Account(Name = 'Test');
        insert acc;

        Test.startTest();
        AccountCalloutService.syncToExternalSystem(new Set<Id>{ acc.Id });
        Test.stopTest();

        // Assert expected behavior
    }
}
```

### Testing with System.runAs

```apex
@IsTest
static void testWithRestrictedUser() {
    Profile standardProfile = [SELECT Id FROM Profile WHERE Name = 'Standard User'];
    User testUser = new User(
        Alias = 'tuser',
        Email = 'testuser@test.org',
        EmailEncodingKey = 'UTF-8',
        LastName = 'Testing',
        LanguageLocaleKey = 'en_US',
        LocaleSidKey = 'en_US',
        ProfileId = standardProfile.Id,
        TimeZoneSidKey = 'America/Los_Angeles',
        Username = 'testuser' + DateTime.now().getTime() + '@test.org'
    );
    insert testUser;

    System.runAs(testUser) {
        Test.startTest();
        // Test code runs as restricted user
        Test.stopTest();
    }
}
```

---

## DML Best Practices

### Partial Success with Error Logging

```apex
Database.SaveResult[] results = Database.insert(records, false);
for (Integer i = 0; i < results.size(); i++) {
    if (!results[i].isSuccess()) {
        for (Database.Error err : results[i].getErrors()) {
            System.debug(LoggingLevel.ERROR,
                'Failed: ' + records[i] + ' Error: ' + err.getMessage());
        }
    }
}
```

### Upsert with External ID

```apex
List<Account> accounts = new List<Account>();
accounts.add(new Account(External_Id__c = 'EXT-001', Name = 'Upserted Account'));
Database.UpsertResult[] results = Database.upsert(accounts, Account.External_Id__c, false);
```

### MIXED_DML_OPERATION Avoidance

```apex
// Setup objects (User, Group, PermissionSet) can't be mixed with non-setup DML
// Solution: Use @future or Queueable
@future
public static void assignPermissionSet(Id userId, Id permSetId) {
    insert new PermissionSetAssignment(AssigneeId = userId, PermissionSetId = permSetId);
}
```

---

## Collections and sObjects

### Dynamic sObject Operations

```apex
// Dynamic field access — get/put fields by string name
sObject record = [SELECT Id, Name FROM Account LIMIT 1];
String name = (String) record.get('Name');
record.put('Description', 'Updated dynamically');

// Dynamic SOQL
String objectName = 'Account';
String query = 'SELECT Id, Name FROM ' + String.escapeSingleQuotes(objectName) + ' LIMIT 10';
List<sObject> records = Database.query(query);

// Determine sObject type at runtime
SObjectType sobjType = record.getSObjectType();
String typeName = sobjType.getDescribe().getName(); // 'Account'
```

### Schema Describe — Dynamic Metadata Inspection

```apex
// Get a map of ALL sObjects in the org (expensive — cache the result)
Map<String, SObjectType> globalDescribe = Schema.getGlobalDescribe();
SObjectType accountType = globalDescribe.get('Account');

// Describe an sObject
DescribeSObjectResult accountDescribe = Account.SObjectType.getDescribe();
String label = accountDescribe.getLabel();               // 'Account'
String pluralLabel = accountDescribe.getLabelPlural();    // 'Accounts'
Boolean isCustom = accountDescribe.isCustom();            // false
Boolean isAccessible = accountDescribe.isAccessible();    // CRUD check

// Describe all fields on an sObject
Map<String, SObjectField> fieldMap = accountDescribe.fields.getMap();
for (String fieldName : fieldMap.keySet()) {
    DescribeFieldResult fieldDesc = fieldMap.get(fieldName).getDescribe();
    System.debug(fieldDesc.getLabel() + ' (' + fieldDesc.getType() + ')');
}

// Describe a specific field
DescribeFieldResult nameField = Account.Name.getDescribe();
Boolean isRequired = !nameField.isNillable();
Boolean isFilterable = nameField.isFilterable();
Integer maxLength = nameField.getLength();
DisplayType fieldType = nameField.getType();  // STRING, PICKLIST, REFERENCE, etc.
```

### Dynamic sObject Instantiation

```apex
// Create an sObject instance dynamically by type name
SObjectType targetType = Schema.getGlobalDescribe().get('Account');
sObject newRecord = targetType.newSObject();
newRecord.put('Name', 'Dynamic Account');
insert newRecord;

// Alternatively, use Type.forName()
Type t = Type.forName('Account');
sObject record2 = (sObject) t.newInstance();
record2.put('Name', 'Another Dynamic Account');
insert record2;
```

### Generic Trigger Handler Using sObject

```apex
// A generic trigger handler that works with any sObject type
public virtual class GenericTriggerHandler {
    public void run() {
        switch on Trigger.operationType {
            when BEFORE_INSERT  { beforeInsert(Trigger.new); }
            when BEFORE_UPDATE  { beforeUpdate(Trigger.new, Trigger.oldMap); }
            when AFTER_INSERT   { afterInsert(Trigger.new); }
            when AFTER_UPDATE   { afterUpdate(Trigger.new, Trigger.oldMap); }
            when BEFORE_DELETE  { beforeDelete(Trigger.old); }
            when AFTER_DELETE   { afterDelete(Trigger.old); }
            when AFTER_UNDELETE { afterUndelete(Trigger.new); }
        }
    }

    // Subclasses override these methods
    protected virtual void beforeInsert(List<sObject> newRecords) {}
    protected virtual void beforeUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap) {}
    protected virtual void afterInsert(List<sObject> newRecords) {}
    protected virtual void afterUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap) {}
    protected virtual void beforeDelete(List<sObject> oldRecords) {}
    protected virtual void afterDelete(List<sObject> oldRecords) {}
    protected virtual void afterUndelete(List<sObject> newRecords) {}

    // Utility: detect changed fields on any sObject
    protected List<sObject> getChangedRecords(List<sObject> newRecs, Map<Id, sObject> oldMap,
                                               Set<SObjectField> fields) {
        List<sObject> changed = new List<sObject>();
        for (sObject rec : newRecs) {
            sObject old = oldMap.get(rec.Id);
            for (SObjectField f : fields) {
                if (rec.get(f) != old.get(f)) {
                    changed.add(rec);
                    break;
                }
            }
        }
        return changed;
    }
}
```

### Dynamic Picklist Values

```apex
// Get picklist values for a field at runtime
List<Schema.PicklistEntry> entries =
    Account.Industry.getDescribe().getPicklistValues();
List<String> activeValues = new List<String>();
for (Schema.PicklistEntry entry : entries) {
    if (entry.isActive()) {
        activeValues.add(entry.getValue());
    }
}
```

### Type Casting and instanceof

```apex
// Safely cast generic sObjects to specific types
sObject record = [SELECT Id, Name FROM Account LIMIT 1];
if (record instanceof Account) {
    Account acc = (Account) record;
    System.debug('Account name: ' + acc.Name);
}

// Polymorphic handling of different sObject types
public static void processRecords(List<sObject> records) {
    if (records.isEmpty()) return;
    String objectType = records[0].getSObjectType().getDescribe().getName();
    switch on objectType {
        when 'Account' { processAccounts((List<Account>) records); }
        when 'Contact' { processContacts((List<Contact>) records); }
        when else { System.debug('Unhandled type: ' + objectType); }
    }
}
```

### Efficient Map Operations

```apex
// Build maps for O(1) lookups instead of nested loops
Map<Id, Account> accountMap = new Map<Id, Account>(
    [SELECT Id, Name FROM Account WHERE Id IN :accountIds]
);

// Group records by field value
Map<String, List<Account>> byIndustry = new Map<String, List<Account>>();
for (Account acc : accounts) {
    if (!byIndustry.containsKey(acc.Industry)) {
        byIndustry.put(acc.Industry, new List<Account>());
    }
    byIndustry.get(acc.Industry).add(acc);
}
```

### Custom Metadata Type Access

```apex
// Custom metadata is cached and doesn't count against SOQL limits
List<My_Config__mdt> configs = My_Config__mdt.getAll().values();

// Or by developer name
My_Config__mdt config = My_Config__mdt.getInstance('Default_Config');
String endpoint = config.Endpoint__c;
Boolean isActive = config.Is_Active__c;
```

---

## JSON Serialization & Deserialization

### JSON.serialize() and JSON.deserialize()

```apex
// Serialize an sObject to JSON
Account acc = [SELECT Id, Name, Industry FROM Account LIMIT 1];
String jsonStr = JSON.serialize(acc);
// Output: {"attributes":{"type":"Account","url":"/services/data/..."},"Id":"001...","Name":"Acme","Industry":"Technology"}

// Serialize a custom class
String jsonStr = JSON.serialize(new MyWrapper('hello', 42));

// Pretty-print for debugging
String prettyJson = JSON.serializePretty(acc);

// Suppress null fields (API v59.0+)
String compactJson = JSON.serialize(acc, true); // suppressApexObjectNulls = true
```

### JSON.deserialize() — Typed Deserialization

```apex
// Deserialize JSON into a specific Apex type
String jsonStr = '{"name":"Acme","industry":"Technology","revenue":1000000}';
AccountWrapper wrapper = (AccountWrapper) JSON.deserialize(jsonStr, AccountWrapper.class);

public class AccountWrapper {
    public String name;
    public String industry;
    public Decimal revenue;
}

// Deserialize into sObject (works for standard fields)
String accJson = '{"Name":"Acme","Industry":"Technology"}';
Account acc = (Account) JSON.deserialize(accJson, Account.class);
```

### JSON.deserializeUntyped() — Dynamic / Unknown Structure

```apex
// Parse JSON when the structure isn't known at compile time
String jsonStr = '{"status":"success","data":{"count":42,"items":["a","b","c"]}}';
Map<String, Object> root = (Map<String, Object>) JSON.deserializeUntyped(jsonStr);

String status = (String) root.get('status');
Map<String, Object> data = (Map<String, Object>) root.get('data');
Integer count = (Integer) data.get('count');
List<Object> items = (List<Object>) data.get('items');
String firstItem = (String) items[0];
```

### JSON.Generator — Build JSON Programmatically

```apex
// Use when you need precise control over the JSON output
JSONGenerator gen = JSON.createGenerator(true); // true = pretty-print
gen.writeStartObject();
gen.writeStringField('orderId', order.Id);
gen.writeNumberField('total', order.TotalAmount);
gen.writeBooleanField('isPriority', true);
gen.writeFieldName('lineItems');
gen.writeStartArray();
for (OrderItem item : items) {
    gen.writeStartObject();
    gen.writeStringField('product', item.Product2.Name);
    gen.writeNumberField('quantity', item.Quantity);
    gen.writeEndObject();
}
gen.writeEndArray();
gen.writeEndObject();
String result = gen.getAsString();
```

### JSONParser — Streaming Event-Based Parsing

```apex
// Use for large JSON payloads to avoid heap issues
String jsonStr = response.getBody();
JSONParser parser = JSON.createParser(jsonStr);

List<String> names = new List<String>();
while (parser.nextToken() != null) {
    if (parser.getCurrentToken() == JSONToken.FIELD_NAME &&
        parser.getText() == 'name') {
        parser.nextToken(); // Move to the value
        names.add(parser.getText());
    }
}
```

### @JsonAccess — Control Serialization Scope

```apex
// Control who can serialize/deserialize your class
@JsonAccess(serializable='always' deserializable='always')
public class PublicResult {
    public String message;
    public Boolean success;
}

// Options: 'never' | 'samePackage' | 'sameNamespace' | 'always'
// Use 'always' for Agentforce action return types and LWC @AuraEnabled
// Use 'sameNamespace' for internal package types
```

### JSON Serialization Caveats

| Scenario | Behavior |
|---|---|
| Date fields | Serialized as `"2024-03-15"` (ISO 8601) |
| DateTime fields | Serialized as `"2024-03-15T10:30:00.000Z"` (UTC) |
| Blob fields | Serialized as Base64-encoded string |
| sObject serialization | Includes `"attributes":{"type":"Account"}` wrapper |
| Null fields | Included by default; use `suppressApexObjectNulls` to omit |
| Reserved Apex words in keys | Use `JSON.deserializeUntyped()` and map manually |
| Circular references | Throws `System.JSONException` |

---

## Wrapper Classes & Inner Classes

### @AuraEnabled Wrapper for LWC

```apex
// Return structured data (non-sObject) to LWC
public with sharing class OpportunityController {
    @AuraEnabled(cacheable=true)
    public static DashboardData getDashboard() {
        DashboardData data = new DashboardData();
        data.totalOpps = [SELECT COUNT() FROM Opportunity WHERE IsClosed = false];
        data.totalValue = 0;
        for (AggregateResult ar : [
            SELECT SUM(Amount) total FROM Opportunity WHERE IsClosed = false
        ]) {
            data.totalValue = (Decimal) ar.get('total');
        }
        data.recentOpps = [
            SELECT Id, Name, Amount, StageName, CloseDate
            FROM Opportunity
            WHERE IsClosed = false
            WITH SECURITY_ENFORCED
            ORDER BY CloseDate ASC LIMIT 10
        ];
        return data;
    }

    // Wrapper — all fields must be @AuraEnabled for LWC access
    public class DashboardData {
        @AuraEnabled public Integer totalOpps;
        @AuraEnabled public Decimal totalValue;
        @AuraEnabled public List<Opportunity> recentOpps;
    }
}
```

### DataTable Wrapper (for lightning-datatable)

```apex
public class DataTableService {
    @AuraEnabled(cacheable=true)
    public static List<ContactRow> getContactRows(Id accountId) {
        List<ContactRow> rows = new List<ContactRow>();
        for (Contact c : [
            SELECT Id, Name, Email, Phone, Account.Name
            FROM Contact WHERE AccountId = :accountId
            WITH SECURITY_ENFORCED
        ]) {
            rows.add(new ContactRow(c));
        }
        return rows;
    }

    // Flatten relationship fields for datatable columns
    public class ContactRow {
        @AuraEnabled public Id contactId;
        @AuraEnabled public String name;
        @AuraEnabled public String email;
        @AuraEnabled public String phone;
        @AuraEnabled public String accountName;

        public ContactRow(Contact c) {
            this.contactId = c.Id;
            this.name = c.Name;
            this.email = c.Email;
            this.phone = c.Phone;
            this.accountName = c.Account?.Name;
        }
    }
}
```

### Sortable Wrapper (Comparable Interface)

```apex
// Make a wrapper class sortable
public class ScoredAccount implements Comparable {
    public Account account;
    public Decimal score;

    public ScoredAccount(Account acc, Decimal score) {
        this.account = acc;
        this.score = score;
    }

    // Sort descending by score
    public Integer compareTo(Object other) {
        ScoredAccount otherSA = (ScoredAccount) other;
        if (this.score > otherSA.score) return -1;
        if (this.score < otherSA.score) return 1;
        return 0;
    }
}

// Usage:
List<ScoredAccount> scored = new List<ScoredAccount>();
scored.add(new ScoredAccount(acc1, 85.0));
scored.add(new ScoredAccount(acc2, 92.5));
scored.sort(); // Sorted by score descending
```

### When to Use Wrappers vs sObjects vs Maps

| Return Type | Use When |
|---|---|
| `sObject` / `List<sObject>` | Standard record data — LDS and wire adapters work natively |
| Wrapper class | Need computed fields, flattened relationships, or non-sObject data |
| `Map<String, Object>` | Truly dynamic structures — avoid in favor of typed wrappers |

---

## Apex Interfaces Reference

### Key Platform Interfaces

| Interface | Purpose | Where Used |
|---|---|---|
| `Database.Batchable<sObject>` | Batch processing (start/execute/finish) | Batch Apex |
| `Database.Stateful` | Maintain state across batch execute() calls | Batch Apex |
| `Database.AllowsCallouts` | Allow HTTP callouts from async context | Batch, Queueable |
| `Database.RaisesPlatformEvents` | Publish `BatchApexErrorEvent` on failure | Batch Apex |
| `Queueable` | Async job with chaining and complex params | Queueable Apex |
| `Schedulable` | Scheduled job execution | Scheduled Apex |
| `System.Finalizer` | Cleanup/retry after Queueable completion | Transaction Finalizers |
| `Comparable` | Custom sort order for `List.sort()` | Wrapper classes |
| `Callable` | Loosely-coupled Apex invocation by name | Package extensibility |
| `HttpCalloutMock` | Mock HTTP responses in tests | Test classes |
| `WebServiceMock` | Mock SOAP callout responses in tests | Test classes |
| `Messaging.InboundEmailHandler` | Process inbound emails | Email Services |
| `Auth.RegistrationHandler` | Provision users on SSO login | Auth Providers |

### Custom Interface Pattern

```apex
// Define a custom interface
public interface ITriggerHandler {
    void beforeInsert(List<sObject> newRecords);
    void beforeUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap);
    void afterInsert(List<sObject> newRecords);
    void afterUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap);
}

// Implement the interface
public class AccountTriggerHandler implements ITriggerHandler {
    public void beforeInsert(List<sObject> newRecords) {
        List<Account> accounts = (List<Account>) newRecords;
        // Business logic
    }
    public void beforeUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap) { /* ... */ }
    public void afterInsert(List<sObject> newRecords) { /* ... */ }
    public void afterUpdate(List<sObject> newRecords, Map<Id, sObject> oldMap) { /* ... */ }
}
```

### Callable Interface — Loosely-Coupled Invocation

```apex
// Callable allows invoking Apex by class name and method name (string-based)
// Useful for managed packages, plugin architectures, and cross-namespace calls
public class MyCallableService implements Callable {
    public Object call(String action, Map<String, Object> args) {
        switch on action {
            when 'processAccount' {
                Id accountId = (Id) args.get('accountId');
                return processAccount(accountId);
            }
            when 'getConfig' {
                return getConfig();
            }
            when else {
                throw new IllegalArgumentException('Unknown action: ' + action);
            }
        }
    }

    private String processAccount(Id accountId) { return 'Processed'; }
    private Map<String, String> getConfig() { return new Map<String, String>(); }
}

// Invoke without compile-time dependency:
Callable service = (Callable) Type.forName('MyCallableService').newInstance();
Object result = service.call('processAccount', new Map<String, Object>{
    'accountId' => someId
});
```

### Interface vs Abstract vs Virtual Class

| Feature | `interface` | `abstract class` | `virtual class` |
|---|---|---|---|
| Method bodies | None (signatures only) | Can have concrete + abstract methods | All methods have bodies |
| Multiple inheritance | A class can implement multiple | Can extend only one | Can extend only one |
| Instance variables | None | Yes | Yes |
| Constructors | None | Yes | Yes |
| Use when | Defining a contract multiple classes follow | Shared behavior + enforced method override | Default behavior with optional override |

---

## Debugging & Logging

### System.debug Best Practices

```apex
// Always include LoggingLevel — makes log filtering effective
System.debug(LoggingLevel.ERROR, 'Critical failure: ' + e.getMessage());
System.debug(LoggingLevel.WARN, 'Approaching limit: ' + Limits.getQueries() + ' SOQL queries');
System.debug(LoggingLevel.INFO, 'Processing ' + records.size() + ' records');
System.debug(LoggingLevel.DEBUG, 'Record values: ' + JSON.serializePretty(record));
System.debug(LoggingLevel.FINE, 'Loop iteration: ' + i);

// Structured debug pattern — tag for easy filtering
System.debug(LoggingLevel.DEBUG, '[AccountService.updateRatings] ' +
    'Input: ' + accounts.size() + ' accounts');
```

### Debug Log Levels

| Level | Use For |
|---|---|
| `ERROR` | Exceptions, failures, data integrity issues |
| `WARN` | Approaching limits, unexpected but recoverable conditions |
| `INFO` | High-level process flow (method entry/exit, record counts) |
| `DEBUG` | Variable values, intermediate state |
| `FINE` | Loop iterations, detailed trace |
| `FINER` / `FINEST` | Maximum verbosity — rarely needed |

### Debug Log Categories (Setup → Debug Logs)

| Category | Controls |
|---|---|
| Apex Code | System.debug output, method entry/exit |
| Database | SOQL/SOSL queries, DML operations, query plans |
| Callout | HTTP callouts, SOAP calls |
| Validation | Validation rule evaluation |
| Workflow | Workflow rules, process builder (legacy) |
| System | System methods, governor limits consumed |
| Visualforce | VF page processing |
| NBA | Einstein Next Best Action |

### Trace Flags
Trace flags control which users/processes generate debug logs and at what detail level.

```
Setup → Debug Logs → New Trace Flag
  ├── User Trace Flag — logs for a specific user
  ├── Automated Process Trace Flag — logs for automated processes (triggers, batch)
  └── Platform Event Trace Flag — logs for platform event triggers
```

- Trace flags expire after a set duration (max 24 hours)
- Debug logs max size: **20 MB** per log (auto-truncated after that)
- Max retained logs: **1,000 MB** per org (oldest purged first)

### Apex Replay Debugger (VS Code)

```bash
# 1. Enable replay-enabled debug logs
sf apex log tail --color --debug-level REPLAY

# 2. Run the operation that needs debugging

# 3. Download the log
sf apex log get --log-id 07L... --output-dir logs/

# 4. In VS Code: "SFDX: Launch Apex Replay Debugger with Last Log File"
# Set breakpoints, step through, inspect variables
```

### Debugging LWC (Browser DevTools)
- **Chrome DevTools → Sources tab**: Find your component under `modules/c/`
- **Console logging**: `console.log()`, `console.table()`, `console.group()`
- **LWC Inspector** Chrome extension: visualize component tree, properties, events
- Wire adapter errors show in DevTools console
- Use `debugger;` statement in JS to force a breakpoint

### Test.isRunningTest() — Context Detection

```apex
// Detect test context to modify behavior (use sparingly — prefer dependency injection)
if (Test.isRunningTest()) {
    // Use mock endpoint instead of real callout
    endpoint = 'https://mock.test/api';
}
```

---

## LLM Anti-Pattern Code Examples

These are the most common mistakes AI code generators make in Salesforce. The SKILL.md lists quick rules; full code examples are here.

### Rule A1: SOQL Field Coverage

Every field referenced in Apex MUST be in the SOQL SELECT clause — the #1 AI mistake.

```apex
// BAD — References Name and Industry but only selects Id
List<Account> accounts = [SELECT Id FROM Account WHERE Id IN :accountIds];
for (Account a : accounts) {
    if (a.Industry == 'Technology') {     // ❌ Runtime: SObjectException
        String name = a.Name;             // ❌ Runtime: SObjectException
    }
}

// GOOD — All referenced fields in the SELECT
List<Account> accounts = [SELECT Id, Name, Industry FROM Account WHERE Id IN :accountIds];
```

### Rule A2: Relationship Fields in SOQL

```apex
// BAD — Using child syntax for parent lookup
SELECT Id, (SELECT Name FROM Account) FROM Contact  // ❌ Account is parent

// GOOD — Parent uses dot notation
SELECT Id, Account.Name FROM Contact

// GOOD — Child uses subquery
SELECT Id, (SELECT Id, LastName FROM Contacts) FROM Account
```

### Rule A3: Non-Existent Apex Methods

These methods DO NOT EXIST in Apex — never generate them:
- `Datetime.addMilliseconds()` — use `Datetime.addSeconds()` or manual math
- `String.contains()` with regex — `contains()` is literal only; use `Pattern`/`Matcher`
- `List.sort()` with a comparator — use `Comparable` interface on the class
- `Map.values().sort()` — returns unmodifiable list; copy to new `List` first

### Rule A4: Non-Existent Apex Types

These Java types DO NOT EXIST in Apex:
- `StringBuffer`/`StringBuilder` → `String` concatenation or `String.join()`
- `HashMap` → `Map<KeyType, ValueType>`
- `ArrayList` → `List<Type>`
- `HashSet` → `Set<Type>`
- `int` → `Integer` (Apex has no Java-style primitive `int`; note that Apex type names are case-insensitive, so `integer` compiles but is non-idiomatic — always use PascalCase: `Integer`, `Decimal`, `Double`, `Boolean`)
- `float` → `Decimal` or `Double` (no Apex type called `float`)
- `char` → `String`
- `byte[]` → `Blob`

### Rule A5: Static vs Instance Method Confusion

```apex
// BAD
String result = String.toLowerCase();    // ❌ toLowerCase() is instance method
Integer len = myString.valueOf(123);     // ❌ valueOf() is static method

// GOOD
String result = myString.toLowerCase();  // instance method on a String variable
String numStr = String.valueOf(123);     // static method on the String class
```

### Rule A6: String Utility Methods

```apex
String.isBlank(str)     // true for null, '', '   ' — USE THIS for user input
String.isEmpty(str)     // true for null and '' only
str == null             // only checks null, NPE risk on str.isEmpty()
String.isNotBlank(str)  // inverse of isBlank — preferred for guard clauses
```

### Rule L1: No Inline Expressions in LWC Templates

```html
<!-- BAD — All cause compilation errors -->
<template if:true={items.length > 0}>           <!-- ❌ binary expression -->
<p>{isActive ? 'Yes' : 'No'}</p>               <!-- ❌ ternary operator -->
<p>{firstName + ' ' + lastName}</p>             <!-- ❌ concatenation -->

<!-- GOOD — Use JavaScript getters -->
<template if:true={hasItems}>
<p>{activeLabel}</p>
```

```javascript
get hasItems() { return this.items && this.items.length > 0; }
get activeLabel() { return this.isActive ? 'Yes' : 'No'; }
```

### Rule R1: Null Checks Before Field Access

```apex
// BAD — Throws QueryException (System.QueryException: List has no rows for assignment to SObject) if no rows match
Account acc = [SELECT Id, Name FROM Account WHERE Id = :someId LIMIT 1];
String name = acc.Name;

// GOOD — Safe null handling
List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id = :someId LIMIT 1];
if (!accounts.isEmpty()) {
    String name = accounts[0].Name;
}
```

### Rule R3: Recursive Trigger Prevention — Use Set<Id>, NOT Boolean

```apex
// BAD — Static Boolean blocks ALL subsequent records
public class TriggerGuard {
    private static Boolean hasRun = false;  // ❌ Blocks entire second pass
}

// GOOD — Static Set<Id> tracks which specific records have been processed
public class TriggerGuard {
    private static Set<Id> processedIds = new Set<Id>();
    public static Set<Id> getUnprocessedIds(Set<Id> incomingIds) {
        Set<Id> unprocessed = new Set<Id>();
        for (Id recordId : incomingIds) {
            if (!processedIds.contains(recordId)) {
                unprocessed.add(recordId);
                processedIds.add(recordId);
            }
        }
        return unprocessed;
    }
}
```

### Rule R5: MIXED_DML_OPERATION

```apex
// BAD — Setup + non-setup DML in same transaction
insert new Account(Name = 'Test');
insert new User(/* ... */);  // ❌ Throws MIXED_DML_OPERATION

// GOOD — Use @future or Queueable for setup object DML
insert new Account(Name = 'Test');
UserCreationService.createUserAsync(userData);  // @future method
```

### Rule AF2: @InvocableVariable Type Restrictions

```apex
// BAD — Map not allowed
public class FlowInput {
    @InvocableVariable
    public Map<String, String> config;           // ❌

}

// GOOD — Primitives, sObjects, and Lists
public class FlowInput {
    @InvocableVariable(required=true)
    public String recordId;
    @InvocableVariable
    public List<String> fieldNames;
    @InvocableVariable
    public SObject record;
}
```

### Rule AF3: @JsonAccess for Agentforce Returns

```apex
@JsonAccess(serializable='always')
public class AgentResult {
    @AuraEnabled public String message;
    @AuraEnabled public Boolean success;
}
```

### JSON Deserialization with Reserved Words

```apex
// Apex reserved words ('type', 'class', 'group') can't be variable names.
// SAFE: Use JSON.deserializeUntyped() and manually map keys
Map<String, Object> rawMap = (Map<String, Object>) JSON.deserializeUntyped(jsonStr);
String recordType = (String) rawMap.get('type');

// AVOID blind String.replace() — corrupts nested instances of the key
```
