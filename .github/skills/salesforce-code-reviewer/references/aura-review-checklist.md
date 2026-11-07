# Aura Component Review Checklist

> **Review Category**: Aura Components, Controllers, Events, Helpers  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT  
> **Note**: Aura is legacy; prefer LWC for new components

---

## 1. Component Basics

### Component Definition & Attributes

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Component defined in `.cmp` file | ☐ Pass ☐ Fail | 🟡 MEDIUM | Standard Aura format |
| `<aura:component>` wrapper present | ☐ Pass ☐ Fail | 🟡 MEDIUM | Root element of every Aura component |
| Attributes defined with `<aura:attribute>` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Specify type, default values |
| Attributes typed (not generic Object) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `type="String"` (not `type="Object"`) |
| Required attributes marked | ☐ Pass ☐ Fail | 🟡 MEDIUM | `required="true"` for mandatory inputs |
| Default values provided where appropriate | ☐ Pass ☐ Fail | ⚪ LOW | Sensible defaults improve usability |

### Event Handling

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Events defined in component | ☐ Pass ☐ Fail | 🟡 MEDIUM | `<aura:registerEvent>` for custom events |
| Event names follow camelCase | ☐ Pass ☐ Fail | 🟡 MEDIUM | `itemSelected` (not `item-selected`) |
| Event handlers use `c:[eventName]` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `c:itemSelected="{!c.handleItemSelected}"` |
| Handlers defined in controller | ☐ Pass ☐ Fail | 🟡 MEDIUM | Event handlers organized in controller |

---

## 2. Markup & Styling

### Template Markup

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Standard components from `aura:` and `ui:` | ☐ Pass ☐ Fail | 🟡 MEDIUM | `<aura:iteration>`, `<ui:inputText>` |
| Data binding with `{!}` syntax | ☐ Pass ☐ Fail | 🟡 MEDIUM | `{!v.attribute}` for view, `{!c.method}` for controller |
| Two-way binding for form inputs | ☐ Pass ☐ Fail | 🟡 MEDIUM | Changes propagate to component's backing field |
| No inline JavaScript (use controller) | ☐ Pass ☐ Fail | 🟠 HIGH | Logic in controller; markup for rendering |

### CSS Styling

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Styles in `.css` file (same name as `.cmp`) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `ComponentName.css` |
| CSS scoped to component | ☐ Pass ☐ Fail | 🟡 MEDIUM | Aura scopes CSS automatically |
| SLDS classes used for styling | ☐ Pass ☐ Fail | 🟡 MEDIUM | Salesforce Lightning Design System |
| Responsive design considered | ☐ Pass ☐ Fail | 🟡 MEDIUM | Works on mobile and desktop |

---

## 3. Controller & Logic

### Controller Structure

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Controller functions handle events | ☐ Pass ☐ Fail | 🟡 MEDIUM | `handleClick: function(cmp, evt, helper)` |
| Helper methods contain business logic | ☐ Pass ☐ Fail | 🟠 HIGH | Keep controller thin; reusable logic in helper |
| No complex calculations in controller | ☐ Pass ☐ Fail | 🟡 MEDIUM | Move to helper or server-side controller |
| Apex calls via `$A.enqueueAction()` | ☐ Pass ☐ Fail | 🟠 HIGH | Asynchronous server calls properly queued |

### Apex Server-Side Controller

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Server controller methods marked `@AuraEnabled` | ☐ Pass ☐ Fail | 🟠 HIGH | Exposes methods to Aura components |
| `@AuraEnabled(cacheable=true)` for reads | ☐ Pass ☐ Fail | 🟠 HIGH | Caches result across multiple calls |
| `@AuraEnabled(cacheable=false)` for DML | ☐ Pass ☐ Fail | 🟠 HIGH | No caching for mutations |
| Error handling in Apex methods | ☐ Pass ☐ Fail | 🟡 MEDIUM | Exceptions caught; friendly error messages returned |

---

## 4. Data Handling

### Server Communication

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Apex action callbacks defined (success/error) | ☐ Pass ☐ Fail | 🟠 HIGH | `.setCallback(this, function(response) { })` |
| State checking on response | ☐ Pass ☐ Fail | 🟠 HIGH | Check `response.getState() === 'SUCCESS'` |
| Error messages shown to user | ☐ Pass ☐ Fail | 🟡 MEDIUM | User sees message on failed action |
| Loading indicator during server calls | ☐ Pass ☐ Fail | 🟡 MEDIUM | Spinner or disabled state during fetch |

### Data Binding

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Value binding for form inputs | ☐ Pass ☐ Fail | 🟡 MEDIUM | `value="{!v.account.Name}"` |
| Calculated fields via getters | ☐ Pass ☐ Fail | 🟡 MEDIUM | Derived data computed, not stored |
| Large data pagination | ☐ Pass ☐ Fail | 🟡 MEDIUM | Don't load 50k records; use pagination |

---

## 5. Event Communication

### Custom Events

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Events follow Aura pattern | ☐ Pass ☐ Fail | 🟡 MEDIUM | `<aura:registerEvent>` and `evt.fire()` |
| Event parameters documented | ☐ Pass ☐ Fail | 🟡 MEDIUM | Document `detail` parameter structure |
| Parent/child communication clear | ☐ Pass ☐ Fail | 🟡 MEDIUM | Child → Parent via events, Parent → Child via attributes |

### App Events

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| App events used sparingly | ☐ Pass ☐ Fail | 🟡 MEDIUM | Prefer component events; app events = loose coupling but hard to track |
| App event handling cleanup | ☐ Pass ☐ Fail | 🟡 MEDIUM | Unregister handlers to prevent memory leaks |

---

## 6. Best Practices & Anti-Patterns

### Performance

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Server calls minimized | ☐ Pass ☐ Fail | 🟡 MEDIUM | Batch requests where possible |
| Large DOM avoided | ☐ Pass ☐ Fail | 🟡 MEDIUM | Render only visible items (pagination/lazy load) |
| Memory leaks prevented | ☐ Pass ☐ Fail | 🟡 MEDIUM | Cleanup listeners in `destroy` event |

### Code Quality

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Consistent naming conventions | ☐ Pass ☐ Fail | 🟡 MEDIUM | Handlers: `handle[Event]`, methods: camelCase |
| Comments for complex logic | ☐ Pass ☐ Fail | 🟡 MEDIUM | Explain WHY not WHAT |
| No duplicated code | ☐ Pass ☐ Fail | 🟡 MEDIUM | Extract common patterns to helper |
| Dead code removed | ☐ Pass ☐ Fail | ⚪ LOW | Remove unused controller methods |

---

## 7. Migration to LWC

### Aura → LWC Considerations

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Component is candidate for LWC migration | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Aura is legacy; plan migration to LWC |
| Migration path documented | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Document steps to convert to LWC |
| LWC equivalent features available | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Verify all Aura features have LWC equivalents |

---

## Review Output Template

### Aura Component Assessment
- **Component Maturity**: Well-Built / Good / Adequate / Needs Work
- **Code Quality**: [Issues found]
- **Migration Status**: Legacy / Candidate for Migration / Migrated
- **Issues Found**: [Count]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Refactoring

### Findings Table

| # | Category | Severity | Issue | Impact | Remediation |
|---|----------|----------|-------|--------|------------|
| 1 | Pattern | 📝 ENHANCEMENT | Aura component (legacy) | Maintenance burden | Plan migration to LWC |
| 2 | Apex | 🟠 HIGH | `@AuraEnabled(cacheable=true)` on DML method | Data stale | Change to `cacheable=false` |
| 3 | Controller | 🟡 MEDIUM | Business logic in controller | Hard to reuse | Move to helper methods |
| 4 | Events | 🟡 MEDIUM | Multiple app events for communication | Hard to track | Use component events instead |

### Positive Findings
- ✅ Clean separation of controller and helper
- ✅ Good error handling for server calls
- ✅ Proper pagination for large datasets

### Overall Assessment
[Component evaluation and LWC migration recommendation]
