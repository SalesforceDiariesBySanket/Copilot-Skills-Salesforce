# Salesforce Data Model Patterns & Anti-Patterns

> **Validated as of: 2026-02** — Review against current Salesforce release notes for OWD, sharing, and LDV limits.

## Table of Contents
1. [Standard Object Relationship Patterns](#standard-object-relationship-patterns)
2. [Custom Data Model Design Principles](#custom-data-model-design-principles)
3. [Sharing Model Design](#sharing-model-design)
4. [Common Multi-Cloud Data Model Considerations](#common-multi-cloud-data-model-considerations)

---

## Standard Object Relationship Patterns

### Lead-to-Cash (Sales Cloud)
```
Lead → (conversion) → Account + Contact + Opportunity
Opportunity → OpportunityLineItem → Product2 + PricebookEntry → Pricebook2
Opportunity → Quote → QuoteLineItem
Quote → (sync) → Opportunity
Order → OrderItem
```

**Key design decisions**:
- Person Accounts vs Business Accounts: Use Person Accounts for B2C, Business Accounts for B2B
- Lead conversion mapping: Plan field mappings before building
- Product catalog: Use multiple price books for channel/region pricing

### Case-to-Resolution (Service Cloud)
```
Account → Contact → Case
Case → CaseComment, EmailMessage, CaseHistory
Case → Entitlement → ServiceContract → Account
Knowledge Article → Case (linked via KnowledgeArticleId)
```

**Key design decisions**:
- Case assignment rules vs Omni-Channel routing
- Entitlement management for SLA tracking
- Knowledge article lifecycle (draft → published → archived)

### Experience Cloud (Partner/Customer Portal)
```
Account → Contact → User (community user)
User → Profile → Permission Set
Account → Partner (for partner communities)
```

**Key design decisions**:
- License type (Customer Community, Customer Community Plus, Partner Community)
- Sharing model (role-based sharing vs sharing sets vs sharing rules)
- External users need explicit access — OWD applies differently

---

## Custom Data Model Design Principles

### Object Design Rules

1. **One object per real-world entity**: Don't overload objects with unrelated data
2. **Max ~800 fields per object** (soft limit): If approaching, split or archive
3. **Relationship limits**: Max 40 lookups, 2 master-detail per object (25 external lookups)
4. **Lookup vs Master-Detail decision**:
   - Master-Detail: Need roll-up summaries, cascading delete, sharing inheritance
   - Lookup: Need independent record ownership, optional relationship, more flexibility
5. **Junction objects**: For many-to-many relationships (two master-detail fields)

### Data Volume Management

| Volume Level | Records | Strategy |
|-------------|---------|----------|
| Low | < 100K | Standard design, no special handling |
| Medium | 100K - 1M | Indexed fields, selective SOQL, consider archiving |
| High | 1M - 10M | Skinny tables, custom indexes, async processing, archiving strategy |
| Very High | 10M+ | Big Objects, Data 360, external storage, consider External Objects |

### Patterns to Build

**Pattern: Metadata-Driven Configuration**
Use Custom Metadata Types for configuration that needs to be deployed:
- Feature flags, routing rules, integration endpoints, field mappings
- Benefits: Deployable, SOQL-queryable in Apex without limits, testable

**Pattern: Trigger Framework**
```
Trigger → TriggerHandler (abstract) → ObjectTriggerHandler
ObjectTriggerHandler → ServiceClass → SelectorClass
```
- One trigger per object, all logic in handler classes
- Service layer for business logic, selector for SOQL queries
- Recursion prevention with static variables

**Pattern: External ID for Integration**
- Add External_ID__c (Text, unique, case-sensitive) on every object involved in integration
- Use upsert operations with external ID for idempotent data loading
- Index external ID fields for query performance

**Pattern: RecordType-Based Processes**
- Use Record Types for process variation, NOT boolean fields
- Combine with page layouts and Lightning record pages for UX
- Business processes (sales, approval) can be Record Type-specific

**Pattern: Polymorphic Lookups with Care**
- Task.WhoId (Contact or Lead), Task.WhatId (any object)
- Use them when the platform provides them (activities, notes, attachments)
- Avoid designing custom polymorphic patterns — they're hard to query and maintain

### Anti-Patterns to Avoid

**Anti-Pattern: God Object**
One object with 500+ fields serving multiple unrelated business purposes.
Fix: Split into separate objects with lookup relationships.

**Anti-Pattern: Excessive Record Types**
More than 5-8 Record Types on a single object, each with wildly different fields.
Fix: Consider separate objects if the entities are fundamentally different.

**Anti-Pattern: Data Model as Org Chart**
Object hierarchy that mirrors the company org chart instead of business processes.
Fix: Design around business processes and data access patterns.

**Anti-Pattern: Lookup Chains (Deep Hierarchy)**
Object A → B → C → D → E (5+ levels deep).
Fix: Flatten where possible, denormalize critical fields, use formula fields for cross-object access.

**Anti-Pattern: Circular References**
Object A references B, B references A (or longer cycles).
Fix: Identify the primary relationship direction, use one lookup instead of two.

**Anti-Pattern: Storing Computed Data**
Fields that store values that can be calculated from other fields.
Fix: Use formula fields or roll-up summaries (unless performance requires denormalization).

**Anti-Pattern: Over-Indexing**
Requesting custom indexes on fields that aren't used in critical query paths.
Fix: Only request indexes for fields used in WHERE clauses on high-volume objects.

---

## Sharing Model Design

### Organization-Wide Defaults (OWD) Strategy

Set OWD to the MOST RESTRICTIVE level needed by any user in the org, then open up access selectively:

```
Most Restrictive → Most Open

Private → Public Read Only → Public Read/Write → Public Full Access
(For child objects with Master-Detail: Controlled by Parent)
```

**Decision framework**:
- If ANY user shouldn't see ALL records → Private
- If all users can see but not edit all records → Public Read Only
- If all users can see AND edit all records → Public Read/Write
- For child objects with Master-Detail → Controlled by Parent (automatic)

### Opening Up Access (in order of preference)

1. **Role Hierarchy** — Managers see their reports' data (automatic with hierarchy)
2. **Sharing Rules (Criteria-Based)** — Share based on field values (most maintainable)
3. **Sharing Rules (Owner-Based)** — Share based on record owner's role/group
4. **Teams** (Account/Opportunity/Case Teams) — Dynamic per-record sharing
5. **Territory Management** — Geographic or segment-based access
6. **Manual Sharing** — Per-record, per-user (least maintainable)
7. **Apex Managed Sharing** — Programmatic sharing for complex rules (most flexible, highest maintenance)

### Sharing Model Scaling Concerns

- Sharing calculations can slow down with > 100K sharing rules
- Group membership recalculation locks users during large changes
- Implicit sharing (account-based) provides automatic access to related records
- High-volume portals skip sharing calculations for external users

---

## Common Multi-Cloud Data Model Considerations

### Account/Contact Unification
When using multiple clouds, Account and Contact are the unifying entities:
- Use Account hierarchies for corporate structures
- Use Contact roles for relationship types
- Consider Account-Contact relationships (many-to-many via AccountContactRelation)
- Data 360 Profile Unification resolves identities across clouds

### Cross-Cloud Field Conventions
- Prefix custom fields with cloud abbreviation for clarity: `SC_Tier__c` (Sales Cloud), `SVC_Priority__c` (Service Cloud)
- Or use namespacing via managed packages for true separation
- Document which fields are used by which cloud/process

### Data Quality Governance
- Duplicate management rules on Account, Contact, Lead at minimum
- Validation rules for data integrity (required fields, format enforcement)
- Data quality dashboards monitoring completeness and accuracy
- Regular data cleansing cadence (quarterly recommended)
