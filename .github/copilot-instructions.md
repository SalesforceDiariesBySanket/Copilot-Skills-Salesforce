# AI Copilot Instructions for ProductionPL Repository

This document provides **deep, discovered patterns** specific to ProductionPL to help AI agents become immediately productive. Rather than generic Salesforce guidance, this focuses on THIS codebase's actual architecture, critical patterns, and non-obvious workflows.

**Last Updated:** June 4, 2026 | **Version:** 2.0 (Enhanced)  
**Maintenance:** Update this guide when adding new integration services, modifying async patterns, or discovering edge cases.

---

## 📋 Project Overview

**Project Name:** ProductionPL (Production Lean)  
**Platform:** Salesforce (Salesforce DX Project)  
**API Version:** 66.0  
**Repository Type:** Bitbucket (keysightcollab/productionpl)  
**Primary Focus:** Enterprise Service Delivery & Project Financial Management

### Key Business Domains
- Service Delivery (SD) - Work Order Management with JitterBit integration
- TaskRay Project Management Integration (read-only managed package)
- Project Financial Tracking & Billing with monthly/amendment records
- Address/Contact Management with custom triggers
- Service Capabilities Management with approval workflows
- Document Management (ContentVersion/ContentDocumentLink)
- Invoice & Billing Processing with currency exchange
- External integrations: JitterBit, AWS Pricing, Oracle, SFI, ZBRAIN

### Why This Matters for AI Agents
Productivity in this codebase requires understanding:
1. **The metadata-driven HTTP integration pattern** - How all external services are configured
2. **The async job governor limit handling** - When/how to use Queueable vs scheduled jobs
3. **The trigger business logic separation** - Where logic lives (triggers vs *BL classes)
4. **The error logging framework** - Which `KC_ErrorLog` method to use when
5. **Non-obvious data flows** - How Work Orders → JitterBit, Projects → TaskRay, etc.

---

## 🔌 CRITICAL PATTERN: Metadata-Driven HTTP Integration

### The Single Source of Truth Pattern
**All HTTP integrations in this codebase MUST use custom metadata type `SD_Integration__mdt`.**

**Location:** `SD_IntegrationUtilityHelper.cls` (154 lines, lines 1-154)

**Why this matters:** 
- ✅ Enables add/modify integrations **WITHOUT code changes**
- ✅ Centralizes all HTTP endpoint configuration
- ✅ Supports enable/disable via `Active__c` flag
- ✅ Reduces tight coupling to external services

### How to Use It

**When you need to make an HTTP callout:**
1. Check `SD_Integration__mdt` for existing service (query by `MasterLabel`)
2. If service doesn't exist, create a custom metadata record with:
   - `MasterLabel` = service name (e.g., "JitterBit", "AWS_Pricing")
   - `URL__c` = base URL (e.g., "https://api.jitterbit.com")
   - `URI__c` = endpoint path (e.g., "/api/v1/workorders")
   - `Method_Type__c` = HTTP method (POST, GET, etc.)
   - `Content_Type__c` = "application/json"
   - `TimeOut__c` = timeout in milliseconds
   - `Active__c` = toggle to enable/disable

3. Call `SD_IntegrationUtilityHelper.fetchHttpRequest(serviceName, jsonBody)`

**Example:**
```apex
// In your Queueable or helper class
String requestBody = JSON.serialize(workOrderList);
HTTPResponse response = SD_IntegrationUtilityHelper.fetchHttpRequest('JitterBit', requestBody);
```

**Special Cases:**
- **AWS Integration:** Use `fetchAWSRequestJSON()` instead - it injects Authorization header from `System.Label.AWS_Authorization`
- **SFI Integration:** After error, `insertSFIErrorLog()` marks failed Work Orders as `Jitter_Bit_Processed__c = 'No'`

### Metadata Records Currently Configured
From codebase analysis, these `SD_Integration__mdt` records exist:
- `JitterBit` - Work Order submission to JitterBit (POST)
- `AWS_Pricing` - AWS pricing lookups (special auth headers)
- `Oracle` - Oracle Parts integration
- `SFI` - SFI fulfillment integration
- `ZBRAIN` - ZBRAIN service (if configured)

### Error Handling Pattern
All HTTP errors are logged via `KC_ErrorLog.createIntegrationErrorLogs()`:
```apex
catch (customException ex) {
  KC_ErrorLog.createIntegrationErrorLogs(
    KC_Constants.ERROR_SEVERITY_HIGH, 
    ex.getTypeName(), 
    String.valueOf(ex.getLineNumber()), 
    ex.getMessage(), 
    ex.getStackTraceString()
  );
}
```

---

## ⚙️ CRITICAL PATTERN: Async Job Governor Limit Handling

### The Problem
Salesforce limits Queueable jobs to 1 per execution. When the queue is full, jobs fail silently.

### The Solution: Intelligent Fallback
**Location:** `SD_IntegrationUtilityHelper.invokeCallouts()` (lines 75-82)

```apex
public static void invokeCallouts(SD_QueueableCalloutHelper queueableObj) {
  Boolean isQueueLimitExceeded = Limits.getQueueableJobs() >= Limits.getLimitQueueableJobs();
  
  if (!isQueueLimitExceeded) {
    // Try Queueable first (async, no wait)
    System.enqueueJob(queueableObj);
  } else {
    // Fall back to scheduled job (deferred execution)
    String nextFireTime = SD_ScheduleWOSCallout.getScheduleTime();
    System.schedule('ScheduledJob' + String.valueOf(Math.random()), 
                    nextFireTime, 
                    new SD_ScheduleWOSCallout(queueableObj));
  }
}
```

### When to Use Each

| Approach | When | Example |
|----------|------|---------|
| **Queueable** | Governor limits available | Bulk Work Order processing |
| **Scheduled** | Queue full, defer processing | Fallback when Queueable limit reached |
| **Batch** | Very large datasets (10K+ records) | Monthly financial calculations |

### Best Practice in Your Code
```apex
// CORRECT: Use the helper, don't decide yourself
SD_IntegrationUtilityHelper.invokeCallouts(new MyQueueable(recordIds));

// WRONG: Don't check limits manually
if (Limits.getQueueableJobs() < Limits.getLimitQueueableJobs()) {
  System.enqueueJob(new MyQueueable(recordIds));
}
```

---

## 📋 CRITICAL PATTERN: Trigger Business Logic Separation

### The Architecture
**Triggers do NOT contain business logic.** They delegate to handler classes which delegate to business logic classes.

**Pattern:**
```
Trigger (SD_AddressContactTrigger.trigger)
  ↓
Handler (SD_AddressContactTriggerHandler extends KC_TriggerHandler)
  ↓
Business Logic (SD_AddressContactTriggerBL.cls)
```

### Why This Matters
- **Testability:** Test BL class directly without firing triggers
- **Reusability:** Call BL methods from flows, controllers, Queueables
- **Maintainability:** Logic isolated in one place
- **Governor Limits:** Can track & optimize more easily

### Real Example from Codebase

**Trigger Definition** (`SD_AddressContactTrigger.trigger`):
```apex
trigger SD_AddressContactTrigger on Address_Contact__c (after insert, after update) {
  SD_OrgTriggerSwitch__c sdTriggerSwitch = SD_OrgTriggerSwitch__c.getInstance();
  
  // Org-level toggle: disable trigger without code changes
  if(sdTriggerSwitch == null || sdTriggerSwitch.Address_Contact_enabled__c) {
    new SD_AddressContactTriggerHandler()
      .execute(SD_Constants.ADDRESS_CONTACT_OBJECT);
  }
}
```

**Handler Class** (`SD_AddressContactTriggerHandler extends KC_TriggerHandler`):
```apex
public class SD_AddressContactTriggerHandler extends KC_TriggerHandler {
  public override void afterInsert() {
    SD_AddressContactTriggerBL.updateCalibreService(true, false, 
      (Map<Id, Address_Contact__c>) newMap);
  }
  
  public override void afterUpdate() {
    SD_AddressContactTriggerBL.updateCalibreService(false, true, 
      (Map<Id, Address_Contact__c>) newMap, 
      (Map<Id, Address_Contact__c>) oldMap);
  }
}
```

**Business Logic Class** (`SD_AddressContactTriggerBL.cls`):
```apex
public with sharing class SD_AddressContactTriggerBL {
  @TestVisible private static Boolean stopRecursiveUpdate = false;
  
  public static void updateCalibreService(Boolean isInsert, Boolean isUpdate, 
                                         Map<Id, Address_Contact__c> newMap) {
    if (stopRecursiveUpdate) return; // Prevent infinite recursion
    stopRecursiveUpdate = true;
    
    try {
      // Business logic here
      List<SomeObject__c> recordsToUpdate = new List<SomeObject__c>();
      // ... populate list ...
      update recordsToUpdate;
    } catch (Exception ex) {
      KC_ErrorLog.logGenericError(ex, 'LEBEIS', 'SD_AddressContactTriggerBL', 
        'updateCalibreService', SD_Constants.APEX_SEVERITY_HIGH, 'Map of IDs involved');
    } finally {
      stopRecursiveUpdate = false;
    }
  }
}
```

### Critical Rules

1. **Org-Level Triggers Switches:**
   - Query `SD_OrgTriggerSwitch__c` custom setting at organization level
   - Check `Address_Contact_enabled__c`, `Capability_enabled__c`, etc.
   - Allows disabling triggers in production without deployment

2. **Recursive Prevention:**
   - Use `static Boolean stopRecursiveUpdate = false` flag
   - Set to `true` at start of logic, `false` in `finally` block
   - Prevents infinite loops when trigger updates same object

3. **Error Logging:**
   - Use `KC_ErrorLog.createApexErrorLogs()` for DML results
   - Use `KC_ErrorLog.logGenericError()` for caught exceptions
   - Always log: severity, class name, method name, additional context

### When Adding a New Trigger

1. Create `.trigger` file (minimal, just delegates)
2. Create `*TriggerHandler extends KC_TriggerHandler`
3. Create `*TriggerBL.cls` (all business logic here)
4. Add toggle field to `SD_OrgTriggerSwitch__c` if needed
5. Write tests for BL class directly, NOT via trigger
6. Add 75%+ code coverage

---

## 🏗️ Project Architecture & Structure

### Directory Organization
```
force-app/main/default/
├── classes/                  # Apex business logic & controllers
├── triggers/                 # Apex trigger definitions
├── lwc/                      # Lightning Web Components
├── aura/                     # Aura components (legacy)
├── objects/                  # Custom object definitions
├── layouts/                  # Page layouts
├── flows/                    # Flow automation
├── flexipages/              # Lightning record pages
└── [other metadata types]    # Various Salesforce metadata
```

### Script Utilities
```
scripts/
├── sprint.js                 # Deployment/retrieval automation
├── package.js                # Package composition
└── codeformatcheck.js        # Code formatting validation
```

---

## 🔧 Technology Stack

### Apex (Backend)
- **Salesforce API:** v66.0
- **Key Frameworks:**
  - KC_TriggerHandler (custom trigger handler framework)
  - SD_ prefix classes (Service Delivery domain)
  - TASKRAY integration classes (managed package)
- **Patterns Used:**
  - Queueable (async processing)
  - Invocable methods (Flow integration)
  - AuraEnabled methods (Lightning component communication)
  - Error logging via KC_ErrorLog

### Frontend (Lightning Components)
- **LWC (Lightning Web Components):** Primary UI framework
- **Aura Components:** Legacy components (being phased out)
- **Testing:** Jest (@salesforce/sfdx-lwc-jest)

### Code Quality Tools
- **Linting:** ESLint (for LWC/Aura)
  - @salesforce/eslint-config-lwc
  - @salesforce/eslint-plugin-aura
- **Formatting:** Prettier with Apex plugin (prettier-plugin-apex)
- **Git Hooks:** Husky (lint-staged on commit)

### Build & Package Management
- **Node.js Scripts:** Custom CLI tools for deployment
- **npm:** Package management
- **sfdx:** Salesforce CLI

---

## 📚 Common Design Patterns

### 1. Trigger Handler Pattern
**Location:** `force-app/main/default/triggers/` + `force-app/main/default/classes/`

```apex
// Trigger Definition
trigger SD_AddressContactTrigger on Address_Contact__c (after insert, after update) {
    SD_OrgTriggerSwitch__c sdTriggerSwitch = SD_OrgTriggerSwitch__c.getInstance();
    if(sdTriggerSwitch == null || sdTriggerSwitch.Address_Contact_enabled__c) {
        new SD_AddressContactTriggerHandler().execute(SD_Constants.ADDRESS_CONTACT_OBJECT);
    }
}

// Business Logic Class (Pattern: *TriggerBL)
public class SD_AddressContactTriggerBL {
    public static Boolean stopRecursiveUpdate = false;
    
    public static void updateCalibreService(Boolean isInsert, Boolean isUpdate, Map<Id,Address_Contact__c> newMap) {
        // Business logic here
    }
}
```

**Key Points:**
- Triggers delegate to handlers (extends KC_TriggerHandler)
- Business logic in separate TriggerBL classes
- Recursive update prevention via static boolean flags
- Org-level trigger switches for enable/disable control
- Error logging via KC_ErrorLog

### 2. Queueable Async Processing
**Location:** `ProjectFinancialsQueueable.cls`, `LaunchMonthlyFinancialProcessing.cls`

```apex
public class ProjectFinancialsQueueable implements Queueable {
    private Set<Id> projectIds;
    private String selectedOrg;
    
    public void execute(QueueableContext context) {
        // Long-running async operations
        // Bulk updates to related records
        // Currency conversions
    }
}

// Invoked via Invocable Method
@InvocableMethod(label='Trigger Bulk Monthly Project Financial Creation')
public static void launch() {
    if (!projectIds.isEmpty()) {
        System.enqueueJob(new ProjectFinancialsQueueable(projectIds, 'ESI'));
    }
}
```

### 3. Lightning Component Communication
**Pattern:** AuraEnabled methods on controllers

```apex
@AuraEnabled(cacheable=true)
public static Map<String, Object> getInvoiceAndTaskRayDetails(Id projectId) {
    // Query logic
    // Return structure for LWC
}
```

### 4. Error Handling & Logging
**Always use:** `KC_ErrorLog` for error tracking

```apex
try {
    // Business logic
} catch (Exception ex) {
    KC_ErrorLog.createApexErrorLogs(records, KC_Constants.ERROR_SEVERITY_HIGH, 'ClassName.MethodName');
    // OR
    KC_ErrorLog.logGenericError(ex, 'LEBEIS', 'ClassName', 'methodName', SD_Constants.APEX_SEVERITY_HIGH, additionalInfo);
}
```

---

## 🎯 Key Classes & Utilities

### Core Frameworks
| Class | Purpose |
|-------|---------|
| `KC_TriggerHandler` | Base trigger handler framework |
| `KC_ErrorLog` | Centralized error logging |
| `SD_Constants` | Service Delivery constants |
| `KC_Constants` | System-wide constants |
| `KC_TestDataFactory` | Test data creation |

### Commonly Referenced Classes
| Class | Purpose |
|-------|---------|
| `ProjectFinancialsQueueable` | Bulk Project Financial creation |
| `ProjectFinancialTriggerHelper` | Project Financial trigger logic |
| `TaskrayProjectValidate` | TaskRay project validation |
| `InvoiceAndTaskRayDetailsController` | Invoice & TaskRay data retrieval |
| `ContentDocumentLinkTriggerHandler` | Document attachment handling |
| `PageRedirect` | URL redirection utility |

### Managed Package Integration
- **TASKRAY Package Classes** (read-only, managed):
  - `TASKRAY__trController`
  - `TASKRAY__trComponentCtrl`
  - `TASKRAY__trStitchProject`
  - `TASKRAY__trLightningComponentDataProvider`

---

## 📝 Naming Conventions

### Apex Classes
- **Triggers:** `{Entity}Trigger` (e.g., `SD_AddressContactTrigger`)
- **Handlers:** `{Entity}TriggerHandler` (e.g., `SD_AddressContactTriggerHandler`)
- **Business Logic:** `{Entity}TriggerBL` (e.g., `SD_AddressContactTriggerBL`)
- **Controllers:** `{Name}Controller` (e.g., `InvoiceAndTaskRayDetailsController`)
- **Helper/Utility:** `{Name}Helper` or `{Name}Utility`
- **Async:** `{Process}Queueable` (e.g., `ProjectFinancialsQueueable`)
- **Test Classes:** `{ClassName}Test`

### Constants
- Use `SD_Constants` for Service Delivery domain
- Use `KC_Constants` for system-wide constants
- Use `NAS_Constants` for NAS domain
- Constants should be UPPER_SNAKE_CASE

### Org-Level Switches
- Use `SD_OrgTriggerSwitch__c` to enable/disable triggers
- Custom Settings stored at Organization level
- Check before trigger execution

---

## 🧪 DISCOVERED PATTERN: Testing & Test Data

### Test Data Creation Pattern
**Location:** `KC_TestDataFactory` - Reusable test data builder

**Always use this factory instead of inline data creation:**
```apex
@isTest
private class ProjectFinancialsQueueableTest {
  @testSetup
  static void setupData() {
    // 1. Create Org Trigger Settings
    List<KC_OrgTriggersSwitchSetting__c> settings = 
      KC_TestDataFactory.getOrgTriggersSwitchSetting();
    insert settings;
    
    // 2. Create basic test records (standard Salesforce)
    Account acc = new Account(Name = 'Test Account');
    insert acc;
    
    // 3. Create domain-specific records
    TASKRAY__Project__c proj = new TASKRAY__Project__c(
      Name = 'Time Project', 
      TASKRAY__trEstimatedHours__c = 80,
      Keysight_Organization__c = 'ESI'
    );
    insert proj;
  }
  
  @isTest
  static void testTimeBasedWeighting() {
    TASKRAY__Project__c proj = [SELECT Id FROM TASKRAY__Project__c LIMIT 1];
    
    Test.startTest();
    System.enqueueJob(new ProjectFinancialsQueueable(
      new Set<Id>{proj.Id}, 'ESI', null));
    Test.stopTest();
    
    // Assert
    List<Project_Financial__c> records = 
      [SELECT Id FROM Project_Financial__c WHERE TaskRay_Project__c = :proj.Id];
    System.assertEquals(1, records.size());
  }
}
```

### Key Testing Rules

1. **Test Classes Live Alongside Source Code**
   - Not in separate `/test/` directory
   - Named with `*Test` suffix (e.g., `ProjectFinancialsQueueableTest.cls`)
   - Keep test classes co-located with implementation

2. **Async Testing Pattern**
   ```apex
   Test.startTest();
   System.enqueueJob(new MyQueueable(recordIds));
   Test.stopTest(); // Executes all queued jobs synchronously
   // Now assert results
   ```

3. **Metadata Queries in Tests**
   - Tests directly query `SD_Integration__mdt` for service config
   - Use `Test.isRunningTest()` to bypass `Active__c` flag checks
   - This allows tests to run without needing metadata in org

4. **Coverage Requirements**
   - **Minimum:** 75% org-wide (enforced by deploy)
   - **Goal:** 90%+ for critical business logic
   - **Critical areas:** Integrations (100%), Financial calcs (95%), Triggers (100%)

---

## 💰 DISCOVERED PATTERN: Project Financial Tracking

### The Financial Model
**Objects Involved:**
- `TASKRAY__Project__c` (TaskRay project, read-only managed package)
- `Project_Financial__c` (Custom object tracking finances)
- `Opportunity` & `OpportunityLineItem` (Sales data)
- `Currency_Exchange_Rate__c` (For multi-currency support)

### Monthly vs Amendment Records
```apex
public class ProjectFinancialTriggerHelper {
  public static void handleAfterInsert(List<Project_Financial__c> newList) {
    Set<Id> monthlyProjectIds = new Set<Id>();
    Set<Id> amendmentProjectIds = new Set<Id>();
    
    for (Project_Financial__c pf : newList) {
      // Separate logic by financial record type
      if (pf.Type__c == 'Monthly') {
        monthlyProjectIds.add(pf.TaskRay_Project__c);
      } else if (pf.Type__c == 'Amendment') {
        amendmentProjectIds.add(pf.TaskRay_Project__c);
      }
    }
    
    // Handle each type separately
    if (!monthlyProjectIds.isEmpty()) {
      updateProjectBooking(monthlyProjectIds); // Monthly logic
    }
    if (!amendmentProjectIds.isEmpty()) {
      updateProjectCumulativeAmendments(amendmentProjectIds); // Amendment logic
    }
  }
}
```

### Key Fields Tracked
| Field | Purpose | Example |
|-------|---------|---------|
| `Type__c` | Monthly or Amendment | "Monthly" |
| `Booking_Cumulative1__c` | Running total for project | 500 |
| `Monthly_Charges_Total__c` | Charges for this month | 45.50 |
| `Completion_Internal__c` | Internal progress % | 65 |
| `Opportunity_Currency__c` | Currency code | "EUR" |

### Currency Exchange Workflow
```apex
// Fetch exchange rates for all currencies
Map<String, Decimal> exchangeRates = new Map<String, Decimal>();
for (Currency_Exchange_Rate__c rate : 
  [SELECT From_Currency_Code__c, To_Currency_Code__c, Conversion_Rate__c 
   FROM Currency_Exchange_Rate__c 
   WHERE From_Currency_Code__c IN :currencyCodes]) {
  String key = rate.From_Currency_Code__c + rate.To_Currency_Code__c;
  exchangeRates.put(key, rate.Conversion_Rate__c);
}

// Convert amounts during financial calculation
Decimal convertedAmount = originalAmount * exchangeRates.get('EURUSD');
```

### Important: Duplicate Prevention
```apex
// Prevent duplicate monthly financials for same project/month
List<Project_Financial__c> existingRecords = 
  [SELECT Id FROM Project_Financial__c 
   WHERE TaskRay_Project__c = :projectId 
   AND Type__c = 'Monthly' 
   AND CreatedDate = THIS_MONTH()];

if (existingRecords.isEmpty()) {
  // Create new monthly financial
} else {
  // Update existing instead
}
```

---

## ✅ Code Standards & Best Practices

### Apex
1. **Always use with sharing by default** (use `without sharing` only when necessary with justification)
   ```apex
   public with sharing class SD_CapabilityTriggerBL { }
   ```

2. **Implement Governor Limit Safety**
   - Query in loops → Bulk operations
   - Batch processes for large datasets
   - Use Queueable for async long-running operations

3. **Leverage Error Logging Framework**
   ```apex
   KC_ErrorLog.createApexErrorLogs(records, ERROR_SEVERITY, 'Context');
   ```

4. **Prevent Recursive Execution**
   ```apex
   public static Boolean stopRecursiveUpdate = false;
   
   public static void handle(List<SObject> records) {
       if (stopRecursiveUpdate) return;
       stopRecursiveUpdate = true;
       // Logic here
   }
   ```

5. **Use Maps for Efficient Lookups**
   - Convert List queries to Map<Id, Object>
   - Enable O(1) lookup performance

6. **Add Comprehensive Comments**
   - Class-level JSDoc comments
   - Complex logic explanation
   - Integration point documentation

### Lightning Web Components (LWC)
1. **Import wire decorators** for reactive data binding
   ```javascript
   import { wire } from 'lwc';
   import { getRecord } from 'lightning/uiRecordApi';
   
   export default class MyComponent extends LightningElement {
     @api recordId;
     @track data;
     
     @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
     wiredRecord({ error, data }) {
       if (data) this.data = data;
     }
   }
   ```

2. **Handle errors gracefully** with try-catch
3. **Use trackBy for lists** to optimize rendering
4. **Cache data** using cacheable=true on controllers
5. **Add JSDoc comments** for public properties

---

## ⚠️ Common Pitfalls to AVOID

1. **Recursive Trigger Execution** → Use static boolean flags (shown in BL pattern)
2. **Governor Limit Violations** → Bulk operations, avoid SOQL in loops
3. **Poor Error Handling** → Always log errors via `KC_ErrorLog`
4. **Unmaintainable Code** → Follow naming conventions, add comments
5. **Hardcoded Values** → Use `SD_Constants` or `KC_Constants` class
6. **Insufficient Test Coverage** → Aim for 80%+ coverage
7. **Ignoring Performance** → Profile queries, use indexes, avoid SOQL in loops
8. **Missing Data Validation** → Validate before DML operations
9. **Direct HTTP Callouts** → MUST use `SD_Integration__mdt` via `SD_IntegrationUtilityHelper`
10. **Queueable Without Limit Check** → MUST use `SD_IntegrationUtilityHelper.invokeCallouts()`

---

## 🚀 Development Workflow Example

### Adding a New Feature Step-by-Step
```
1. Create feature branch: git checkout -b feature/JIRA-123-description
2. Create Apex class following naming conventions (SD_*, with sharing, JSDoc)
3. Implement business logic with error handling
4. Create trigger/handler/BL structure if needed
5. Add comprehensive test cases (75%+ coverage minimum)
6. Run linting: npm run lint
7. Format code: npm run prettier
8. Run tests: npm test
9. Create Pull Request with detailed description
10. Address review feedback
11. Merge to develop, then to main
12. CI/CD pipeline handles deployment
```

### Making HTTP Integration Changes
```
1. Need new external service?
   → Create `SD_Integration__mdt` record (NOT code change)
   → Set Active__c = false initially (test safely)
   → Reference in code via: SD_IntegrationUtilityHelper.fetchHttpRequest('ServiceName', body)

2. Updating existing integration?
   → Query by MasterLabel
   → Modify SD_Integration__mdt fields (URL, timeout, etc.)
   → No code change needed!
   → Set Active__c = true when ready
```

### Adding Trigger Business Logic
```
1. Create trigger with org-level switch check
2. Create handler extending KC_TriggerHandler
3. Create *BL class with actual logic
4. Add static stopRecursiveUpdate = false flag
5. Wrap logic in try/finally with KC_ErrorLog
6. Test BL class directly (don't fire trigger in tests)
7. Ensure 100% trigger coverage
```

---

## � Integration Points & Data Flows

### Work Order → JitterBit Flow
```
Trigger: SD_Work_Order__c insert/update
  ↓
Handler: SD_WorkOrderTriggerHandler
  ↓
BL: SD_WorkOrderTriggerBL.submitToJitterBit()
  ↓
Queueable: SD_WorkOrderQueueable (async)
  ↓
HTTP: SD_IntegrationUtilityHelper.fetchHttpRequest('JitterBit', workOrderJSON)
  ↓
Metadata: SD_Integration__mdt (MasterLabel='JitterBit')
  ↓
Error: If fails → KC_ErrorLog.createIntegrationErrorLogs()
       If SFI specific → insertSFIErrorLog() marks WO as 'Jitter_Bit_Processed__c = No'
```

### Project → TaskRay & Financial Tracking
```
TASKRAY__Project__c updated
  ↓
Trigger: TASKRAY__ProjectTrigger
  ↓
Create: Project_Financial__c (Type__c = 'Monthly' or 'Amendment')
  ↓
Trigger: ProjectFinancialTriggerHelper.handleAfterInsert()
  ↓
Logic splits by Type__c:
  - If Monthly: Calculate monthly charges
  - If Amendment: Update Booking_Cumulative1__c
  ↓
Update: Related TASKRAY__Project__c.Booking_Cumulative1__c
  ↓
Currency Conversion: Use Currency_Exchange_Rate__c for multi-currency
```

### Address/Contact Management Flow
```
Address_Contact__c insert/update
  ↓
Trigger: SD_AddressContactTrigger
  ↓
Handler: SD_AddressContactTriggerHandler
  ↓
BL: SD_AddressContactTriggerBL.updateCalibreService()
  ↓
Updates: Related Calibre records
  ↓
Error: KC_ErrorLog.logGenericError() if exception
```

---

## 🎓 Important Notes for AI Agents

### When Making Changes:
1. **Always search for references** before modifying existing code
   - Use `grep_search` to find all usages of a function/class
   - Check for dependencies before refactoring

2. **Run tests locally** before committing
   - Execute test classes that cover your changes
   - Verify 75%+ coverage maintained

3. **Check org-level switches** for feature toggles
   - `SD_OrgTriggerSwitch__c` controls trigger execution
   - Can disable features without deployment

4. **Validate against naming conventions** in this guide
   - SD_* for Service Delivery domain
   - KC_* for system-wide utilities
   - *Test for test classes

5. **Review existing similar implementations** for consistency
   - Look for existing patterns before creating new ones
   - Maintain architectural consistency

6. **Add JSDoc comments** for new public methods
   - Class-level: What does this class do?
   - Method-level: What is the purpose?
   - Complex logic: Why this approach?

7. **Update tests** when modifying existing code
   - Don't break existing test expectations
   - Add tests for new scenarios

8. **Check for recursive execution** in trigger-related changes
   - Always use static boolean flag pattern
   - Test recursion scenarios

### Code Review Checklist Before Committing:
- [ ] Code follows naming conventions
- [ ] Error handling implemented via KC_ErrorLog
- [ ] Test coverage 75%+ (or 90%+ for critical code)
- [ ] No governor limit violations (no loops with queries)
- [ ] `with sharing` used (unless justified `without sharing`)
- [ ] Comments added for complex logic
- [ ] Linting passes: `npm run lint`
- [ ] Formatting passes: `npm run prettier:verify`
- [ ] Tests pass: `npm test`
- [ ] No hardcoded values (use Constants)
- [ ] Metadata-driven for HTTP integrations
- [ ] Queueable jobs use `SD_IntegrationUtilityHelper.invokeCallouts()`

### When Stuck:
1. Search workspace for similar patterns using semantic_search
2. Review existing test cases for examples
3. Check KC_ErrorLog for error context from previous runs
4. Verify org-level trigger switches are enabled
5. Consult this guide for best practices
6. Look at related trigger/handler/BL classes for architecture

---

**Last Updated:** 2026-06-04
**Version:** 2.0 (Enhanced with discovered patterns)

### Branch Strategy
- **main:** Production-ready code
- **develop:** Integration branch
- **feature/JIRA-###:** Feature branches
- **hotfix/JIRA-###:** Emergency fixes

### Pre-Commit Validation
Husky + lint-staged automatically:
- Runs Prettier formatting
- Runs ESLint validation
- Blocks commit if issues found

### Deployment Workflow
1. **Validate:** `npm run cf:p` (code format check)
2. **Test:** `npm test` (run Jest tests)
3. **Package:** `npm run dev:pk` (create package.xml)
4. **Deploy:** Use CI/CD pipeline (.github/workflows/deploy.yml)

### Important Commands
```bash
# Code formatting
npm run prettier              # Format all files
npm run cf                    # Format force-app

# Linting
npm run lint                  # Lint LWC + Aura
npm run lint:lwc              # Lint LWC only
npm run lint:aura             # Lint Aura only

# Testing
npm test                      # Run all Jest tests
npm run test:unit:coverage    # Run with coverage
npm run test:unit:watch       # Run in watch mode

# Deployment
npm run c:r                   # Retrieve code
npm run dev:pk                # Package components
npm run dp                    # Deploy code
npm run dp:x                  # Deploy with no test
```

---

## 🧪 Testing Guidelines

### Unit Test Best Practices
1. **Test one feature at a time**
2. **Use descriptive test method names**
3. **Arrange-Act-Assert pattern**
4. **Mock external dependencies**
5. **Test boundary conditions**

### Coverage Requirements
- **Apex Classes:** 75% minimum (org-wide)
- **Triggers:** 100% coverage recommended
- **Controllers:** 80%+ coverage
- **Utilities:** 90%+ coverage

### Test Data Creation
Use `KC_TestDataFactory` for consistent test data:
```apex
List<KC_OrgTriggersSwitchSetting__c> settings = KC_TestDataFactory.getOrgTriggersSwitchSetting();
insert settings;
```

---

## 📦 Key Custom Objects & Fields

### Service Delivery Objects
- `SD_Work_Order__c` - Service work orders
- `SD_Bulk_WO__c` - Bulk work order processing
- `Capability__c` - Service capabilities
- `Address_Contact__c` - Address contact associations

### Financial Objects
- `Project_Financial__c` - Project financial tracking
- `Invoice_Request__c` - Invoice requests
- `Taskray_Invoice_Details__c` - TaskRay invoice integration

### Integrations
- `TASKRAY__Project__c` - TaskRay project (managed package)
- `ContentVersion` - File storage
- `ContentDocumentLink` - Document linking

---

## 🔐 Security Considerations

1. **Always use "with sharing"** by default
2. **Sanitize external inputs** before queries
3. **Use @AuraEnabled(cacheable=true)** carefully (may expose sensitive data)
4. **Encrypt sensitive custom settings** where applicable
5. **Audit critical operations** via error logs
6. **Validate SOQL injection vectors**
7. **Implement proper Apex sharing rules** for multi-tenant scenarios

---

## ⚠️ Common Pitfalls to Avoid

1. **Recursive Trigger Execution** → Use static boolean flags
2. **Governor Limit Violations** → Bulk operations, avoid loops with queries
3. **Poor Error Handling** → Always log errors via KC_ErrorLog
4. **Unmaintainable Code** → Follow naming conventions, add comments
5. **Hardcoded Values** → Use Constants class
6. **Insufficient Test Coverage** → Aim for 80%+ coverage
7. **Ignoring Performance** → Profile queries, use indexes, avoid SOQL in loops
8. **Missing Data Validation** → Validate before DML operations

---

## 🚀 Development Workflow Example

### Adding a New Feature
1. Create feature branch: `git checkout -b feature/JIRA-123-description`
2. Create Apex class following naming conventions
3. Implement business logic with error handling
4. Add comprehensive test cases (75%+ coverage)
5. Run linting: `npm run lint`
6. Format code: `npm run prettier`
7. Run tests: `npm test`
8. Create Pull Request with detailed description
9. Address review feedback
10. Merge to develop, then to main
11. CI/CD pipeline handles deployment

---

## 📞 Integration Points

### External Systems
- **TaskRay:** Project & task management (managed package)
- **Oracle:** Order line integration (Oracle_Order_Line_Number__c)
- **CCC/SFI:** Service fulfillment integration
- **HTTP Callouts:** Via named credentials

### Salesforce Features
- **Flow:** Invocable methods for flow automation
- **Lightning Components:** AuraEnabled controllers
- **Batch Processing:** For large data operations
- **Platform Events:** For async communication (if implemented)

---

## 📖 Documentation & References

- **Salesforce DX:** https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/
- **Apex:** https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/
- **Lightning Web Components:** https://developer.salesforce.com/docs/component-library/documentation/en/lwc/
- **Jest Testing:** https://jestjs.io/
- **ESLint:** https://eslint.org/

---

## 🎓 Important Notes for AI Agents

### When Making Changes:
1. **Always search for references** before modifying existing code
2. **Run tests locally** before committing
3. **Check org-level switches** for feature toggles
4. **Validate against naming conventions** in this guide
5. **Review existing similar implementations** for consistency
6. **Add JSDoc comments** for new public methods
7. **Update tests** when modifying existing code
8. **Check for recursive execution** in trigger-related changes

### Code Review Checklist:
- [ ] Code follows naming conventions
- [ ] Error handling implemented via KC_ErrorLog
- [ ] Test coverage 75%+ (or 90%+ for critical code)
- [ ] No governor limit violations
- [ ] With sharing used (unless justified)
- [ ] Comments added for complex logic
- [ ] Linting passes: `npm run lint`
- [ ] Formatting passes: `npm run prettier:verify`
- [ ] Tests pass: `npm test`

### When Stuck:
1. Search workspace for similar patterns
2. Review existing test cases for examples
3. Check KC_ErrorLog for error context
4. Verify org-level trigger switches
5. Consult this guide for best practices

---

**Last Updated:** 2026-06-03  
**Version:** 1.0


# Salesforce Copilot Instructions

You are an expert Salesforce Developer and Solution Architect specializing in Apex, Lightning Web Components (LWC), Agentforce, and Salesforce best practices. Always write clean, scalable, secure, and bulkified code that adheres to Salesforce governor limits.

---

## ⚡ MANDATORY: Read Skills & Rulesets Before Generating Code

Before generating any Salesforce code or answering Salesforce questions, you **MUST** read the relevant skill and ruleset files below. These contain detailed patterns, anti-patterns, reference tables, and code examples that are essential for correct output.

### Skills (read the SKILL.md + appropriate reference files)

| Scenario | Skill File | When to Read |
|---|---|---|
| **Apex, LWC, SOQL, triggers, testing, deployment, Agentforce development** | [`skills/salesforce-developer/SKILL.md`](skills/salesforce-developer/SKILL.md) | Any code generation, debugging, or development question |
| **Architecture, solution design, data modeling, integrations, Well-Architected** | [`skills/salesforce-architect-skill/SKILL.md`](skills/salesforce-architect-skill/SKILL.md) | Any architecture, design, or integration question |

### Coding Rulesets (comprehensive rules with code examples)

| Ruleset | File | When to Read |
|---|---|---|
| **Apex coding rules** (bulkification, SOQL, DML, triggers, async, security, testing, PMD) | [`Blogs/salesforce-apex-coding-rules.md`](Blogs/salesforce-apex-coding-rules.md) | Any Apex class, trigger, test class, or server-side code |
| **LWC coding rules** (templates, JS, wire, events, navigation, Jest, accessibility) | [`Blogs/salesforce-lwc-coding-rules.md`](Blogs/salesforce-lwc-coding-rules.md) | Any LWC component, Aura, or front-end code |

### Skill Reference Files (detailed patterns with code examples)

Each skill has a `references/` directory with deep-dive guides. Read the ones matching the user's task:

| Reference File | Location | When to Read |
|---|---|---|
| Apex patterns, triggers, async, JSON, debugging | `skills/salesforce-developer/references/apex-patterns.md` | Apex code generation |
| SOQL/SOSL optimization, dynamic SOQL, LDV, cursors | `skills/salesforce-developer/references/soql-optimization.md` | Query optimization |
| LWC guide, dynamic components, lazy loading | `skills/salesforce-developer/references/lwc-guide.md` | LWC development |
| REST/Bulk/SOAP API, OAuth, Named Credentials | `skills/salesforce-developer/references/api-integration.md` | Integrations |
| Flows, screen flows, process automation | `skills/salesforce-developer/references/flows-automation.md` | Flow/automation work |
| Security, sharing, CRUD/FLS, encryption | `skills/salesforce-developer/references/security-sharing.md` | Security questions |
| Deployment, sf CLI, CI/CD, packaging | `skills/salesforce-developer/references/deployment-devops.md` | Deployment tasks |
| Agentforce, AI agents, Prompt Builder, platform events | `skills/salesforce-developer/references/agentforce-ai.md` | Agentforce / AI |
| Formulas, validation rules | `skills/salesforce-developer/references/formulas-validation.md` | Declarative logic |
| Data model patterns, LDV, data skew, sharing model | `skills/salesforce-architect-skill/references/data-model-patterns.md` | Data modeling |
| Integration patterns, API selection, event-driven | `skills/salesforce-architect-skill/references/integration-patterns.md` | Integration design |
| Well-Architected checklist, compliance, performance | `skills/salesforce-architect-skill/references/well-architected-checklist.md` | Architecture review |

**Workflow:** For a typical Salesforce development task:
1. Read the relevant **skill file(s)** to understand patterns and architecture
2. Read the relevant **ruleset file(s)** for detailed coding standards and anti-patterns
3. Read the matching **reference file(s)** from the table above for the specific task
4. Generate code that follows ALL rules from the skill, ruleset, and reference files

**When to load both skills:** If the task involves BOTH code AND architecture (e.g., "build an LWC with integration" or "design and implement a trigger framework"), read **both** skills, **both** rulesets, and the relevant reference files from each.

---

## Architecture

- Layer order: **Trigger → Handler → Service → Selector**. Triggers are logic-free; all business logic lives in Service classes.
- **One trigger per object**. Trigger body calls only a handler class — no inline logic.
- Service classes are stateless with static methods. Selector classes centralize all SOQL per SObject.
- Use `with sharing` on every class by default. Only use `without sharing` with a documented reason. Use `inherited sharing` for utility/library classes.

---

## Apex — Critical Rules

- **API version: 66.0** (Spring '26) for all new components.
- **Never** put SOQL, DML, or HTTP callouts inside loops. Collect, query once, process in bulk.
- Always use bind variables (`:variable`) in SOQL — never concatenate user input (SOQL injection risk).
- Prefer `Database.insert/update/delete` with `allOrNone=false` for partial-success handling; always check `SaveResult`.
- Use **User Mode** for all new DML/SOQL (API 60.0+): `Database.insert(records, AccessLevel.USER_MODE)` and `SELECT ... WITH USER_MODE`.
- Use the **Safe Navigation Operator** (`?.`) to prevent NPEs: `account?.Name`. Avoid `?.` in boolean conditions — use `accounts != null && accounts.isEmpty()` instead.
- Use `switch on` instead of long `if-else` chains. Use `Assert.areEqual()` not `System.assertEquals()`.
- Prefer **Queueable** over `@future` for all new async code. Attach a `Finalizer` via `System.attachFinalizer()` for error recovery.
- `@InvocableMethod` must have `label` + `description`, accept `List<Input>`, return `List<Output>`, and delegate to a Service class. One per class.
- Never hardcode IDs, org URLs, or credentials — use Custom Metadata, Named Credentials, or Custom Labels.
- Remove all `System.debug` statements before deploying, or gate them: `System.debug(LoggingLevel.ERROR, msg)`.
- Never use empty `catch` blocks — always handle, log, or rethrow. Use `addError()` on records in trigger context instead of throwing exceptions.
- Use custom exception classes for domain logic: `public class CaseRoutingException extends Exception {}`

---

## Naming Conventions

- Classes: `PascalCase` → `AccountService`, `CaseTriggerHandler`
- Methods/variables: `camelCase` → `getAccounts()`, `accountList`
- Constants: `UPPER_SNAKE_CASE` → `MAX_RETRY_COUNT`
- Booleans: prefix with `is`, `has`, `should`, `can` → `isActive`, `hasEmail`
- Maps: `[value]By[Key]` → `contactsByAccountId`
- Triggers: `[Object]Trigger` → `AccountTrigger`. Handlers: `[Object]TriggerHandler`
- LWC folders: `camelCase` → `caseRoutingList`. HTML tags: `kebab-case` → `<c-case-routing-list>`
- LWC events: **lowercase only** → `'itemselected'`. Handlers: `handle[Event]` → `handleItemSelected`

---

## Formatting

- 4-space indentation (no tabs). Max line length: 120 characters.
- Always use braces `{}` for `if`, `else`, `for`, `while`, `do-while` — even single-line bodies.
- One variable declaration per line. Field declarations before methods in a class.
- LWC JS: `const`/`let` only (never `var`). Use ES6+ features: arrow functions, destructuring, template literals, `async/await`.
- No `console.log` in LWC production code. No `System.debug` in Apex production code.

---

## LWC — Critical Rules

- Use `lwc:if` / `lwc:elseif` / `lwc:else` — **never** the legacy `if:true` / `if:false`.
- Use `this.template.querySelector()` — **never** `document.querySelector()`. Prefer `lwc:ref` over `querySelector` for element references.
- Wire service for read operations; imperative Apex for DML/side effects. Always `async/await` with `try/catch/finally`.
- Reset loading state in `finally`. Show loading spinner (`lightning-spinner`) during all async calls.
- Event names are **lowercase only** (e.g., `'caseselected'`). Parent listens with `oncaseselected={handler}`.
- Component communication: `@api` (parent→child), `CustomEvent` (child→parent), **LMS** (siblings/cross-component) — never `window.addEventListener`.
- Never use `window.alert()`, `window.confirm()`, or `window.prompt()` — use `lightning/alert`, `lightning/confirm`, or `ShowToastEvent`.
- Always use `NavigationMixin` for navigation — never `window.location.href`.
- `@AuraEnabled(cacheable=true)` only for pure reads. No DML, callouts, or enqueue in cacheable methods.
- `@AuraEnabled` methods do **not** support overloading — use distinct method names.
- Prefer Lightning base components (`lightning-datatable`, `lightning-record-form`, etc.) and SLDS classes over custom HTML/CSS.

---

## Testing

- Apex: 95%+ coverage target (75% is deployment minimum, not the quality bar). Use `@testSetup`, never `@SeeAllData=true`.
- Test method naming: `test_[method]_[scenario]_[expectedResult]`. Every assertion must include a descriptive message.
- Always use `Test.startTest()` / `Test.stopTest()` for governor limit resets and async execution.
- LWC: Jest tests in `__tests__/[componentName].test.js`. Always `afterEach(() => { while (document.body.firstChild) document.body.removeChild(...) })`.

---

## Security

- SOQL: `WITH USER_MODE` (preferred) or `WITH SECURITY_ENFORCED`. DML: `Security.stripInaccessible(AccessType.CREATABLE/UPDATABLE, records)`.
- Never use `global` access modifier unless building a managed package or REST/SOAP endpoint — use `public`.
- Mixed DML: never combine setup objects (User, PermissionSet) and non-setup objects (Account, Contact) in the same transaction.
- Triggers: NEVER perform callouts directly — use `@future(callout=true)` or Queueable with `Database.AllowsCallouts`.
- Never use `eval()`, `Function()`, or `innerHTML` with dynamic content in LWC.
- Never store sensitive data (tokens, passwords) in LWC component state or local storage.
