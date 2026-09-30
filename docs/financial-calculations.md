# Financial Underwriting Calculations & Mathematical Engine

This document provides a transparent, engineering-grade explanation of the mathematical models and deterministic formulas employed by the **AI Loan Eligibility Checker**.

---

## 1. Equated Monthly Installment (EMI) Formula

Retail banking institutions in India calculate monthly loan repayments using a **reducing-balance amortization formula**.

### Formula:
$$\text{EMI} = \frac{P \times r \times (1 + r)^n}{(1 + r)^n - 1}$$

### Variable Definitions:
- **$P$**: Principal loan amount requested (in INR)
- **$r$**: Monthly interest rate, derived from the annual percentage:
  $$r = \frac{\text{Annual Interest Rate}}{12 \times 100}$$
- **$n$**: Total tenure duration in months ($1 \le n \le 360$)

### Boundary Cases:
- **Zero Interest ($r = 0$)**:
  $$\text{EMI} = \frac{P}{n}$$
- **Total Repayment Amount**:
  $$\text{Total Repayment} = \text{EMI} \times n$$
- **Total Interest Paid**:
  $$\text{Total Interest} = \text{Total Repayment} - P$$

---

## 2. Debt-to-Income (DTI) & FOIR

In Indian banking underwriting, **Fixed Obligation to Income Ratio (FOIR)** represents the percentage of a borrower's net monthly income consumed by existing and proposed debt obligations.

### Calculations:
1. **Current DTI**:
   $$\text{Current DTI (\%)} = \left(\frac{\text{Existing Monthly EMI}}{\text{Net Monthly Income}}\right) \times 100$$

2. **Total EMI Burden**:
   $$\text{Total Monthly EMI} = \text{Existing EMI} + \text{Proposed EMI}$$

3. **Post-Loan DTI (FOIR)**:
   $$\text{Post-Loan DTI (\%)} = \left(\frac{\text{Total Monthly EMI}}{\text{Net Monthly Income}}\right) \times 100$$

4. **Net Disposable Surplus**:
   $$\text{Disposable Surplus} = \text{Monthly Income} - (\text{Total Monthly EMI} + \text{Monthly Living Expenses})$$

### Industry Benchmark Interpretation:
- **$\le 35\%$**: Excellent borrowing capacity. Substantial margin for discretionary spending and savings.
- **$36\% - 50\%$**: Normal/Comfortable banking threshold. Typical ceiling for unsecured personal loans.
- **$51\% - 60\%$**: Stretched capacity. Lenders may demand co-signers, collateral, or lower loan amounts.
- **$> 60\%$**: High default risk. Generally rejected under conservative bank credit policies.

---

## 3. Revolving Credit Line Utilization

Credit utilization measures how much of the sanctioned revolving credit card limit is being actively used.

### Formula:
$$\text{Credit Utilization (\%)} = \left(\frac{\text{Current Used Credit Balance}}{\text{Total Sanctioned Limit}}\right) \times 100$$

### Scoring Benchmarks:
- **$0\% - 20\%$**: Optimal. Demonstrates high repayment discipline and strong credit line headroom.
- **$21\% - 30\%$**: Healthy. Adheres to bureau best practices.
- **$31\% - 50\%$**: Moderate. May cause slight downward drag on bureau scores.
- **$> 50\%$**: Elevated Risk. High credit dependency signals potential cash flow distress.

---

## 4. Proprietary 1000-Point Estimated Financial Eligibility Score

The application synthesizes five distinct financial dimensions into an educational score from **100 to 1000 points**.

| Scoring Component | Maximum Points | Evaluation Criteria |
| :--- | :---: | :--- |
| **Credit Bureau History** | **350 pts** | Normalized bureau score: $\frac{\text{Credit Score} - 300}{600} \times 350$. Scores $\ge 750$ receive top tier points. |
| **Debt-to-Income Capacity** | **250 pts** | Evaluates post-loan DTI. DTI $\le 30\%$ awards 250 pts; $30\% - 40\%$ awards 210 pts; $>60\%$ drops to 20 pts. |
| **Employment & Income Stability** | **150 pts** | Salaried profiles receive base 95 pts + experience bonus; Business/Self-employed receive base 80 pts + experience bonus. |
| **Credit Line Discipline** | **150 pts** | Utilization $\le 20\%$ awards 150 pts; $21\% - 30\%$ awards 130 pts; $>75\%$ drops to 15 pts. |
| **Disposable Cash Buffer** | **100 pts** | Evaluates monthly surplus ratio: surplus $\ge 35\%$ of income awards 100 pts; negative surplus awards 0 pts. |
| **TOTAL MAXIMUM SCORE** | **1000 pts** | Clamped strictly between 100 and 1000. |

---

## 5. Outcome Category Determination

The algorithm maps the aggregate score and critical thresholds into three educational categories:

1. **"Likely Eligible"**:
   - Total Score $\ge 710$
   - Post-Loan DTI $\le 48\%$
   - Bureau Credit Score $\ge 680$
   - Net Disposable Surplus $> 0$

2. **"May Require Review"**:
   - Total Score between $540$ and $709$
   - Post-Loan DTI $\le 65\%$
   - Bureau Credit Score $\ge 600$
   - Net Disposable Surplus $\ge -₹5,000$

3. **"Potentially Difficult"**:
   - Total Score $< 540$ OR Post-Loan DTI $> 65\%$ OR Bureau Credit Score $< 600$ OR Severe Cash Deficit.
