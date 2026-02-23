# Flows & Process Automation Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes for Flow runtime limits and recursion behavior.

## Table of Contents
1. [Flow Types Overview](#flow-types-overview)
2. [Record-Triggered Flows](#record-triggered-flows)
3. [Screen Flows](#screen-flows)
4. [Schedule-Triggered Flows](#schedule-triggered-flows)
5. [Platform Event-Triggered Flows](#platform-event-triggered-flows)
6. [Flow Best Practices](#flow-best-practices)
7. [Invocable Apex for Flows](#invocable-apex-for-flows)
8. [Flow Orchestration](#flow-orchestration)
9. [Apex vs Flow Decision Guide](#apex-vs-flow-decision-guide)

---

## Flow Types Overview

Salesforce Flow is the primary automation tool on the platform. Process Builder and Workflow Rules
are in maintenance mode — all new automation should use Flow.

### Core Flow Types

| Flow Type | Trigger | User Interaction | Use Case |
|---|---|---|---|
| **Record-Triggered (Before Save)** | Record create/update, before commit | None | Field defaults, simple field updates on the triggering record |
| **Record-Triggered (After Save)** | Record create/update, after commit | None | Create/update related records, send notifications, callouts |
| **Record-Triggered (Delete)** | Record deletion, runs before delete | None | Prevent deletion, cleanup validation |
| **Screen Flow** | User-initiated (button, page, URL) | Yes — screens, inputs | Guided wizards, data entry, multi-step processes |
| **Schedule-Triggered** | Time-based (CRON) | None | Batch processing, periodic cleanup, scheduled notifications |
| **Autolaunched (No Trigger)** | Invoked by Apex, REST API, other flows | None | Reusable logic, subflows, API-callable automation |
| **Platform Event-Triggered** | Platform event published | None | Event-driven processing, integration responses |

### Order of Execution Context

Record-triggered flows run within the Salesforce Order of Execution:

1. System validation rules
2. **Before-save record-triggered flows** (fast, no DML needed for triggering record)
3. Before triggers (Apex)
4. Custom validation rules
5. After triggers (Apex)
6. Assignment rules, auto-response rules
7. **After-save record-triggered flows** (can create/update other records)
8. Entitlement rules
9. Roll-up summary fields, cross-object workflow
10. Criteria-based sharing evaluation

---

## Record-Triggered Flows

### Before-Save Flows (Fast Field Updates)

Before-save flows are the most performant way to update the triggering record. They run before
the record is committed and do NOT count against DML limits.

**Supported elements:** Assignment, Decision, Get Records, Loop, Formula
**NOT supported:** Create/Update/Delete Records, Send Email, Apex Actions, Subflows, Screen

**Best for:**
- Setting default field values on insert
- Calculating field values based on other fields
- Conditional field stamps (e.g., set Region based on State)

**Example — Auto-set Account Rating:**
```
Trigger: Account — Before Save — Create or Update
Entry Conditions: AnnualRevenue is not null

Decision: Check Revenue Tier
  Outcome "Enterprise": AnnualRevenue > 1,000,000
  Outcome "Mid-Market": AnnualRevenue > 100,000
  Default: "SMB"

Assignment (Enterprise): Rating = "Hot"
Assignment (Mid-Market): Rating = "Warm"
Assignment (SMB): Rating = "Cold"
```

### After-Save Flows

After-save flows run after the record is saved but before the transaction is committed, and can perform DML on related records.

**Supported elements:** All (Create/Update/Delete Records, Send Email, Apex Actions, Subflows, etc.)
**NOT supported:** Screen elements

**Best for:**
- Creating related records (Tasks, Contacts, child records)
- Updating parent records
- Sending notifications
- Making callouts (via Apex actions)

**Example — Create Follow-Up Task on Opportunity Close:**
```
Trigger: Opportunity — After Save — Update
Entry Conditions: StageName = "Closed Won" AND StageName is changed

Create Records: Task
  Subject = "Follow up on won opportunity: {!$Record.Name}"
  OwnerId = {!$Record.OwnerId}
  WhatId = {!$Record.Id}
  ActivityDate = {!$Flow.CurrentDate} + 7
  Status = "Not Started"
  Priority = "High"
```

### Preventing Infinite Loops

Record-triggered flows have built-in recursion prevention:
- A before-save flow on the same object runs only once per record per transaction
- An after-save flow can re-trigger itself, but by default each flow interview runs a maximum of **2 times total** per record per transaction (the original run + 1 additional re-trigger). This limit may vary by Salesforce release — consult current release notes to confirm.
- Use a **Decision element** to check if the field actually changed before making updates

**Pattern — Check Field Change Before Update:**
```
Decision: "Did Rating Change?"
  Condition: {!$Record.Rating} != {!$Record__Prior.Rating}
  → Proceed with automation
  Default → End flow
```

### Entry Conditions Best Practice

Always set entry conditions to narrow the scope:
```
// GOOD — Only fires when relevant fields change
Entry Conditions: StageName is changed AND StageName equals "Closed Won"

// BAD — Fires on every update, wastes resources
Entry Conditions: None (runs on every record update)
```

---

## Screen Flows

### Screen Flow Components

Screen flows support interactive UI elements:

| Component | Description |
|---|---|
| `Text` | Display read-only text, supports merge fields |
| `Text Input` | Single-line text entry |
| `Long Text Area` | Multi-line text entry |
| `Number` | Numeric input |
| `Currency` | Currency input with formatting |
| `Date` / `Date Time` | Date/datetime picker |
| `Checkbox` | Boolean toggle |
| `Picklist` / `Multi-Select Picklist` | Dropdown selection |
| `Radio Buttons` | Single-select radio group |
| `Checkbox Group` | Multi-select checkbox group |
| `Lookup` | Record lookup with search |
| `File Upload` | File attachment |
| `Data Table` | Display records in a table |
| `Section` | Group components with columns |
| `Display Image` | Show an image |

### Distribution Methods

| Method | How |
|---|---|
| Lightning Record Page | Add flow component in Lightning App Builder |
| Lightning App Page | Embed in app page |
| Home Page | Add to home page layout |
| Quick Action | Create a flow action on the object |
| Button / Link | Custom button with flow URL |
| Experience Cloud | Embed in community pages |
| Utility Bar | Add to utility bar item |
| Direct URL | `/flow/FlowApiName?param1=value1` |
| Visualforce | `<flow:interview name="FlowApiName"/>` |
| LWC | `<lightning-flow flow-api-name="FlowApiName"></lightning-flow>` |
| Apex | `Flow.Interview.FlowApiName flow = new Flow.Interview.FlowApiName(inputs);` |

### Passing Parameters to Screen Flows

**From URL:**
```
/flow/MyScreenFlow?recordId={!Account.Id}&source=ButtonClick
```

**From LWC:**
```javascript
import { LightningElement, api } from 'lwc';

export default class FlowContainer extends LightningElement {
    @api recordId;

    get flowInputVariables() {
        return [
            { name: 'recordId', type: 'String', value: this.recordId },
            { name: 'source', type: 'String', value: 'LWC' }
        ];
    }

    handleFlowStatusChange(event) {
        if (event.detail.status === 'FINISHED') {
            // Flow completed — refresh or navigate
            const outputVariables = event.detail.outputVariables;
            const resultId = outputVariables.find(v => v.name === 'outputRecordId');
        }
    }
}
```

```html
<template>
    <lightning-flow
        flow-api-name="My_Screen_Flow"
        flow-input-variables={flowInputVariables}
        onstatuschange={handleFlowStatusChange}>
    </lightning-flow>
</template>
```

**From Apex:**
```apex
Map<String, Object> inputs = new Map<String, Object>();
inputs.put('recordId', accountId);
inputs.put('amount', 50000);

Flow.Interview.My_AutoLaunched_Flow flow = new Flow.Interview.My_AutoLaunched_Flow(inputs);
flow.start();

// Get output variables
String result = (String) flow.getVariableValue('outputResult');
```

---

## Schedule-Triggered Flows

Run a flow on a schedule for batches of records.

**Configuration:**
- **Frequency:** Once, daily, weekly
- **Start date/time:** When the schedule begins
- **Object & conditions:** Which records to process (like a batch query)
- **Batch size:** Records processed per transaction (up to 200)

**Best for:**
- Periodic data cleanup
- Sending scheduled reminders
- Updating stale records
- Compliance checks

**Example — Flag Stale Leads:**
```
Schedule: Daily at 6:00 AM
Object: Lead
Conditions: LastActivityDate < TODAY - 30 AND Status != "Converted"

Update Records: Set Status = "Stale", Description = "Flagged by automation"
```

**Limits:**
- Max 300,000 records per scheduled flow execution
- Max 250,000 record-triggered interviews per 24 hours per org
- Batch size default: 200 records per transaction

---

## Platform Event-Triggered Flows

Subscribe to platform events without writing Apex trigger code.

```
Trigger: Order_Event__e
Conditions: Status__c = "Completed"

Create Records: Task
  Subject = "Follow up on completed order"
  WhatId = {!$Record.Order_Id__c}
```

**Considerations:**
- Platform event-triggered flows run in system context
- They don't support undo/rollback — published events are committed
- Use the `$Record` variable to access event fields
- Maximum 2,000 event messages per batch

---

## Flow Best Practices

### Performance

1. **Use before-save flows** instead of after-save when updating only the triggering record
2. **Bulkify Get Records** — use collections and avoid Get Records inside loops
3. **Limit subflow calls** — each subflow adds overhead
4. **Use Decision elements** with entry conditions to exit early
5. **Avoid DML in loops** — use collection variables and a single Create/Update Records element

### Maintainability

1. **Use descriptive names** for all elements, variables, and resources
2. **Add Description fields** on the flow and key elements
3. **Use subflows** for reusable logic (DRY principle)
4. **Version management** — create new versions, don't modify active versions
5. **Use Custom Labels** for user-facing text to support translation

### Error Handling

1. **Use Fault Paths** on every Create/Update/Delete Records element
2. **Create a custom error-handling subflow** for consistent error logging
3. **Use Custom Error elements** in record-triggered flows to show validation messages
4. **Roll back on failure** — in screen flows, use fault connectors to handle errors gracefully

### Custom Error Element (Record-Triggered Flows)
```
Custom Error Message: "Cannot close opportunity without at least one line item."
Display Where: On a specific field (Amount) OR as a generic page-level error
```

---

## Invocable Apex for Flows

### Basic Invocable Method

```apex
public with sharing class FlowAccountActions {
    @InvocableMethod(
        label='Merge Duplicate Accounts'
        description='Merges duplicate accounts into a master account'
        category='Account'
    )
    public static List<MergeResult> mergeDuplicates(List<MergeRequest> requests) {
        List<MergeResult> results = new List<MergeResult>();

        // Bulkify: collect all IDs and query outside the loop
        Set<Id> masterIds = new Set<Id>();
        Set<Id> duplicateIds = new Set<Id>();
        for (MergeRequest req : requests) {
            masterIds.add(req.masterAccountId);
            duplicateIds.add(req.duplicateAccountId);
        }

        Map<Id, Account> masterMap = new Map<Id, Account>(
            [SELECT Id, Name FROM Account WHERE Id IN :masterIds WITH SECURITY_ENFORCED]
        );
        Map<Id, Account> duplicateMap = new Map<Id, Account>(
            [SELECT Id FROM Account WHERE Id IN :duplicateIds WITH SECURITY_ENFORCED]
        );

        for (MergeRequest req : requests) {
            MergeResult result = new MergeResult();
            try {
                Account master = masterMap.get(req.masterAccountId);
                Account duplicate = duplicateMap.get(req.duplicateAccountId);
                if (master == null || duplicate == null) {
                    result.success = false;
                    result.errorMessage = 'Master or duplicate account not found';
                } else {
                    Database.MergeResult mergeRes = Database.merge(master, duplicate);
                    result.success = mergeRes.isSuccess();
                    result.mergedRecordId = master.Id;
                }
            } catch (Exception e) {
                result.success = false;
                result.errorMessage = e.getMessage();
            }
            results.add(result);
        }
        return results;
    }

    public class MergeRequest {
        @InvocableVariable(label='Master Account ID' required=true)
        public Id masterAccountId;

        @InvocableVariable(label='Duplicate Account ID' required=true)
        public Id duplicateAccountId;
    }

    public class MergeResult {
        @InvocableVariable(label='Success')
        public Boolean success;

        @InvocableVariable(label='Merged Record ID')
        public Id mergedRecordId;

        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }
}
```

### Invocable Method with Callout

```apex
public with sharing class FlowExternalCallout {
    @InvocableMethod(
        label='Verify Address'
        description='Validates address via external service'
        callout=true
    )
    public static List<AddressResult> verifyAddress(List<AddressRequest> requests) {
        List<AddressResult> results = new List<AddressResult>();
        for (AddressRequest req : requests) {
            HttpRequest httpReq = new HttpRequest();
            httpReq.setEndpoint('callout:Address_Verification/verify');
            httpReq.setMethod('POST');
            httpReq.setHeader('Content-Type', 'application/json');
            httpReq.setBody(JSON.serialize(new Map<String, String>{
                'street' => req.street,
                'city' => req.city,
                'state' => req.state,
                'zip' => req.zipCode
            }));

            HttpResponse res = new Http().send(httpReq);
            AddressResult result = new AddressResult();
            result.isValid = res.getStatusCode() == 200;
            result.standardizedAddress = res.getBody();
            results.add(result);
        }
        return results;
    }

    public class AddressRequest {
        @InvocableVariable(label='Street' required=true)
        public String street;
        @InvocableVariable(label='City' required=true)
        public String city;
        @InvocableVariable(label='State' required=true)
        public String state;
        @InvocableVariable(label='Zip Code' required=true)
        public String zipCode;
    }

    public class AddressResult {
        @InvocableVariable(label='Is Valid')
        public Boolean isValid;
        @InvocableVariable(label='Standardized Address')
        public String standardizedAddress;
    }
}
```

---

## Flow Orchestration

Flow Orchestration coordinates multi-step, multi-user processes that span days or weeks.

### Key Concepts

| Concept | Description |
|---|---|
| **Orchestration** | The top-level container, similar to a flow |
| **Stage** | A phase of the process (e.g., "Manager Review", "Finance Approval") |
| **Step** | An individual unit of work within a stage |
| **Interactive Step** | Assigns a screen flow to a user via Action Item |
| **Background Step** | Runs an autolaunched flow automatically |
| **Exit Conditions** | Criteria to advance from a stage or step |

### Use Cases
- Multi-level approval processes
- Employee onboarding workflows
- Quote-to-order processes
- Complex case escalation paths

### Orchestration vs Standard Flow

| Feature | Standard Flow | Flow Orchestration |
|---|---|---|
| Duration | Single transaction (seconds) | Days/weeks |
| Users | Single user | Multiple users |
| Steps | Sequential elements | Parallel or sequential stages |
| Persistence | Runs to completion or pauses | Long-running, state persisted |
| Complexity | Simple to moderate | Complex multi-party processes |

---

## Apex vs Flow Decision Guide

### When to Use Flow
- Simple field updates (before-save flows)
- Record creation/update automation
- Sending email alerts and notifications
- Admin-maintainable business logic
- Screen-based guided processes
- Scheduled batch operations on moderate data volumes
- No complex error handling needed

### When to Use Apex
- Complex business logic with conditional branching
- Operations requiring precise transaction control
- Callouts with complex retry/error handling
- Processing large data volumes (millions of records)
- Unit-testable business rules
- Reusable across multiple entry points
- Performance-critical operations
- Complex data transformations

### When to Use Both (Hybrid)
- Flow for orchestration + Invocable Apex for complex logic
- Record-triggered flow for simple field updates + Apex trigger for complex cross-object logic
- Screen flow for UI + Apex controller for backend processing

### Migration from Process Builder / Workflow Rules

| Old Tool | Replacement |
|---|---|
| Workflow Rule — Field Update | Before-save record-triggered flow |
| Workflow Rule — Email Alert | After-save record-triggered flow |
| Workflow Rule — Outbound Message | After-save flow + HTTP callout action |
| Workflow Rule — Task Creation | After-save record-triggered flow |
| Process Builder | Record-triggered flow (before or after save) |
| Process Builder — Invocable Process | Autolaunched flow (subflow) |

**Salesforce provides a "Migrate to Flow" tool** in Setup → Process Automation → Migrate to Flow.
