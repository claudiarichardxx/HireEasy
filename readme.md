# Candidate Shortlisting Automation

Link to the GitHub repository: https://github.com/claudiarichardxx/HireEasy.git
This repository automates an Airtable-backed applicant pipeline. It:

* Creates the Airtable schema (tables + fields) via API.
* Normalizes and compresses multi-table applicant data into a single JSON blob for storage/routing.
* Decompresses that JSON back into normalized tables when needed.
* Calls an LLM to generate a summary/score/follow-ups per applicant.
* Applies rules to shortlist strong candidates into a "Shortlisted Leads" table.
* Logs everything to a file and console for auditing.

---

## Quick Start

```bash
git clone https://github.com/claudiarichardxx/HireEasy.git
cd HireEasy
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Add your credentials and table names
cp .env.example .env  # or create a .env (see "Environment Variables")

# 1) Create Airtable schema
python setupAirTables.py

# 2) (Optional) Backfill compressed JSON in Applicants
python compress.py

# 3) (Optional) Decompress compressed JSON into child tables
python decompress.py

# 4) Generate LLM fields (summary/score/follow-ups)
python summaryGeneration.py

# 5) Apply shortlisting logic
python shortlist.py
```

---

## Repository Structure

```
.
├─ utils/
│  ├─ airTableHelpers.py      # Airtable REST helpers (create table, CRUD records, etc.)
│  └─ dbModel.py              # Table definitions + schema creation routines
├─ compress.py                # Builds “Compressed JSON” in Applicants
├─ decompress.py              # Expands “Compressed JSON” back into normalized child tables
├─ loggerConfig.py            # Central logging config (file + console)
├─ requirements.txt
├─ setupAirTables.py          # Creates all tables via Airtable Meta API
├─ shortlist.py               # Rules-based shortlisting to “Shortlisted Leads”
└─ summaryGeneration.py       # LLM call + writes LLM Summary/Score/Follow-Ups
```

> Note: File names are case-sensitive on Linux/macOS. Ensure imports match the actual casing (e.g., `from utils.dbModel import ...`). If your file is `dbmodel.py`, rename it to `dbModel.py` (or update imports) for consistency.

---

## Environment Variables

Create a `.env` in the repo root. Example:

```
# Airtable
airtable_token=pat_xxx
airtable_base_id=app_yyyyyyyyyyyyyy

# Table names (customize as needed)
applicants_table_name=Applicants
personal_details_table_name=Personal Details
work_experience_table_name=Work Experience
salary_preferences_table_name=Salary Preferences
shortlisted_leads_table_name=Shortlisted Leads

# OpenAI
openai_api_key=sk-...

# Logging
log_file=app.log
log_level=INFO
```

**Scopes:** Your Airtable token must have the appropriate scopes to create schema (Meta API write) and read/write records. If table creation fails, check token scopes and base permissions.

Add `.env` to `.gitignore` (already in this repo) so secrets never land in version control.

---

## Logging

All scripts use a shared logger from `loggerConfig.py`. Configuration:

```python
# loggerConfig.py
import logging
import os

def setup_logger(name="my_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, os.getenv("log_level", "INFO")))

    if not logger.handlers:
        fh = logging.FileHandler(os.getenv("log_file", "app.log"))
        ch = logging.StreamHandler()

        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(ch)

        # Avoid logger message duplication via root propagation
        logger.propagate = False

    return logger
```

If you run scripts repeatedly in notebooks, avoid duplicate handlers by keeping the `if not logger.handlers:` guard.

---

## Airtable Schema: Tables and Field Definitions

Tables are created by `setupAirTables.py` using `utils/dbModel.py`. Field definitions live directly in `dbModel.py`. Summary:

### Applicants (parent)

* **Applicant ID**: `email`
* **Compressed JSON**: `multilineText`
* **Shortlist Status**: `checkbox` (green, check icon) → automatically ticked when an entry is created in the 'Shortlisted Leads' table 
* **LLM Summary**: `multilineText`
* **LLM Score**: `number` (precision: 2)
* **LLM Follow-Ups**: `multilineText`

### Personal Details (child)

* **Full Name**: `singleLineText`
* **Applicant ID**: `multipleRecordLinks` -> links to Applicants
* **Email**: `email`
* **Location**: `multilineText`
* **LinkedIn Profile**: `url`

### Work Experience (child)

* **Experience ID**: `number` (precision: 0)
* **Applicant ID**: `multipleRecordLinks` -> links to Applicants
* **Company**: `singleLineText`
* **Title**: `singleLineText`
* **Start**: `date` (local)
* **End**: `date` (local)
* **Technologies**: `multilineText`

### Salary Preferences (child)

* **Salary Preference ID**: `number` (precision: 0)
* **Applicant ID**: `multipleRecordLinks` -> links to Applicants
* **Preferred Rate**: `currency` (\$, precision: 2)
* **Minimum Rate**: `currency` (\$, precision: 2)
* **Currency**: `singleLineText`
* **Availability**: `singleLineText`

### Shortlisted Leads

* **Lead ID**: `number` (precision: 0)
* **Applicant ID**: `multipleRecordLinks` -> links to Applicants
* **Compressed JSON**: `richText`
* **Score Reason**: `multilineText`
* **Created At**: `dateTime` (America/Toronto, 12-hour)

> The Meta API endpoint used to create tables is `POST /v0/meta/bases/{base_id}/tables`. Ensure your token has schema write access.

---

## How Each Automation Works

### 1) `utils/airTableHelpers.py`: Airtable Helpers

**What it does:** Thin wrappers around Airtable’s REST API to create tables and perform record CRUD. Also includes a convenience filter to fetch Applicants with/without “Compressed JSON”.

**Key functions:**

```python
def createAirTable(name, description, fields) -> dict:
    # POST https://api.airtable.com/v0/meta/bases/{base_id}/tables
    # returns API response (includes table id)

def getAllEntries(filled: bool = False) -> dict:
    # If filled=False -> filter records where {Compressed JSON} == ""
    # If filled=True  -> filter records where {Compressed JSON} != ""

def getRecordsById(record_id: str, table_name: str) -> dict:
    # GET a single record by id

def update_record(record_id: str, table_name: str, field: str, value) -> dict:
    # PATCH a single field; serializes non str/int with json.dumps

def add_record(table_name: str, value: dict) -> dict | None:
    # POST a new record; returns created record or None on error
```

---

### 2) `utils/dbModel.py`: Schema Creation

**What it does:** Defines Python classes for each table and posts schema to Airtable Meta API when instantiated. `Applicants` returns the new table’s `id`, used to link child tables.

**Snippet (abridged):**

```python
class Applicants:
    def __init__(self):
        self.name = os.getenv("applicants_table_name", "Applicants")
        self.fields = [...]
        returned = createAirTable(self.name, self.description, self.fields)
        self.parent_id = returned.get('id')

class PersonalDetails:
    def __init__(self, parent_id):
        self.fields = [
          {"name": "Applicant ID", "type": "multipleRecordLinks",
           "options": {"linkedTableId": parent_id}}
        ]
        createAirTable(...)

# Similar for WorkExperience, SalaryPreferences, ShortlistedLeads
```

Run all via:

```bash
python setupAirTables.py
```

---

### 3) `compress.py`: Build “Compressed JSON”

**What it does:** Reads Applicants and fetches their related child records, then assembles a compact JSON structure and writes it into the “Compressed JSON” field on Applicants.

**Shape of the compressed JSON:**

```json
{
  "Applicant ID": "applicant@example.com",
  "Personal Details": { "Full Name": "...", "Email": "...", "Location": "...", ... },
  "Salary Preferences": { "Preferred Rate": 80, "Availability": 20, ... },
  "Work Experience": [
    {"Company": "...", "Title": "...", "Start": "YYYY-MM-DD", "End": "YYYY-MM-DD", ...},
    ...
  ]
}
```

**Command:**

```bash
python compress.py
```

---

### 4) `decompress.py`: Backfill Child Tables

**What it does:** For each Applicant with a “Compressed JSON”, parses the JSON and creates any missing child records into Personal Details, Salary Preferences, and Work Experience.

**Key functions:**

```python
def decompress_json(data: str) -> dict | str:
    try:
        return json.loads(data)
    except Exception as e:
        logger.info("Decompression failed: %s", e)
        return data

def fillChildTables() -> None:
    # For each applicant:
    #   - parse compressed JSON
    #   - if child records absent in fields, add them via add_record(...)
```

**Command:**

```bash
python decompress.py
```

---

### 5) `summaryGeneration.py`: LLM Summaries/Scores/Follow-Ups

**What it does:** Calls an LLM with the Applicant’s “Compressed JSON” and expects a JSON response containing three fields:

* `LLM Summary` (one line)
* `LLM Score` (1–10)
* `LLM Follow-Ups` (list of 2–3 questions)

It retries on failure (exponential backoff), parses the JSON, and writes fields back to Applicants.

**LLM call (abridged):**

```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("openai_api_key"))

def get_llm_output(input_text: str, max_retries: int) -> dict:
    prompt = f"""You are an assistant evaluating candidate applications...
    Input text:
    \"\"\"{input_text}\"\"\" ... return ONLY JSON ...
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are a helpful evaluator that outputs only JSON."},
                    {"role":"user","content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            output_text = (response.choices[0].message.content or "").strip()
            break
        except Exception as e:
            logger.error("LLM call failed (attempt %d): %s", attempt+1, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

    try:
        return json.loads(output_text)
    except Exception:
        return {"error": "Invalid JSON from model", "raw_output": output_text}
```

**Command:**

```bash
python summaryGeneration.py
```

---

### 6) `shortlist.py`: Rules-Based Shortlisting

**What it does:** Reads Applicants → parses compressed JSON → computes total years of experience → checks company pedigree, rate, availability, and location → writes qualified candidates into "Shortlisted Leads" with a human-readable `Score Reason`.

**Core logic:**

```python
def calculate_experience(work_experiences) -> float:
    # Sum day deltas across entries, return years rounded to 2 decimals

tier_one_companies = ["Meta", "Apple", "Amazon", "Microsoft", "Google", ... ]

def shortlist_applicants():
    # years >= 4 OR any(company in tier_one_companies)
    # AND Preferred Rate <= 100
    # AND Availability >= 20
    # AND Location in allowed set
    # => add record to Shortlisted Leads with Applicant ID link + Compressed JSON + Score Reason
```

**Command:**

```bash
python shortlist.py
```

---

## LLM Integration: Configuration and Security

* **SDK**: OpenAI Python SDK.
* **Model**: Defaults to `gpt-4o-mini` (adjust per budget/quality needs).
* **Auth**: `openai_api_key` is read from `.env`.
* **Backoff**: Exponential backoff with up to 3 attempts by default.
* **Budget Guardrails**: `max_tokens=500` in the call; adjust as needed.
* **Response Validation**: Model is instructed to return JSON only. We `json.loads` the response and log raw text on failure.

Additional hardening idea:

* Add a deterministic fallback scorer if the LLM response is invalid after N retries.

---

## Extending / Customizing the Shortlist Criteria

All shortlisting rules live in `shortlist.py`.

### Provision to add or change rules

Examples:

1. **Adjust experience threshold**

```python
MIN_YEARS = 4.0  # change here
if years >= MIN_YEARS:
    ...
```

2. **Tier-one companies**

```python
tier_one_companies.extend(["Anthropic", "Palantir"])
```

3. **Rate and availability**

```python
MAX_RATE = 100
MIN_AVAIL = 20
if prefs["Preferred Rate"] <= MAX_RATE and prefs["Availability"] >= MIN_AVAIL:
    ...
```

4. **Location allowlist**

```python
ALLOWED_LOCATIONS = {"US", "United States", "Canada", "UK", "Germany", "India"}
if details["Location"] in ALLOWED_LOCATIONS:
    ...
```

5. **Add language/skill keywords**
   Parse `Technologies` from Work Experience and add weights:

```python
PREFERRED_TECH = {"python": 5, "pytorch": 5, "llama": 5, "spark": 3}

def tech_score(work_experiences) -> int:
    score = 0
    for exp in work_experiences:
        techs = (exp.get("Technologies") or "").lower()
        for k, w in PREFERRED_TECH.items():
            if k in techs:
                score += w
    return score
```

Then use `tech_score()` as part of our decision to create a lead.

### Make criteria data-driven

For non-dev teammates, move thresholds/allowlists into a JSON or YAML file (e.g., `config/rules.yaml`) and load it at runtime. That lets us change rules without code changes.

---

## Running the Project End-to-End

1. **Create schema**
   `python setupAirTables.py`

2. **Ingest/normalize data into tables**
   Use your own Airtable UI to create forms to ingest data into Applicants, Personal Details, Work Experience and Salary Preferences.

3. **Compress data to JSON and insert into parent**
   `python compress.py`

4. **(Optional) Decompress back to child tables**
   `python decompress.py`

5. **Shortlist**
   `python shortlist.py`

6. **Generate LLM fields**
   `python summaryGeneration.py`

---

## Error Handling and Retries

* Airtable requests raise for non-200 responses in `update_record` and `add_record`. Failures are logged with context.
* LLM calls retry with backoff. Final failure raises and is logged.
* JSON parsing errors in `decompress_json` and LLM outputs are caught and logged.

---

## Observability and Auditing

* All scripts log to both console and file (`app.log` by default).
* Each major step logs start/finish, per-record progress, and any errors.

---

## Security

* Secrets live in `.env`. `.env` is .gitignored.
* Restrict Airtable token to the minimal scopes required.
* If you share logs externally, scrub or redact values.

---

## Known Pitfalls and Fixes

* **Duplicate logs**: If you see duplicate lines, ensure `setup_logger()` is only attaching handlers once and `logger.propagate = False`.
* **Case-sensitive imports**: Match the exact filename casing (e.g., `dbModel.py` vs `dbmodel.py`).


---

## Appendix A: Example `.env.example`

```dotenv
airtable_token=pat_xxx
airtable_base_id=app_yyyyyyyyyyyyyy

applicants_table_name = Applicants
personal_details_table_name = Personal Details
work_experience_table_name = Work Experience
salary_preferences_table_name = Salary Preferences
shortlisted_leads_table_name = Shortlisted Leads

openai_api_key=sk-...
```
