# Salesforce Lightning Web Components (LWC) Coding Rules — Vibe Coding Ruleset

**A comprehensive, tool-agnostic LWC coding ruleset for AI-assisted development tools (GitHub Copilot, Cursor, Claude Code, Windsurf, etc.)**

---
document_id: "RULESET_LWC_CODING_STANDARDS"
status: "Published"
classification: "Public"
last_updated: "2026-02-24"
audience: [Developers, AI_Assistants, Vibe_Coders]
usage: "Drop into .github/copilot-instructions.md, .cursor/rules/, .cursorrules, AGENTS.md, or any AI coding tool's instruction layer"
---

## How to Use This Document

This is a **copy-paste-ready** ruleset. Depending on your tool:

| Tool | Where to Place These Rules |
|------|---------------------------|
| **GitHub Copilot (VS Code)** | `.github/copilot-instructions.md` or `.instructions.md` in `force-app/main/default/lwc/` |
| **Cursor** | `.cursor/rules/lwc.md` (with frontmatter: `globs: "**/*.js, **/*.html, **/*.css"` inside `lwc/`) |
| **Claude Code** | `CLAUDE.md` in project root |
| **Windsurf** | `.windsurfrules` in project root |
| **Cline / Roo Code** | `.clinerules` or `.roo/rules/` |
| **Universal** | `AGENTS.md` in project root |

---

## Table of Contents

1. [General LWC Standards](#1-general-lwc-standards)
2. [Component Structure & File Organization](#2-component-structure--file-organization)
3. [Naming Conventions](#3-naming-conventions)
4. [HTML Template Rules](#4-html-template-rules)
5. [JavaScript Rules](#5-javascript-rules)
6. [Reactive Properties & State Management](#6-reactive-properties--state-management)
7. [Wire Service Rules](#7-wire-service-rules)
8. [Imperative Apex Calls](#8-imperative-apex-calls)
9. [Lightning Data Service (LDS) Rules](#9-lightning-data-service-lds-rules)
10. [Event Handling Rules](#10-event-handling-rules)
11. [CSS Styling Rules](#11-css-styling-rules)
12. [Navigation Rules](#12-navigation-rules)
13. [Error Handling & User Feedback](#13-error-handling--user-feedback)
14. [Security Rules](#14-security-rules)
15. [Performance Rules](#15-performance-rules)
16. [Accessibility (a11y) Rules](#16-accessibility-a11y-rules)
17. [Testing Rules (Jest)](#17-testing-rules-jest)
18. [Component Communication Patterns](#18-component-communication-patterns)
19. [Metadata & Configuration Rules](#19-metadata--configuration-rules)
20. [Salesforce Base Components Usage](#20-salesforce-base-components-usage)
21. [Integration with Flows & Agentforce](#21-integration-with-flows--agentforce)
22. [Light DOM & Advanced Directives](#22-light-dom--advanced-directives)
23. [Lightning Web Security (LWS)](#23-lightning-web-security-lws)
24. [ESLint Rules & Static Analysis](#24-eslint-rules--static-analysis)
25. [Anti-Patterns to Avoid](#25-anti-patterns-to-avoid)
26. [Common LWC Runtime Errors & Prevention](#26-common-lwc-runtime-errors--prevention-stackexchange-top-issues)

---

## 1. General LWC Standards

```
RULES:
- Use API version 66.0 (Spring '26) or later for all new LWC components. Keep all components on the same API version.
- Follow the Web Components standard — LWC is built on it.
- Every component must work correctly in both Lightning Experience and the Salesforce mobile app unless explicitly scoped.
- Components must be self-contained — no external CDN dependencies (jQuery, Bootstrap, etc.) embedded directly. Use Static Resources or standard SLDS if needed.
- All LWC code must pass ESLint with the @salesforce/eslint-config-lwc ruleset.
- Never modify the DOM directly using querySelector and imperative DOM manipulation when a reactive/declarative approach is available.
- All components must handle loading, empty, and error states gracefully.
- No console.log statements in production code. Use a custom logging utility or remove before deployment.
- Every component must have a corresponding -meta.xml configuration file.
- Prefer composition (smaller, reusable child components) over monolithic components.
```

---

## 2. Component Structure & File Organization

```
RULES:
- Every LWC component is a folder inside force-app/main/default/lwc/ containing at minimum:
    myComponent/
    ├── myComponent.html          (template — required)
    ├── myComponent.js            (JavaScript controller — required)
    ├── myComponent.js-meta.xml   (metadata config — required)
    ├── myComponent.css           (styles — optional)
    ├── __tests__/                (Jest tests — required for all components)
    │   └── myComponent.test.js
    └── myComponent.svg           (custom icon — optional)

- Component folder names must be camelCase and match the JS class file name.
- Maximum component file length guidelines:
    - HTML: aim for under 200 lines. Extract child components if larger.
    - JS: aim for under 300 lines. Extract utilities into shared modules.
    - CSS: aim for under 150 lines. Use CSS custom properties for theming.
- Shared utility modules go in a dedicated LWC service component (no HTML, just JS exports):
    lwc/
    ├── utils/
    │   ├── utils.js               (export helper functions)
    │   └── utils.js-meta.xml      (isExposed: false)
    ├── constants/
    │   ├── constants.js           (export shared constants)
    │   └── constants.js-meta.xml

- Group related components with a naming prefix:
    caseRouting/          → parent
    caseRoutingList/      → child: list view
    caseRoutingDetail/    → child: detail view
    caseRoutingFilter/    → child: filter bar
```

---

## 3. Naming Conventions

```
RULES:
- Component folder/file names: camelCase → myComponent, caseRoutingList, leadScoreCard
- HTML tags in parent templates: kebab-case with c- namespace → <c-my-component>, <c-case-routing-list>
- JavaScript class names: PascalCase → export default class MyComponent extends LightningElement
- Public properties (@api): camelCase → @api recordId, @api objectApiName
- Private reactive properties: camelCase, NO underscore prefix for tracked fields → count, isLoading, errorMessage
- Private non-reactive properties: camelCase with underscore prefix → _internalState, _cachedValue
- Event names: lowercase only, no hyphens or uppercase in the event type string (underscores are valid for namespaced events like 'mydomain__myevent'):
    - Dispatch: this.dispatchEvent(new CustomEvent('itemselected', { detail: data }))
    - Listen in parent HTML: onitemselected={handleItemSelected}
- Handler methods: handle[EventDescription] → handleClick, handleSave, handleCaseSelected
- Wire methods/properties: use descriptive names → wiredAccounts, wiredCaseResult
- Constants: UPPER_SNAKE_CASE → MAX_RECORDS, DEFAULT_PAGE_SIZE, COLUMNS
- Boolean properties: prefix with is, has, should, can → isLoading, hasError, shouldRefresh, canEdit
- CSS classes: kebab-case following SLDS conventions → .container-header, .card-body, .action-bar

MAPPING — Component Name to HTML Tag:
    JS/Folder: caseRoutingList
    HTML Tag:  <c-case-routing-list>
    
    JS/Folder: leadScoreCard  
    HTML Tag:  <c-lead-score-card>
```

---

## 4. HTML Template Rules

```
RULES:
- The root element of every template must be <template>.
- Use <template> directives for conditionals and loops:
    - lwc:if|elseif|else (preferred, modern):
        <template lwc:if={isLoading}>
            <lightning-spinner alternative-text="Loading"></lightning-spinner>
        </template>
        <template lwc:elseif={hasError}>
            <c-error-panel message={errorMessage}></c-error-panel>
        </template>
        <template lwc:else>
            <!-- main content -->
        </template>
    
    - No longer recommended (may be deprecated in a future release) — Do NOT use if:true / if:false. Use lwc:if|elseif|else instead.

- Use for:each for iteration with a key:
    <template for:each={accounts} for:item="account">
        <div key={account.Id}>{account.Name}</div>
    </template>
    
    - The key directive is MANDATORY on the direct child element of for:each.
    - key must be a unique, stable identifier (use record Id, not array index).

- Use iterator for first/last detection:
    <template iterator:it={items}>
        <div key={it.value.Id} class={it.first ? 'first-item' : ''}>
            {it.value.Name}
        </div>
    </template>

- Never use innerHTML or lwc:dom="manual" unless absolutely necessary (e.g., rendering rich text from a trusted source).
- Always escape user-provided content — LWC templates auto-escape by default. Don't bypass this.
- Use lightning-formatted-* components for displaying data (currency, dates, numbers, etc.):
    <lightning-formatted-number value={amount} format-style="currency" currency-code="USD">
    </lightning-formatted-number>
- Limit template depth — flatten deeply nested structures into child components.
- Always provide alternative-text for lightning-icon and lightning-spinner.
- Use SLDS utility classes via lightning-layout and lightning-layout-item for responsive grids:
    <lightning-layout multiple-rows>
        <lightning-layout-item size="12" medium-device-size="6" large-device-size="4">
            <!-- content -->
        </lightning-layout-item>
    </lightning-layout>
```

---

## 5. JavaScript Rules

```
RULES:
- Always extend LightningElement:
    import { LightningElement, api, wire, track } from 'lwc';
    export default class MyComponent extends LightningElement { }

- Use ES6+ features consistently:
    - const/let (never var)
    - Arrow functions for callbacks and inline functions
    - Template literals for string interpolation
    - Destructuring for cleaner parameter handling
    - Spread/rest operators
    - Optional chaining (?.) and nullish coalescing (??)
    - async/await for asynchronous operations (not raw Promises with .then chains in complex flows)

- Import Apex methods explicitly:
    import getAccounts from '@salesforce/apex/AccountController.getAccounts';

- Import labels, custom permissions, schema, and user info:
    import ACCOUNT_NAME_FIELD from '@salesforce/schema/Account.Name';
    import GREETING_LABEL from '@salesforce/label/c.Greeting';
    import userId from '@salesforce/user/Id';
    import HAS_CUSTOM_PERMISSION from '@salesforce/customPermission/MyPermission';

- Never access the DOM in the constructor. Use connectedCallback() for initialization logic.
- Lifecycle hooks execution order:
    1. constructor() → Initialize state, NO DOM access, NO @api properties yet
    2. connectedCallback() → Component inserted into DOM, can access @api props, start data fetching
    3. renderedCallback() → DOM rendered, use for post-render DOM interaction (guard against infinite loops)
    4. disconnectedCallback() → Cleanup (remove event listeners, clear intervals, abort controllers)
    5. errorCallback(error, stack) → Catch errors from child component tree

- Always clean up in disconnectedCallback():
    - Remove window/document event listeners
    - Clear setInterval/setTimeout references
    - Abort any pending fetch calls
    - Unsubscribe from message channels or Emp API

- Guard renderedCallback() with a flag to prevent infinite re-renders:
    renderedCallback() {
        if (this._isRendered) return;
        this._isRendered = true;
        // DOM manipulation
    }

- Do NOT use setTimeout/setInterval as a way to "wait for the DOM." Use renderedCallback() or requestAnimationFrame instead.
- this.template.querySelector() returns null if the element is not rendered yet. Only use it in renderedCallback() or after user interaction — never in constructor() or connectedCallback().
- Prefer lwc:ref over this.template.querySelector() for direct element references — it's safer and more readable (see Section 22).
- Never use document.querySelector() — use this.template.querySelector() to stay within the shadow DOM boundary.
- Use getter methods for computed/derived values in templates:
    get fullName() {
        return `${this.firstName} ${this.lastName}`;
    }
    get hasRecords() {
        return this.records && this.records.length > 0;
    }
```

---

## 6. Reactive Properties & State Management

```
RULES:
- Public reactive properties use @api:
    @api recordId;
    @api objectApiName;
    
    - Non-primitive @api values passed from a parent are wrapped in a read-only proxy — you cannot mutate nested properties (e.g., this.obj.name = 'x' throws). Reassignment (this.obj = {...}) works locally but does NOT propagate back to the parent (one-way data flow). Avoid reassigning @api values — copy to a private property instead.
    - To work with an @api value internally, copy it to a private property:
        @api get selectedId() { return this._selectedId; }
        set selectedId(value) { this._selectedId = value; }
        _selectedId;

- Private reactive properties are reactive by default in modern LWC (no decorator needed):
    isLoading = false;
    records = [];
    errorMessage;
    
    - Assigning a new value to a class field triggers re-render automatically.
    - For objects and arrays, you must reassign (not mutate) to trigger reactivity:
        // GOOD — triggers re-render:
        this.records = [...this.records, newRecord];
        this.filters = { ...this.filters, status: 'Active' };
        
        // BAD — does NOT trigger re-render:
        this.records.push(newRecord);
        this.filters.status = 'Active';

- @track is only needed for deep reactivity on nested objects/arrays where you want to detect deep property changes:
    @track complexData = { nested: { value: 1 } };
    // Changing this.complexData.nested.value WILL trigger re-render with @track
    
    In most modern LWC code, @track is unnecessary — prefer immutable patterns (spread/reassign).

- Never store large datasets in reactive properties — use pagination or virtualization.
- Keep component state minimal — derive from existing state via getters when possible.
- Reset state explicitly when the component is reused (e.g., in list iterations or dynamic component creation).
```

---

## 7. Wire Service Rules

```
RULES:
- Prefer wire service over imperative Apex calls for read operations.
- Wire functions are reactive and automatically re-invoke when parameters change.
- Wire to a property for simple use cases:
    @wire(getRecord, { recordId: '$recordId', fields: [NAME_FIELD] })
    account;
    
    - Access data: this.account.data
    - Access error: this.account.error

- Wire to a function for more control:
    @wire(getAccounts, { searchKey: '$searchTerm' })
    wiredAccounts({ error, data }) {
        if (data) {
            this.accounts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.accounts = undefined;
        }
    }

- Use the $ prefix for reactive wire parameters — the wire re-fires when the property changes:
    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    // '$recordId' means: re-fetch whenever this.recordId changes

- Never call imperative Apex inside a wire function — it creates unpredictable side effects.
- Always handle both data and error in wire provisions.
- For wire adapters that return data: check for undefined (initial render) vs null vs data:
    get hasData() {
        return this.wiredResult && this.wiredResult.data && this.wiredResult.data.length > 0;
    }

- Use getRecord and getFieldValue for individual record operations:
    import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
    import ACCOUNT_NAME from '@salesforce/schema/Account.Name';
    
    @wire(getRecord, { recordId: '$recordId', fields: [ACCOUNT_NAME] })
    account;
    
    get accountName() {
        return getFieldValue(this.account.data, ACCOUNT_NAME);
    }

- Use lightning/uiListsApi (getListInfoByName, etc.) for list views. Note: getListUi (lightning/uiListApi) is deprecated.
- Use getRelatedListRecords from lightning/uiRelatedListApi for related list data.
- Wire parameters that are undefined cause the wire to NOT fire. Use null to indicate "no filter."
- Do NOT use wire for operations that have side effects (create, update, delete) — use imperative calls.

STANDARD WIRE ADAPTERS TO PREFER:
    lightning/uiRecordApi:
        getRecord, getFieldValue, getFieldDisplayValue, createRecord, updateRecord, deleteRecord
    lightning/uiObjectInfoApi:
        getObjectInfo, getPicklistValues, getPicklistValuesByRecordType
    lightning/uiRelatedListApi:
        getRelatedListRecords, getRelatedListCount
```

---

## 8. Imperative Apex Calls

```
RULES:
- Use imperative Apex calls for operations with side effects (insert, update, delete, callouts).
- Always use async/await pattern (preferred over .then/.catch chains):
    import saveCase from '@salesforce/apex/CaseController.saveCase';
    
    async handleSave() {
        this.isLoading = true;
        try {
            const result = await saveCase({ caseRecord: this.caseData });
            this.showToast('Success', 'Case saved successfully', 'success');
            // navigate or refresh
        } catch (error) {
            this.handleError(error);
        } finally {
            this.isLoading = false;
        }
    }

- Always show a loading state during Apex calls.
- Always handle errors with try/catch.
- Always reset loading state in the finally block.
- Use @AuraEnabled(cacheable=true) on Apex methods that are read-only for wire compatibility:
    - cacheable=true means the method cannot perform DML, send emails, or enqueue jobs.
    - Data is cached client-side. Use refreshApex() to force a re-fetch:
        import { refreshApex } from '@salesforce/apex';
        
        @wire(getAccounts)
        wiredAccountResult;
        
        async handleRefresh() {
            await refreshApex(this.wiredAccountResult);
        }
    
    - IMPORTANT: Pass the entire wire result to refreshApex, not just the data.

- Use @AuraEnabled (without cacheable) for methods that perform DML or have side effects.
- Apex method parameters:
    - Primitive types, Lists, Maps, and SObject types are supported.
    - Parameter names in JS must EXACTLY match the Apex method parameter names.
    - Pass SObject data as plain objects — LWC serializes them automatically:
        await saveCase({ caseRecord: { Subject: 'New Case', Priority: 'High' } });
    
- For complex operations, return wrapper/DTO classes from Apex, not raw SObjects.
- Never expose more data from Apex than the component needs.
```

---

## 9. Lightning Data Service (LDS) Rules

```
RULES:
- Use Lightning Data Service (lightning-record-form, lightning-record-edit-form, lightning-record-view-form) 
  whenever possible instead of custom Apex for standard CRUD operations.
- LDS provides automatic caching, conflict detection, and security-enforced access — less code, fewer bugs.

- lightning-record-form (auto-generates UI based on layout):
    <lightning-record-form
        record-id={recordId}
        object-api-name="Account"
        layout-type="Full"
        mode="view"
        onsuccess={handleSuccess}
        onerror={handleError}>
    </lightning-record-form>

- lightning-record-edit-form (custom layout with individual fields):
    <lightning-record-edit-form
        record-id={recordId}
        object-api-name="Case"
        onsuccess={handleSuccess}
        onerror={handleError}>
        <lightning-input-field field-name="Subject"></lightning-input-field>
        <lightning-input-field field-name="Priority"></lightning-input-field>
        <lightning-button type="submit" label="Save"></lightning-button>
    </lightning-record-edit-form>

- lightning-record-view-form (read-only custom layout):
    <lightning-record-view-form record-id={recordId} object-api-name="Account">
        <lightning-output-field field-name="Name"></lightning-output-field>
        <lightning-output-field field-name="Industry"></lightning-output-field>
    </lightning-record-view-form>

- Use createRecord, updateRecord, deleteRecord from lightning/uiRecordApi for programmatic operations:
    import { createRecord } from 'lightning/uiRecordApi';
    
    const fields = { Subject: 'New Case', Priority: 'High' };
    const recordInput = { apiName: 'Case', fields };
    const record = await createRecord(recordInput);

- Always handle onsuccess and onerror events on record forms.
- Use getRecordNotifyChange to refresh wire adapters after imperative DML (deprecated in favor of notifyRecordUpdateAvailable):
    import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
    await notifyRecordUpdateAvailable([{ recordId: this.recordId }]);
```

---

## 10. Event Handling Rules

```
RULES:
- Use CustomEvent for child-to-parent communication:
    // Child dispatches:
    this.dispatchEvent(new CustomEvent('caseselected', {
        detail: { caseId: this.selectedCaseId, caseName: this.selectedName }
    }));
    
    // Parent listens (in HTML):
    <c-case-list oncaseselected={handleCaseSelected}></c-case-list>
    
    // Parent handler (in JS):
    handleCaseSelected(event) {
        this.selectedCaseId = event.detail.caseId;
    }

- Event name rules:
    - Lowercase, no hyphens or uppercase in the event type string.
    - Underscores are valid (e.g., namespaced events: 'mydomain__myevent').
    - GOOD: 'caseselected', 'itemadded', 'statuschanged', 'case_selected'
    - BAD: 'case-selected', 'CaseSelected', 'Case-Selected'
    - In parent HTML, prefix with "on": oncaseselected, onitemadded, oncase_selected

- Use bubbles: true and composed: true ONLY when the event must cross shadow DOM boundaries (rare):
    new CustomEvent('globalnotification', { 
        detail: data, 
        bubbles: true, 
        composed: true 
    });
    - Default: bubbles=false, composed=false (event stays within the parent-child boundary — preferred).

- For sibling or unrelated component communication, use Lightning Message Service (LMS):
    import { publish, subscribe, unsubscribe, MessageContext } from 'lightning/messageService';
    import CASE_SELECTED_CHANNEL from '@salesforce/messageChannel/CaseSelected__c';
    
    @wire(MessageContext) messageContext;
    
    // Publish:
    publish(this.messageContext, CASE_SELECTED_CHANNEL, { caseId: id });
    
    // Subscribe:
    connectedCallback() {
        this.subscription = subscribe(this.messageContext, CASE_SELECTED_CHANNEL, (message) => {
            this.handleMessage(message);
        });
    }
    
    // Always unsubscribe in disconnectedCallback:
    disconnectedCallback() {
        unsubscribe(this.subscription);
        this.subscription = null;
    }

- For communication between LWC and Aura (or Visualforce), use LMS.
- Never use window.postMessage for component communication within Lightning — use LMS.
- Prefer Lightning Message Service (LMS) over custom pub-sub utilities for cross-component communication. A pub-sub utility is still valid per Salesforce docs, but LMS is the recommended standard.
- Keep event payloads small and serializable. Don't pass entire SObject records — pass IDs and let the receiver query.
- Use stopPropagation() sparingly and only when you explicitly need to prevent bubbling.
```

---

## 11. CSS Styling Rules

```
RULES:
- LWC components use Shadow DOM — CSS is scoped to the component by default.
- Use Salesforce Lightning Design System (SLDS) classes and tokens:
    - Import tokens: use CSS custom properties from SLDS (--slds-c-*, --sds-c-*)
    - Use lightning-* base components which have SLDS built in.
- Strictly use SLDS utility classes for styling. Avoid writing custom CSS unless absolutely necessary — SLDS covers most layout, spacing, typography, and color needs.
- When custom CSS is unavoidable, document the reason in a comment.

- Use :host selector for component-level styling:
    :host {
        display: block;
        padding: var(--lwc-spacingMedium);
    }

- Use :host() with a selector for conditional styling:
    :host(.compact) {
        padding: var(--lwc-spacingSmall);
    }

- Never use !important unless absolutely necessary to override base component styles (and document why).
- Never use global CSS selectors that leak outside the shadow DOM.
- Use CSS custom properties for theming and configurability:
    :host {
        --card-background: var(--lwc-colorBackground, #ffffff);
    }
    .card {
        background: var(--card-background);
    }

- Use relative units (rem, em, %) instead of fixed pixels for responsive design.
- Use SLDS spacing tokens:
    padding: var(--lwc-spacingSmall);    /* 0.5rem */
    padding: var(--lwc-spacingMedium);   /* 1rem */
    padding: var(--lwc-spacingLarge);    /* 1.5rem */

- Never use inline styles in HTML templates. Use CSS classes.
- Use lightning-layout and lightning-layout-item for responsive grid layouts instead of custom CSS grids / flexbox (unless the layout is too complex for the base components).
- For custom icons, include an SVG file in the component bundle (myComponent.svg).
```

---

## 12. Navigation Rules

```
RULES:
- Use the NavigationMixin for all navigation in LWC:
    import { NavigationMixin } from 'lightning/navigation';
    export default class MyComponent extends NavigationMixin(LightningElement) { }

- Navigate to a record page:
    this[NavigationMixin.Navigate]({
        type: 'standard__recordPage',
        attributes: {
            recordId: this.recordId,
            objectApiName: 'Case',
            actionName: 'view'   // 'view', 'edit', 'clone'
        }
    });

- Navigate to a list view:
    this[NavigationMixin.Navigate]({
        type: 'standard__objectPage',
        attributes: {
            objectApiName: 'Account',
            actionName: 'list'
        },
        state: {
            filterName: 'Recent'
        }
    });

- Navigate to a custom app page or tab:
    this[NavigationMixin.Navigate]({
        type: 'standard__navItemPage',
        attributes: {
            apiName: 'My_Custom_Tab'
        }
    });

- Navigate to a web page:
    this[NavigationMixin.Navigate]({
        type: 'standard__webPage',
        attributes: {
            url: 'https://example.com'
        }
    });

- Generate a URL without navigating (for href attributes):
    this[NavigationMixin.GenerateUrl]({
        type: 'standard__recordPage',
        attributes: { recordId: id, actionName: 'view' }
    }).then(url => { this.recordUrl = url; });

- Never use window.location.href or window.open for navigation within Lightning.
- Never hardcode URLs to Salesforce pages — always use NavigationMixin.
```

---

## 13. Error Handling & User Feedback

```
RULES:
- Always handle errors from wire services and imperative Apex calls.
- Display user-friendly error messages — never show raw Apex exceptions to users.
- Prefer lightning/toast (the modern API) for toast notifications. Use lightning/platformShowToastEvent as a fallback:
    // PREFERRED — lightning/toast (supports inline links, works in more environments):
    import LightningToast from 'lightning/toast';
    
    async showToast(label, message, variant) {
        await LightningToast.show({ label, message, variant }, this);
    }
    
    // FALLBACK — lightning/platformShowToastEvent (NOT supported on LWR Experience Cloud sites, login pages in Aura sites, or standalone apps):
    import { ShowToastEvent } from 'lightning/platformShowToastEvent';
    
    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({
            title: title,
            message: message,
            variant: variant   // 'success', 'error', 'warning', 'info'
        }));
    }

- Create a reusable error handling utility:
    reduceErrors(errors) {
        if (!Array.isArray(errors)) {
            errors = [errors];
        }
        return errors
            .filter(error => !!error)
            .map(error => {
                if (Array.isArray(error.body)) {
                    return error.body.map(e => e.message);
                } else if (error.body && typeof error.body.message === 'string') {
                    return error.body.message;
                } else if (typeof error.message === 'string') {
                    return error.message;
                }
                return error.statusText || 'Unknown error';
            })
            .reduce((prev, curr) => prev.concat(curr), []);
    }

- Always show loading spinners during async operations:
    <template lwc:if={isLoading}>
        <lightning-spinner alternative-text="Loading" size="medium"></lightning-spinner>
    </template>

- Show empty states when there's no data:
    <template lwc:if={isEmpty}>
        <div class="slds-illustration slds-illustration_small">
            <p>No records found. Try adjusting your filters.</p>
        </div>
    </template>

- Use errorCallback() lifecycle hook to catch errors from child components:
    errorCallback(error, stack) {
        this.error = error;
        console.error('Error in child component:', error, stack);
    }

- In forms, use reportValidity() to show field-level validation errors:
    handleSubmit() {
        const allValid = [...this.template.querySelectorAll('lightning-input')]
            .reduce((validSoFar, inputCmp) => {
                inputCmp.reportValidity();
                return validSoFar && inputCmp.checkValidity();
            }, true);
        if (allValid) {
            // proceed with save
        }
    }

- Never use window.alert(), window.confirm(), or window.prompt() — they do not work in Lightning because LWC runs in cross-origin iframes where browsers (Chrome, Safari) suppress these dialogs. Use the platform replacements: lightning/alert, lightning/confirm, and lightning/prompt modules, or ShowToastEvent for simple notifications.
```

---

## 14. Security Rules

```
RULES:
- Never use lwc:dom="manual" with unsanitized HTML content — it opens XSS vulnerabilities.
- LWC templates automatically escape expressions — never bypass this.
- Never store sensitive data (tokens, passwords) in component state or local storage.
- Use Custom Permissions to control component visibility:
    import HAS_ADMIN_ACCESS from '@salesforce/customPermission/Admin_Access';
    
    get showAdminPanel() {
        return HAS_ADMIN_ACCESS;
    }

- All data security must be enforced server-side (in Apex). Never rely on client-side checks alone.
- Use @AuraEnabled methods with proper sharing context (with sharing) in the backing Apex.
- Validate user input on the server side — client-side validation is for UX, not security.
- Use Content Security Policy (CSP) trusted sites for external resource loading.
- Never use eval(), Function(), or innerHTML with dynamic content.
- LWC components run under Lightning Web Security (LWS) — see Section 23 for detailed LWS rules and restrictions.
- Use lightning/platformResourceLoader for loading static resources (JS/CSS) — never inject scripts via DOM manipulation.
- In Experience Cloud (Community), be especially cautious about data exposure. Use isGuestUser to conditionally hide data.
```

---

## 15. Performance Rules

```
RULES:
- Minimize wire adapter calls — each one is a server round trip.
- Use @AuraEnabled(cacheable=true) wherever possible for client-side caching.
- Implement pagination for lists — never load all records at once:
    - Use OFFSET/LIMIT in Apex
    - Or use lightning-datatable with infinite loading
- Lazy load components and data:
    - Use lwc:if to defer rendering of off-screen components.
    - Don't fetch data in constructor — wait for connectedCallback.
- Avoid expensive computations in getters — they fire on every re-render. Cache results:
    get processedData() {
        if (!this._cachedData || this._dataChanged) {
            this._cachedData = this.rawData.map(/* heavy transform */);
            this._dataChanged = false;
        }
        return this._cachedData;
    }

- Debounce search/filter inputs:
    handleSearchKeyChange(event) {
        window.clearTimeout(this._delayTimeout);
        const searchKey = event.target.value;
        this._delayTimeout = setTimeout(() => {
            this.searchKey = searchKey;
        }, 300);
    }

- Use lightning-datatable with enableInfiniteLoading for large datasets.
- Minimize DOM size — fewer elements = faster rendering. Use pagination, virtual scrolling, or collapsible sections.
- Keep component nesting shallow — deep nesting impacts render performance.
- Avoid unnecessary re-renders:
    - Don't reassign the same value to a reactive property.
    - Use immutable patterns to ensure the framework detects actual changes.
- Use lightning/uiRecordApi instead of custom Apex for standard record operations — it uses LDS caching.
- Do NOT use getRecordUi — it is deprecated. Use getRecord + getLayout (from lightning/uiLayoutApi) instead for record page data.
- Import only what you need from modules:
    import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
    // NOT: import * as uiRecordApi from 'lightning/uiRecordApi';
```

---

## 16. Accessibility (a11y) Rules

```
RULES:
- All components must be keyboard navigable.
- Always provide alternative-text on lightning-icon, lightning-spinner, and images.
- Use semantic HTML elements (button, a, label, h1-h6, etc.) instead of styled divs for interactive elements.
- Associate labels with form inputs:
    <lightning-input label="Case Subject" value={subject}></lightning-input>
    - lightning-input has built-in label support. For custom inputs, use <label for="...">

- Use aria-* attributes for dynamic content:
    <div role="alert" aria-live="polite">{statusMessage}</div>
    <button aria-expanded={isExpanded} aria-controls="panel-id">Toggle</button>

- Ensure color is not the only means of conveying information (add text/icons alongside color cues).
- Test with screen readers (NVDA, VoiceOver) and keyboard-only navigation.
- Use SLDS assistive text patterns:
    <span class="slds-assistive-text">Close dialog</span>

- Focus management:
    - Set focus to the first interactive element when a modal opens.
    - Return focus to the trigger element when a modal closes.
    - Use this.template.querySelector('...').focus() for programmatic focus.
- Support reduced motion preferences:
    @media (prefers-reduced-motion: reduce) {
        .animated-element { animation: none; }
    }

- Minimum color contrast: 4.5:1 for normal text, 3:1 for large text (WCAG 2.1 AA).
- Interactive elements must have a minimum touch target size of 44x44 CSS pixels on mobile.
```

---

## 17. Testing Rules (Jest)

```
RULES:
- Every LWC component must have Jest tests in a __tests__/ directory inside the component folder.
- Test file naming: [componentName].test.js
- Install and configure LWC Jest:
    npm install --save-dev @salesforce/sfdx-lwc-jest
    // Or use: sf force lightning lwc test setup

- Run tests with: npm run test:unit or sfdx-lwc-jest

- Test structure:
    import { createElement } from 'lwc';
    import MyComponent from 'c/myComponent';
    
    describe('c-my-component', () => {
        afterEach(() => {
            // Clean up DOM after each test
            while (document.body.firstChild) {
                document.body.removeChild(document.body.firstChild);
            }
        });
        
        it('displays account name when data is loaded', async () => {
            const element = createElement('c-my-component', { is: MyComponent });
            document.body.appendChild(element);
            
            // assertions
        });
    });

- ALWAYS clean up DOM in afterEach — prevents test pollution.
- Mock Apex methods:
    jest.mock('@salesforce/apex/AccountController.getAccounts', () => ({
        default: jest.fn()
    }), { virtual: true });

- Mock wire adapters:
    import { registerLdsTestWireAdapter } from '@salesforce/sfdx-lwc-jest';
    import { getRecord } from 'lightning/uiRecordApi';
    const getRecordAdapter = registerLdsTestWireAdapter(getRecord);
    
    // In test:
    getRecordAdapter.emit(mockData);

- Mock Lightning Message Service:
    jest.mock('lightning/messageService', () => ({
        publish: jest.fn(),
        subscribe: jest.fn(),
        MessageContext: jest.fn()
    }), { virtual: true });

- Mock navigation:
    import { getNavigateCalledWith } from 'lightning/navigation';
    // Assert navigation was called correctly

- Test categories to include:
    1. Rendering: Does the component render correct HTML?
    2. User interaction: Click, input change, form submit — do handlers fire correctly?
    3. Wire: Does the component handle wired data and errors?
    4. Events: Are custom events dispatched with correct detail?
    5. Edge cases: Null data, empty arrays, error states, loading states
    6. Accessibility: Does the component have correct aria attributes?

- Use flushPromises() to resolve async operations in tests:
    function flushPromises() {
        return new Promise(resolve => setTimeout(resolve, 0));
    }
    
    // In test:
    await flushPromises();
    // Now assert on DOM updates

- Test user-visible behavior, not implementation details. Don't test private methods directly.
- Use descriptive test names: 'displays error panel when Apex call fails'
```

---

## 18. Component Communication Patterns

```
RULES — CHOOSE THE RIGHT PATTERN:

| Communication Type | Pattern | When to Use |
|--------------------|---------|-------------|
| Parent → Child | @api properties | Passing data down the component tree |
| Parent → Child method call | @api method | Parent needs to trigger child action (e.g., refresh, reset) |
| Child → Parent | CustomEvent | Child notifies parent of an action/state change |
| Sibling ↔ Sibling | Lightning Message Service (LMS) | Components on the same page that don't share a parent |
| Any ↔ Any (same page) | Lightning Message Service (LMS) | Cross-component communication regardless of hierarchy |
| LWC ↔ Aura | Lightning Message Service (LMS) | Cross-framework communication |
| Cross-page | URL parameters or Platform Events | Navigation with state, or real-time updates |

- Parent → Child (@api properties):
    // Parent HTML:
    <c-child-component selected-id={activeId} mode="edit"></c-child-component>
    
    // Child JS:
    @api selectedId;
    @api mode;

- Parent → Child method (@api method):
    // Child JS:
    @api
    refresh() {
        // refresh data
    }
    
    // Parent JS:
    this.template.querySelector('c-child-component').refresh();

- Never reach into child component internals. Only use public @api properties and methods.
- Never use global JavaScript events (window.addEventListener) for component communication. Use LMS.
- Keep data flow unidirectional wherever possible: Parent → Child for data, Child → Parent for events.
```

---

## 19. Metadata & Configuration Rules

```
RULES:
- Every LWC must have a .js-meta.xml file:
    <?xml version="1.0" encoding="UTF-8"?>
    <LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
        <apiVersion>66.0</apiVersion>
        <isExposed>true</isExposed>
        <masterLabel>Case Routing Dashboard</masterLabel>
        <description>Displays and manages case routing assignments</description>
        <targets>
            <target>lightning__RecordPage</target>
            <target>lightning__AppPage</target>
            <target>lightning__HomePage</target>
            <target>lightning__FlowScreen</target>
        </targets>
        <targetConfigs>
            <targetConfig targets="lightning__RecordPage">
                <objects>
                    <object>Case</object>
                </objects>
                <property name="showFilters" type="Boolean" default="true" label="Show Filters" />
                <property name="maxRecords" type="Integer" default="10" label="Max Records" />
            </targetConfig>
        </targetConfigs>
    </LightningComponentBundle>

- Set isExposed=true for components that need to be used in Lightning App Builder, Flows, or Experience Builder.
- Set isExposed=false for utility/service components and private child components.
- Always include masterLabel and description — these show in the Lightning App Builder UI.
- Specify targets explicitly — don't expose everywhere if the component is designed for a specific context.
- Use targetConfigs with property definitions for admin-configurable properties.
- Supported property types: Boolean, Integer, String, Color, Date, DateTime.
- For Flow Screen components, use @api properties that map to flow input/output variables.
- For Record Pages, the component automatically receives recordId and objectApiName if you declare them as @api.

AVAILABLE TARGETS:
    lightning__RecordPage      → Record detail pages
    lightning__AppPage         → App pages in Lightning Apps
    lightning__HomePage        → Home page
    lightning__FlowScreen      → Flow screen components
    lightning__UtilityBar      → Utility bar
    lightning__Tab             → Lightning tabs
    lightning__Inbox           → Outlook/Gmail integration
    lightning__RecordAction    → Quick Actions
    lightningCommunity__Page   → Experience Cloud pages
    lightningCommunity__Default → Experience Cloud (all pages)
    lightning__UrlAddressable  → URL-addressable tabs
    lightningSnapin__ChatMessage → Embedded Service chat
```

---

## 20. Salesforce Base Components Usage

```
RULES:
- Always prefer Salesforce Lightning base components over custom HTML when a base component exists.
- Base components provide built-in SLDS styling, accessibility, and mobile responsiveness.

COMMON BASE COMPONENTS — USE THESE:

| Component | Use For |
|-----------|---------|
| lightning-button | All buttons |
| lightning-input | Text, number, email, phone, date, datetime, checkbox, toggle inputs |
| lightning-combobox | Dropdown/select inputs |
| lightning-textarea | Multi-line text input |
| lightning-datatable | Data tables with sorting, selection, inline edit |
| lightning-card | Content containers with header/footer |
| lightning-accordion / lightning-accordion-section | Collapsible content sections |
| lightning-tab / lightning-tabset | Tabbed interfaces |
| lightning-modal | Modal dialogs (use LightningModal class) |
| lightning-record-form | Auto-generated record forms |
| lightning-record-edit-form + lightning-input-field | Custom record edit layouts |
| lightning-record-view-form + lightning-output-field | Custom record view layouts |
| lightning-spinner | Loading indicators |
| lightning-progress-indicator | Multi-step wizards/progress |
| lightning-pill / lightning-pill-container | Tags/chips for selected items |
| lightning-tree | Hierarchical/tree data |
| lightning-breadcrumbs | Navigation breadcrumbs |
| lightning-formatted-date-time | Date/time display |
| lightning-formatted-number | Number/currency/percent display |
| lightning-formatted-rich-text | Rich text display |
| lightning-layout + lightning-layout-item | Responsive grid layout |
| lightning-helptext | Tooltip/info icon with help text |

- For modals, extend LightningModal:
    import LightningModal from 'lightning/modal';
    export default class MyModal extends LightningModal {
        handleClose() {
            this.close('result data');
        }
    }
    
    // Opening from parent:
    import MyModal from 'c/myModal';
    const result = await MyModal.open({
        size: 'medium',
        description: 'Modal description for accessibility',
        content: 'Modal content',
    });

- For data tables with advanced features, use lightning-datatable with column definitions:
    columns = [
        { label: 'Name', fieldName: 'Name', type: 'text', sortable: true },
        { label: 'Amount', fieldName: 'Amount', type: 'currency', sortable: true },
        { label: 'Close Date', fieldName: 'CloseDate', type: 'date' },
        { label: 'Actions', type: 'action', typeAttributes: { rowActions: actions } }
    ];

- Never rebuild functionality that a base component already provides.
```

---

## 21. Integration with Flows & Agentforce

```
RULES:
- For Flow Screen Components, dispatch navigation events from lightning/flowSupport (there is no mixin — it is purely event-based):
    import { FlowNavigationNextEvent, FlowNavigationBackEvent, FlowNavigationFinishEvent } 
        from 'lightning/flowSupport';
    
    handleNext() {
        this.dispatchEvent(new FlowNavigationNextEvent());
    }

- Flow input/output properties:
    @api inputVariable;       // Set from Flow input
    @api get outputVariable() { return this._outputVariable; }
    set outputVariable(value) { this._outputVariable = value; }
    _outputVariable;
    
    // Notify Flow of output changes:
    handleChange(event) {
        this._outputVariable = event.target.value;
        const attributeChangeEvent = new FlowAttributeChangeEvent('outputVariable', this._outputVariable);
        this.dispatchEvent(attributeChangeEvent);
    }

- Validate before allowing Flow navigation:
    @api
    validate() {
        if (this.isInputValid()) {
            return { isValid: true };
        } else {
            return {
                isValid: false,
                errorMessage: 'Please fill in all required fields.'
            };
        }
    }

- For Agentforce components:
    - Use @InvocableMethod in Apex as the agent action backend.
    - The LWC provides the UI while the Apex provides the logic the agent invokes.
    - Design the LWC to work both as a standalone component and as an agent action UI.
    - Make agent action descriptions clear and natural language for the AI to understand.

- Expose LWC to Flows by adding lightning__FlowScreen to targets in the meta.xml.
```

---

## 22. Light DOM & Advanced Directives

```
RULES:

LIGHT DOM (lwc:render-mode="light"):
- By default, LWC uses Shadow DOM for strong encapsulation. Light DOM disables shadow DOM, rendering 
  the component's template into the parent's DOM tree.
- Use Light DOM only when:
    - Building highly customizable UI where consumers need full CSS control.
    - Using third-party libraries incompatible with Shadow DOM.
    - Building components for Experience Cloud that need global CSS theming.
- Enable Light DOM by adding lwc:render-mode="light" to the root <template> tag AND setting `static renderMode = 'light';` in the JS class:
    // In HTML:
    <template lwc:render-mode="light">
        <div class="my-component">
            <!-- content renders in parent's DOM, no shadow boundary -->
        </div>
    </template>
    
    // In JS:
    export default class MyComponent extends LightningElement {
        static renderMode = 'light';
    }
- TRADEOFF: Light DOM exposes component internals — consumers can access your DOM, making 
  it harder to change without breaking consumers. Prefer Shadow DOM unless you have a specific reason.
- A Shadow DOM component CANNOT render a Light DOM template and vice versa. Mixing causes a runtime error.
- Light DOM components still support all LWC features (wire, events, lifecycle hooks, @api).
- CSS in Light DOM components is NOT scoped — styles leak out and in. Use specific class name prefixes 
  or BEM naming to avoid conflicts.

lwc:spread DIRECTIVE:
- Use lwc:spread to pass all properties of an object as attributes to a child component:
    <c-child-component lwc:spread={childProps}></c-child-component>
    
    // In JS:
    get childProps() {
        return {
            recordId: this.recordId,
            mode: 'edit',
            showHeader: true
        };
    }
- lwc:spread is useful when dynamically constructing property sets or wrapping components.
- Properties in the spread object must match the child's @api properties (camelCase in JS → kebab-case 
  in HTML is automatic).

lwc:ref DIRECTIVE:
- Use lwc:ref to get a direct reference to a DOM element without querySelector:
    <template>
        <lightning-input lwc:ref="nameInput" label="Name"></lightning-input>
        <lightning-button label="Focus" onclick={handleFocus}></lightning-button>
    </template>
    
    // In JS:
    handleFocus() {
        this.refs.nameInput.focus();
    }
- this.refs is available in renderedCallback() and event handlers (not constructor or connectedCallback).
- lwc:ref is safer and more readable than this.template.querySelector().
- Each ref name must be unique within the template.

DYNAMIC COMPONENT CREATION (lwc:is):
- Use lwc:is for dynamically choosing which component to render at runtime:
    <template>
        <lwc:component lwc:is={componentConstructor}></lwc:component>
    </template>
    
    // In JS:
    async connectedCallback() {
        const { default: ctor } = await import('c/dynamicChild');
        this.componentConstructor = ctor;
    }
- Use lwc:is for plugin architectures, configurable dashboards, or A/B testing different components.
- The imported constructor must be a valid LWC component.
- Dynamic imports are async — always handle the loading state.
```

---

## 23. Lightning Web Security (LWS)

```
RULES:
- Lightning Web Security (LWS) is the modern security architecture replacing Lightning Locker.
- LWS uses browser-native security features (JavaScript sandboxing, distortion handlers) instead 
  of Locker's secure wrappers — resulting in better performance and fewer compatibility issues.
- LWS is enabled at the org level and applies to all LWC components. Aura components in Aura sites 
  may still use Lightning Locker unless LWS is enabled for Aura.
- LWS restricts:
    - Access to global objects (window, document) — distorted to prevent cross-namespace interference.
    - eval(), Function(), and dynamic code execution — blocked entirely.
    - DOM access across namespace boundaries — components can only access their own DOM.
    - Cookie and storage access — scoped per namespace.
- Key differences from Lightning Locker:
    | Feature | Lightning Locker | Lightning Web Security |
    |---------|-----------------|----------------------|
    | Architecture | Secure wrappers (Proxy objects) | Browser sandboxes + distortions |
    | Performance | Slower (proxy overhead) | Faster (native browser APIs) |
    | Third-party lib support | Limited | Better compatibility |
    | Shadow DOM | Synthetic Shadow | Native Shadow DOM preferred |
    | DOM APIs | Many blocked/distorted | More APIs available |
- Write components that are LWS-compatible:
    - Never use eval() or Function() for dynamic code.
    - Never access document.cookie directly — use the platform APIs.
    - Never use window.postMessage for cross-component communication — use LMS.
    - Don't rely on global state (window.myVar) — it may be distorted or inaccessible.
    - Use Content Security Policy (CSP) Trusted Sites for any external script/resource loading.
- Use the LWC Security MCP Tools (Beta) for automated security analysis:
    - guide_lwc_security tool analyzes components for XSS/DOM injection risks.
    - Identifies anti-patterns based on LWS best practices.
    - Recommends fixes and safe integration patterns.
```

---

## 24. ESLint Rules & Static Analysis

```
RULES:
- All LWC code must pass ESLint with @salesforce/eslint-config-lwc ruleset.
- Install: npm install --save-dev @salesforce/eslint-config-lwc @salesforce/eslint-plugin-lwc
- Configure .eslintrc.json in project root:
    {
        "extends": ["@salesforce/eslint-config-lwc/recommended"]
    }
- Available configurations (in order of strictness):
    - @salesforce/eslint-config-lwc/base       → Minimum rules
    - @salesforce/eslint-config-lwc/recommended → Recommended (use this)
    - @salesforce/eslint-config-lwc/extended    → Strictest

KEY ESLINT RULES ENFORCED:
    @salesforce/lwc/no-api-reassignments        → Prevent reassigning @api properties.
    @salesforce/lwc/no-async-operation           → Flag async operations in connectedCallback without cleanup.
    @salesforce/lwc/no-deprecated                → Flag deprecated APIs (if:true, if:false, etc.).
    @salesforce/lwc/no-document-query            → Prevent document.querySelector (use this.template.querySelector).
    @salesforce/lwc/no-inner-html                → Prevent innerHTML usage.
    @salesforce/lwc/no-dupe-class-members        → No duplicate class members.
    @salesforce/lwc/valid-api                    → Validate @api decorator usage.
    @salesforce/lwc/valid-wire                   → Validate @wire decorator usage.
    no-var                                       → Use const/let, never var.
    prefer-const                                 → Use const when variable is never reassigned.
    no-console                                   → No console.log in production code.
    eqeqeq                                      → Use === and !==, never == and !=.

RUN ESLINT:
    npx eslint force-app/main/default/lwc/ --ext .js
    
INTEGRATE WITH CI/CD:
    - Run ESLint as a pre-commit hook (husky + lint-staged).
    - Fail the build pipeline on any ESLint errors.
    - Use ESLint --fix for auto-fixable issues.

PMD FOR LWC HTML TEMPLATES:
    - PMD does not have LWC-specific rules, but Salesforce Visualforce rules can catch some issues.
    - For HTML template linting, rely on the ESLint LWC plugin + the LWC compiler's own validation.
```

---

## 25. Anti-Patterns to Avoid

```
NEVER DO THESE:

1. Direct DOM manipulation when reactive approach exists:
   // BAD:
   this.template.querySelector('.output').textContent = 'Hello';
   // GOOD:
   this.outputText = 'Hello';  // Use reactive property + {outputText} in template

2. Using var instead of const/let:
   // BAD:
   var accounts = [];
   // GOOD:
   const accounts = [];  // or let if reassignment needed

3. Mutating @api properties:
   // BAD:
   this.recordId = '001...';  // Parent owns this — can't set from child
   // GOOD:
   this._localRecordId = this.recordId;  // Copy to private property

4. Not cleaning up in disconnectedCallback:
   // BAD: Event listener leak
   connectedCallback() {
       window.addEventListener('resize', this.handleResize);
   }
   // GOOD:
   connectedCallback() { window.addEventListener('resize', this._boundHandleResize); }
   disconnectedCallback() { window.removeEventListener('resize', this._boundHandleResize); }

5. Using alert(), confirm(), prompt():
   // BAD:
   alert('Saved!');
   // GOOD:
   this.dispatchEvent(new ShowToastEvent({ title: 'Success', message: 'Saved!', variant: 'success' }));

6. Hardcoded record IDs or org URLs:
   // BAD:
   this.navigateToUrl('/001000000000001');
   // GOOD:
   this[NavigationMixin.Navigate]({ type: 'standard__recordPage', attributes: { recordId: id, actionName: 'view' }});

7. Missing error handling on Apex calls:
   // BAD:
   const result = await getAccounts();
   this.accounts = result;
   // GOOD:
   try {
       this.isLoading = true;
       this.accounts = await getAccounts();
   } catch (error) {
       this.handleError(error);
   } finally {
       this.isLoading = false;
   }

8. Nested wire adapters or imperative calls inside wire handlers:
   // BAD: Wire triggers another Apex call — unpredictable cascade
   @wire(getAccounts) wiredAccounts({ data }) {
       if (data) { getContactsImperative({ accountIds: data.map(a => a.Id) }); } // VIOLATION
   }

9. Using if:true / if:false (no longer recommended):
   // BAD:
   <template if:true={isVisible}>   <!-- NO LONGER RECOMMENDED -->
   // GOOD:
   <template lwc:if={isVisible}>    <!-- MODERN -->

10. Not debouncing user input:
    // BAD: Fires Apex call on every keystroke
    handleSearch(event) {
        this.searchKey = event.target.value;   // triggers wire on every character
    }
    // GOOD: Debounce
    handleSearch(event) {
        window.clearTimeout(this._delayTimeout);
        const searchKey = event.target.value;
        this._delayTimeout = setTimeout(() => { this.searchKey = searchKey; }, 300);
    }

11. Loading all records without pagination:
    // BAD: Fetches potentially thousands of records
    @wire(getAllAccounts) accounts;
    // GOOD: Paginated query with LIMIT/OFFSET
    @wire(getAccountsPage, { pageSize: 20, offset: '$offset' }) accounts;

12. Publishing sensitive data in events:
    // BAD: Sending SSN or credit card in event detail
    new CustomEvent('submit', { detail: { ssn: '123-45-6789' } });
    // GOOD: Send only IDs, let the receiver fetch securely

13. Not providing loading/empty/error states:
    // BAD: Component shows nothing while loading
    // GOOD: Show spinner while loading, message when empty, error panel when failed

14. Using console.log in production:
    // BAD: console.log('data:', data);
    // GOOD: Use a configurable logging utility or remove before deployment

15. Creating monolithic components:
    // BAD: 500+ line component doing everything
    // GOOD: Break into parent + focused child components under 200 lines each
```

---

## 26. Common LWC Runtime Errors & Prevention (StackExchange Top Issues)

```
These are the most frequently asked LWC issues on Salesforce StackExchange. Build awareness of each into your components:

1. "Cannot read properties of undefined" in wire handler
   CAUSE: Accessing data from a wire before it has provisioned (wire returns undefined initially, then fires with data or error).
   FIX: Always check for data/error existence:
       @wire(getAccounts) wiredResult;
       get accounts() {
           return this.wiredResult?.data ?? [];
       }

2. "refreshApex is not refreshing data"
   CAUSE: Passing the .data property to refreshApex instead of the entire wired result.
   FIX: Store the raw wire result and pass that:
       @wire(getAccounts) wiredAccountResult;
       await refreshApex(this.wiredAccountResult); // NOT this.wiredAccountResult.data

3. this.template.querySelector() returns null
   CAUSE: Calling querySelector in constructor() or connectedCallback() before the DOM has rendered.
   FIX: Use querySelector only in renderedCallback(), event handlers, or user-triggered methods.

4. Custom event handler "has no effect" / never fires
   CAUSE: Event name in dispatch doesn't match the onXxx handler in parent HTML.
   RULES:
   - Event name must be all lowercase, no hyphens (underscores are valid for namespaced events).
   - If you dispatch 'caseSelected', parent must listen with oncaseselected (lowercase!).
   - If you dispatch 'case-selected', it WON'T work — hyphens are invalid in event names.

5. "[LWC error]: Invalid event type" or event doesn't bubble
   CAUSE: Using uppercase, hyphens, or special characters in CustomEvent name.
   FIX: Lowercase only, no hyphens:
       new CustomEvent('itemselected')  // GOOD
       new CustomEvent('item-selected') // BAD
       new CustomEvent('ItemSelected')  // BAD

6. @api property change not triggering re-render
   CAUSE: Parent passes an object/array via @api but mutates it in place (push, direct property assignment).
   FIX: Parent must create a new reference (spread operator) to trigger child re-render:
       // In parent:
       this.childData = [...this.childData, newItem]; // triggers child update
       this.childData.push(newItem); // DOES NOT trigger child update

7. Wire adapter fires with undefined parameters
   CAUSE: Wire parameter references a property that is undefined at component creation.
   FIX: Wire does NOT fire when a reactive parameter is undefined. Initialize properties with null (not undefined) if you want the wire to fire with "no filter" semantics.

8. "You do not have access to the Apex class" at runtime
   CAUSE: @AuraEnabled Apex method is not accessible to the running user's profile, or the Apex class is not assigned to the user's connected app or permission set.
   FIX: Ensure the Apex class is included in a Permission Set or Profile's Apex Class Access.

9. Lightning Toast not showing in Experience Cloud
   CAUSE: lightning/platformShowToastEvent is NOT supported on LWR sites for Experience Cloud, login pages in Aura sites, or standalone apps. It works in Lightning Experience and Aura-based Experience Cloud sites.
   FIX: Use lightning/toast (the modern API) which has broader support. For LWR Experience Cloud sites where neither works, build a custom toast/notification component using SLDS styling.

10. "Cannot set properties of undefined" when setting a reactive field in constructor
    CAUSE: Trying to access @api properties in the constructor — they haven't been set yet.
    FIX: Move initialization logic to connectedCallback() where @api properties are available.

11. Infinite loop in renderedCallback()
    CAUSE: Setting a reactive property inside renderedCallback triggers a re-render, which calls renderedCallback again.
    FIX: Guard with a boolean flag:
        renderedCallback() {
            if (this._hasRendered) return;
            this._hasRendered = true;
            // safe to do work here
        }

12. "Maximum call stack size exceeded" from component recursion
    CAUSE: A getter or setter triggers itself (e.g., setting a property in a setter that fires the same setter via reactivity).
    FIX: Break the cycle by using a private backing field and avoid setting reactive props inside their own setters.

13. Data table columns not showing / wrong data
    CAUSE: fieldName in column definition doesn't match the exact property name in the data. For nested data (e.g., Account.Name on a Contact), use a flattened property.
    FIX: Pre-process data to flatten nested fields:
        this.tableData = data.map(record => ({
            ...record,
            accountName: record.Account?.Name
        }));
        // Column: { label: 'Account', fieldName: 'accountName' }

14. LWC component not appearing in Lightning App Builder
    CAUSE: isExposed is false, or no targets declared, or missing masterLabel in meta.xml.
    FIX: Ensure isExposed=true, at least one target (e.g., lightning__RecordPage), and provide masterLabel and description.

15. Wire not re-firing after imperative DML
    CAUSE: Wire adapters cache data. After imperative DML, the cache isn't automatically invalidated.
    FIX: Call notifyRecordUpdateAvailable([{recordId}]) or refreshApex(wiredResult) after DML.
```

---

## Quick Reference Card

| Category | Rule | Priority |
|----------|------|----------|
| Templates | Use lwc:if (not if:true/if:false) | **CRITICAL** |
| Templates | Always include key on for:each items | **CRITICAL** |
| JavaScript | No var — use const/let | **HIGH** |
| JavaScript | Never mutate @api properties | **CRITICAL** |
| JavaScript | Clean up in disconnectedCallback | **HIGH** |
| JavaScript | querySelector only in renderedCallback or event handlers | **HIGH** |
| Wire | Handle both data and error in wire | **HIGH** |
| Wire | Use $ prefix for reactive wire params | **HIGH** |
| Wire | Pass full wired result to refreshApex, not .data | **HIGH** |
| Apex Calls | Always try/catch with loading state | **HIGH** |
| Events | Lowercase event names, no hyphens | **HIGH** |
| Events | Use LMS for cross-component communication, not pub-sub | **MEDIUM** |
| Security | Never use eval() or innerHTML with user data | **CRITICAL** |
| Security | Enforce security server-side (Apex) | **CRITICAL** |
| CSS | Use SLDS utility classes first, custom CSS only when necessary | **HIGH** |
| Performance | Debounce search inputs (300ms) | **HIGH** |
| Performance | Paginate large datasets | **HIGH** |
| Accessibility | Alt text on all icons/spinners | **HIGH** |
| Accessibility | Keyboard navigable | **HIGH** |
| Testing | Jest tests for every component | **HIGH** |
| Testing | Clean up DOM in afterEach | **HIGH** |
| Base Comps | Use lightning-* base components | **MEDIUM** |
| Metadata | Include .js-meta.xml with targets, API version 66.0 | **HIGH** |
| LDS | Use record forms over custom CRUD | **MEDIUM** |
| Navigation | Use NavigationMixin, never window.location | **HIGH** |
| Light DOM | Use only when Shadow DOM won't work; document tradeoffs | **MEDIUM** |
| Directives | Use lwc:ref over querySelector for element refs | **MEDIUM** |
| Directives | Use lwc:spread for dynamic property passing | **MEDIUM** |
| LWS | Never use eval(), Function(), or dynamic code execution | **CRITICAL** |
| LWS | Don't rely on global window state across namespaces | **HIGH** |
| ESLint | Pass @salesforce/eslint-config-lwc/recommended | **HIGH** |
| ESLint | No console.log, no var, use === not == | **HIGH** |
| Experience Cloud | ShowToastEvent doesn't work — build custom toast | **MEDIUM** |

---

*This ruleset is tool-agnostic. It works with GitHub Copilot, Cursor, Claude Code, Windsurf, Cline, Roo Code, or any AI-assisted coding tool that supports custom instructions.*
