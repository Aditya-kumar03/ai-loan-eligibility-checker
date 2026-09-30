# Security Policy & Architecture

The **AI Loan Eligibility Checker** is engineered in alignment with Indian BFSI regulatory privacy guidelines (Digital Personal Data Protection Act - DPDP) and OWASP Top 10 API Security Standards.

---

## 1. Zero Sensitive Financial PII Storage
The platform is an **educational decision-support system**, not an account aggregator or payment processor.

- **Never Accepted or Stored**:
  - Full bank account numbers
  - Debit/Credit card PANs, CVVs, or expiration dates
  - Netbanking passwords, PINs, or OTPs
  - Aadhaar numbers or government credentials
- **Audit Logging Minimization**:
  - Session IDs are randomly generated (`SES-XXXXXXXX`).
  - Google Sheets audit rows store only statistical parameters (age, income bracket, calculated DTI, eligibility score) without identifying names or contact data.

---

## 2. API Key Protection
- **Zero Frontend Secret Exposure**:
  - Frontend client code contains no API tokens or private keys.
  - All calls to the Anthropic Claude API and Google Sheets API originate strictly from the FastAPI server runtime.
- **Git Hygiene**:
  - `.env` and service account JSON files are strictly excluded via `.gitignore`.
  - `.env.example` provides an empty template for configuration.

---

## 3. Server-Side Security Middleware
- **Request Size Limiting**: Enforced 1MB maximum payload constraint via custom middleware to protect against DoS attacks.
- **Security Headers Injected**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **CORS Defense**: Domain whitelisting configured via `ALLOWED_ORIGINS` in `.env`.

---

## 4. Input Sanitization & Error Handling
- Comprehensive Pydantic models validate all incoming data types and enforce realistic financial ranges (e.g., age 18–75, credit score 300–900, non-negative income).
- Production exception handlers mask Python stack traces, returning safe, actionable error messages to the client while logging detailed diagnostic traces securely on the server.
