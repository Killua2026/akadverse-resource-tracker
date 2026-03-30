# AkadVerse: Learning & Faculty Resource Tracker

**Tier 4 Data Pipeline / Integration | Microservice Port: `8003`**

A high-performance redirect and analytics engine that captures student engagement with external educational resources while maintaining seamless learning transitions.

## Table of Contents
- [What This Microservice Does](#what-this-microservice-does)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Testing with Swagger UI](#testing-with-swagger-ui)
- [Example Test Inputs](#example-test-inputs)
- [Understanding the Responses](#understanding-the-responses)
- [Generated Files](#generated-files)
- [Common Errors and Fixes](#common-errors-and-fixes)
- [Project Structure](#project-structure)

## What This Microservice Does

This service is a Tier 4 component of the AkadVerse platform, operating within the My Learning and My Teaching modules as a passive data aggregator.

**Primary User:** Faculty (for engagement analytics) and the Insight Engine.

**Core Workflow:**

1.  **Intercept:** Instead of linking directly to external sites (e.g., Coursera), the platform routes students through this service.
2.  **Log:** Captures the `user_id`, `target_url`, and the `source_page` (e.g., "CSC332 Syllabus") into a local SQLite database.
3.  **Enrich:** Appends UTM (Urchin Tracking Module) parameters to the URL so external providers can identify AkadVerse as the traffic source.
4.  **Redirect:** Forwards the student to the final destination using a 307 Temporary Redirect.

**Key Design Decisions:**

*   **SQLite for Persistence:** Chosen for zero-configuration local development while providing full SQL query capabilities for the Insight Engine.
*   **Fail-Safe Redirection:** The service is architected to prioritize the user's destination. If a database error occurs, the redirect still completes.
*   **Transparent UTM Tagging:** Automatically adds `utm_source=akadverse` to all outbound traffic for professional-grade conversion tracking.

## Architecture Overview

| Component      | Technology             | Purpose                      |
| :------------- | :--------------------- | :--------------------------- |
| API Layer      | FastAPI (Python 3.12)  | High-speed async redirect handling |
| URL Logic      | urllib.parse           | Safe reconstruction of complex URLs |
| Storage        | SQLite                 | Local persistence of click telemetry |

## Prerequisites

*   Python 3.10 or higher
*   `pip` (Python package manager)
*   No external API keys are required for this specific microservice.

## Installation

**Step 1 -- Set up your project folder**

Create folder: `akadverse-resource-tracker/`

**Step 2 -- Create and activate a virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

**Step 3 -- Install dependencies**

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --host 127.0.0.1 --port 8003 --reload
```

Expected terminal output:

```
[Startup] Database setup complete.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8003 (Press CTRL+C to quit)
```

## API Endpoints

### 1. `GET /redirect`

**What it does:** Logs a resource click and forwards the user to the `target_url`.

**Request Parameters:**

| Field | Required | Description |
|---|---|---|
| `target_url` | Yes | The final destination (e.g., https://www.google.com) |
| `user_id` | Yes | The ID of the student clicking the link |
| `source` | Yes | The platform page where the link was found |

**Success response (307 Redirect):**

Redirects browser to the target URL with UTM parameters appended.

### 2. `GET /analytics/clicks`

**What it does:** Returns a JSON list of all tracked interactions for administrative review.

**Success response (200 OK):**

```json
{
  "total_clicks": 1,
  "data": [
    {
      "id": 1,
      "user_id": "ikay_300L",
      "target_url": "https://www.coursera.org",
      "source_page": "study_dashboard",
      "timestamp": "2026-03-30 11:45:00"
    }
  ]
}
```

## Testing with Swagger UI

Open: [http://127.0.0.1:8003/docs](http://127.0.0.1:8003/docs)

## Example Test Inputs

**Test 1 -- Standard Redirect**

Open your browser and enter:

`http://localhost:8003/redirect?target_url=https://www.google.com&user_id=ikay_test&source=sidebar`

Expected: Browser redirects to Google. Terminal shows "Logged click".

**Test 2 -- Verify Analytics**

`GET /analytics/clicks`

Expected: The record from Test 1 appears in the JSON output with a correct timestamp.

## Understanding the Responses

*   **Why use a 307 Redirect?**
    A 307 Temporary Redirect ensures that the browser does not "cache" the redirect. This is critical because we want every single click to hit our server so we can log it, rather than the browser skipping our service on the second visit.

*   **The UTM parameters**
    We append `utm_source`, `utm_medium`, and `utm_campaign`. These are industry standard tags used by marketing and analytics tools (like Google Analytics) to track where visitors come from.

## Generated Files

| File / Folder        | What it is              | Gitignore?              |
| :------------------- | :---------------------- | :---------------------- |
| `tracker_logs.db`    | SQLite database file    | Yes -- never commit     |
| `__pycache__/`       | Python cache files      | Yes                     |

## Common Errors and Fixes

*   `sqlite3.OperationalError: table click_events already exists`
    This is handled automatically by the `CREATE TABLE IF NOT EXISTS` logic. If you see this, ensure your database connection is not locked by another process.

*   `Redirect service failed: https://www.merriam-webster.com/dictionary/error`
    Ensure the `target_url` you are passing is a full URL including `https://`.

## Project Structure

```
akadverse-resource-tracker/
|-- main.py                # Redirect logic and SQLite setup
|-- requirements.txt       # Dependencies
|-- README.md              # This file
|-- .gitignore             # Excludes local DB
|-- tracker_logs.db        # Generated on first run -- DO NOT COMMIT
```

## Part of the AkadVerse Platform

This microservice is Tier 4 in the AkadVerse AI architecture, operating within the My Learning module alongside:

*   Google Workspace Service
*   Schedule Manager AI

---

AkadVerse AI Architecture -- v1.0