# Local Setup & Configuration Guide

This guide walks through configuring the local environment, Python runtime, Anthropic Claude API, and optional Google Sheets service account.

---

## 1. Prerequisites
- **Python**: Version 3.10+ (Tested on Python 3.14)
- **Git**
- Modern web browser (Chrome, Edge, Firefox, Safari)

---

## 2. Quickstart Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ai-loan-eligibility-checker.git
   cd ai-loan-eligibility-checker
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   # Windows PowerShell
   py -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to add your Claude API Key or leave empty to use the built-in deterministic rule engine.*

5. **Start Application Server**:
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn backend.main:app --reload --port 8000
   ```

6. **Access Application**:
   - Web Application: [http://localhost:8000](http://localhost:8000)
   - Swagger API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 3. Configuring Anthropic Claude API (Optional)
1. Sign up at [https://console.anthropic.com](https://console.anthropic.com).
2. Generate an API Key under **API Keys**.
3. Open `.env` and set:
   ```env
   CLAUDE_API_KEY=sk-ant-api03-...
   ```
4. Restart the server. The health endpoint (`/api/health`) will now report `"mode": "Active"`.

---

## 4. Configuring Google Sheets Audit Logging (Optional)
1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project and enable the **Google Sheets API** and **Google Drive API**.
3. Navigate to **IAM & Admin > Service Accounts** and create a Service Account.
4. Generate a JSON Key for this service account.
5. Create a new Google Sheet and click **Share**, adding the Service Account email as **Editor**.
6. Copy the Sheet ID from the URL (`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`).
7. Update `.env`:
   ```env
   GOOGLE_SHEETS_ID=your_sheet_id_here
   GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   ```
   *If unconfigured, the system automatically runs in local-only fallback mode without errors.*

---

## 5. Running the Test Suite
Execute the comprehensive unit and API test suite:
```bash
pytest -v
```
All 16 tests covering mathematical underwriting, edge cases, and API routes will execute.
