/**
 * AI Loan Eligibility Checker - Pure Mathematical Client Utility
 * Ensures instant UI responsiveness before server requests
 */

const FinCalc = (() => {
  function formatINR(val) {
    if (val === null || val === undefined || isNaN(val)) return "₹0";
    return "₹" + Math.round(val).toLocaleString("en-IN");
  }

  function calculateEMI(principal, annualRate, tenureMonths) {
    if (principal <= 0 || tenureMonths <= 0) return { emi: 0, interest: 0, total: 0 };
    if (annualRate <= 0) {
      const emi = Math.round(principal / tenureMonths);
      return { emi, interest: 0, total: principal };
    }

    const r = (annualRate / 100) / 12;
    const power = Math.pow(1 + r, tenureMonths);
    const denominator = power - 1;

    if (denominator === 0) {
      const emi = Math.round(principal / tenureMonths);
      return { emi, interest: 0, total: principal };
    }

    const emi = Math.round((principal * r * power) / denominator);
    const total = emi * tenureMonths;
    const interest = Math.max(0, total - principal);

    return { emi, interest, total };
  }

  function calculateDTI(existingEMI, proposedEMI, monthlyIncome) {
    if (monthlyIncome <= 0) return { currentDTI: 0, postLoanDTI: 0 };
    const currentDTI = +((existingEMI / monthlyIncome) * 100).toFixed(1);
    const postLoanDTI = +(((existingEMI + proposedEMI) / monthlyIncome) * 100).toFixed(1);
    return { currentDTI, postLoanDTI };
  }

  function calculateUtilization(used, limit) {
    if (!limit || limit <= 0) return 0;
    return +Math.min(100, Math.max(0, (used / limit) * 100)).toFixed(1);
  }

  return {
    formatINR,
    calculateEMI,
    calculateDTI,
    calculateUtilization
  };
})();

window.FinCalc = FinCalc;
