# System Architecture

The **AI Loan Eligibility Checker** is a BFSI-focused financial decision-support platform designed specifically for the Indian lending ecosystem. It employs a decoupled architecture separating deterministic mathematical underwriting from explainable generative AI.

---

## 1. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  - HTML5 / Vanilla CSS3 (Deep Navy Fintech Design System)                         |
|  - Modular Vanilla JS (api.js, calculator.js, loan.js, credit.js, emi.js, app.js)|
+------------------------------------------+----------------------------------------+
                                           |
                                      REST / JSON
                                           |
+------------------------------------------v----------------------------------------+
|                               FASTAPI APPLICATION                                 |
|  - Security Middleware (Body size limits, security headers, CORS)                 |
|  - Route Controllers (/api/health, /api/loan, /api/credit, /api/emi, /api/ai)     |
+---------------------+--------------------+--------------------+-------------------+
                      |                    |                    |
                      v                    v                    v
+-----------------------------+ +---------------------+ +---------------------------+
| DETERMINISTIC MATH ENGINE   | | CLAUDE AI SERVICE   | | GOOGLE SHEETS AUDIT SYNC  |
| - Reducing Balance EMI      | | - Anthropic Claude  | | - Service Account OAuth2  |
| - Current & Post-Loan DTI   | | - Structured JSON   | | - Anonymized Audit Logs   |
| - Revolving Utilization     | | - Strict Guardrails | | - Asynchronous Background |
| - 1000-Point Scoring Model  | | - Fallback Engine   | | - Graceful Degradation    |
+-----------------------------+ +---------------------+ +---------------------------+
```

---

## 2. Core Architectural Pillars

### A. Separation of Concerns & Deterministic-First Philosophy
In financial technology, generative AI must **never** be the primary calculator of financial numbers or debt ratios.
1. The deterministic engine calculates exact EMI, DTI, FOIR, credit utilization, and the 1000-point Estimated Financial Eligibility Score.
2. The AI engine receives pre-computed metrics and borrower context to generate explainable, natural language underwriting commentary and recommendations.
3. If AI connectivity fails or API keys are missing, the system gracefully degrades to deterministic rule-based analysis without any disruption to the borrower.

### B. Client-Side Performance
- Zero heavy framework bundles (React/Vue/Angular) loaded over the wire.
- Native CSS variables with deep navy `#090D16` surfaces and accessible typography.
- Client-side calculation mirror in `calculator.js` allows instant real-time slider updates (<1ms) before server submission.

### C. Security & Data Minimization
- No personally identifiable information (PII) like names, email addresses, phone numbers, or passwords are required to run underwriting calculations.
- No bank account credentials, card numbers, or CVVs are ever accepted.
- Environment secrets (`CLAUDE_API_KEY`, `GOOGLE_PRIVATE_KEY`) reside exclusively on the server.
