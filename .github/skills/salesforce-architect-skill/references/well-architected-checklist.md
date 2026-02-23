# Salesforce Well-Architected Validation Checklist

> **Validated as of: 2026-02** — Review against current Salesforce Well-Architected framework updates.

## Table of Contents
1. [TRUSTED](#trusted) — Secure, Compliant, Reliable
2. [EASY](#easy) — Intentional, Engaging, Maintainable
3. [ADAPTABLE](#adaptable) — Resilient, Composable
4. [Quick Health Score](#quick-health-score)

Use this checklist to validate any Salesforce solution design against the Well-Architected framework.
Items are in priority order within each section.

---

## TRUSTED

### Secure (Priority 1)

**Authentication**
- [ ] SSO configured for all interactive users (SAML 2.0 or OpenID Connect)
- [ ] MFA enforced for all user types (especially admins and API users)
- [ ] OAuth 2.0 used for all API integrations (no username/password auth in production)
- [ ] JWT Bearer or Client Credentials flow for server-to-server integrations
- [ ] Connected Apps configured with appropriate scopes (least privilege)
- [ ] Session settings hardened (timeout, IP restrictions, secure cookies)
- [ ] Agentforce agent users have unique accounts, never shared across agents
- [ ] Login IP ranges and login hours restricted where appropriate

**Authorization**
- [ ] Organization-Wide Defaults (OWD) set to most restrictive necessary
- [ ] Permission sets used instead of profiles for granting access
- [ ] Permission set groups used to bundle related permissions
- [ ] Role hierarchy reflects data access needs (not org chart)
- [ ] Sharing rules use criteria-based where possible (more maintainable than owner-based)
- [ ] Field-Level Security (FLS) applied for sensitive fields
- [ ] Record-level access analyzed with sharing model diagram
- [ ] Agentforce agent actions audited for data exposure in elevated security context

**Data Protection**
- [ ] Shield Platform Encryption enabled for sensitive fields (if required)
- [ ] TLS 1.2+ enforced for all data in transit
- [ ] Event Monitoring enabled for audit and threat detection
- [ ] Data classification applied (public, internal, confidential, restricted)
- [ ] External data masked or encrypted appropriately

### Compliant (Priority 2)
- [ ] Regulatory requirements documented (GDPR, HIPAA, SOX, FedRAMP, etc.)
- [ ] Data residency requirements met (Hyperforce region selection)
- [ ] Consent management implemented where required
- [ ] Audit trail configured (field history tracking on critical fields, max 20 per object)
- [ ] Data retention and deletion policies implemented
- [ ] Data processing agreements in place for third-party integrations
- [ ] Privacy policy reflects actual data handling practices

### Reliable (Priority 3)

**Availability**
- [ ] Continuity plan documented for Salesforce outages
- [ ] Architectural playbooks for failure scenarios
- [ ] Proactive Monitoring configured with real-time alerting
- [ ] Graceful degradation designed for integration failures

**Performance**
- [ ] SOQL queries use selective filters (indexed fields)
- [ ] No SOQL or DML inside loops
- [ ] Bulkification implemented in all Apex triggers and handlers
- [ ] Async processing used for heavy operations (Batch, Queueable, Future)
- [ ] Apex Cursors considered for large dataset pagination (Spring '26+)
- [ ] Data model optimized (avoid excessive lookups, deep hierarchies)
- [ ] Custom indexes requested for high-volume query patterns
- [ ] Page load times acceptable (< 3s for Lightning pages)

**Scalability**
- [ ] Data volume management strategy defined (archiving, Big Objects, skinny tables)
- [ ] API usage budgeted and monitored across all integrations
- [ ] Storage growth projected and monitored
- [ ] Batch processing designed for volume growth (future-proofed batch sizes)
- [ ] Scale testing performed before go-live

---

## EASY

### Intentional (Priority 1)

**Strategy**
- [ ] Architecture aligns to business objectives (not technology preferences)
- [ ] Standard Salesforce features used before custom development
- [ ] Click-first approach: declarative before programmatic
- [ ] Solution complexity matches business requirement complexity
- [ ] Future roadmap considered in design (not just immediate needs)

**Prioritization**
- [ ] Features phased by business value (MVP → iterative enhancement)
- [ ] Technical debt tracked and has a remediation plan
- [ ] Quick wins identified for early business value

**Efficiency**
- [ ] No duplicate automation paths for the same business process
- [ ] KPIs defined for measuring solution success
- [ ] Unnecessary fields, objects, and automations removed or planned for removal

### Engaging (Priority 2)
- [ ] User experience considered (not just data model)
- [ ] Lightning App Builder used for page composition where possible
- [ ] Dynamic Forms used for conditional field display
- [ ] Screen Flows used for guided data entry where appropriate
- [ ] Mobile experience considered (responsive components, offline support if needed)
- [ ] In-app guidance configured for complex processes
- [ ] Accessibility standards met (WCAG compliance in custom components)

### Maintainable (Priority 3)
- [ ] Naming conventions documented and enforced
- [ ] Apex follows separation of concerns (trigger handler → service → selector → domain)
- [ ] Flow naming convention applied (Object_TriggerType_Purpose)
- [ ] Custom metadata types used for configuration instead of Custom Settings where possible
- [ ] Comments and documentation in code and flows
- [ ] Admin/developer runbooks created for operational tasks
- [ ] Technical documentation maintained (solution design doc, ERDs, integration specs)

---

## ADAPTABLE

### Resilient (Priority 1)

**Incident Response**
- [ ] Incident response plan documented and tested
- [ ] Rollback procedures defined for each release type
- [ ] Error monitoring and alerting configured
- [ ] Integration failure handling: retry logic, circuit breakers, dead-letter queues
- [ ] Business continuity plan accounts for Salesforce dependencies

**Testing Strategy**
- [ ] Unit tests achieve > 75% code coverage (aim for 85%+)
- [ ] Unit tests include positive, negative, and bulk scenarios
- [ ] Integration tests cover end-to-end scenarios
- [ ] UAT plan involves actual business users
- [ ] Regression testing automated where possible
- [ ] Performance testing done for high-volume operations
- [ ] Agentforce testing uses Testing Center for response validation

### Composable (Priority 2)

**Application Lifecycle Management**
- [ ] Source control used for all metadata (Git-based)
- [ ] CI/CD pipeline configured (or plan to implement)
- [ ] Deployment strategy documented (scratch orgs, sandboxes, DevOps Center)
- [ ] Unlocked packages used for modular deployment (for complex orgs)

**Environment Strategy**
- [ ] Environment plan: Dev → QA → UAT → Staging → Production
- [ ] Sandbox refresh schedule defined
- [ ] Data seeding strategy for test environments
- [ ] Scratch org definitions maintained for feature development

**Release Management**
- [ ] Release cadence established (aligned with business and Salesforce release cycles)
- [ ] Release notes produced for each deployment
- [ ] Post-deployment validation checklist used
- [ ] Rollback tested and verified before each release

---

## Quick Health Score

Count the checked items and assess:

| Score | Health Level | Recommended Action |
|-------|-------------|-------------------|
| 80%+ | Healthy | Maintain and continuously improve |
| 60-79% | Needs Attention | Prioritize gaps in TRUSTED first |
| 40-59% | At Risk | Create remediation roadmap immediately |
| < 40% | Critical | Engage architect for comprehensive review |
