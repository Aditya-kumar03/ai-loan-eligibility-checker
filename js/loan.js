/**
 * AI Loan Eligibility Checker - Form Controller & Result Renderer
 */

const LoanController = (() => {
  const sampleProfile = {
    age: 28,
    employment_type: "Salaried",
    employment_experience_years: 4.0,
    existing_bank_relationship: "Salary Account (HDFC/ICICI/SBI)",
    preferred_loan_type: "Personal Loan",
    monthly_income: 75000,
    existing_monthly_emi: 12000,
    monthly_expenses: 25000,
    loan_amount_required: 500000,
    loan_tenure_months: 60,
    expected_interest_rate: 12.0,
    credit_score: 760,
    total_credit_limit: 300000,
    credit_used: 90000,
    number_of_existing_loans: 1,
    number_of_credit_cards: 2
  };

  function init() {
    const form = document.getElementById("loan-form");
    const loadSampleBtn = document.getElementById("btn-load-sample");
    const resetBtn = document.getElementById("btn-reset-loan");

    if (loadSampleBtn) {
      loadSampleBtn.addEventListener("click", () => loadSampleData());
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        form.reset();
        clearResults();
      });
    }

    if (form) {
      form.addEventListener("submit", handleLoanSubmit);

      // Add real-time live preview update on input change
      form.querySelectorAll("input, select").forEach(el => {
        el.addEventListener("input", updateLiveSummary);
      });
    }
  }

  function loadSampleData() {
    document.getElementById("loan-age").value = sampleProfile.age;
    document.getElementById("loan-emp-type").value = sampleProfile.employment_type;
    document.getElementById("loan-emp-exp").value = sampleProfile.employment_experience_years;
    document.getElementById("loan-bank-rel").value = sampleProfile.existing_bank_relationship;
    document.getElementById("loan-type").value = sampleProfile.preferred_loan_type;
    document.getElementById("loan-income").value = sampleProfile.monthly_income;
    document.getElementById("loan-existing-emi").value = sampleProfile.existing_monthly_emi;
    document.getElementById("loan-expenses").value = sampleProfile.monthly_expenses;
    document.getElementById("loan-amount").value = sampleProfile.loan_amount_required;
    document.getElementById("loan-tenure").value = sampleProfile.loan_tenure_months;
    document.getElementById("loan-rate").value = sampleProfile.expected_interest_rate;
    document.getElementById("loan-credit-score").value = sampleProfile.credit_score;
    document.getElementById("loan-credit-limit").value = sampleProfile.total_credit_limit;
    document.getElementById("loan-credit-used").value = sampleProfile.credit_used;
    document.getElementById("loan-active-loans").value = sampleProfile.number_of_existing_loans;
    document.getElementById("loan-cards-count").value = sampleProfile.number_of_credit_cards;

    updateLiveSummary();
    App.showToast("Loaded sample profile (Salaried, ₹75,000/mo, 760 Credit Score).", "info");
  }

  function getFormData() {
    return {
      age: parseInt(document.getElementById("loan-age").value, 10),
      employment_type: document.getElementById("loan-emp-type").value,
      employment_experience_years: parseFloat(document.getElementById("loan-emp-exp").value) || 2.0,
      existing_bank_relationship: document.getElementById("loan-bank-rel").value,
      preferred_loan_type: document.getElementById("loan-type").value,
      monthly_income: parseFloat(document.getElementById("loan-income").value),
      existing_monthly_emi: parseFloat(document.getElementById("loan-existing-emi").value) || 0,
      monthly_expenses: parseFloat(document.getElementById("loan-expenses").value) || 0,
      loan_amount_required: parseFloat(document.getElementById("loan-amount").value),
      loan_tenure_months: parseInt(document.getElementById("loan-tenure").value, 10),
      expected_interest_rate: parseFloat(document.getElementById("loan-rate").value),
      credit_score: parseInt(document.getElementById("loan-credit-score").value, 10),
      total_credit_limit: parseFloat(document.getElementById("loan-credit-limit").value) || 0,
      credit_used: parseFloat(document.getElementById("loan-credit-used").value) || 0,
      number_of_existing_loans: parseInt(document.getElementById("loan-active-loans").value, 10) || 0,
      number_of_credit_cards: parseInt(document.getElementById("loan-cards-count").value, 10) || 0
    };
  }

  function validateFormData(data) {
    if (isNaN(data.age) || data.age < 18 || data.age > 75) {
      throw new Error("Age must be between 18 and 75 years.");
    }
    if (isNaN(data.monthly_income) || data.monthly_income <= 0) {
      throw new Error("Monthly income must be a positive number.");
    }
    if (isNaN(data.loan_amount_required) || data.loan_amount_required <= 0) {
      throw new Error("Loan amount required must be greater than zero.");
    }
    if (isNaN(data.loan_tenure_months) || data.loan_tenure_months <= 0 || data.loan_tenure_months > 360) {
      throw new Error("Loan tenure must be between 1 and 360 months.");
    }
    if (isNaN(data.expected_interest_rate) || data.expected_interest_rate < 0 || data.expected_interest_rate > 50) {
      throw new Error("Interest rate must be between 0% and 50%.");
    }
    if (isNaN(data.credit_score) || data.credit_score < 300 || data.credit_score > 900) {
      throw new Error("Credit score must be between 300 and 900.");
    }
    if (data.existing_monthly_emi < 0 || data.monthly_expenses < 0) {
      throw new Error("Existing EMI and monthly expenses cannot be negative.");
    }
    if (data.total_credit_limit < 0 || data.credit_used < 0) {
      throw new Error("Credit limits and used credit cannot be negative.");
    }
  }

  function updateLiveSummary() {
    const income = parseFloat(document.getElementById("loan-income")?.value) || 0;
    const amount = parseFloat(document.getElementById("loan-amount")?.value) || 0;
    const tenure = parseInt(document.getElementById("loan-tenure")?.value, 10) || 0;
    const rate = parseFloat(document.getElementById("loan-rate")?.value) || 0;
    const existingEmi = parseFloat(document.getElementById("loan-existing-emi")?.value) || 0;

    const liveBox = document.getElementById("loan-live-summary");
    if (!liveBox) return;

    if (amount > 0 && tenure > 0 && income > 0) {
      const calc = FinCalc.calculateEMI(amount, rate, tenure);
      const dti = FinCalc.calculateDTI(existingEmi, calc.emi, income);

      document.getElementById("live-est-emi").textContent = FinCalc.formatINR(calc.emi);
      document.getElementById("live-post-dti").textContent = `${dti.postLoanDTI}%`;
      liveBox.style.display = "flex";
    } else {
      liveBox.style.display = "none";
    }
  }

  async function handleLoanSubmit(e) {
    e.preventDefault();

    const submitBtn = document.getElementById("btn-submit-loan");
    const originalBtnText = submitBtn.innerHTML;

    try {
      const data = getFormData();
      validateFormData(data);

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Analyzing Financial Profile...`;

      App.showLoading("Analyzing financial profile & calculating affordability metrics...");

      const result = await API.analyzeLoan(data);

      App.hideLoading();
      renderLoanResults(result);

      // Smooth scroll to results
      const resContainer = document.getElementById("loan-results-container");
      resContainer.style.display = "block";
      resContainer.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
      App.hideLoading();
      App.showToast(err.message || "Unable to complete loan analysis.", "danger");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  }

  function clearResults() {
    const resContainer = document.getElementById("loan-results-container");
    if (resContainer) resContainer.style.display = "none";
  }

  function renderLoanResults(res) {
    const scoreVal = document.getElementById("res-score-value");
    const statusBadge = document.getElementById("res-status-badge");
    const statusHeadline = document.getElementById("res-status-headline");
    const statusSummary = document.getElementById("res-status-summary");

    // 1. Score display
    scoreVal.textContent = res.estimated_eligibility_score;

    // 2. Status Badge & Headline
    statusBadge.className = "status-badge";
    if (res.eligibility_category === "Likely Eligible") {
      statusBadge.classList.add("likely-eligible");
      statusBadge.innerHTML = `● Likely Eligible`;
      statusHeadline.textContent = "Strong Eligibility Profile";
    } else if (res.eligibility_category === "May Require Review") {
      statusBadge.classList.add("review-required");
      statusBadge.innerHTML = `▲ May Require Review`;
      statusHeadline.textContent = "Moderate Financial Profile";
    } else {
      statusBadge.classList.add("potentially-difficult");
      statusBadge.innerHTML = `✕ Potentially Difficult`;
      statusHeadline.textContent = "High Debt Burden Detected";
    }

    statusSummary.textContent = res.ai_analysis.summary || "";

    // 3. Metrics Cards
    document.getElementById("res-post-dti").textContent = `${res.metrics.post_loan_dti_pct}%`;
    document.getElementById("res-proposed-emi").textContent = FinCalc.formatINR(res.metrics.proposed_emi);
    document.getElementById("res-total-emi").textContent = FinCalc.formatINR(res.metrics.total_emi_burden);
    document.getElementById("res-utilization").textContent = `${res.metrics.credit_utilization_pct}%`;
    document.getElementById("res-surplus").textContent = FinCalc.formatINR(res.metrics.net_disposable_surplus);
    document.getElementById("res-total-interest").textContent = FinCalc.formatINR(res.metrics.total_interest_payable);

    // 4. Deterministic Reasons ("Why this result?")
    const reasonsContainer = document.getElementById("res-reasons-list");
    reasonsContainer.innerHTML = "";
    (res.deterministic_reasons || []).forEach(reason => {
      const isNegative = reason.includes("exceeds") || reason.includes("high") || reason.includes("restrict") || reason.includes("elevated");
      const li = document.createElement("li");
      li.className = "reason-item";
      li.innerHTML = `
        <span class="reason-icon ${isNegative ? 'warning' : 'positive'}">${isNegative ? '!' : '✓'}</span>
        <span>${escapeHTML(reason)}</span>
      `;
      reasonsContainer.appendChild(li);
    });

    // 5. Score Breakdown Components
    const b = res.score_breakdown;
    renderComponentRow("comp-credit", b.credit_score_component);
    renderComponentRow("comp-dti", b.dti_component);
    renderComponentRow("comp-stability", b.income_stability_component);
    renderComponentRow("comp-util", b.credit_utilization_component);
    renderComponentRow("comp-buffer", b.expense_buffer_component);

    // 6. AI Insights Section
    const aiNotice = document.getElementById("res-ai-notice");
    if (res.ai_analysis.notice) {
      aiNotice.style.display = "block";
      aiNotice.textContent = res.ai_analysis.notice;
    } else {
      aiNotice.style.display = "none";
    }

    document.getElementById("res-ai-explanation").textContent = res.ai_analysis.eligibility_explanation || "";

    renderList("res-ai-strengths", res.ai_analysis.strengths);
    renderList("res-ai-concerns", res.ai_analysis.concerns);
    renderList("res-ai-recommendations", res.ai_analysis.recommendations);
    renderList("res-ai-questions", res.ai_analysis.questions_for_lender);
  }

  function renderComponentRow(elementId, comp) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const pct = Math.min(100, Math.round((comp.points_awarded / comp.max_points) * 100));
    el.innerHTML = `
      <div class="breakdown-header">
        <span>${escapeHTML(comp.name)}</span>
        <span>${comp.points_awarded} / ${comp.max_points} pts (${comp.rating})</span>
      </div>
      <div class="breakdown-bar-track">
        <div class="breakdown-bar-fill" style="width: ${pct}%"></div>
      </div>
      <div class="breakdown-explanation">${escapeHTML(comp.explanation)}</div>
    `;
  }

  function renderList(elementId, items) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = "";
    (items || []).forEach(item => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function escapeHTML(str) {
    return String(str).replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }

  return {
    init,
    loadSampleData
  };
})();

window.LoanController = LoanController;
