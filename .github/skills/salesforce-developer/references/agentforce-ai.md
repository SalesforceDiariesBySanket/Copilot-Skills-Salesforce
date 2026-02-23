# Agentforce, AI & Platform Events Reference

> **Validated as of: 2026-02** — Agentforce is evolving rapidly. Review against current Salesforce release notes for agent limits, MCP support, and topic/action constraints.

## Table of Contents
1. [Agentforce Overview](#agentforce-overview)
2. [Custom Agent Actions with Apex](#custom-agent-actions-with-apex)
3. [Prompt Builder & Prompt Templates](#prompt-builder)
4. [Models API](#models-api)
5. [Platform Events (Detailed)](#platform-events)
6. [Change Data Capture](#change-data-capture)
7. [Einstein Features for Developers](#einstein-features)
8. [Event-Driven Architecture Patterns](#event-driven-architecture)

---

## Agentforce Overview

Agentforce is the agent-driven layer of the Salesforce Platform. It enables:

- **AI agents** that assist users conversationally within Salesforce
- **Custom actions** that extend agent capabilities with Apex, Flows, and Prompt Templates
- **Trust Layer** that secures data between your org and LLMs
- **Agent Builder** for declarative agent configuration
- **Agent Script** for pro-code agent development

### Key Concepts

| Concept | Description |
|---|---|
| **Agent** | A conversational AI assistant that performs tasks for users |
| **Topic** | A category of related actions (e.g., "Order Management") |
| **Action** | A specific capability — backed by Apex, Flow, or Prompt Template |
| **Instruction** | Natural language guidance for how/when the agent should use an action |
| **Trust Layer** | Security framework: data masking, toxicity detection, audit trail |
| **Agent Script** | DSL for building agents in code (pro-code alternative to Agent Builder) |

### Agent Action Types

| Type | Backed By | Best For |
|---|---|---|
| **Apex Action** | `@InvocableMethod` | Complex logic, callouts, data processing |
| **Flow Action** | Autolaunched or Screen Flow | Declarative multi-step processes |
| **Prompt Template Action** | Prompt Builder template | Text generation, summarization, analysis |
| **MCP Action** | External MCP server | Connecting to external tools and services |

---

## Custom Agent Actions with Apex

### Building an Invocable Action for Agents

Agent actions use the same `@InvocableMethod` pattern used by Flows, with careful attention
to input/output descriptions (the agent uses these to understand how to call the action).

```apex
public with sharing class AgentOrderActions {
    /**
     * @description Looks up an order by order number and returns its status and details.
     * The agent calls this action when a customer asks about their order status.
     */
    @InvocableMethod(
        label='Get Order Status'
        description='Retrieves the current status and details of an order by its order number.
                     Use this when the user asks about order status, tracking, or delivery.'
        category='Order Management'
    )
    public static List<OrderStatusResult> getOrderStatus(List<OrderStatusRequest> requests) {
        List<OrderStatusResult> results = new List<OrderStatusResult>();

        for (OrderStatusRequest req : requests) {
            OrderStatusResult result = new OrderStatusResult();
            try {
                List<Order> orders = [
                    SELECT Id, OrderNumber, Status, TotalAmount, EffectiveDate,
                           Account.Name, Description
                    FROM Order
                    WHERE OrderNumber = :req.orderNumber
                    WITH SECURITY_ENFORCED
                    LIMIT 1
                ];

                if (orders.isEmpty()) {
                    result.success = false;
                    result.message = 'No order found with number: ' + req.orderNumber;
                } else {
                    Order ord = orders[0];
                    result.success = true;
                    result.orderNumber = ord.OrderNumber;
                    result.status = ord.Status;
                    result.totalAmount = ord.TotalAmount;
                    result.orderDate = ord.EffectiveDate;
                    result.accountName = ord.Account.Name;
                    result.message = 'Order ' + ord.OrderNumber + ' is currently ' +
                                    ord.Status + '. Total: $' + ord.TotalAmount;
                }
            } catch (Exception e) {
                result.success = false;
                result.message = 'Error retrieving order: ' + e.getMessage();
            }
            results.add(result);
        }
        return results;
    }

    public class OrderStatusRequest {
        @InvocableVariable(
            label='Order Number'
            description='The order number to look up (e.g., 00000123)'
            required=true
        )
        public String orderNumber;
    }

    public class OrderStatusResult {
        @InvocableVariable(label='Success' description='Whether the lookup succeeded')
        public Boolean success;

        @InvocableVariable(label='Message' description='Human-readable status message')
        public String message;

        @InvocableVariable(label='Order Number')
        public String orderNumber;

        @InvocableVariable(label='Status' description='Current order status')
        public String status;

        @InvocableVariable(label='Total Amount')
        public Decimal totalAmount;

        @InvocableVariable(label='Order Date')
        public Date orderDate;

        @InvocableVariable(label='Account Name')
        public String accountName;
    }
}
```

### Action Design Best Practices for Agents

1. **Descriptive labels and descriptions** — the agent LLM reads these to decide when to call the action
2. **Clear input descriptions** — describe the expected format and constraints
3. **Return a human-readable message** — the agent renders this to the user
4. **Handle errors gracefully** — return error info in the result, don't throw exceptions
5. **Keep actions focused** — one action per task, not multi-purpose
6. **Use `with sharing`** — agents run in user context
7. **Test thoroughly** — agent actions are invocable methods, testable like any Apex

### Invoking an Agent from Apex

```apex
// API v63.0+ — invoke an agent programmatically
ConnectApi.AgentJobInput input = new ConnectApi.AgentJobInput();
input.agentId = 'YOUR_AGENT_ID';
input.prompt = 'What is the status of order 00000123?';

ConnectApi.AgentJobOutput output = ConnectApi.Agent.createAgentJob(input);
String jobId = output.id;

// Poll for result
ConnectApi.AgentJobOutput result = ConnectApi.Agent.getAgentJob(jobId);
```

### Invoking an Agent from Flow
Use the "Run Agent" action element (available in Flow Builder when Agentforce is enabled).

---

## Prompt Builder and Prompt Templates

### Prompt Template Types

| Template Type | Use Case | Grounding |
|---|---|---|
| **Sales Email** | Generate personalized sales emails | Record data, related records |
| **Record Summary** | Summarize a record for the agent | Record data, related lists |
| **Field Generation** | Auto-populate a field value | Record data |
| **Flex** | Custom template for any purpose | Record data, Flow, Apex |

### Invoking Prompt Templates from Apex

```apex
// Use ConnectApi to invoke a prompt template
ConnectApi.EinsteinPromptTemplateGenerationsInput input =
    new ConnectApi.EinsteinPromptTemplateGenerationsInput();
input.additionalConfig = new ConnectApi.EinsteinLlmAdditionalConfigInput();
input.additionalConfig.applicationName = 'PromptBuilderPreview';
input.isPreview = false;

// Map input variables
Map<String, ConnectApi.WrappedValue> inputParams =
    new Map<String, ConnectApi.WrappedValue>();
ConnectApi.WrappedValue recordIdValue = new ConnectApi.WrappedValue();
recordIdValue.value = recordId;
inputParams.put('Input:Account', recordIdValue);

input.inputParams = inputParams;

// Invoke the template
ConnectApi.EinsteinPromptTemplateGenerationsRepresentation result =
    ConnectApi.EinsteinLlm.generateMessagesForPromptTemplate(
        'My_Prompt_Template_API_Name', input
    );

// Get the generated text
String generatedText = result.generations[0].text;
```

### Prompt Engineering Best Practices

1. **Be specific** in instructions — "Summarize in 3 bullet points" not "Summarize"
2. **Provide context** — ground the prompt with record data and related records
3. **Set constraints** — max length, tone, format, language
4. **Include examples** — few-shot prompting improves quality
5. **Use merge fields** — `{!$Input:Account.Name}` for dynamic data
6. **Test with diverse data** — edge cases, empty fields, long text
7. **Use the Trust Layer** — enable toxicity detection and data masking

---

## Models API

The Models API lets you call LLMs directly from Apex for custom AI use cases.

### Basic Generation Call

```apex
// Using ConnectApi.EinsteinLlm (API v62.0+)
ConnectApi.EinsteinLlmGenerationInput input = new ConnectApi.EinsteinLlmGenerationInput();

ConnectApi.EinsteinLlmMessageInput systemMessage = new ConnectApi.EinsteinLlmMessageInput();
systemMessage.role = 'system';
systemMessage.content = 'You are a helpful assistant for Salesforce administrators.';

ConnectApi.EinsteinLlmMessageInput userMessage = new ConnectApi.EinsteinLlmMessageInput();
userMessage.role = 'user';
userMessage.content = 'Explain the difference between before and after triggers in 2 sentences.';

input.messages = new List<ConnectApi.EinsteinLlmMessageInput>{ systemMessage, userMessage };
input.model = 'sfdc_ai__DefaultGPT4Omni'; // Or your configured model

ConnectApi.EinsteinLlmGenerationOutput output = ConnectApi.EinsteinLlm.generateChat(input);
String response = output.generationDetails.generations[0].content;
```

### Model Configuration

| Model | Description |
|---|---|
| `sfdc_ai__DefaultGPT4Omni` | Default OpenAI GPT-4 model |
| `sfdc_ai__DefaultBedrockAnthropic` | AWS Bedrock Anthropic model |
| Custom models via Model Builder | Bring Your Own Model (BYOM) |
| Custom models via LLM Open Connector | Connect any LLM via API gateway |

---

## Platform Events (Detailed)

### Defining a Platform Event

```xml
<!-- force-app/main/default/objects/Order_Event__e/Order_Event__e.object-meta.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <deploymentStatus>Deployed</deploymentStatus>
    <description>Event published when order status changes</description>
    <eventType>HighVolume</eventType>
    <label>Order Event</label>
    <pluralLabel>Order Events</pluralLabel>
    <publishBehavior>PublishAfterCommit</publishBehavior>
</CustomObject>
```

### Publish Behavior

| Behavior | Description |
|---|---|
| `PublishAfterCommit` | Event published only after transaction commits successfully (default) |
| `PublishImmediately` | Event published immediately, even if transaction rolls back |

### Publishing from Apex

```apex
// Single event
Order_Event__e event = new Order_Event__e(
    Order_Id__c = order.Id,
    Status__c = 'Shipped',
    Customer_Email__c = order.Account.Email__c
);
Database.SaveResult sr = EventBus.publish(event);
if (!sr.isSuccess()) {
    for (Database.Error err : sr.getErrors()) {
        System.debug(LoggingLevel.ERROR, 'Publish error: ' + err.getMessage());
    }
}

// Bulk publish
List<Order_Event__e> events = new List<Order_Event__e>();
for (Order ord : orders) {
    events.add(new Order_Event__e(
        Order_Id__c = ord.Id,
        Status__c = ord.Status
    ));
}
List<Database.SaveResult> results = EventBus.publish(events);
```

### Subscribing with Apex Trigger

```apex
trigger OrderEventTrigger on Order_Event__e (after insert) {
    List<Task> tasks = new List<Task>();

    for (Order_Event__e event : Trigger.new) {
        if (event.Status__c == 'Shipped') {
            tasks.add(new Task(
                Subject = 'Follow up: Order ' + event.Order_Id__c + ' shipped',
                Status = 'Open',
                Priority = 'Normal',
                ActivityDate = Date.today().addDays(3)
            ));
        }
    }

    if (!tasks.isEmpty()) {
        insert tasks;
    }

    // Set replay ID checkpoint for recovery
    EventBus.TriggerContext.currentContext().setResumeCheckpoint(
        Trigger.new[Trigger.new.size() - 1].ReplayId
    );
}
```

### Subscribing in LWC (empApi)

```javascript
import { LightningElement } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';

export default class OrderEventListener extends LightningElement {
    subscription = {};
    channelName = '/event/Order_Event__e';

    connectedCallback() {
        this.handleSubscribe();
        this.registerErrorListener();
    }

    handleSubscribe() {
        const messageCallback = (response) => {
            const event = response.data.payload;
            console.log('Order event received:', event.Order_Id__c, event.Status__c);
            // Update UI, show toast, refresh data
        };

        subscribe(this.channelName, -1, messageCallback).then((response) => {
            this.subscription = response;
            console.log('Subscribed to', this.channelName);
        });
    }

    disconnectedCallback() {
        unsubscribe(this.subscription, () => {
            console.log('Unsubscribed from', this.channelName);
        });
    }

    registerErrorListener() {
        onError((error) => {
            console.error('EMP API error:', JSON.stringify(error));
        });
    }
}
```

### Testing Platform Events

```apex
@IsTest
private class OrderEventTriggerTest {
    @IsTest
    static void testOrderEventProcessing() {
        // Publish test event
        Order_Event__e event = new Order_Event__e(
            Order_Id__c = '801000000000001',
            Status__c = 'Shipped'
        );

        Test.startTest();
        Database.SaveResult sr = EventBus.publish(event);
        Test.stopTest(); // Causes trigger to fire synchronously in test context

        System.assert(sr.isSuccess(), 'Event should publish successfully');

        // Verify the trigger created a task
        List<Task> tasks = [SELECT Subject FROM Task WHERE Subject LIKE '%shipped%'];
        System.assertEquals(1, tasks.size(), 'Should create one follow-up task');
    }
}
```

### Platform Event Limits

| Resource | Limit |
|---|---|
| Standard-volume events per hour | 1,000 (varies by edition) |
| High-volume events per hour | 100,000+ (varies by edition; can purchase more) |
| Max event payload size | 1 MB |
| Max custom fields per event | 100 |
| Event retention (high-volume) | 72 hours |
| Max CometD/empApi subscribers | 2,000 per org |
| Max Pub/Sub API subscribers | Based on entitlement |

### EventBus.RetryableException — Trigger Retry Mechanism

When a platform event trigger encounters a transient error (e.g., lock contention, external
service timeout), throw `EventBus.RetryableException` to retry the trigger with the same batch.

```apex
trigger OrderEventTrigger on Order_Event__e (after insert) {
    try {
        List<Order> ordersToUpdate = new List<Order>();
        for (Order_Event__e event : Trigger.new) {
            ordersToUpdate.add(new Order(Id = event.Order_Id__c, Status = event.Status__c));
        }
        update ordersToUpdate;
    } catch (DmlException e) {
        // Retry up to 9 times (platform limit) with exponential backoff
        throw new EventBus.RetryableException(
            'Transient error, retrying: ' + e.getMessage()
        );
    }
}
```

**Retry rules:**
- Max 9 retries per event batch
- Salesforce applies exponential backoff between retries
- After all retries exhausted, events are lost (unless you implement dead-letter logic)
- Only use for transient errors — permanent errors should NOT be retried

### Delivery Semantics

| Behavior | Detail |
|---|---|
| Delivery guarantee | **At least once** — events may be delivered more than once |
| Ordering | Events published in the same transaction are delivered in order |
| Idempotency | Subscribers should be idempotent — handle duplicate events gracefully |
| PublishAfterCommit | Event delivered only after the publishing transaction commits (default for high-volume) |
| PublishImmediately | Event delivered even if the publishing transaction rolls back |

### Pub/Sub API (gRPC-Based Subscribe/Publish)

The Pub/Sub API is the modern replacement for CometD-based streaming. It uses gRPC for
high-throughput, bidirectional streaming.

```
Endpoint: api.pubsub.salesforce.com:7443
Protocol: gRPC with Protocol Buffers
Auth:     OAuth 2.0 access token + tenant ID (org ID)
```

**Key methods:**
| Method | Description |
|---|---|
| `Subscribe` | Stream events from a channel (platform event or CDC) |
| `Publish` | Publish events to a platform event channel |
| `GetTopic` | Get metadata about a channel (schema, fields) |
| `GetSchema` | Get the Avro schema for event deserialization |

**When to use Pub/Sub API vs empApi:**
- **empApi (LWC/Aura):** For in-browser real-time UI updates
- **Pub/Sub API:** For external system integration, middleware, high-volume processing

---

## Change Data Capture

Change Data Capture (CDC) publishes real-time change events for Salesforce record changes.

### Enabling CDC

```
Setup → Change Data Capture → Select objects to track
```

### CDC Channel Names

| Object | Channel |
|---|---|
| Account | `/data/AccountChangeEvent` |
| Contact | `/data/ContactChangeEvent` |
| Opportunity | `/data/OpportunityChangeEvent` |
| Custom (MyObj__c) | `/data/MyObj__ChangeEvent` |
| All changes | `/data/ChangeEvents` |

### CDC Event Payload Structure

```json
{
  "schema": "...",
  "payload": {
    "ChangeEventHeader": {
      "entityName": "Account",
      "changeType": "UPDATE",
      "changedFields": ["Name", "Industry", "LastModifiedDate"],
      "commitTimestamp": 1234567890000,
      "transactionKey": "abc-123-def",
      "recordIds": ["001xx000003GYQX"],
      "commitUser": "005xx000001SvWO"
    },
    "Name": "Updated Account Name",
    "Industry": "Technology"
  }
}
```

### Subscribing to CDC in LWC

```javascript
import { subscribe } from 'lightning/empApi';

// Subscribe to Account changes
subscribe('/data/AccountChangeEvent', -1, (message) => {
    const changeType = message.data.payload.ChangeEventHeader.changeType;
    const recordIds = message.data.payload.ChangeEventHeader.recordIds;
    console.log(`${changeType} on Account records:`, recordIds);

    if (changeType === 'UPDATE') {
        // Refresh related data
    }
});
```

### CDC vs Platform Events

| Feature | Change Data Capture | Platform Events |
|---|---|---|
| Trigger | Automatic on record changes | Manual publish from code/flow |
| Schema | Auto-generated from object | Custom-defined fields |
| Use case | Syncing external systems on record changes | Custom event-driven logic |
| Configuration | Select objects in Setup | Create custom event objects |
| Payload | Changed fields + metadata | Custom fields you define |

### Subscribing to CDC with Apex Triggers

```apex
// Apex trigger on Change Events — delegates to handler class
trigger AccountChangeEventTrigger on AccountChangeEvent (after insert) {
    AccountChangeEventHandler.handleEvents(Trigger.new);
}
```

```apex
// Handler class — contains all logic (triggers cannot declare methods)
public with sharing class AccountChangeEventHandler {
    public static void handleEvents(List<AccountChangeEvent> events) {
        for (AccountChangeEvent event : events) {
            EventBus.ChangeEventHeader header = event.ChangeEventHeader;
            String changeType = header.getChangeType();
            List<String> changedFields = header.getChangedFields();
            List<String> recordIds = header.getRecordIds();
            String commitUser = header.getCommitUser();

            switch on changeType {
                when 'CREATE' {
                    System.debug('New accounts created: ' + recordIds);
                    // Sync to external system
                }
                when 'UPDATE' {
                    System.debug('Accounts updated: ' + recordIds +
                        ' Changed fields: ' + changedFields);
                    // Only process if relevant fields changed
                    if (changedFields.contains('Industry') || changedFields.contains('AnnualRevenue')) {
                        // Trigger external sync
                    }
                }
                when 'DELETE' {
                    System.debug('Accounts deleted: ' + recordIds);
                }
                when 'UNDELETE' {
                    System.debug('Accounts restored: ' + recordIds);
                }
                when 'GAP_CREATE', 'GAP_UPDATE', 'GAP_DELETE', 'GAP_UNDELETE' {
                    // Gap events indicate the system could not track individual changes
                    // (e.g., overflow due to high volume). Re-sync the full record.
                    System.debug('Gap event — full re-sync needed for: ' + recordIds);
                    handleGapEvent(recordIds);
                }
                when 'GAP_OVERFLOW' {
                    // Too many changes to track. Full re-sync of the entire object is needed.
                    System.debug('GAP_OVERFLOW — re-sync entire object: ' + header.getEntityName());
                    handleFullResync(header.getEntityName());
                }
            }
        }
    }

    private static void handleGapEvent(List<String> recordIds) {
        // Query current state and re-sync to external system
    }

    private static void handleFullResync(String entityName) {
        // Trigger a full export/sync batch job for the object
    }
}
```

### CDC Change Types Reference

| Change Type | Description |
|---|---|
| `CREATE` | Record was created |
| `UPDATE` | Record was updated |
| `DELETE` | Record was deleted |
| `UNDELETE` | Record was restored from Recycle Bin |
| `GAP_CREATE` | System gap — one or more creates may have been missed |
| `GAP_UPDATE` | System gap — one or more updates may have been missed |
| `GAP_DELETE` | System gap — one or more deletes may have been missed |
| `GAP_UNDELETE` | System gap — one or more undeletes may have been missed |
| `GAP_OVERFLOW` | System cannot track changes — full object re-sync required |

### CDC Entity Selection Best Practices

- **Max entities:** Up to 100 objects can be enabled for CDC (varies by edition)
- **Choose wisely:** Each enabled object generates events for ALL changes — adds load
- **High-churn objects:** Avoid enabling on objects with very high DML volume unless needed
- **Subscribe selectively:** Use specific channels (`/data/AccountChangeEvent`) rather than
  the catch-all `/data/ChangeEvents` to reduce processing overhead
- **External subscribers:** Use Pub/Sub API (gRPC) for highest throughput from external systems
- **Retention:** CDC events are retained for **3 days** (72 hours)

---

## Einstein Features for Developers

### Einstein Prediction Builder (Custom Predictions)

```apex
// Access prediction results via formula fields or Apex
// Predictions are stored on the record after processing
Opportunity opp = [
    SELECT Id, Name, Einstein_Score__c, Einstein_Recommendation__c
    FROM Opportunity
    WHERE Id = :oppId
];
```

### Einstein Next Best Action

```apex
// Recommendation strategy outputs feed the NBA component
// Build recommendations using Recommendation objects
Recommendation rec = new Recommendation();
rec.Name = 'Upgrade to Premium';
rec.Description = 'Customer usage indicates they would benefit from Premium tier';
rec.ActionReference = 'Upgrade_Flow'; // Flow API name to execute
rec.AcceptanceLabel = 'Upgrade Now';
rec.RejectionLabel = 'Not Interested';
insert rec;
```

### Einstein Activity Capture & Analytics

- Automatically captures emails and calendar events
- Provides engagement scoring on leads/contacts
- Accessible via standard fields and reports

---

## Event-Driven Architecture Patterns

### Pattern 1: Decoupled Integration (Pub/Sub)

```
[Salesforce Trigger] → [Publish Platform Event] → [External Subscriber via Pub/Sub API]
                                                 → [Apex Trigger Subscriber]
                                                 → [Flow Subscriber]
```

### Pattern 2: External System Notification

```
[External System] → [Pub/Sub API or REST API] → [Publish Platform Event]
                                                      → [Apex Trigger processes event]
```

### Pattern 3: Real-Time Sync with CDC

```
[Record Change in Salesforce] → [CDC Event Auto-Published]
                                     → [External Middleware Subscriber]
                                     → [Data Warehouse Sync]
                                     → [Cache Invalidation]
```

### When to Use Which

| Scenario | Technology |
|---|---|
| Notify external system of specific business events | Platform Events |
| Sync all record changes to external data store | Change Data Capture |
| Decouple trigger logic from cross-object updates | Platform Events |
| Real-time UI refresh when data changes | CDC + empApi in LWC |
| Complex multi-system orchestration | Platform Events + Flow/Apex |
| Legacy integration with existing event infrastructure | Streaming API (consider migrating to Pub/Sub API for new projects) |
