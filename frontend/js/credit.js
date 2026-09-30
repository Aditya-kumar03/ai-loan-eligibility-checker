/**
 * AI Loan Eligibility Checker - Credit Score Analyzer Controller
 */

const CreditController = (() => {
  function init() {
    const scoreSlider = document.getElementById("credit-slider-score");
    const scoreInput = document.getElementById("credit-input-score");
    const limitInput = document.getElementById("credit-input-limit");
    const usedInput = document.getElementById("credit-input-used");
    const analyzeBtn = document.getElementById("btn-analyze-credit");

    // Sync Slider & Numeric Input
    if (scoreSlider && scoreInput) {
      scoreSlider.addEventListener("input", (e) => {
        scoreInput.value = e.target.value;
        updateLiveUtilization();
      });
      scoreInput.addEventListener("input", (e) => {
        const val = parseInt(e.target.value, 10);
        if (!isNaN(val) && val >= 300 && val <= 900) {
          scoreSlider.value = val;
        }
        updateLiveUtilization();
      });
    }

    if (limitInput && usedInput) {
      limitInput.addEventListener("input", updateLiveUtilization);
      usedInput.addEventListener("input", updateLiveUtilization);
    }

    if (analyzeBtn) {
      analyzeBtn.addEventListener("click", runCreditAnalysis);
    }

    // Run initial calculation with default inputs
    updateLiveUtilization();
  }

  function updateLiveUtilization() {
    const limit = parseFloat(document.getElementById("credit-input-limit")?.value) || 0;
    const used = parseFloat(document.getElementById("credit-input-used")?.value) || 0;
    const meterFill = document.getElementById("credit-meter-fill");
    const meterText = document.getElementById("credit-meter-text");
    const meterLabel = document.getElementById("credit-meter-label");

    if (!meterFill || !meterText) return;

    if (limit > 0) {
      const util = FinCalc.calculateUtilization(used, limit);
      meterFill.style.width = `${util}%`;
      meterText.textContent = `${util}%`;

      if (util <= 30) {
        meterFill.style.backgroundColor = "var(--success)";
        meterLabel.textContent = "Optimal (≤30%)";
        meterLabel.style.color = "var(--success)";
      } else if (util <= 50) {
        meterFill.style.backgroundColor = "var(--warning)";
        meterLabel.textContent = "Moderate (30%–50%)";
        meterLabel.style.color = "var(--warning)";
      } else {
        meterFill.style.backgroundColor = "var(--danger)";
        meterLabel.textContent = "High Risk (>50%)";
        meterLabel.style.color = "var(--danger)";
      }
    } else {
      meterFill.style.width = "0%";
      meterText.textContent = "0%";
      meterLabel.textContent = "No active card limits";
      meterLabel.style.color = "var(--text-tertiary)";
    }
  }

  async function runCreditAnalysis() {
    const score = parseInt(document.getElementById("credit-input-score").value, 10);
    const limit = parseFloat(document.getElementById("credit-input-limit").value) || 0;
    const used = parseFloat(document.getElementById("credit-input-used").value) || 0;
    const cards = parseInt(document.getElementById("credit-input-cards").value, 10) || 1;
    const loans = parseInt(document.getElementById("credit-input-loans").value, 10) || 0;
    const income = parseFloat(document.getElementById("credit-input-income").value) || 50000;
    const emi = parseFloat(document.getElementById("credit-input-emi").value) || 0;

    if (isNaN(score) || score < 300 || score > 900) {
      App.showToast("Please enter a valid credit score between 300 and 900.", "warning");
      return;
    }

    try {
      App.showLoading("Analyzing credit profile & bureau benchmarks...");
      const payload = {
        credit_score: score,
        total_credit_limit: limit,
        used_credit: used,
        number_of_credit_cards: cards,
        number_of_active_loans: loans,
        monthly_income: income,
        existing_monthly_emi: emi
      };

      const result = await API.analyzeCredit(payload);
      App.hideLoading();

      renderCreditResults(result);

      const resBox = document.getElementById("credit-analysis-results");
      if (resBox) {
        resBox.style.display = "block";
        resBox.scrollIntoView({ behavior: "smooth" });
      }

    } catch (err) {
      App.hideLoading();
      App.showToast(err.message || "Failed to analyze credit profile.", "danger");
    }
  }

  function renderCreditResults(res) {
    // 1. Highlight reference range cards
    const bandsContainer = document.getElementById("credit-bands-container");
    if (bandsContainer) {
      bandsContainer.innerHTML = "";
      res.all_reference_ranges.forEach(band => {
        const div = document.createElement("div");
        div.className = `credit-band-card ${band.is_user_band ? 'active-band' : ''}`;
        div.innerHTML = `
          <div class="band-range">${band.range_label}</div>
          <div class="band-name">${band.band_name}</div>
          ${band.is_user_band ? '<span class="band-user-tag">Your Range</span>' : ''}
        `;
        bandsContainer.appendChild(div);
      });
    }

    // 2. Health Factors Table
    const factorsContainer = document.getElementById("credit-factors-list");
    if (factorsContainer) {
      factorsContainer.innerHTML = "";
      res.credit_health_factors.forEach(f => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-weight: 600; color: var(--text-primary); font-family: var(--font-family);">${escapeHTML(f.factor)}</td>
          <td><span class="status-badge" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">${escapeHTML(f.status)}</span></td>
          <td style="font-family: var(--font-family);">${escapeHTML(f.detail)}</td>
        `;
        factorsContainer.appendChild(tr);
      });
    }

    // 3. Actionable recommendations
    const recsList = document.getElementById("credit-recommendations-list");
    if (recsList) {
      recsList.innerHTML = "";
      res.actionable_recommendations.forEach(rec => {
        const li = document.createElement("li");
        li.className = "reason-item";
        li.innerHTML = `
          <span class="reason-icon positive">✓</span>
          <span>${escapeHTML(rec)}</span>
        `;
        recsList.appendChild(li);
      });
    }
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
    init
  };
})();

window.CreditController = CreditController;
