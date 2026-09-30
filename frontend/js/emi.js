/**
 * AI Loan Eligibility Checker - EMI Calculator Controller
 */

const EMIController = (() => {
  let tenureType = "years";

  function init() {
    const amountSlider = document.getElementById("emi-slider-amount");
    const amountInput = document.getElementById("emi-input-amount");
    const rateSlider = document.getElementById("emi-slider-rate");
    const rateInput = document.getElementById("emi-input-rate");
    const tenureSlider = document.getElementById("emi-slider-tenure");
    const tenureInput = document.getElementById("emi-input-tenure");
    const tenureYearsBtn = document.getElementById("btn-tenure-years");
    const tenureMonthsBtn = document.getElementById("btn-tenure-months");
    const scheduleToggle = document.getElementById("btn-toggle-schedule");

    // Two-way slider & input binding
    bindSliderAndInput(amountSlider, amountInput, 10000, 20000000, updateCalculation);
    bindSliderAndInput(rateSlider, rateInput, 1, 30, updateCalculation);
    bindSliderAndInput(tenureSlider, tenureInput, 1, 30, updateCalculation);

    // Tenure Toggle
    if (tenureYearsBtn && tenureMonthsBtn) {
      tenureYearsBtn.addEventListener("click", () => {
        if (tenureType !== "years") {
          tenureType = "years";
          tenureYearsBtn.classList.add("active");
          tenureMonthsBtn.classList.remove("active");
          // Adjust slider limits: 1 to 30 years
          tenureSlider.min = 1;
          tenureSlider.max = 30;
          tenureSlider.value = Math.max(1, Math.min(30, Math.round(tenureInput.value / 12)));
          tenureInput.value = tenureSlider.value;
          updateCalculation();
        }
      });

      tenureMonthsBtn.addEventListener("click", () => {
        if (tenureType !== "months") {
          tenureType = "months";
          tenureMonthsBtn.classList.add("active");
          tenureYearsBtn.classList.remove("active");
          // Adjust slider limits: 12 to 360 months
          tenureSlider.min = 6;
          tenureSlider.max = 360;
          tenureSlider.value = Math.max(6, Math.min(360, tenureInput.value * 12));
          tenureInput.value = tenureSlider.value;
          updateCalculation();
        }
      });
    }

    if (scheduleToggle) {
      scheduleToggle.addEventListener("click", () => {
        const scheduleContainer = document.getElementById("emi-schedule-container");
        if (scheduleContainer) {
          const isVisible = scheduleContainer.style.display === "block";
          scheduleContainer.style.display = isVisible ? "none" : "block";
          scheduleToggle.textContent = isVisible ? "View Amortization Schedule ↓" : "Hide Amortization Schedule ↑";
        }
      });
    }

    // Initial calculation
    updateCalculation();
  }

  function bindSliderAndInput(slider, input, min, max, callback) {
    if (!slider || !input) return;

    slider.addEventListener("input", (e) => {
      input.value = e.target.value;
      callback();
    });

    input.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      if (!isNaN(val) && val >= min && val <= max) {
        slider.value = val;
      }
      callback();
    });
  }

  function updateCalculation() {
    const principal = parseFloat(document.getElementById("emi-input-amount")?.value) || 0;
    const rate = parseFloat(document.getElementById("emi-input-rate")?.value) || 0;
    const tenureVal = parseInt(document.getElementById("emi-input-tenure")?.value, 10) || 0;

    const tenureMonths = tenureType === "years" ? tenureVal * 12 : tenureVal;

    const calc = FinCalc.calculateEMI(principal, rate, tenureMonths);

    // Update displays
    document.getElementById("emi-display-amount").textContent = FinCalc.formatINR(calc.emi);
    document.getElementById("emi-total-interest").textContent = FinCalc.formatINR(calc.interest);
    document.getElementById("emi-total-payment").textContent = FinCalc.formatINR(calc.total);
    document.getElementById("emi-principal-display").textContent = FinCalc.formatINR(principal);

    // Ratio Progress Bar
    const barPrincipal = document.getElementById("emi-bar-principal");
    const barInterest = document.getElementById("emi-bar-interest");
    const legendPrincipal = document.getElementById("emi-legend-principal");
    const legendInterest = document.getElementById("emi-legend-interest");

    if (calc.total > 0) {
      const principalPct = +((principal / calc.total) * 100).toFixed(1);
      const interestPct = +((calc.interest / calc.total) * 100).toFixed(1);

      if (barPrincipal) barPrincipal.style.width = `${principalPct}%`;
      if (barInterest) barInterest.style.width = `${interestPct}%`;
      if (legendPrincipal) legendPrincipal.textContent = `Principal: ${principalPct}% (${FinCalc.formatINR(principal)})`;
      if (legendInterest) legendInterest.textContent = `Interest: ${interestPct}% (${FinCalc.formatINR(calc.interest)})`;
    }

    // Update Amortization Table
    buildAmortizationTable(principal, rate, tenureMonths, calc.emi);
  }

  function buildAmortizationTable(principal, annualRate, tenureMonths, monthlyEmi) {
    const tbody = document.getElementById("emi-schedule-tbody");
    if (!tbody) return;

    tbody.innerHTML = "";
    const monthlyRate = (annualRate / 100) / 12;
    let balance = principal;
    const totalYears = Math.ceil(tenureMonths / 12);

    let monthCount = 0;
    for (let year = 1; year <= totalYears; year++) {
      let yearPrincipal = 0;
      let yearInterest = 0;

      for (let m = 0; m < 12; m++) {
        if (monthCount >= tenureMonths || balance <= 0) break;
        monthCount++;

        const interestMonth = monthlyRate > 0 ? balance * monthlyRate : 0;
        const principalMonth = Math.min(balance, monthlyEmi - interestMonth);
        balance = Math.max(0, balance - principalMonth);

        yearPrincipal += principalMonth;
        yearInterest += interestMonth;
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>Year ${year}</td>
        <td>${FinCalc.formatINR(yearPrincipal)}</td>
        <td>${FinCalc.formatINR(yearInterest)}</td>
        <td>${FinCalc.formatINR(yearPrincipal + yearInterest)}</td>
        <td>${FinCalc.formatINR(balance)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  return {
    init,
    updateCalculation
  };
})();

window.EMIController = EMIController;
