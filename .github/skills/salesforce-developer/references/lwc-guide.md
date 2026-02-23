# Lightning Web Components (LWC) & Aura Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes for LWC API changes.

## Table of Contents
1. [LWC Fundamentals](#lwc-fundamentals)
2. [Data Binding & Reactivity](#data-binding-and-reactivity)
3. [Wire Service & Apex Integration](#wire-service-and-apex-integration)
4. [Lightning Data Service](#lightning-data-service)
5. [Component Communication](#component-communication)
6. [Navigation & Toast Messages](#navigation-and-toast-messages)
7. [LWC vs Aura Decision Guide](#lwc-vs-aura)
8. [Aura Quick Reference](#aura-quick-reference)
9. [Dynamic LWC Components](#dynamic-lwc-components)

---

## LWC Fundamentals

### Component File Structure
```
myComponent/
├── myComponent.html          <!-- Template (required) -->
├── myComponent.js            <!-- Controller (required) -->
├── myComponent.css           <!-- Styles (optional) -->
├── myComponent.js-meta.xml   <!-- Configuration (required) -->
└── __tests__/                <!-- Jest tests (optional) -->
    └── myComponent.test.js
```

### Basic Component

**HTML Template:**
```html
<template>
    <lightning-card title={cardTitle} icon-name="standard:account">
        <div class="slds-m-around_medium">
            <template if:true={accounts.data}>
                <template for:each={accounts.data} for:item="account">
                    <p key={account.Id}>{account.Name} — {account.Industry}</p>
                </template>
            </template>
            <template if:true={accounts.error}>
                <p class="slds-text-color_error">Error loading accounts</p>
            </template>
        </div>
        <div slot="footer">
            <lightning-button label="Refresh" onclick={handleRefresh}></lightning-button>
        </div>
    </lightning-card>
</template>
```

**JavaScript Controller:**
```javascript
import { LightningElement, api, wire } from 'lwc';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import { refreshApex } from '@salesforce/apex';

export default class MyComponent extends LightningElement {
    @api recordId;           // Public property (set by parent or record page)
    cardTitle = 'Accounts';  // Reactive property

    // Wire to Apex — store result for refreshApex; template uses {accounts.data}
    accounts;
    wiredAccountsResult;

    @wire(getAccounts)
    wiredAccounts(result) {
        this.wiredAccountsResult = result;
        this.accounts = result;  // { data, error }
    }

    handleRefresh() {
        refreshApex(this.wiredAccountsResult);
    }

    // Lifecycle hooks
    connectedCallback() {
        // Component inserted into DOM
        console.log('Component connected, recordId:', this.recordId);
    }

    disconnectedCallback() {
        // Component removed from DOM — cleanup event listeners
    }

    renderedCallback() {
        // After every render — use sparingly, can cause infinite loops
    }

    errorCallback(error, stack) {
        // Error boundary — catches errors in child components
        console.error('Error:', error.message, 'Stack:', stack);
    }
}
```

**Meta XML (Configuration):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>66.0</apiVersion>
    <isExposed>true</isExposed>
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <target>lightning__FlowScreen</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordPage">
            <objects>
                <object>Account</object>
                <object>Contact</object>
            </objects>
            <property name="cardTitle" type="String" default="My Accounts"
                      label="Card Title" description="Title shown on the card header"/>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

## Data Binding and Reactivity

### Decorators

| Decorator | Purpose | Usage |
|---|---|---|
| `@api` | Public property, settable by parent | `@api recordId;` |
| `@track` | Deep-track objects/arrays (rarely needed since Spring '20) | `@track complexObj = {};` |
| `@wire` | Reactive data from wire adapter or Apex | `@wire(getRecord, ...)` |

Since Spring '20, all fields in a component are reactive by default. `@track` is only needed for
deep-tracking changes inside objects/arrays (e.g., changing `obj.nested.value` directly).

### Computed Properties (Getters)
```javascript
get isHighValue() {
    return this.account?.data?.fields?.AnnualRevenue?.value > 1000000;
}

get formattedRevenue() {
    const rev = this.account?.data?.fields?.AnnualRevenue?.value;
    return rev ? new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD'
    }).format(rev) : 'N/A';
}
```

### Conditional Rendering
```html
<template if:true={isLoading}>
    <lightning-spinner alternative-text="Loading"></lightning-spinner>
</template>
<template if:false={isLoading}>
    <template if:true={hasData}>
        <!-- Show data -->
    </template>
    <template if:false={hasData}>
        <p>No data available</p>
    </template>
</template>

<!-- lwc:if/lwc:elseif/lwc:else (API 55.0+, preferred) -->
<template lwc:if={isLoading}>
    <lightning-spinner></lightning-spinner>
</template>
<template lwc:elseif={hasData}>
    <!-- Show data -->
</template>
<template lwc:else>
    <p>No data available</p>
</template>
```

---

## Wire Service and Apex Integration

### Wire to Apex (Cacheable — Reactive)
```javascript
import getAccounts from '@salesforce/apex/AccountController.getAccounts';

// Wire with parameters — re-fires when params change
@wire(getAccounts, { industry: '$selectedIndustry' })
wiredAccounts;

// Or wire to a function for more control
@wire(getAccounts, { industry: '$selectedIndustry' })
wiredAccounts({ error, data }) {
    if (data) {
        this.accounts = data;
        this.error = undefined;
    } else if (error) {
        this.error = error.body.message;
        this.accounts = [];
    }
}
```

The Apex method must be `@AuraEnabled(cacheable=true)` for `@wire`.

### Imperative Apex Calls (Non-Cacheable)
```javascript
import saveAccount from '@salesforce/apex/AccountController.saveAccount';

async handleSave() {
    this.isLoading = true;
    try {
        const result = await saveAccount({ accountData: this.accountRecord });
        this.dispatchEvent(new ShowToastEvent({
            title: 'Success',
            message: 'Account saved successfully',
            variant: 'success'
        }));
    } catch (error) {
        this.dispatchEvent(new ShowToastEvent({
            title: 'Error',
            message: error.body?.message || 'An error occurred',
            variant: 'error'
        }));
    } finally {
        this.isLoading = false;
    }
}
```

### Apex Controller Pattern for LWC
```apex
public with sharing class AccountController {
    // Cacheable — for @wire
    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts(String industry) {
        return [
            SELECT Id, Name, Industry, AnnualRevenue
            FROM Account
            WHERE Industry = :industry
            WITH SECURITY_ENFORCED
            ORDER BY Name
            LIMIT 50
        ];
    }

    // Non-cacheable — for imperative calls that modify data
    @AuraEnabled
    public static Account saveAccount(Account accountData) {
        // Enforce CRUD
        if (!Schema.sObjectType.Account.isUpdateable()) {
            throw new AuraHandledException('Insufficient access');
        }
        try {
            upsert accountData;
            return accountData;
        } catch (DmlException e) {
            throw new AuraHandledException(e.getMessage());
        }
    }
}
```

---

## Lightning Data Service

### getRecord / getFieldValue (No Apex Needed)
```javascript
import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
import REVENUE_FIELD from '@salesforce/schema/Account.AnnualRevenue';

const FIELDS = [NAME_FIELD, INDUSTRY_FIELD, REVENUE_FIELD];

export default class AccountDetail extends LightningElement {
    @api recordId;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    account;

    get accountName() {
        return getFieldValue(this.account.data, NAME_FIELD);
    }

    get industry() {
        return getFieldValue(this.account.data, INDUSTRY_FIELD);
    }
}
```

### lightning-record-form (Quickest Way)
```html
<!-- Auto-generates form with all fields -->
<lightning-record-form
    record-id={recordId}
    object-api-name="Account"
    fields={fields}
    mode="edit"
    onsuccess={handleSuccess}
    onerror={handleError}>
</lightning-record-form>
```

### lightning-record-edit-form (More Control)
```html
<lightning-record-edit-form
    record-id={recordId}
    object-api-name="Account"
    onsuccess={handleSuccess}>
    <lightning-messages></lightning-messages>
    <lightning-input-field field-name="Name"></lightning-input-field>
    <lightning-input-field field-name="Industry"></lightning-input-field>
    <lightning-input-field field-name="AnnualRevenue"></lightning-input-field>
    <lightning-button type="submit" label="Save" variant="brand"></lightning-button>
</lightning-record-edit-form>
```

---

## Component Communication

### Parent to Child (`@api`)
```javascript
// Parent template
<c-child-component account-name={parentAccountName} record-id={parentRecordId}>
</c-child-component>

// Child JS
export default class ChildComponent extends LightningElement {
    @api accountName;
    @api recordId;
}
```

### Child to Parent (Custom Events)
```javascript
// Child dispatches event
handleSelect() {
    this.dispatchEvent(new CustomEvent('accountselect', {
        detail: { accountId: this.account.Id, accountName: this.account.Name }
    }));
}

// Parent listens
<c-child-component onaccountselect={handleAccountSelect}></c-child-component>

handleAccountSelect(event) {
    const { accountId, accountName } = event.detail;
    console.log('Selected:', accountName);
}
```

### Unrelated Components (Lightning Message Service)
```javascript
// Publisher
import { publish, MessageContext } from 'lightning/messageService';
import RECORD_SELECTED from '@salesforce/messageChannel/Record_Selected__c';

@wire(MessageContext)
messageContext;

handleSelect(event) {
    publish(this.messageContext, RECORD_SELECTED, {
        recordId: event.detail.recordId
    });
}

// Subscriber
import { subscribe, unsubscribe, MessageContext } from 'lightning/messageService';
import RECORD_SELECTED from '@salesforce/messageChannel/Record_Selected__c';

@wire(MessageContext)
messageContext;
subscription = null;

connectedCallback() {
    this.subscription = subscribe(
        this.messageContext, RECORD_SELECTED,
        (message) => this.handleMessage(message)
    );
}

disconnectedCallback() {
    unsubscribe(this.subscription);
    this.subscription = null;
}

handleMessage(message) {
    this.selectedRecordId = message.recordId;
}
```

---

## Navigation and Toast Messages

### Navigation
```javascript
import { NavigationMixin } from 'lightning/navigation';

export default class MyComponent extends NavigationMixin(LightningElement) {
    // Navigate to record page
    navigateToRecord(recordId) {
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: recordId,
                objectApiName: 'Account',
                actionName: 'view'
            }
        });
    }

    // Navigate to list view
    navigateToList() {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName: 'Account',
                actionName: 'list'
            },
            state: { filterName: 'Recent' }
        });
    }

    // Navigate to custom tab / web page
    navigateToWebPage(url) {
        this[NavigationMixin.Navigate]({
            type: 'standard__webPage',
            attributes: { url: url }
        });
    }
}
```

### Toast Messages
```javascript
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

showToast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({
        title: title,       // 'Success', 'Error', 'Warning', 'Info'
        message: message,
        variant: variant,   // 'success', 'error', 'warning', 'info'
        mode: 'dismissible' // 'dismissible', 'pester', 'sticky'
    }));
}
```

---

## LWC vs Aura

| Feature | LWC | Aura |
|---|---|---|
| Performance | Faster (native web components) | Slower (proprietary framework) |
| Standards | W3C Web Components | Proprietary |
| Future direction | Active development | Maintenance mode |
| Learning curve | Modern JS developers feel at home | Steeper, unique patterns |
| When to use | All new development | Legacy components, some specific features |

**Use Aura only when:** you need functionality not yet supported in LWC (some overlay libraries,
certain Lightning Out scenarios), or you're maintaining existing Aura components.

---

## Aura Quick Reference

### Aura Component Structure
```xml
<!-- myComponent.cmp -->
<aura:component implements="force:appHostable,flexipage:availableForAllPageTypes"
                access="global" controller="MyApexController">

    <aura:attribute name="accounts" type="List" default="[]"/>
    <aura:attribute name="isLoading" type="Boolean" default="false"/>

    <aura:handler name="init" value="{!this}" action="{!c.doInit}"/>

    <lightning:card title="Accounts">
        <aura:iteration items="{!v.accounts}" var="acc">
            <p>{!acc.Name}</p>
        </aura:iteration>
    </lightning:card>
</aura:component>
```

### Aura Controller + Helper
```javascript
// myComponentController.js
({
    doInit : function(component, event, helper) {
        helper.loadAccounts(component);
    }
})

// myComponentHelper.js
({
    loadAccounts : function(component) {
        var action = component.get("c.getAccounts");
        action.setCallback(this, function(response) {
            var state = response.getState();
            if (state === "SUCCESS") {
                component.set("v.accounts", response.getReturnValue());
            } else {
                console.error("Error:", response.getError());
            }
        });
        $A.enqueueAction(action);
    }
})
```

### Key $A Methods
| Method | Description |
|---|---|
| `$A.get("e.force:navigateToSObject")` | Navigate to record |
| `$A.enqueueAction(action)` | Queue Apex call |
| `$A.get("e.force:showToast")` | Show toast |
| `component.get("v.attributeName")` | Get attribute value |
| `component.set("v.attributeName", val)` | Set attribute value |
| `component.find("auraId")` | Find child component |

---

## Dynamic LWC Components

### Dynamic Component Creation with lwc:component (API v61.0+)

`lwc:component` with `lwc:is` lets you dynamically instantiate a component at runtime, based on
a constructor resolved via `import()`. This enables plugin architectures, lazy loading, and
configurable UIs.

```html
<!-- dynamicContainer.html -->
<template>
    <div class="slds-box">
        <lwc:component lwc:is={componentConstructor}
                       record-id={recordId}
                       onaction={handleAction}>
        </lwc:component>
    </div>
    <template if:false={componentConstructor}>
        <lightning-spinner alternative-text="Loading component"></lightning-spinner>
    </template>
</template>
```

```javascript
// dynamicContainer.js
import { LightningElement, api } from 'lwc';

export default class DynamicContainer extends LightningElement {
    @api recordId;
    _componentName;      // backing field for componentName
    componentConstructor;

    // Use getter/setter pattern for @api property that triggers side-effects
    @api
    get componentName() {
        return this._componentName;
    }
    set componentName(value) {
        this._componentName = value;
        this.loadComponent();
    }

    connectedCallback() {
        this.loadComponent();
    }

    async loadComponent() {
        if (!this._componentName) return;
        try {
            // Dynamic import — loads the component on demand
            const { default: ctor } = await import(this._componentName);
            this.componentConstructor = ctor;
        } catch (error) {
            console.error('Error loading component:', error);
        }
    }

    handleAction(event) {
        // Handle events from dynamically loaded component
        console.log('Action from dynamic component:', event.detail);
    }
}
```

### Dynamic Component Use Cases

| Use Case | Pattern |
|---|---|
| **Plugin architecture** | Admin configures which component to render per record type |
| **Lazy loading** | Load heavy components only when the user scrolls to them or clicks a tab |
| **Configurable dashboards** | Users choose which widgets to display |
| **Multi-step wizards** | Load step components dynamically based on progress |
| **Record-type–specific UIs** | Different components for different record types on the same page |

### Lazy Loading Pattern

```javascript
// Load a component only when the user clicks "Show Details"
import { LightningElement } from 'lwc';

export default class LazyLoader extends LightningElement {
    detailConstructor;
    showDetails = false;

    async handleShowDetails() {
        if (!this.detailConstructor) {
            const { default: ctor } = await import('c/heavyDetailComponent');
            this.detailConstructor = ctor;
        }
        this.showDetails = true;
    }
}
```

```html
<template>
    <lightning-button label="Show Details" onclick={handleShowDetails}></lightning-button>
    <template if:true={showDetails}>
        <lwc:component lwc:is={detailConstructor}></lwc:component>
    </template>
</template>
```

### Important Rules for Dynamic Components

1. **Only LWC components can be loaded dynamically** — not Aura components
2. **The imported component must be in the same namespace** or be a managed package component accessible to your namespace
3. **`lwc:is` must be bound to a constructor**, not a string — use `import()` to get it
4. **Pass data via `@api` properties** on the `<lwc:component>` tag — they work normally
5. **Events work normally** — use `on{eventname}` on the `<lwc:component>` tag
6. **Error handling is critical** — `import()` will reject if the component doesn't exist
7. **Not supported in Aura wrapper contexts** — only works in pure LWC hierarchies
8. **Component name uses forward-slash format**: `c/myComponent`, not `c-my-component`
