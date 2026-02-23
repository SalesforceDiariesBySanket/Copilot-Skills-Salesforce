# Formulas, Validation Rules & Date/Time Reference

> **Validated as of: 2026-02** — Review against current Salesforce release notes for formula function changes.

## Table of Contents
1. [Formula Field Patterns](#formula-field-patterns)
2. [Validation Rule Patterns](#validation-rule-patterns)
3. [Date and Time Formulas](#date-and-time-formulas)
4. [Cross-Object Formulas](#cross-object-formulas)
5. [Common Functions Reference](#common-functions-reference)

---

## Formula Field Patterns

### Conditional Logic
```
// IF statement
IF(AnnualRevenue > 1000000, "Enterprise", IF(AnnualRevenue > 100000, "Mid-Market", "SMB"))

// CASE statement (cleaner for multiple values)
CASE(Industry,
    "Technology", "Tech",
    "Healthcare", "Health",
    "Financial Services", "Finance",
    "Other"
)

// Nested CASE with numeric values
CASE(Rating,
    "Hot", 3,
    "Warm", 2,
    "Cold", 1,
    0
)
```

### Text Manipulation
```
// Concatenation
FirstName & " " & LastName

// Conditional text
IF(ISBLANK(MiddleName),
    FirstName & " " & LastName,
    FirstName & " " & MiddleName & " " & LastName
)

// Extract domain from email
MID(Email, FIND("@", Email) + 1, LEN(Email) - FIND("@", Email))

// Pad with leading zeros
RIGHT("000000" & TEXT(Invoice_Number__c), 6)

// Convert text to hyperlink
HYPERLINK("/lightning/r/Account/" & Id & "/view", Name, "_self")

// Image formula
IMAGE(
    CASE(Rating,
        "Hot", "/img/samples/color_red.gif",
        "Warm", "/img/samples/color_yellow.gif",
        "Cold", "/img/samples/color_green.gif",
        "/img/samples/color_gray.gif"
    ),
    "Rating: " & TEXT(Rating),
    20, 20
)
```

### Numeric Calculations
```
// Percentage
IF(Total_Revenue__c != 0,
    (Total_Revenue__c - Total_Cost__c) / Total_Revenue__c * 100,
    0
)

// Weighted score
(Criteria_1__c * 0.4) + (Criteria_2__c * 0.3) + (Criteria_3__c * 0.3)

// Currency with null safety
BLANKVALUE(Amount, 0) * BLANKVALUE(Discount_Percent__c, 0) / 100

// Round to 2 decimal places
ROUND(Amount * Tax_Rate__c / 100, 2)
```

### Record Age & Elapsed Time
```
// Days since creation
TODAY() - DATEVALUE(CreatedDate)

// Business days since creation (excludes weekends)
CASE(MOD(DATEVALUE(CreatedDate) - DATE(1900, 1, 6), 7),
    0, (TODAY() - DATEVALUE(CreatedDate)) - 2 * FLOOR((TODAY() - DATEVALUE(CreatedDate)) / 7),
    6, (TODAY() - DATEVALUE(CreatedDate)) - 2 * FLOOR((TODAY() - DATEVALUE(CreatedDate)) / 7) - 1,
    (TODAY() - DATEVALUE(CreatedDate)) - 2 * FLOOR((TODAY() - DATEVALUE(CreatedDate) - 1) / 7)
)

// Aging bucket
IF(TODAY() - DATEVALUE(CreatedDate) <= 30, "0-30 Days",
IF(TODAY() - DATEVALUE(CreatedDate) <= 60, "31-60 Days",
IF(TODAY() - DATEVALUE(CreatedDate) <= 90, "61-90 Days",
    "90+ Days")))
```

---

## Validation Rule Patterns

### Required Field Validation
```
// Require Industry when Account is "Customer"
AND(
    ISPICKVAL(Type, "Customer"),
    ISPICKVAL(Industry, "")
)
Error: "Industry is required for Customer accounts."

// Require Close Date in the future for new Opportunities
AND(
    ISNEW(),
    CloseDate <= TODAY()
)
Error: "Close Date must be in the future for new opportunities."
```

### Format Validation
```
// US Phone format (10 digits)
NOT(REGEX(Phone, "\\(?\\d{3}\\)?[-\\s]?\\d{3}[-\\s]?\\d{4}"))
Error: "Phone must be in format (XXX) XXX-XXXX or XXX-XXX-XXXX"

// Email format
NOT(REGEX(Email, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))
Error: "Please enter a valid email address."

// US Zip Code (5 or 5+4)
NOT(REGEX(BillingPostalCode, "\\d{5}(-\\d{4})?"))
Error: "Zip code must be in XXXXX or XXXXX-XXXX format."

// Canadian Postal Code
AND(
    OR(BillingCountry = "CAN", BillingCountry = "CA", BillingCountry = "Canada"),
    NOT(REGEX(BillingPostalCode, "(?i)[ABCEGHJKLMNPRSTVXY]\\d[A-Z]?\\s?\\d[A-Z]\\d"))
)
Error: "Canadian postal code must be in A9A 9A9 format."

// SSN format (XXX-XX-XXXX)
NOT(REGEX(SSN__c, "\\d{3}-\\d{2}-\\d{4}"))
Error: "SSN must be in XXX-XX-XXXX format."
```

### Business Logic Validation
```
// Discount cannot exceed 40% without VP approval
AND(
    Discount_Percent__c > 40,
    NOT(ISPICKVAL(VP_Approval_Status__c, "Approved"))
)
Error: "Discounts above 40% require VP approval."

// Prevent changing Stage backward
AND(
    NOT(ISNEW()),
    CASE(StageName,
        "Prospecting", 1,
        "Qualification", 2,
        "Needs Analysis", 3,
        "Proposal", 4,
        "Negotiation", 5,
        "Closed Won", 6,
        "Closed Lost", 7,
        0
    ) <
    CASE(PRIORVALUE(StageName),
        "Prospecting", 1,
        "Qualification", 2,
        "Needs Analysis", 3,
        "Proposal", 4,
        "Negotiation", 5,
        "Closed Won", 6,
        "Closed Lost", 7,
        0
    )
)
Error: "Opportunity stage cannot be moved backward."

// Ensure Amount is positive when Stage is Closed Won
AND(
    ISPICKVAL(StageName, "Closed Won"),
    OR(ISBLANK(Amount), Amount <= 0)
)
Error: "Amount must be greater than zero for Closed Won opportunities."

// Prevent editing closed cases (unless System Admin)
AND(
    ISPICKVAL(Status, "Closed"),
    NOT(ISNEW()),
    $Profile.Name != "System Administrator",
    ISCHANGED(Subject) || ISCHANGED(Description) || ISCHANGED(Priority)
)
Error: "Closed cases cannot be edited. Please reopen the case first."
```

### Cross-Object Validation
```
// Prevent creating Contact if Account is inactive
AND(
    ISNEW(),
    NOT(Account.Active__c)
)
Error: "Cannot create contacts for inactive accounts."
```

---

## Date and Time Formulas

### Date Functions
| Function | Description | Example |
|---|---|---|
| `TODAY()` | Current date | `TODAY()` |
| `NOW()` | Current date/time | `NOW()` |
| `DATE(year, month, day)` | Construct date | `DATE(2025, 12, 31)` |
| `DATEVALUE(datetime)` | Extract date from datetime | `DATEVALUE(CreatedDate)` |
| `DATETIMEVALUE(text)` | Parse text to datetime | `DATETIMEVALUE("2025-01-15 08:00:00")` |
| `DAY(date)` | Day of month (1-31) | `DAY(CloseDate)` |
| `MONTH(date)` | Month (1-12) | `MONTH(CloseDate)` |
| `YEAR(date)` | Year | `YEAR(CloseDate)` |
| `WEEKDAY(date)` | Day of week (1=Sun, 7=Sat) | `WEEKDAY(TODAY())` |

### Common Date Calculations
```
// Add/subtract days
CloseDate + 30

// Add months
ADDMONTHS(TODAY(), 3)

// First day of current month
DATE(YEAR(TODAY()), MONTH(TODAY()), 1)

// Last day of current month
ADDMONTHS(DATE(YEAR(TODAY()), MONTH(TODAY()), 1), 1) - 1

// First day of current quarter
DATE(YEAR(TODAY()),
    3 * CEILING(MONTH(TODAY()) / 3) - 2, 1)

// End of current year
DATE(YEAR(TODAY()), 12, 31)

// Is weekend?
OR(WEEKDAY(TODAY()) = 1, WEEKDAY(TODAY()) = 7)

// Next business day
IF(WEEKDAY(TODAY() + 1) = 1, TODAY() + 2,
IF(WEEKDAY(TODAY() + 1) = 7, TODAY() + 3,
    TODAY() + 1))
```

### Time Zone Handling
```
// Convert UTC datetime to specific timezone (approximate with offset)
// PST = UTC - 8 hours
CreatedDate - (8/24)

// For proper timezone handling, use Apex:
// TimeZone tz = TimeZone.getTimeZone('America/Los_Angeles');
// Integer offset = tz.getOffset(dt);
```

### Duration / Elapsed Time
```
// Hours between two datetimes
(DATEVALUE(End_Date__c) - DATEVALUE(Start_Date__c)) * 24

// Business hours elapsed (approximate, 8 hours/day)
(DATEVALUE(End_Date__c) - DATEVALUE(Start_Date__c)) * 8

// Age in years
FLOOR((TODAY() - Date_of_Birth__c) / 365.25)
```

---

## Cross-Object Formulas

### Traversing Relationships
```
// Access parent fields (up to 10 levels, or 5 in some contexts)
Account.Owner.Manager.Email
Account.Parent.Name
Opportunity.Account.Industry

// Access related object through lookup
Contact.Account.BillingState
Order__c.Account__r.Owner.Name
```

### Cross-Object Formula Limits
- Max 10 unique cross-object references per formula
- Performance impact: each cross-object reference adds query overhead
- Cannot reference: long text fields, multi-select picklists across objects
- Formula size limit: 5,000 characters (compiled: 15,000)

---

## Common Functions Reference

### Logical
| Function | Description |
|---|---|
| `IF(condition, true_val, false_val)` | Conditional |
| `AND(cond1, cond2, ...)` | All true |
| `OR(cond1, cond2, ...)` | Any true |
| `NOT(condition)` | Negate |
| `CASE(expr, val1, result1, ..., default)` | Switch |
| `ISBLANK(field)` | Null/empty check |
| `BLANKVALUE(field, default)` | Null coalesce |
| `NULLVALUE(field, default)` | Null coalesce (legacy) |
| `ISNEW()` | Record being created |
| `ISCHANGED(field)` | Field value changed |
| `PRIORVALUE(field)` | Previous value |

### Text
| Function | Description |
|---|---|
| `LEN(text)` | String length |
| `LEFT(text, n)` / `RIGHT(text, n)` | Substring |
| `MID(text, start, length)` | Substring |
| `FIND(search, text)` | Find position (1-based) |
| `SUBSTITUTE(text, old, new)` | Replace all occurrences |
| `TRIM(text)` | Remove whitespace |
| `UPPER(text)` / `LOWER(text)` | Case conversion |
| `TEXT(value)` | Convert to text |
| `VALUE(text)` | Convert to number |
| `REGEX(text, pattern)` | Regex match (boolean) |
| `CONTAINS(text, search)` | Contains substring |
| `BEGINS(text, prefix)` | Starts with |

### Math
| Function | Description |
|---|---|
| `ROUND(number, places)` | Round |
| `CEILING(number)` | Round up |
| `FLOOR(number)` | Round down |
| `ABS(number)` | Absolute value |
| `MAX(n1, n2, ...)` / `MIN(n1, n2, ...)` | Max/Min |
| `MOD(dividend, divisor)` | Modulus |
| `SQRT(number)` | Square root |
