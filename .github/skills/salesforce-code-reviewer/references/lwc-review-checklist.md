# Lightning Web Component (LWC) Review Checklist

> **Review Category**: LWC Components, Templates, JavaScript, Events, Jest Tests  
> **Severity Levels**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ⚪ LOW | 📝 ENHANCEMENT

---

## 1. Template Best Practices

### Template Structure

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| No inline expressions (no `{a + b}`, no ternary) | ☐ Pass ☐ Fail | 🔴 CRITICAL | LWC templates don't support expressions; use JS getters |
| Lightning base components preferred over custom HTML | ☐ Pass ☐ Fail | 🟠 HIGH | `<lightning-card>`, `<lightning-datatable>` etc. |
| SLDS classes used for styling | ☐ Pass ☐ Fail | 🟡 MEDIUM | Salesforce Lightning Design System for consistent look |
| Accessibility standards: aria-*, labels, roles | ☐ Pass ☐ Fail | 🟡 MEDIUM | Screen readers, keyboard navigation |
| Event handlers use kebab-case | ☐ Pass ☐ Fail | 🟡 MEDIUM | `onitemselected="{handleItemSelected}"` (handler is camelCase) |
| No `lwc:ref` for simple queries (use ID/selector) | ☐ Pass ☐ Fail | ⚪ LOW | Prefer `querySelector()`; lwc:ref for complex cases |
| No `style` attribute (use CSS classes) | ☐ Pass ☐ Fail | 🟡 MEDIUM | CSS classes = reusability; inline styles = hard to maintain |

### Conditional Rendering

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `lwc:if` / `lwc:elseif` / `lwc:else` | ☐ Pass ☐ Fail | 🟠 HIGH | Not legacy `if:true` / `if:false` |
| Conditions are simple (computed in JS getters for complex) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Template conditions should be simple boolean checks |
| No nested `lwc:if` (limit nesting depth) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Deep nesting = hard to read; extract to getter |
| Fallback UI shown when data loading | ☐ Pass ☐ Fail | 🟡 MEDIUM | Loading spinner or skeleton screen |

### List Rendering

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `lwc:for` (not manual list generation) | ☐ Pass ☐ Fail | 🟡 MEDIUM | `<template lwc:for={items} lwc:key="id">` |
| `lwc:key` set to unique value (not index) | ☐ Pass ☐ Fail | 🟠 HIGH | `lwc:key="id"` preserves state when list reorders |
| List updates via new array assignment (not mutation) | ☐ Pass ☐ Fail | 🟠 HIGH | `this.items = [...this.items, newItem]` (not `push()`) |
| Conditional inside list for sparse rendering | ☐ Pass ☐ Fail | 🟡 MEDIUM | `<template lwc:if={showItem}>` inside `lwc:for` |

---

## 2. JavaScript Best Practices

### Decorators & Properties

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Imports: `api`, `track`, `wire` from `'lwc'` | ☐ Pass ☐ Fail | 🔴 CRITICAL | Must import decorators before using |
| `@api` for parent→child communication | ☐ Pass ☐ Fail | 🟡 MEDIUM | Public properties exposed to parents |
| `@track` for reactive data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Changes trigger re-render; avoid if read-only |
| `@wire` for read-only data (services, methods) | ☐ Pass ☐ Fail | 🟠 HIGH | Reactive queries; updates when dependency changes |
| No `@track` for `@wire` properties | ☐ Pass ☐ Fail | 🟡 MEDIUM | `@wire` already reactive; @track redundant |
| Private properties not exposed as `@api` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Private = internal; `@api` = public contract |

### Lifecycle Hooks

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `connectedCallback()` for initialization | ☐ Pass ☐ Fail | 🟡 MEDIUM | Set up event listeners, fetch initial data |
| `disconnectedCallback()` for cleanup | ☐ Pass ☐ Fail | 🟡 MEDIUM | Remove listeners, cancel subscriptions, clear timers |
| `renderedCallback()` for DOM operations | ☐ Pass ☐ Fail | 🟡 MEDIUM | Access DOM after render; not before |
| No heavy processing in `renderedCallback()` | ☐ Pass ☐ Fail | 🟠 HIGH | Called after every render; defer to async |

### Event Handling

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Event names lowercase (no hyphens) | ☐ Pass ☐ Fail | 🔴 CRITICAL | `'itemselected'` (not `'item-selected'`) |
| Custom events dispatch via `dispatchEvent()` | ☐ Pass ☐ Fail | 🟠 HIGH | `this.dispatchEvent(new CustomEvent('itemselected', { detail: ... }))` |
| Parent listens with `on[event]` | ☐ Pass ☐ Fail | 🟠 HIGH | `onitemselected="{handleItemSelected}"` in template |
| Event details include all necessary data | ☐ Pass ☐ Fail | 🟡 MEDIUM | Pass via `detail` property; parent accesses `event.detail` |
| Event bubbling/canceling configured | ☐ Pass ☐ Fail | 🟡 MEDIUM | `{ bubbles: true, composed: true }` for cross-shadow-boundary |

---

## 3. Apex Integration

### @AuraEnabled Methods

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@AuraEnabled` methods exist for DML/complex logic | ☐ Pass ☐ Fail | 🟠 HIGH | LWC doesn't do DML directly; call Apex |
| `cacheable=true` only for pure reads | ☐ Pass ☐ Fail | 🔴 CRITICAL | Cached across users; no DML, no side effects |
| `cacheable=false` for user-specific or mutable data | ☐ Pass ☐ Fail | 🟠 HIGH | Recalculates per user; no caching |
| Methods properly tested (LWC calls tested) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Mock Apex methods in Jest |

### Data Binding & Imperative Calls

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@wire` used for read operations | ☐ Pass ☐ Fail | 🟠 HIGH | Reactive data binding; automatically updates |
| Imperative Apex calls for DML operations | ☐ Pass ☐ Fail | 🟠 HIGH | `import { method } from '@salesforce/apex/...'` + call directly |
| `async/await` used for imperative calls | ☐ Pass ☐ Fail | 🟠 HIGH | Cleaner than `.then()` chains |
| Error handling in imperative calls | ☐ Pass ☐ Fail | 🟠 HIGH | `catch(error)` block logs error, shows user message |
| Loading state managed during async operations | ☐ Pass ☐ Fail | 🟡 MEDIUM | Show spinner while fetching; disable inputs |

---

## 4. Data Handling & State Management

### State Management

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@track` used for mutable component state | ☐ Pass ☐ Fail | 🟡 MEDIUM | Changes trigger re-render |
| Immutable update patterns (new objects/arrays) | ☐ Pass ☐ Fail | 🟠 HIGH | `this.items = [...items, newItem]` (not `push()`) |
| No unnecessary @track properties | ☐ Pass ☐ Fail | 🟡 MEDIUM | Use computed getter if derived from other data |
| Complex state managed via Signals (advanced) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | For complex reactive state management |

### Data Fetching & Caching

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| `@wire` refresh via `wiredMethod.refresh()` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Manually refresh cached data |
| Large datasets paginated (200 records max) | ☐ Pass ☐ Fail | 🟡 MEDIUM | Load/display 200 records at a time |
| Lazy loading for large lists | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Load more on scroll/pagination click |
| No polling (subscribe to platform events instead) | ☐ Pass ☐ Fail | 📝 ENHANCEMENT | Real-time updates via platform events |

---

## 5. Navigation & Routing

### Lightning Navigation

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Uses `NavigationMixin` for navigation | ☐ Pass ☐ Fail | 🟠 HIGH | Never `window.location.href` |
| Record page navigation: `PAGE_OBJECTVIEW` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Navigate to record detail pages |
| List page navigation: `LIST_VIEW` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Navigate to list views |
| Custom page navigation: `NAMED_PAGE` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Navigate to custom pages |
| Modal vs. new tab navigation appropriate | ☐ Pass ☐ Fail | 🟡 MEDIUM | Modal for inline actions; new tab for full page |

---

## 6. Styling & CSS

### CSS Scope

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Styles in `[component].css` file | ☐ Pass ☐ Fail | 🟡 MEDIUM | Scoped to component; doesn't leak to parent |
| No `!important` in CSS | ☐ Pass ☐ Fail | 🟡 MEDIUM | Indicates fragile styling; use specificity instead |
| SLDS variables used for colors/spacing | ☐ Pass ☐ Fail | 🟡 MEDIUM | `var(--slds-c-somecomponent-color-background)` |
| Mobile responsiveness tested | ☐ Pass ☐ Fail | 🟡 MEDIUM | Works on mobile, tablet, desktop |

### Accessibility

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| ARIA labels for interactive elements | ☐ Pass ☐ Fail | 🟡 MEDIUM | `aria-label`, `aria-labelledby` for screen readers |
| Keyboard navigation supported | ☐ Pass ☐ Fail | 🟡 MEDIUM | Tab, Enter, Escape work as expected |
| Color contrast sufficient (WCAG AA minimum) | ☐ Pass ☐ Fail | 🟡 MEDIUM | 4.5:1 ratio for text; 3:1 for UI components |
| Focus indicators visible | ☐ Pass ☐ Fail | 🟡 MEDIUM | Keyboard users can see which element has focus |

---

## 7. Jest Testing

### Test Setup

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Jest tests in `__tests__/[component].test.js` | ☐ Pass ☐ Fail | 🟡 MEDIUM | Alongside component files |
| DOM cleanup in `afterEach()` | ☐ Pass ☐ Fail | 🟠 HIGH | `while (document.body.firstChild) document.body.removeChild(...)` |
| Jest configuration for LWC | ☐ Pass ☐ Fail | 🟡 MEDIUM | `jest.config.js` with `@lwc/jest-preset` |

### Test Cases

| Review Item | Status | Severity | Guidance |
|---|---|---|---|
| Component renders without errors | ☐ Pass ☐ Fail | 🟠 HIGH | Basic smoke test |
| Properties set and propagate correctly | ☐ Pass ☐ Fail | 🟡 MEDIUM | `@api` properties work as documented |
| Wire methods mocked and tested | ☐ Pass ☐ Fail | 🟠 HIGH | Mock Apex methods; verify LWC handles responses |
| Events dispatched correctly | ☐ Pass ☐ Fail | 🟡 MEDIUM | Custom events fired with correct detail |
| User interactions trigger expected behavior | ☐ Pass ☐ Fail | 🟡 MEDIUM | Click, input, submit → correct outcomes |
| Error states handled gracefully | ☐ Pass ☐ Fail | 🟡 MEDIUM | API error → user-facing error message |
| Loading states shown | ☐ Pass ☐ Fail | 🟡 MEDIUM | Spinner shown while fetching data |

---

## Review Output Template

### LWC Assessment
- **Component Maturity**: Well-Built / Good / Adequate / Needs Work
- **Template Quality**: [Issues found]
- **JavaScript Quality**: [Issues found]
- **Test Coverage**: [Percentage]
- **Accessibility**: [WCAG compliance level]
- **Pass/Fail**: ✅ Pass | ⚠️ Pass with Notes | ❌ Needs Refactoring

### Findings Table

| # | Category | Severity | Issue | Impact | Remediation |
|---|----------|----------|-------|--------|------------|
| 1 | Template | 🔴 CRITICAL | Inline expressions: `{a + b}` | Won't render | Use JS getter: `get sum() { return a + b; }` |
| 2 | Events | 🔴 CRITICAL | Event name `item-selected` (hyphenated) | Event won't fire | Change to `itemselected` |
| 3 | Apex | 🟠 HIGH | `@AuraEnabled(cacheable=true)` on method with DML | Data stale for other users | Change to `cacheable=false` |
| 4 | Testing | 🟡 MEDIUM | No Jest tests present | Untestable | Add `__tests__/component.test.js` |
| 5 | Navigation | 🟠 HIGH | Uses `window.location.href` | Breaks Salesforce navigation | Use `NavigationMixin` |

### Positive Findings
- ✅ Clean component structure with proper lifecycle hooks
- ✅ Excellent accessibility (WCAG AA compliant)
- ✅ Comprehensive Jest test coverage (87%)
- ✅ Good use of SLDS components

### Overall Assessment
[Component evaluation and recommendations]
