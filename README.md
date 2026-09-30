# AI Loan Eligibility Checker 💳🇮🇳

> **"Understand Your Loan Eligibility Before You Apply."**

🔗 **Live Deployment**: [https://aditya-kumar03.github.io/ai-loan-eligibility-checker/](https://aditya-kumar03.github.io/ai-loan-eligibility-checker/)  
📦 **GitHub Repository**: [https://github.com/Aditya-kumar03/ai-loan-eligibility-checker](https://github.com/Aditya-kumar03/ai-loan-eligibility-checker)

A production-quality, BFSI-focused financial decision-support platform designed for Indian borrowers. It pairs deterministic banking mathematics (reducing-balance EMI, DTI, FOIR, revolving credit utilization) with Anthropic Claude AI to evaluate loan affordability, explain underwriting criteria, and provide practical debt management guidance.

---

## 🌟 Executive Summary

| Category | Details |
| :--- | :--- |
| **Domain** | Banking, Financial Services, and Insurance (BFSI) / FinTech |
| **Target Users** | Salaried professionals, self-employed individuals, students, first-time borrowers |
| **Primary Goal** | Demystify bank credit underwriting, estimate loan affordability, and calculate debt capacity before approaching formal lenders |
| **Key Principle** | **Deterministic-First AI Architecture** (Strict rule-based underwriting math runs first; AI provides contextual, non-hallucinatory explanations) |

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Deep Navy Fintech Design System), Modular Vanilla JavaScript (Zero bloated framework dependencies).
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn, Requests / HTTPX.
- **Artificial Intelligence**: Anthropic Claude API (`claude-3-7-sonnet-20250219`) with structured JSON schema prompt engineering and automated offline fallback.
- **Audit Storage**: Google Sheets API (v4) via Service Account OAuth2 with asynchronous background synchronization.
- **Testing & Quality Assurance**: pytest, pytest-asyncio, FastAPI TestClient (100% passing test suite across formulas and boundary cases).

---

## 🚀 The Four Core Tools

### 1. Loan Eligibility Checker
- Structured multi-section borrower form capturing age, employment type, monthly income, existing EMIs, living expenses, desired loan amount, tenure, expected interest rate, and bureau credit metrics.
- One-click **"Load Example Profile"** button for quick demonstration (Salaried, ₹75,000/mo income, ₹12,000 existing EMI, 760 bureau score).
- Calculates Post-Loan Debt-to-Income (DTI), Fixed Obligation to Income Ratio (FOIR), and Net Disposable Surplus.
- Outputs an internal **1000-Point Estimated Financial Eligibility Score** with category ratings:
  - `Likely Eligible` (Score ≥ 710, DTI ≤ 48%, Credit Score ≥ 680)
  - `May Require Review` (Score 540–709, DTI ≤ 65%, Credit Score ≥ 600)
  - `Potentially Difficult` (High debt burden or low bureau scores)
- Delivers deterministic positive/negative drivers and Claude AI underwriting insights (Strengths, Concerns, Recommendations, and Questions to Ask Lenders).

### 2. Credit Score Analyzer
- Two-way interactive score slider and numeric input (300 to 900 range).
- Real-time revolving credit card line utilization meter (Optimal ≤ 30%, Moderate 30%–50%, High Risk > 50%).
- Educational benchmark alignment across **5 Commonly Used Reference Ranges** (800–900, 740–799, 670–739, 580–669, 300–579).
- Actionable score repair recommendations tailored for CIBIL/Experian credit bureau mechanisms.

### 3. EMI Calculator
- Real-time reducing-balance amortization calculator ($EMI = P \times r \times (1+r)^n / ((1+r)^n - 1)$).
- Two-way sliders and numerical inputs for Principal (₹10,000 to ₹2 Crore), Interest Rate (1% to 30%), and Tenure.
- Instant toggle between **Months** and **Years**.
- Pure CSS principal vs. interest visual ratio bar.
- Toggleable yearly amortization schedule table.

### 4. AI Financial Tips
- Guidance across 7 essential financial topics:
  - **Credit Score**
  - **Loans**
  - **EMI Management**
  - **Budgeting**
  - **Debt Management**
  - **Savings**
  - **Financial Planning**
- Outputs contextual cards with Impact Level tags (`Fundamental`, `High`, `Medium`), actionable 1-step directives, and insider Pro-Tips for Indian retail consumers.

---

## 📸 UI & Aesthetics Overview

The platform uses a dark, human-designed financial aesthetic inspired by leading fintech interfaces:
- **Background**: Deep Navy / Charcoal (`#090D16`, `#0F172A`, `#131C31`).
- **Typography**: Clean system sans-serif hierarchy (Inter).
- **Accents**: Subtle blue/cyan accents (`#2563EB`, `#0EA5E9`), minimal purple badges for AI, and soft borders (`rgba(255,255,255,0.08)`).
- **No Gimmicks**: No blinding neons, no fake bank partnerships, no fake customer testimonials, no excessive animations.

---

## 📂 Project Structure

```
ai-loan-checker/
├── backend/
│   ├── app/
│   │   ├── config/          # Pydantic v2 application settings (.env loader)
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── models/          # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── loan.py
│   │   │   ├── credit.py
│   │   │   ├── emi.py
│   │   │   ├── tips.py
│   │   │   └── feedback.py
│   │   ├── routes/          # Clean REST API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── loan.py
│   │   │   ├── credit.py
│   │   │   ├── emi.py
│   │   │   ├── tips.py
│   │   │   └── feedback.py
│   │   ├── services/        # Business logic & integrations
│   │   │   ├── __init__.py
│   │   │   ├── calculator.py    # Deterministic financial math engine
│   │   │   ├── claude_service.py # Anthropic Claude API + offline fallback
│   │   │   └── sheets_service.py # Google Sheets service account sync
│   │   └── utils/           # Logging & validation utilities
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── validators.py
│   └── main.py              # FastAPI server setup, security middleware, static mounting
├── frontend/
│   ├── assets/              # SVG brand icons and logos
│   │   ├── favicon.svg
│   │   └── logo.svg
│   ├── css/                 # Pure CSS design system
│   │   └── style.css
│   ├── js/                  # Modular client-side logic
│   │   ├── api.js           # REST API client
│   │   ├── calculator.js    # Client-side instant calculation helpers
│   │   ├── loan.js          # Loan form controller & results renderer
│   │   ├── credit.js        # Credit score analyzer controller
│   │   ├── emi.js           # EMI calculator controller
│   │   ├── tips.js          # AI financial tips controller
│   │   └── app.js           # SPA router & notification manager
│   ├── pages/               # Standalone informational pages
│   │   ├── about.html
│   │   └── privacy.html
│   └── index.html           # Main single-page application
├── docs/                    # In-depth architectural & calculation documentation
│   ├── architecture.md
│   ├── api.md
│   ├── security.md
│   ├── setup.md
│   └── financial-calculations.md
├── tests/                   # Automated pytest test suite
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_api.py
│   └── test_ai_fallback.py
├── main.py                  # Root application entrypoint (python main.py)
├── requirements.txt         # Production dependencies
├── .env.example             # Environment configuration template
├── .env                     # Local environment settings (git-ignored)
├── .gitignore               # Comprehensive gitignore
└── README.md                # Project documentation
```

---

## ⚡ Quickstart: Running Locally

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/your-username/ai-loan-eligibility-checker.git
cd ai-loan-eligibility-checker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Default settings run completely out-of-the-box with deterministic calculations and local fallbacks.)*

### 4. Launch Application Server
```bash
python main.py
```
Or with Uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Access the Web Application
Open your browser and navigate to:
- **Application Interface**: [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs (Swagger UI)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **API Redoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

---

## 🧪 Automated Testing

Run the full automated test suite covering mathematical calculations, edge cases (zero interest, zero income, 100% utilization, credit scores outside bounds), API status codes, and AI fallback behavior:

```bash
pytest -v
```

Expected result:
```
tests/test_ai_fallback.py::test_loan_ai_fallback_when_unconfigured PASSED
tests/test_ai_fallback.py::test_financial_tips_fallback PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_loan_analyze_endpoint PASSED
tests/test_api.py::test_loan_analyze_invalid_input PASSED
tests/test_api.py::test_credit_analyze_endpoint PASSED
tests/test_api.py::test_emi_calculate_endpoint PASSED
tests/test_api.py::test_financial_tips_endpoint PASSED
tests/test_api.py::test_feedback_endpoint PASSED
tests/test_calculator.py::test_emi_exact_calculation PASSED
tests/test_calculator.py::test_emi_zero_interest PASSED
tests/test_calculator.py::test_emi_zero_or_negative_inputs PASSED
tests/test_calculator.py::test_dti_and_metrics_calculation PASSED
tests/test_calculator.py::test_eligibility_score_and_outcomes PASSED
tests/test_calculator.py::test_credit_analyzer_service PASSED
tests/test_calculator.py::test_emi_calculator_service PASSED

============================= 16 passed in 0.50s =============================
```

---

## 🔐 Security & Data Governance

1. **Zero Sensitive PII**: No passwords, card numbers, CVVs, or account numbers are collected.
2. **Key Isolation**: Claude and Google Sheets secrets reside strictly on the server and are never delivered to the client browser.
3. **Graceful Fallback**: If `CLAUDE_API_KEY` is not provided, the platform switches seamlessly to the deterministic underwriting engine and displays:
   > *"AI analysis temporarily unavailable. Showing rule-based analysis."*
4. **Google Sheets Audit Safeguards**: Background audits record only anonymous statistical metrics (age, income bracket, calculated DTI, eligibility score). If unconfigured, the system operates locally without errors.

---

## ⚖️ Important Financial Disclaimer

> **Important:** This platform provides educational estimates and AI-assisted insights. It does not provide guaranteed loan approval, official credit scores, financial advice, or lending decisions. Actual decisions are made by banks/NBFCs based on their own policies and verification processes.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
