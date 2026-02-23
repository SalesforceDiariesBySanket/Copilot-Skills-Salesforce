# Deployment, DevOps & Salesforce CLI Reference

> **Validated as of: 2026-02** — Review against current Salesforce CLI release notes for command changes.

## Table of Contents
1. [Salesforce CLI (sf) Commands](#salesforce-cli-commands)
2. [Project Structure](#project-structure)
3. [Scratch Orgs](#scratch-orgs)
4. [Sandboxes](#sandboxes)
5. [Source Tracking & Deployment](#source-tracking-and-deployment)
6. [Packaging (2GP & Unlocked)](#packaging)
7. [CI/CD Pipeline Setup](#ci-cd-pipeline-setup)
8. [DevOps Center](#devops-center)
9. [Code Analysis & Quality](#code-analysis-and-quality)
10. [Metadata API vs Source API](#metadata-api-vs-source-api)

---

## Salesforce CLI (sf) Commands

The Salesforce CLI (`sf`) is the primary tool for Salesforce development. It replaces the older
`sfdx` executable (which is now an alias for `sf`).

### Installation & Setup

```bash
# Install via npm
npm install @salesforce/cli --global

# Verify installation
sf --version

# Update CLI
sf update

# Get help
sf --help
sf project deploy start --help
```

### Authentication

```bash
# Login to org via browser (OAuth Web Server flow)
sf org login web --alias myDevOrg --instance-url https://login.salesforce.com

# Login to sandbox
sf org login web --alias mySandbox --instance-url https://test.salesforce.com

# Login with JWT (for CI/CD — no browser needed)
sf org login jwt \
  --client-id YOUR_CONNECTED_APP_CLIENT_ID \
  --jwt-key-file server.key \
  --username user@example.com \
  --alias myOrg \
  --instance-url https://login.salesforce.com

# Login with SFDX Auth URL (for CI/CD)
sf org login sfdx-url --sfdx-url-file authUrl.txt --alias myOrg

# List authenticated orgs
sf org list

# Set default org
sf config set target-org myDevOrg

# Set default Dev Hub
sf config set target-dev-hub myDevHub

# Logout
sf org logout --target-org myDevOrg
```

### Essential Commands Reference

| Task | Command |
|---|---|
| Create project | `sf project generate --name myProject` |
| Deploy source | `sf project deploy start --source-dir force-app` |
| Deploy with manifest | `sf project deploy start --manifest manifest/package.xml` |
| Deploy specific metadata | `sf project deploy start --metadata ApexClass:MyClass` |
| Retrieve source | `sf project retrieve start --source-dir force-app` |
| Retrieve with manifest | `sf project retrieve start --manifest manifest/package.xml` |
| Preview deploy | `sf project deploy preview` |
| Run Apex tests | `sf apex run test --test-level RunLocalTests --wait 10` |
| Run specific tests | `sf apex run test --class-names MyTestClass --wait 10` |
| Execute anonymous Apex | `sf apex run --file scripts/apex/myScript.apex` |
| Open org in browser | `sf org open` |
| View org info | `sf org display` |
| Generate Apex class | `sf apex generate class --name MyClass --output-dir force-app/main/default/classes` |
| Generate LWC | `sf lightning generate component --name myComponent --type lwc --output-dir force-app/main/default/lwc` |
| Generate trigger | `sf apex generate trigger --name MyTrigger --sobject Account --output-dir force-app/main/default/triggers` |

---

## Project Structure

### Standard SFDX Project Layout

```
my-salesforce-project/
├── .forceignore                    # Files to ignore in source tracking
├── .gitignore                      # Git ignores
├── sfdx-project.json               # Project configuration (REQUIRED)
├── manifest/
│   └── package.xml                 # Metadata manifest for deployments
├── config/
│   └── project-scratch-def.json    # Scratch org definition
├── scripts/
│   └── apex/
│       └── init.apex               # Anonymous Apex scripts
├── data/
│   └── sample-data-plan.json      # Data import plans
├── force-app/
│   └── main/
│       └── default/
│           ├── classes/            # Apex classes (.cls + .cls-meta.xml)
│           ├── triggers/           # Apex triggers (.trigger + .trigger-meta.xml)
│           ├── lwc/                # Lightning Web Components
│           ├── aura/               # Aura Components
│           ├── pages/              # Visualforce Pages
│           ├── objects/            # Custom objects, fields, validation rules
│           ├── layouts/            # Page layouts
│           ├── flexipages/         # Lightning pages
│           ├── flows/              # Flow definitions
│           ├── permissionsets/     # Permission sets
│           ├── profiles/           # Profiles (minimize — use permission sets)
│           ├── customMetadata/     # Custom metadata records
│           ├── labels/             # Custom labels
│           ├── staticresources/   # Static resources
│           ├── tabs/               # Custom tabs
│           ├── applications/       # Lightning apps
│           └── messageChannels/    # Lightning Message Channels
└── README.md
```

### sfdx-project.json

```json
{
  "packageDirectories": [
    {
      "path": "force-app",
      "default": true,
      "package": "MyPackage",
      "versionNumber": "1.0.0.NEXT"
    },
    {
      "path": "unpackaged",
      "default": false
    }
  ],
  "name": "my-salesforce-project",
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "66.0"
}
```

### .forceignore

```
# Ignore profiles (use permission sets instead)
**/profiles/**

# Ignore admin-only metadata
**/settings/**

# Ignore specific items
**/AppSwitcher.appMenu-meta.xml
**/Admin.profile-meta.xml

# Ignore build artifacts
**/.sfdx/
**/.sf/
```

---

## Scratch Orgs

Scratch orgs are disposable, source-driven environments for development and testing.

### Scratch Org Definition File

```json
// config/project-scratch-def.json
{
  "orgName": "My Dev Scratch Org",
  "edition": "Developer",
  "features": [
    "EnableSetPasswordInApi",
    "Communities",
    "ServiceCloud",
    "LightningSalesConsole",
    "PlatformEncryption"
  ],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1DesktopEnabled": true
    },
    "mobileSettings": {
      "enableS1EncryptedStoragePref2": false
    },
    "securitySettings": {
      "passwordPolicies": {
        "enableSetPasswordInApi": true
      }
    },
    "languageSettings": {
      "enableTranslationWorkbench": true
    }
  }
}
```

### Common Scratch Org Commands

```bash
# Create a scratch org (30-day default, max 30 days)
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias myScratch \
  --duration-days 30 \
  --set-default

# Push source to scratch org (source-tracked)
sf project deploy start

# Pull source changes from scratch org
sf project retrieve start

# View source tracking status
sf project deploy preview
sf project retrieve preview

# Delete scratch org
sf org delete scratch --target-org myScratch --no-prompt

# Generate password for scratch org user
sf org generate password --target-org myScratch

# Import sample data
sf data import tree --plan data/sample-data-plan.json

# Export data for test data plans
sf data export tree --query "SELECT Id, Name, Industry FROM Account" --plan

# List active scratch orgs
sf org list --all
```

### Scratch Org Limits

| Resource | Limit |
|---|---|
| Active scratch orgs per Dev Hub | Varies by edition (default: 3-100) |
| Daily scratch org creations | Varies by edition (default: 6-200) |
| Maximum duration | 30 days |
| Scratch org storage | Based on edition features |

---

## Sandboxes

### Sandbox Types

| Type | Data | Storage | Refresh | Use Case |
|---|---|---|---|---|
| **Developer** | Metadata only | 200 MB | 1 day | Individual development |
| **Developer Pro** | Metadata only | 1 GB | 1 day | Development with more storage |
| **Partial Copy** | Metadata + sample data (via template) | 5 GB | 5 days | Testing, QA |
| **Full Copy** | Full production copy | Same as prod | 29 days | UAT, staging, performance testing |

### Sandbox CLI Commands

```bash
# Create a sandbox
sf org create sandbox \
  --definition-file config/sandbox-def.json \
  --alias devSandbox \
  --target-org prodOrg \
  --wait 60

# Clone a sandbox (faster than creating new)
sf org create sandbox \
  --clone existingSandbox \
  --alias newSandbox \
  --target-org prodOrg

# Resume sandbox creation check
sf org resume sandbox --name devSandbox --target-org prodOrg

# Delete sandbox
sf org delete sandbox --target-org devSandbox
```

### Sandbox Definition File

```json
{
  "sandboxName": "DevSandbox",
  "licenseType": "DEVELOPER",
  "autoActivate": true,
  "description": "Development sandbox for feature work"
}
```

---

## Source Tracking and Deployment

### Deploy Strategies

| Strategy | When to Use | Command |
|---|---|---|
| **Source tracking** (scratch orgs/sandboxes) | Active development | `sf project deploy start` / `sf project retrieve start` |
| **Source path deploy** | Deploy specific directories | `sf project deploy start --source-dir force-app/main/default/classes` |
| **Manifest deploy** | Deploy based on package.xml | `sf project deploy start --manifest manifest/package.xml` |
| **Metadata type deploy** | Deploy specific metadata | `sf project deploy start --metadata ApexClass:MyClass` |
| **Delta deploy** | Deploy only changed files | Use Git diff + manifest generation |

### Test Levels for Deployment

```bash
# No tests (sandbox only, not production)
sf project deploy start --source-dir force-app --test-level NoTestRun

# Run tests for deployed Apex only (recommended minimum)
sf project deploy start --source-dir force-app --test-level RunSpecifiedTests \
  --tests MyTestClass AnotherTestClass

# Run org-local tests (excludes managed package tests)
sf project deploy start --source-dir force-app --test-level RunLocalTests

# Run ALL tests including managed packages
sf project deploy start --source-dir force-app --test-level RunAllTestsInOrg
```

### Production Deployment Requirements

- **75% org-wide code coverage** (aim for 85%+)
- All tests must pass
- Validation-only deploy (check before committing):
  ```bash
  sf project deploy validate --source-dir force-app --test-level RunLocalTests --wait 30
  ```
- Quick deploy after successful validation:
  ```bash
  sf project deploy quick --job-id 0Af...
  ```

### package.xml Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>AccountTriggerHandler</members>
        <members>AccountService</members>
        <members>AccountSelector</members>
        <members>AccountTriggerHandlerTest</members>
        <name>ApexClass</name>
    </types>
    <types>
        <members>AccountTrigger</members>
        <name>ApexTrigger</name>
    </types>
    <types>
        <members>accountList</members>
        <members>accountDetail</members>
        <name>LightningComponentBundle</name>
    </types>
    <types>
        <members>Account.My_Custom_Field__c</members>
        <name>CustomField</name>
    </types>
    <types>
        <members>My_Flow</members>
        <name>Flow</name>
    </types>
    <types>
        <members>My_Permission_Set</members>
        <name>PermissionSet</name>
    </types>
    <version>66.0</version>
</Package>
```

### destructiveChanges.xml (Deleting Metadata)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>ObsoleteClass</members>
        <name>ApexClass</name>
    </types>
    <types>
        <members>Account.Old_Field__c</members>
        <name>CustomField</name>
    </types>
    <version>66.0</version>
</Package>
```

```bash
# Deploy with destructive changes
sf project deploy start --manifest manifest/package.xml \
  --post-destructive-changes manifest/destructiveChanges.xml
```

---

## Packaging (2GP and Unlocked)

### Package Types

| Type | Description | Use Case |
|---|---|---|
| **Unlocked Package** | Source-tracked, versionable, customizable by subscriber | Internal deployment, modular development |
| **Managed 2GP** | ISV distribution, namespace-protected, LMA-enabled | AppExchange apps |
| **Managed 1GP** | Legacy packaging in packaging orgs | Existing AppExchange apps |
| **Unmanaged** | One-time install, no upgrade path | Sharing samples/templates |

### Unlocked Package Commands

```bash
# Create a package
sf package create \
  --name "My Feature Package" \
  --package-type Unlocked \
  --path force-app \
  --target-dev-hub myDevHub

# Create a package version
sf package version create \
  --package "My Feature Package" \
  --installation-key-bypass \
  --wait 20 \
  --code-coverage

# List package versions
sf package version list --packages "My Feature Package"

# Install a package version
sf package install \
  --package 04t... \
  --target-org targetOrg \
  --wait 10

# Promote a package version (mark as released)
sf package version promote --package 04t...
```

---

## CI/CD Pipeline Setup

### GitHub Actions Example

```yaml
# .github/workflows/salesforce-ci.yml
name: Salesforce CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Salesforce CLI
        run: npm install @salesforce/cli --global

      - name: Authenticate to org
        run: |
          echo "${{ secrets.SFDX_AUTH_URL }}" > authUrl.txt
          sf org login sfdx-url --sfdx-url-file authUrl.txt --alias targetOrg

      - name: Run Code Analyzer
        run: sf code-analyzer run --target force-app --engine pmd,eslint --format json

      - name: Validate deployment (check only)
        run: |
          sf project deploy validate \
            --source-dir force-app \
            --target-org targetOrg \
            --test-level RunLocalTests \
            --wait 30

  deploy:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Salesforce CLI
        run: npm install @salesforce/cli --global

      - name: Authenticate to production
        run: |
          echo "${{ secrets.PROD_AUTH_URL }}" > authUrl.txt
          sf org login sfdx-url --sfdx-url-file authUrl.txt --alias prodOrg

      - name: Deploy to production
        run: |
          sf project deploy start \
            --source-dir force-app \
            --target-org prodOrg \
            --test-level RunLocalTests \
            --wait 30
```

### JWT Auth for CI/CD

1. Create a Connected App in Salesforce (enable "Use digital signatures")
2. Generate a self-signed certificate and private key
3. Upload the certificate to the Connected App
4. Store the private key as a CI/CD secret

```bash
# Generate certificate and key
openssl req -x509 -sha256 -nodes -days 36500 -newkey rsa:2048 \
  -keyout server.key -out server.crt

# Authenticate with JWT in CI/CD
sf org login jwt \
  --client-id $SF_CLIENT_ID \
  --jwt-key-file server.key \
  --username $SF_USERNAME \
  --instance-url https://login.salesforce.com \
  --alias targetOrg
```

---

## DevOps Center

Salesforce DevOps Center is a native change management tool built into the platform.

### Key Features
- Track work items linked to user stories
- Source-controlled pipeline (Git-backed)
- Promote changes through environments (Dev → Integration → UAT → Production)
- No external CI/CD tool required (but integrates with them)

### Setup Requirements
1. Enable DevOps Center in Setup
2. Connect a GitHub repository
3. Configure environments (Development, Integration, Staging, Production)
4. Create projects and work items

---

## Code Analysis and Quality

### Salesforce Code Analyzer

```bash
# Install Code Analyzer plugin
sf plugins install @salesforce/plugin-code-analyzer

# Run analysis on all code
sf code-analyzer run --target force-app

# Run specific engines
sf code-analyzer run --target force-app --engine pmd,eslint

# Run with specific rules
sf code-analyzer run --target force-app --engine pmd \
  --pmd-category "Best Practices,Security"

# Generate HTML report
sf code-analyzer run --target force-app --format html --output-file report.html
```

### PMD Rules for Apex

| Rule | Description |
|---|---|
| `ApexCRUDViolation` | Missing CRUD/FLS check before DML |
| `ApexSOQLInjection` | SOQL injection vulnerability |
| `AvoidGlobalModifier` | Unnecessary `global` keyword |
| `ApexUnitTestClassShouldHaveAsserts` | Test method missing assertions |
| `ApexUnitTestMethodShouldHaveIsTestAnnotation` | Missing `@IsTest` annotation |
| `CyclomaticComplexity` | Method too complex |
| `OperationWithLimitsInLoop` | DML/SOQL in loop |

### ESLint for LWC

```json
// .eslintrc.json (project root)
{
  "extends": ["@salesforce/eslint-config-lwc/recommended"],
  "rules": {
    "no-console": "warn",
    "@lwc/lwc/no-async-operation": "error",
    "@lwc/lwc/no-inner-html": "error"
  }
}
```

---

## Metadata API vs Source API

### Comparison

| Feature | Metadata API | Source Format (SFDX) |
|---|---|---|
| File format | Single large XML files | Decomposed, human-readable files |
| Git-friendly | Poor (large XML diffs) | Excellent (small granular files) |
| Deployment tool | `sf project deploy start --metadata-dir` | `sf project deploy start --source-dir` |
| Source tracking | No | Yes (scratch orgs + sandboxes) |
| Use case | Legacy, enterprise, change sets | Modern source-driven development |

### Converting Between Formats

```bash
# Convert source format → metadata format
sf project convert source --output-dir mdapi_output --source-dir force-app

# Convert metadata format → source format
sf project convert mdapi --root-dir mdapi_input --output-dir force-app
```
