# Salesforce Integration Patterns — Reference Guide

> **Validated as of: 2026-02** — Review against current Salesforce release notes for API limits and integration patterns.

## Table of Contents
1. [Pattern Selection Decision Tree](#pattern-selection-decision-tree)
2. [Pattern Details](#pattern-details)
3. [Integration Architecture Checklist](#integration-architecture-checklist)
4. [Middleware Decision: Direct API vs MuleSoft vs Other](#middleware-decision-direct-api-vs-mulesoft-vs-other)

---

## Pattern Selection Decision Tree

Use this decision tree to select the right integration pattern:

```
START: Does data need to be stored in Salesforce?
│
├── YES → Is it triggered by an external event?
│   ├── YES → How much data?
│   │   ├── Small (< 200 records) → Remote Call-In (REST/SOAP API)
│   │   ├── Medium (200-50K) → Remote Call-In (Composite API / Bulk API)
│   │   └── Large (50K+) → Batch Data Sync (Bulk API 2.0 / MuleSoft)
│   │
│   └── NO → Is it scheduled/periodic?
│       ├── YES → Batch Data Synchronization
│       └── NO → Event-Driven (Platform Events / CDC / Pub/Sub API)
│
├── NO → Does Salesforce need to access it in real-time?
│   ├── YES → Data Virtualization (Salesforce Connect / External Objects)
│   └── NO → Is it for analytics / AI?
│       ├── YES → Data 360 Ingestion (CRM Streams, Ingestion API, connectors)
│       └── NO → UI Mashup or External link (no integration needed)
│
└── BIDIRECTIONAL → What's the primary system of record?
    ├── Salesforce is SoR → Outbound: Platform Events / Outbound Messages / API callout
    ├── External is SoR → Inbound: Remote Call-In or Batch Sync
    └── Shared ownership → Event-Driven Architecture with conflict resolution
```

## Pattern Details

### 1. Remote Process Invocation — Request and Reply
- **Scenario**: Salesforce initiates a real-time call to an external system and waits for a response
- **Implementation**: Apex callouts (HTTP/REST/SOAP), External Services (declarative), Named Credentials
- **When to use**: Real-time validation, enrichment, payment processing, address verification
- **Limits**: Max 100 callouts per transaction, 120s cumulative timeout, 10s per callout default
- **Best practices**: Use Named Credentials (not hardcoded endpoints), implement retry logic, use Continuation for long-running calls in LWC/Visualforce

### 2. Remote Process Invocation — Fire and Forget
- **Scenario**: Salesforce sends a message to an external system without waiting for a response
- **Implementation**: Platform Events (publish), Outbound Messages, Apex async callouts (@future, Queueable)
- **When to use**: Notifications, logging, triggering external workflows, non-blocking updates
- **Best practices**: Implement error handling at the receiver, use Platform Events for guaranteed delivery with replay

### 3. Batch Data Synchronization
- **Scenario**: Large volumes of data need to be moved on a schedule
- **Implementation**: Bulk API 2.0, MuleSoft batch jobs, Informatica, custom ETL
- **When to use**: Nightly syncs, data warehouse loads, large migrations, periodic reconciliation
- **Volume guidance**: Bulk API 2.0 handles up to 150M records/day; use serial mode for lock-sensitive objects
- **Best practices**: Use upsert with external IDs, implement delta/incremental loads, monitor with Integration User

### 4. Remote Call-In
- **Scenario**: External system calls Salesforce APIs
- **APIs available**:
  - REST API: General-purpose CRUD, supports JSON/XML
  - SOAP API: Enterprise-grade, strongly typed, WSDL-based
  - Composite API: Multiple operations in a single request (up to 25 subrequests)
  - GraphQL API: Flexible queries, request only needed fields
  - Bulk API 2.0: High-volume async CRUD
  - Streaming API (PushTopic, CDC): Real-time event subscription
  - Pub/Sub API (gRPC): Modern event streaming for Platform Events and CDC
- **Authentication**: OAuth 2.0 (Web Server flow for interactive, JWT Bearer for server-to-server, Client Credentials for service accounts)
- **Best practices**: API versioning strategy, rate limit monitoring, use Connected Apps with appropriate scopes

### 5. Data Virtualization
- **Scenario**: Salesforce users need to see external data without storing it
- **Implementation**: Salesforce Connect with External Objects
- **Adapters**: OData 2.0/4.0, Cross-Org, Custom Apex, GraphQL
- **Features**: SOQL on external objects, federated search, external lookup relationships, indirect lookups
- **Limitations**: No triggers on external objects, limited SOQL support, latency dependent on external source
- **Best practices**: Cache when possible, use Salesforce Connect Validator tool, implement error handling

### 6. Event-Driven Architecture
- **Scenario**: Loosely coupled systems need to react to changes in near-real-time
- **Components**:
  - **Platform Events**: Custom event schemas, publish/subscribe, replay capability
  - **Change Data Capture (CDC)**: Automatic events for record changes on standard/custom objects
  - **Pub/Sub API**: gRPC-based subscription for external consumers
  - **AWS Event Relay**: Bridge Salesforce events to AWS EventBridge
- **When to use**: Decoupled microservices, cross-org sync, real-time notifications, audit trails
- **Anti-patterns**: Using Platform Events for batch data transfer, oversized payloads, ignoring replay for error recovery

### 7. Data 360 Integration Patterns
- **CRM Data Streams**: Automatic sync of Salesforce CRM data into Data 360
- **Ingestion API**: REST-based streaming (JSON) or bulk (CSV) data loading
- **Cloud Storage Connectors**: S3, GCS, Azure Blob for file-based ingestion
- **Event Stream Connectors**: Amazon Kinesis, Confluent MSK for real-time streaming
- **MuleSoft Anypoint Connector**: Broad application/database connectivity via Anypoint Exchange
- **Zero-Copy Partners**: Snowflake, Databricks, BigQuery (federated access without data movement)

## Integration Architecture Checklist

For every integration, document:

- [ ] Data ownership (system of record for each entity)
- [ ] Direction of data flow (inbound, outbound, bidirectional)
- [ ] Timing (real-time, near-real-time, batch/scheduled)
- [ ] Volume (records per hour/day, peak vs average)
- [ ] Error handling strategy (retry, dead-letter queue, alerting)
- [ ] Authentication method (OAuth flow type, credential management)
- [ ] API version and deprecation strategy
- [ ] Rate limit budget (how many API calls allocated to this integration)
- [ ] Monitoring and alerting (Proactive Monitoring, event monitoring, custom dashboards)
- [ ] Idempotency (how to handle duplicate messages)
- [ ] Transformation logic (where does mapping happen — middleware vs Salesforce)
- [ ] Rollback strategy (what happens if the integration fails mid-transaction)

## Middleware Decision: Direct API vs MuleSoft vs Other

| Factor | Direct API | MuleSoft | Other iPaaS |
|--------|-----------|----------|-------------|
| Complexity | Simple point-to-point | Complex orchestration | Varies |
| Volume | Low-medium | Any | Varies |
| Transformations | Minimal | Complex | Moderate |
| Monitoring | Custom build | Built-in Anypoint | Platform-dependent |
| Cost | Low (API calls only) | License + consumption | License-dependent |
| Recommended when | 1-2 integrations, simple mapping | Enterprise-scale, many systems | Team already uses specific iPaaS |
