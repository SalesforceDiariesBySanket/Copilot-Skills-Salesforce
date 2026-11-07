# Performance & Governor Limits Review Checklist

> **Review Category**: Query Optimization, Bulkification, Governor Limits, Performance  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Bulkification & Query Optimization

### SOQL Inside Loops (Critical Anti-Pattern)

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No SOQL queries inside loops | ☐ Pass ☐ Fail | 🔴 CRITICAL | 200 records × 1 query = 200 queries (limit: 100 sync) |
| No DML inside loops | ☐ Pass ☐ Fail | 🔴 CRITICAL | Batching DML reduces from 200 to 1 operation (limit: 150) |
| No nested loops on 100+ item collections | ☐ Pass ☐ Fail | 🔴 CRITICAL | O(n²): 200 × 200 = 40k iterations = CPU exceeded |
| Map<Id, Collection> used for lookups | ☐ Pass ☐ Fail | 🟠 HIGH | Replaces nested loop pattern; O(1) lookup vs O(n) |
| No List.contains() in tight loops | ☐ Pass ☐ Fail | 🟠 HIGH | O(n) per call; use Set for O(1) containment checks |

### Query Consolidation

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Related data queried in single SOQL (subquery) | ☐ Pass ☐ Fail | 🟠 HIGH | `SELECT ... (SELECT ... FROM Children) FROM Parent` |
| Aggregate queries used (COUNT, SUM, MIN, MAX) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Server aggregation faster than client-side loop |
| Query reuse via caching where possible | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cache frequently-queried reference data (Record Types, Picklist values) |
| LIMIT clause applied to prevent excessive rows | ☐ Pass ☐ Fail | 🟠 HIGH | 50k row limit per transaction; use pagination |

### Field Selection

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SELECT clause includes only required fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | Full table scan less efficient than targeted query |
| SELECT * avoided (use explicit field list) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Explicit = clear intent, easier to maintain |
| Large text/blob fields excluded from bulk queries | ☐ Pass ☐ Fail | 🟡 MEDIUM | Large fields increase heap/API payload; query separately |

### WHERE Clause Optimization

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| WHERE clause uses indexed fields (Id, Name, lookups) | ☐ Pass ☐ Fail | 🟠 HIGH | Unindexed fields trigger full table scans |
| WHERE clause is selective (filters majority of rows) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Broad WHERE = many rows = CPU/heap exceeded |
| Avoid non-selective operators (LIKE %, !=, NOT IN) | ☐ Pass ☐ Fail | 🟡 MEDIUM | These operators often bypass indexes |
| OR conditions use indexed fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | `WHERE (Id IN :ids) OR (Status = 'Active')` optimized when Id indexed |

---

## 2. Governor Limits Compliance

### Synchronous Limits (Trigger Context)

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| SOQL queries < 100 | ☐ Pass ☐ Fail | 🟠 HIGH | Track cumulative queries across all triggers |
| DML statements < 150 | ☐ Pass ☐ Fail | 🟠 HIGH | One insert/update/delete = one DML; batching saves limit |
| CPU time < 10,000 ms (10 seconds) | ☐ Pass ☐ Fail | 🟠 HIGH | Complex loops, regex, crypto consume CPU |
| Heap size < 6 MB | ☐ Pass ☐ Fail | 🟡 MEDIUM | Large collections, cloning lists exceeds heap |
| Query row limits < 50,000 | ☐ Pass ☐ Fail | 🟠 HIGH | Sum of all query results across transaction |
| API callouts < 100 | ☐ Pass ☐ Fail | 🟡 MEDIUM | HTTP callouts counted against limit; batch carefully |

### Async Limits (Queueable, Batch, Scheduled)

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Queueable SOQL < 200 | ☐ Pass ☐ Fail | 🟡 MEDIUM | Higher than sync; but still bounded |
| Queueable DML < 200 | ☐ Pass ☐ Fail | 🟡 MEDIUM | Async job has more generous limits |
| Batch Apex chunk size appropriate (200-500 records) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Small chunks = more overhead; large = more risk |
| Batch execute() stays within DML/SOQL limits per batch | ☐ Pass ☐ Fail | 🟠 HIGH | Each batch chunk is a separate transaction |
| Scheduled Apex runs outside peak hours | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Batch jobs at night/weekend minimize user impact |

### Time Limits

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@future` methods complete within 60 seconds | ☐ Pass ☐ Fail | 🟡 MEDIUM | @future timeout = job abandoned; Queueable better |
| Batch Apex execute() within 60 seconds per batch | ☐ Pass ☐ Fail | 🟡 MEDIUM | Timeout = batch chunk fails; remaining chunks continue |
| Callout timeout set appropriately | ☐ Pass ☐ Fail | 🟡 MEDIUM | Default 120s; configure for external API SLA |
| Scheduled job start/finish time monitored | ☐ Pass ☐ Fail | 🟡 MEDIUM | Jobs queued if previous run still active |

---

## 3. Async Apex Patterns

### Choosing Async Approach

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@future` used only for simple, fast operations | ☐ Pass ☐ Fail | 🟡 MEDIUM | No return value, hard to debug; avoid if possible |
| Queueable used for deferred processing | ☐ Pass ☐ Fail | 🟡 MEDIUM | Better error handling, can chain, supports callouts |
| Batch used for 1000+ record processing | ☐ Pass ☐ Fail | 🟡 MEDIUM | Handles chunking, large datasets |
| Scheduled used for recurring/periodic jobs | ☐ Pass ☐ Fail | 🟡 MEDIUM | Daily, hourly, monthly tasks |

### Implementation Quality

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Queueable implements `Queueable` interface correctly | ☐ Pass ☐ Fail | 🟡 MEDIUM | `execute(QueueableContext)` required |
| Batch implements `Database.Batchable<sObject>` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `start()`, `execute()`, `finish()` required |
| Scheduled implements `Schedulable` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `execute(SchedulableContext)` required |
| Exception handling in execute() methods | ☐ Pass ☐ Fail | 🟠 HIGH | Async job failure shouldn't crash org; log and notify |
| Finalizer attached to Queueable for cleanup | ☐ Pass ☐ Fail | 🟡 MEDIUM | `System.attachFinalizer(new MyFinalizer())` handles post-job cleanup |

---

## 4. Heap & Memory Management

### String & Collection Optimization

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| String concatenation in loop uses List<String>.join() | ☐ Pass ☐ Fail | 🟠 HIGH | `str += item` = exponential heap growth; use List |
| Large collections paginated (200 records at a time) | ☐ Pass ☐ Fail | 🟡 MEDIUM | 50k-row query = heap exceeded; loop through pages |
| Collections cleared after use | ☐ Pass ☐ Fail | 🟡 MEDIUM | `clear()` or reassign to null; helps garbage collector |
| Deep cloning avoided on large collections | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cloning 200-record list multiple times wastes heap |
| Map size estimation provided at initialization | ☐ Pass ☐ Fail | ⚪ LOW | `new Map<Id, Account>(200)` preallocates for efficiency |

### Memory Leaks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Static collections don't grow unbounded | ☐ Pass ☐ Fail | 🟠 HIGH | Static persists across transactions; can exhaust heap |
| Event listener unregistration implemented | ☐ Pass ☐ Fail | 🟡 MEDIUM | Listeners not removed = memory leak in long-running code |
| References to large objects cleared | ☐ Pass ☐ Fail | 🟡 MEDIUM | `largeMap = null` allows garbage collection |

---

## 5. CPU & Regex Performance

### CPU-Intensive Operations

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Complex regex only on necessary fields | ☐ Pass ☐ Fail | 🟡 MEDIUM | Regex matching is CPU-expensive; use String methods where possible |
| Cryptographic operations batched | ☐ Pass ☐ Fail | 🟡 MEDIUM | Crypto.generateDigest() CPU-intensive; don't call in tight loops |
| Large JSON parsing monitored | ☐ Pass ☐ Fail | 🟡 MEDIUM | Parsing multi-MB JSON exceeds CPU/heap |
| Recursive algorithms have depth guards | ☐ Pass ☐ Fail | 🟡 MEDIUM | Unconstrained recursion = stack overflow |
| Math operations optimized (avoid expensive calculations in loops) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Precompute outside loop; avoid repeated calculations |

### Database vs. Application Logic

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Sorting via SOQL ORDER BY (not in Apex) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Database sorting faster than in-memory sort |
| Filtering via SOQL WHERE (not in Apex loop) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Query filtering = index usage; Apex filtering = full scan |
| Aggregation via SQL (COUNT, SUM, etc.) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Database aggregation faster than looping and counting |

---

## 6. Query Plan Analysis

### Query Efficiency

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Query execution plan reviewed (SOQL Analyzer) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Identify inefficient queries before deploy |
| Index usage verified for complex queries | ☐ Pass ☐ Fail | 🟡 MEDIUM | Developer Console shows if query uses index |
| Filter complexity balanced (too many = slow, too few = data overload) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Find sweet spot for selective WHERE clause |
| Join strategy for large related objects optimized | ☐ Pass ☐ Fail | 🟡 MEDIUM | Subquery vs. separate query vs. map-based join |

---

## 7. Testing & Performance Validation

### Performance Tests

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Test includes 200-record bulk scenario | ☐ Pass ☐ Fail | 🟠 HIGH | Governor limits only hit with realistic data volume |
| Governor limit consumption measured (System.Limits API) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Assert: `System.assertEquals(expectedQueries, Limits.getQueries())` |
| Recursive trigger tested without breaking bulk | ☐ Pass ☐ Fail | 🟠 HIGH | Recursion prevention must allow 200-record batches |
| Timeout scenarios tested (HTTP callouts, batch timeouts) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Mock callout timeout; verify error handling |
| Monitoring/alerting set for production | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Alert on slow query performance, timeout spikes |

---

## Review Output Template

### Performance Assessment
- **Risk Level**: Critical / High / Medium / Low
- **Governor Limits Headroom**: [Percentage]
- **Performance Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Optimization

### Findings Table

| # | Category | Severity | Issue | Impact | Optimization |
|---|----------|----------|-------|--------|--------------|
| 1 | Bulkification | 🔴 CRITICAL | SOQL in loop (line 42) | 200 queries for 200 records | Bulkify: move query outside loop |
| 2 | Bulkification | 🔴 CRITICAL | DML in loop (line 78) | 150 DML limit reached | Batch: collect updates, single DML |
| 3 | Limits | 🟠 HIGH | Nested loop O(n²) (line 65) | CPU exceeded at 200 records | Use Map for O(1) lookup |
| 4 | Memory | 🟡 MEDIUM | String concatenation (line 112) | Heap growth exponential | Use List<String>.join() |

### Positive Findings
- ✅ Efficient pagination for large result sets (200 records/page)
- ✅ Aggregate SOQL used for reports (COUNT, SUM)
- ✅ 200-record test validates bulk operation compliance

### Overall Assessment
[Pass/Fail with optimization recommendations]
