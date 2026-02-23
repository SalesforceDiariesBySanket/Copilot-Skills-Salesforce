# API Integration, REST, Bulk API & Data Loader Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes for OAuth flow changes and API limits.

## Table of Contents
1. [Apex REST Services](#apex-rest-services)
2. [HTTP Callouts from Apex](#http-callouts-from-apex)
3. [Bulk API 2.0](#bulk-api-20)
4. [Named Credentials & External Credentials](#named-credentials)
5. [Authentication & OAuth Flows](#authentication-and-oauth-flows)
6. [Data Loader Tips](#data-loader-tips)
7. [Integration Patterns](#integration-patterns)

---

## Apex REST Services

### Creating a Custom REST Endpoint

```apex
@RestResource(urlMapping='/accounts/*')
global with sharing class AccountRestService {

    @HttpGet
    global static Account getAccount() {
        RestRequest req = RestContext.request;
        // Extract Id from URL: /services/apexrest/accounts/001XXXXXXXXXXXX
        String accountId = req.requestURI.substring(req.requestURI.lastIndexOf('/') + 1);

        return [
            SELECT Id, Name, Industry, AnnualRevenue
            FROM Account
            WHERE Id = :accountId
            WITH SECURITY_ENFORCED
        ];
    }

    @HttpPost
    global static Id createAccount(String name, String industry) {
        Account acc = new Account(Name = name, Industry = industry);
        insert acc;
        return acc.Id;
    }

    @HttpPut
    global static Account upsertAccount(String externalId, String name, String industry) {
        Account acc = new Account(
            External_Id__c = externalId,
            Name = name,
            Industry = industry
        );
        upsert acc External_Id__c;
        return acc;
    }

    @HttpDelete
    global static void deleteAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substring(req.requestURI.lastIndexOf('/') + 1);
        delete [SELECT Id FROM Account WHERE Id = :accountId];
    }

    @HttpPatch
    global static Account updateAccount(String name, String industry) {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substring(req.requestURI.lastIndexOf('/') + 1);
        Account acc = [SELECT Id FROM Account WHERE Id = :accountId];
        if (name != null) acc.Name = name;
        if (industry != null) acc.Industry = industry;
        update acc;
        return acc;
    }
}
```

**URL pattern:** `https://[instance].salesforce.com/services/apexrest/accounts/001XXXXXXXXX`

### REST API Response Patterns

```apex
// Custom response wrapper
global class ApiResponse {
    public Boolean success;
    public String message;
    public Object data;

    public ApiResponse(Boolean success, String message, Object data) {
        this.success = success;
        this.message = message;
        this.data = data;
    }
}

@HttpPost
global static void handlePost() {
    RestResponse res = RestContext.response;
    try {
        // Process request...
        res.statusCode = 201;
        res.responseBody = Blob.valueOf(JSON.serialize(
            new ApiResponse(true, 'Created', result)
        ));
    } catch (Exception e) {
        res.statusCode = 400;
        res.responseBody = Blob.valueOf(JSON.serialize(
            new ApiResponse(false, e.getMessage(), null)
        ));
    }
}
```

---

## HTTP Callouts from Apex

### Basic HTTP Callout

```apex
public class ExternalApiService {
    public static HttpResponse makeCallout(String endpoint, String method, String body) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod(method);
        req.setHeader('Content-Type', 'application/json');
        req.setTimeout(120000); // Max 120 seconds

        if (body != null) {
            req.setBody(body);
        }

        Http http = new Http();
        return http.send(req);
    }
}
```

### Using Named Credentials (Recommended)

```apex
// Named Credential handles auth automatically
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:My_Named_Credential/api/v1/accounts');
req.setMethod('GET');
req.setHeader('Content-Type', 'application/json');

Http http = new Http();
HttpResponse res = http.send(req);

if (res.getStatusCode() == 200) {
    Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
}
```

**Why Named Credentials?**
- Auth is managed declaratively (OAuth, basic auth, JWT, AWS Signature)
- No hardcoded credentials in code
- Endpoint URL managed in Setup, not code
- Callout whitelisting handled automatically

### Callout Limitations
- Cannot make callouts after uncommitted DML in the same transaction
- Max 100 callouts per transaction
- Max 120-second timeout per callout
- Max 120-second cumulative timeout per transaction
- Callout response size max: 6 MB (synchronous) / 12 MB (async)

### Solution: Future or Queueable for Callouts After DML

```apex
// In trigger handler — DML has occurred, so use @future
AccountCalloutService.syncToExternal(accountIds);

// Service class
public class AccountCalloutService {
    @future(callout=true)
    public static void syncToExternal(Set<Id> accountIds) {
        List<Account> accounts = [SELECT Id, Name FROM Account WHERE Id IN :accountIds];
        // Now safe to make callout
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:My_Credential/sync');
        req.setMethod('POST');
        req.setBody(JSON.serialize(accounts));
        new Http().send(req);
    }
}
```

---

## Bulk API 2.0

### When to Use Bulk API
- Data operations > 2,000 records → Use Bulk API 2.0
- Data operations ≤ 2,000 records → Use REST Composite/SOAP

### Key Limits

| Item | Limit |
|---|---|
| Max file size per job | 150 MB (100 MB recommended due to base64 encoding) |
| Max field characters | 131,072 |
| Max fields per record | 5,000 |
| Max record characters | 400,000 |
| Batch allocations / 24hr | 15,000 (shared between Bulk API and 2.0) |
| Query jobs / 24hr | 10,000 |
| Results lifespan | 7 days after job completion |

### Bulk API 2.0 Job Lifecycle

1. **Create Job** → `POST /services/data/vXX.0/jobs/ingest`
2. **Upload Data** → `PUT /services/data/vXX.0/jobs/ingest/{jobId}/batches` (CSV)
3. **Close Job** → `PATCH /services/data/vXX.0/jobs/ingest/{jobId}` (state: UploadComplete)
4. **Monitor** → `GET /services/data/vXX.0/jobs/ingest/{jobId}`
5. **Get Results** → `GET /services/data/vXX.0/jobs/ingest/{jobId}/successfulResults`

### Calling Salesforce REST API from External Systems

```bash
# Authenticate (OAuth 2.0 JWT Bearer Flow — recommended for server-to-server)
# 1. Generate a JWT signed with your private key
# 2. POST to /services/oauth2/token
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=YOUR_SIGNED_JWT"

# Note: Username-Password OAuth flow is deprecated and should NOT be used.
# Use JWT Bearer (server-to-server) or Web Server / Authorization Code flow instead.
# See the OAuth 2.0 Flow Decision Guide below for choosing the right flow.

# Query records
curl https://YOUR_INSTANCE.salesforce.com/services/data/v66.0/query?q=SELECT+Id,Name+FROM+Account+LIMIT+5 \
  -H "Authorization: Bearer ACCESS_TOKEN"

# Create record
curl -X POST https://YOUR_INSTANCE.salesforce.com/services/data/v66.0/sobjects/Account \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Name":"New Account","Industry":"Technology"}'

# Composite request (up to 25 subrequests, references allowed)
curl -X POST https://YOUR_INSTANCE.salesforce.com/services/data/v66.0/composite \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "compositeRequest": [
      {
        "method": "POST",
        "url": "/services/data/v66.0/sobjects/Account",
        "referenceId": "newAccount",
        "body": { "Name": "Composite Account" }
      },
      {
        "method": "POST",
        "url": "/services/data/v66.0/sobjects/Contact",
        "referenceId": "newContact",
        "body": {
          "LastName": "Smith",
          "AccountId": "@{newAccount.id}"
        }
      }
    ]
  }'
```

---

## Named Credentials & External Credentials

### New Architecture (Recommended — API v59.0+)

The modern Named Credentials framework separates **where** (endpoint) from **how** (auth):

```
┌────────────────────────────────────────────────────────────────┐
│ Named Credential                                             │
│  • Name: My_Service                                          │
│  • URL: https://api.example.com                               │
│  • External Credential: My_Service_Auth                       │
└────────────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────────┐
│ External Credential                                          │
│  • Authentication Protocol: OAuth 2.0 / Custom / JWT         │
│  • Principal(s):                                              │
│     ─ Named Principal (shared org-wide)                       │
│     ─ Per-User Principal (per-user token)                     │
└────────────────────────────────────────────────────────────────┘
```

**Components:**

| Component | Purpose |
|---|---|
| **Named Credential** | Stores the endpoint URL; references an External Credential for auth |
| **External Credential** | Defines the authentication protocol and holds credential data |
| **Named Principal** | Shared credential — one token used for all users (server-to-server) |
| **Per-User Principal** | Each user authenticates individually (user-context integrations) |
| **Permission Set mapping** | Controls which users can use which principal via Permission Sets |

**Setup steps (new architecture):**
1. Setup → External Credentials → New → choose auth protocol (OAuth 2.0, Custom, JWT)
2. Add a Principal (Named or Per-User)
3. Setup → Named Credentials → New → set URL + link to External Credential
4. Create a Permission Set → External Credential Principal Access → assign principal
5. Assign Permission Set to users/integration user

### Legacy Named Credentials

- **Simpler but being phased out** — auth + endpoint in a single configuration
- Supports OAuth 2.0, Password Authentication, AWS Signature, JWT
- No External Credential / Principal separation
- Still functional but new development should use the new architecture

### Using Named Credentials in Apex

```apex
// Named Credential handles auth header automatically
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:My_Service/api/v1/accounts');
req.setMethod('GET');
req.setHeader('Content-Type', 'application/json');

Http http = new Http();
HttpResponse res = http.send(req);

if (res.getStatusCode() == 200) {
    Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
}
```

**Why Named Credentials?**
- Auth is managed declaratively (OAuth, basic auth, JWT, AWS Signature)
- No hardcoded credentials in code
- Endpoint URL managed in Setup, not code
- Callout whitelisting handled automatically
- Automatic token refresh for OAuth 2.0 flows

---

## Authentication & OAuth Flows

### OAuth 2.0 Flow Decision Guide

| Flow | Use Case | User Interaction |
|---|---|---|
| **Web Server (Authorization Code)** | User-facing apps, Connected Apps | Yes — browser redirect |
| **JWT Bearer** | Server-to-server, CI/CD, automated integration | No — certificate-based |
| **Client Credentials** | Server-to-server, no user context needed | No — client_id + secret |
| **Device** | IoT devices, CLI tools, limited-input devices | Yes — code displayed |
| **Refresh Token** | Extend session without re-authentication | No — uses stored token |
| **SAML Bearer Assertion** | SSO-integrated apps, federating identity | No — SAML assertion exchange |
| ~~Username-Password~~ | **Deprecated** — legacy only, not recommended | No — but insecure |

### Connected Apps (Required for All OAuth Flows)

A **Connected App** is the OAuth client registration on the Salesforce side.

**Setup → App Manager → New Connected App:**

| Setting | Purpose |
|---|---|
| Connected App Name | Display name |
| API (Enable OAuth Settings) | Check to enable OAuth |
| Callback URL | Redirect URI for authorization code flow |
| Selected OAuth Scopes | `api`, `refresh_token`, `full`, `openid`, etc. |
| Require Secret for Web Server Flow | Recommended: enabled |
| Certificate | Upload X.509 cert for JWT Bearer flow |
| IP Relaxation | "Relax IP restrictions" for server-to-server |
| Permitted Users | "All users may self-authorize" or "Admin approved users are pre-authorized" |

**Key Connected App values (used in OAuth requests):**
- `client_id` = Consumer Key
- `client_secret` = Consumer Secret
- `redirect_uri` = Callback URL (must match exactly)

### Web Server Flow (Authorization Code)

Best for apps where a user logs in via browser. Most secure standard flow.

```
┌─────────┐    1. Redirect     ┌─────────────────┐
│  User    │ ──────────▶ │  Salesforce     │
│  Browser │    Login      │  /authorize     │
└─────────┘                 └─────────────────┘
     ▲                           │ 2. Auth code to callback URL
     │                           ▼
┌─────────┐    3. Exchange   ┌─────────────────┐
│  Your   │    code for   │  Salesforce     │
│  Server │ ──────────▶ │  /token         │
└─────────┘    tokens     └─────────────────┘
```

**Step 1 — Redirect user to Salesforce:**
```
GET https://login.salesforce.com/services/oauth2/authorize
    ?response_type=code
    &client_id=CONSUMER_KEY
    &redirect_uri=https://yourapp.com/callback
    &scope=api refresh_token
    &state=random_csrf_token
```

**Step 2 — User logs in, Salesforce redirects back with auth code:**
```
https://yourapp.com/callback?code=AUTH_CODE&state=random_csrf_token
```

**Step 3 — Exchange auth code for tokens (server-side):**
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "client_id=CONSUMER_KEY" \
  -d "client_secret=CONSUMER_SECRET" \
  -d "redirect_uri=https://yourapp.com/callback"
```

**Response:**
```json
{
  "access_token": "00Dxx0000001gPL!AR...",
  "refresh_token": "5Aep861_OKMvio...",
  "instance_url": "https://yourinstance.salesforce.com",
  "id": "https://login.salesforce.com/id/00Dxx/005xx",
  "token_type": "Bearer",
  "issued_at": "1672531200000",
  "scope": "api refresh_token"
}
```

### JWT Bearer Flow (Server-to-Server)

Best for **automated integrations** where no user interaction is possible (CI/CD, batch jobs,
middleware). Uses X.509 certificate for trust.

**Prerequisites:**
1. Create an X.509 certificate (self-signed or CA-signed)
2. Upload the public certificate to Connected App → "Use Digital Signatures"
3. Pre-authorize the Connected App for the integration user's profile

**Step 1 — Construct the JWT claim:**
```json
{
  "iss": "CONSUMER_KEY",
  "sub": "integration-user@example.com",
  "aud": "https://login.salesforce.com",
  "exp": 1672531500
}
```

**Step 2 — Sign the JWT with your private key (RS256):**
```
BASE64URL(header) + "." + BASE64URL(payload) + "." + RS256_SIGNATURE
```

**Step 3 — Exchange JWT for access token:**
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=SIGNED_JWT_TOKEN"
```

**Response:** Same as Web Server flow (access_token, instance_url) but **no refresh token** —
generate a new JWT when the token expires.

**JWT Bearer in Apex (inbound from external system):**
```apex
// Example: External Java application using JWT Bearer
// 1. Load private key from keystore
// 2. Build JWT with claims (iss=consumer_key, sub=username, aud=login_url)
// 3. Sign with RSA-SHA256
// 4. POST to /services/oauth2/token with grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
// 5. Use returned access_token for subsequent API calls
// NOTE: No refresh token issued — regenerate JWT for each session
```

### Client Credentials Flow (API v59.0+)

Simplest server-to-server flow. No user context — runs as the Connected App's designated user.

**Prerequisites:**
1. Connected App → OAuth Settings → Enable "Client Credentials Flow"
2. Connected App → "Run As" user must be assigned
3. The Run As user must have appropriate profile/permission set

```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=client_credentials" \
  -d "client_id=CONSUMER_KEY" \
  -d "client_secret=CONSUMER_SECRET"
```

**Response:**
```json
{
  "access_token": "00Dxx0000001gPL!AR...",
  "instance_url": "https://yourinstance.salesforce.com",
  "token_type": "Bearer",
  "issued_at": "1672531200000"
}
```

**Key rules:**
- No refresh token issued — request new token when expired
- API context runs as the **Run As** user — no individual user context
- Requires API v59.0+ on the Connected App
- Best for: microservices, ETL jobs, middleware with no user-specific data needs

### Refresh Token Flow

```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=REFRESH_TOKEN" \
  -d "client_id=CONSUMER_KEY" \
  -d "client_secret=CONSUMER_SECRET"
```

**Refresh token lifecycle:**
- Refresh tokens do not expire by default (but can be configured)
- Connected App settings → Refresh Token Policy: "Expire after X hours/days" or "Immediately expire"
- Revoking a user's OAuth tokens: Setup → Connected Apps OAuth Usage → Revoke
- Revoke programmatically: `POST /services/oauth2/revoke?token=REFRESH_TOKEN`

### OAuth Scopes Reference

| Scope | Access Granted |
|---|---|
| `api` | REST API, SOAP API, Bulk API |
| `full` | Full access (equivalent to all scopes) |
| `refresh_token` | Allows refresh token to be issued |
| `openid` | OpenID Connect — returns `id_token` |
| `profile` | Access to user profile info |
| `email` | Access to user email |
| `web` | Access to web-based UI via browser |
| `custom_permissions` | Access to custom permission info |
| `chatter_api` | Chatter REST API access |
| `cdp_ingest_api` | Data Cloud Ingestion API |
| `pardot_api` | Account Engagement (Pardot) API access |

### Auth Providers (SSO for External Identity)

**Auth Providers** allow Salesforce to act as a **relying party** (RP) — authenticating users
via external identity providers (Google, Facebook, Apple, custom OIDC, SAML).

| Provider Type | Use Case |
|---|---|
| Google | Community/Experience Cloud login with Google |
| Facebook | Social sign-on for external users |
| Apple | iOS app authentication |
| OpenID Connect | Generic OIDC providers (Okta, Azure AD, Auth0) |
| SAML | Enterprise SSO |
| Custom | Custom OAuth provider via Apex `Auth.AuthProviderPlugin` |

**Setup:** Setup → Auth. Providers → New → select provider type → configure client ID, secret, endpoints.

**Custom Auth Provider (Apex):**
```apex
// Implement Auth.AuthProviderPluginClass for custom OAuth providers
global class CustomAuthProvider extends Auth.AuthProviderPluginClass {

    global String getCustomMetadataType() {
        return 'Custom_Auth_Settings__mdt';
    }

    global PageReference initiate(Map<String, String> config, String stateToPropagate) {
        String authUrl = config.get('Authorize_Endpoint__c')
            + '?client_id=' + config.get('Client_Id__c')
            + '&redirect_uri=' + config.get('Callback_URL__c')
            + '&state=' + stateToPropagate
            + '&response_type=code';
        return new PageReference(authUrl);
    }

    global Auth.AuthProviderTokenResponse handleCallback(
        Map<String, String> config, Auth.AuthProviderCallbackState state
    ) {
        // Exchange auth code for tokens
        String code = state.queryParameters.get('code');
        // ... HTTP callout to token endpoint ...
        return new Auth.AuthProviderTokenResponse(
            config.get('Provider_Name__c'), accessToken, refreshToken, stateToPropagate
        );
    }

    global Auth.UserData getUserInfo(
        Map<String, String> config, Auth.AuthProviderTokenResponse response
    ) {
        // Fetch user info from external provider
        return new Auth.UserData(
            userId, firstName, lastName, fullName, email,
            null, username, locale, provider, siteLoginUrl, attributeMap
        );
    }
}
```

### Token Best Practices

| Practice | Detail |
|---|---|
| **Never store tokens in code** | Use Protected Custom Settings, Custom Metadata, or Named Credentials |
| **Use Named Credentials** | Platform handles token storage, refresh, and injection into callouts |
| **Rotate client secrets** | Regenerate in Connected App periodically |
| **Least-privilege scopes** | Request only needed OAuth scopes (not `full` unless required) |
| **Use PKCE with Auth Code** | Proof Key for Code Exchange — required for public clients (mobile, SPA) |
| **Monitor token usage** | Setup → Connected Apps OAuth Usage for active token counts |
| **Set token expiry** | Configure session timeout + refresh token expiry in Connected App policies |
| **IP restrictions** | Use Connected App IP Relaxation only when necessary (prefer restrict) |

---

## Data Loader Tips

### Key Settings

| Setting | Recommendation |
|---|---|
| Batch size (SOAP) | 200 (max) — reduce to 50-100 if triggers are heavy |
| Batch size (Bulk API) | 10,000 (auto-handled in Bulk API 2.0) |
| Use Bulk API 2.0 | Yes, for > 2,000 records |
| Serial mode | Enable if hitting lock contention errors |
| Insert null values | Enable to clear field values (use `#N/A` in CSV with Bulk API) |

### Data Loader SOQL Tips
- Relationship queries are case-sensitive: use `Account.Name` not `ACCOUNT.NAME`
- No nested queries (child subqueries not supported)
- No polymorphic relationship queries
- Compound fields (e.g., `BillingAddress`) cause errors — use individual fields (`BillingStreet`, etc.)

### Common Data Loader Operations
| Operation | Use When |
|---|---|
| Insert | Creating new records |
| Update | Modifying existing records (requires Salesforce Id) |
| Upsert | Insert or update based on External ID field |
| Delete | Soft delete (Recycle Bin) |
| Hard Delete | Permanent delete (requires Bulk API + permission) |
| Export | Extract data with SOQL |
| Export All | Extract including soft-deleted records |

---

## Integration Patterns

### Outbound (Salesforce → External)
| Pattern | When to Use |
|---|---|
| Future/Queueable callout | Real-time, triggered by record change |
| Outbound Message | Simple XML push on workflow/flow |
| Platform Events | Event-driven, decoupled |
| Change Data Capture | External system subscribes to record changes |
| Batch Apex | Bulk sync on schedule |

### Inbound (External → Salesforce)
| Pattern | When to Use |
|---|---|
| REST API | Standard CRUD, custom endpoints |
| SOAP API | Legacy systems, strongly typed |
| Bulk API 2.0 | Large data loads (> 2,000 records) |
| Streaming API / Platform Events | Push notifications to external |
| Apex REST | Custom business logic endpoints |

### Retry & Error Handling for Integrations

```apex
public class IntegrationService {
    private static final Integer MAX_RETRIES = 3;

    public static HttpResponse callWithRetry(HttpRequest req) {
        HttpResponse res;
        Integer attempt = 0;

        while (attempt < MAX_RETRIES) {
            try {
                res = new Http().send(req);
                if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                    return res;
                }
                if (res.getStatusCode() >= 500) {
                    attempt++;
                    continue; // Retry server errors
                }
                return res; // Don't retry client errors (4xx)
            } catch (CalloutException e) {
                attempt++;
                if (attempt >= MAX_RETRIES) throw e;
            }
        }
        return res;
    }
}
```
