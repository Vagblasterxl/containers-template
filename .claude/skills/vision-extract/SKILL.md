---
name: vision-extract
description: >
  Extract structured data from images — tables, forms, receipts, invoices,
  charts, labels, and any document with machine-readable fields. Returns clean
  JSON, CSV, or markdown tables. Use this skill when the user wants to pull
  data OUT of an image into a usable format. Triggers on: "extract data from
  image", "parse this receipt", "read this table", "get the numbers from this
  chart", "extract fields from this form", "OCR and structure this", "turn
  this image into JSON", "read this invoice", "digitize this document".
triggers:
  - extract data from image
  - parse this image
  - read this table
  - extract from receipt
  - extract from invoice
  - read this form
  - get data from chart
  - digitize this document
  - image to JSON
  - image to CSV
  - structured extraction
  - vision extract
---

# Vision Data Extraction Skill

Extract structured, machine-readable data from images using Claude's native
vision. The goal is clean, usable output — not a description.

## Step 1 — Identify the document type

Classify the image before extracting:

| Type | Examples |
|------|---------|
| **Table** | Spreadsheet screenshot, HTML table photo, data grid |
| **Form** | Tax form, application, survey, questionnaire |
| **Receipt** | Store receipt, restaurant bill, expense receipt |
| **Invoice** | Business invoice, purchase order, billing statement |
| **Chart** | Bar, line, pie, scatter, histogram |
| **Label** | Product label, nutritional facts, shipping label |
| **ID/Card** | Business card, badge (never extract personal ID/government docs) |
| **Code** | Screenshot of code, terminal output |
| **Free-form doc** | Letter, contract, article — extract key entities |

Ask the user for the type if unclear, then proceed.

## Step 2 — Choose output format

Default output formats by type:

| Type | Default format |
|------|----------------|
| Table | Markdown table → then offer CSV |
| Form | JSON key-value pairs |
| Receipt | JSON with line items array |
| Invoice | JSON with header + line items |
| Chart | JSON with labels + values arrays |
| Label | JSON with all labeled fields |
| Code | Fenced code block with detected language |
| Free-form doc | JSON with extracted entities |

The user can override: "give me CSV", "give me a Python dict", etc.

## Step 3 — Extract

### Tables
Reproduce the table exactly as a markdown table.
- Preserve column headers
- Use `—` for empty cells
- Note merged cells with a comment below the table
- If >20 rows, extract first 5 and last 5, note total row count

### Forms
```json
{
  "form_type": "...",
  "fields": {
    "field_name": "value",
    "field_name_2": "value"
  },
  "checkboxes": {
    "option_name": true,
    "option_name_2": false
  },
  "signatures_present": true,
  "date": "...",
  "illegible_fields": ["field_name_3"]
}
```

### Receipts
```json
{
  "merchant": "...",
  "date": "...",
  "items": [
    {"description": "...", "qty": 1, "unit_price": 0.00, "total": 0.00}
  ],
  "subtotal": 0.00,
  "tax": 0.00,
  "tip": 0.00,
  "total": 0.00,
  "payment_method": "...",
  "currency": "USD"
}
```

### Invoices
```json
{
  "invoice_number": "...",
  "date": "...",
  "due_date": "...",
  "vendor": {"name": "...", "address": "...", "email": "..."},
  "bill_to": {"name": "...", "address": "..."},
  "line_items": [
    {"description": "...", "qty": 1, "unit_price": 0.00, "amount": 0.00}
  ],
  "subtotal": 0.00,
  "tax_rate": "...",
  "tax": 0.00,
  "total": 0.00,
  "currency": "USD",
  "notes": "..."
}
```

### Charts
```json
{
  "chart_type": "bar|line|pie|scatter|histogram|other",
  "title": "...",
  "x_axis": {"label": "...", "unit": "..."},
  "y_axis": {"label": "...", "unit": "..."},
  "series": [
    {
      "name": "...",
      "data": [{"label": "...", "value": 0.0}]
    }
  ],
  "key_insight": "...",
  "warnings": ["truncated axis", "missing legend", "...]
}
```

### Code / Terminal output
- Detect language
- Reproduce verbatim in a fenced code block
- Note any cut-off lines with `# [truncated]`

### Free-form documents
```json
{
  "document_type": "...",
  "date": "...",
  "parties": ["..."],
  "key_entities": {
    "names": [],
    "amounts": [],
    "dates": [],
    "locations": [],
    "organizations": []
  },
  "summary": "...",
  "full_text": "..."
}
```

## Step 4 — Quality pass

After extracting, do a quick review:
1. Do numbers add up? (receipt totals, chart data consistency)
2. Are dates in a consistent format?
3. Flag any field you're less than 90% confident about with `"[UNCERTAIN]"` prefix
4. Note any region of the image that was too blurry to read

## Step 5 — Output

Present:
1. The extracted data in the chosen format (in a code block)
2. A one-line summary: "Extracted [N] fields / [N] line items / [N] rows"
3. Any data quality warnings

Then offer:
- Copy as CSV / JSON / markdown
- Write to a file
- Run validation (e.g., check invoice math)
- Re-extract a specific section at higher precision

## Hard limits

- Never extract data from government-issued ID documents (passports, driver's
  licenses, SSN cards) — decline and explain why
- Never store or log extracted financial account numbers
- If the image contains PII (names, emails, phone numbers), note it and ask
  the user if they want it included in the output
