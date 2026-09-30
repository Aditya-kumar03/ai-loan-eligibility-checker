/**
 * AI Loan Eligibility Checker - Centralized REST API Service
 * Supports backend FastAPI communication with intelligent client-side
 * deterministic fallback for static deployments (e.g. GitHub Pages).
 */

const API = (() => {
  const isLocalOrigin = window.location.port === "8000";
  const isGitHubPages = window.location.hostname.includes("github.io");
  const BASE_URL = isLocalOrigin ? "/api" : "http://127.0.0.1:8000/api";

  const DISCLAIMER_TEXT = (
    "This tool provides estimates for educational and informational purposes only. "
    "Actual loan approval, interest rates, eligibility, and credit decisions are determined "
    "by banks/NBFCs and may depend on additional factors."
  );

  async function request(endpoint, options = {}) {
    // If hosted on GitHub Pages and no local/remote backend specified, try network with short timeout
    // or fall back directly to deterministic client engine.
    const url = `${BASE_URL}${endpoint}`;
    const defaultHeaders = {
      "Content-Type": "application/json",
      "Accept": "application/json"
    };

    const controller = new AbortController();
    const timeoutMs = isGitHubPages ? 1500 : 8000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    const config = {
      ...options,
      signal: controller.signal,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorDetail = "Something went wrong while processing your request.";
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            if (Array.isArray(errData.detail)) {
              errorDetail = errData.detail.map(d => d.msg || d.loc?.join(".")).join(", ");
            } else {
              errorDetail = errData.detail;
            }
          }
        } catch (_) {
          errorDetail = `Server error (${response.status}): Please check backend status.`;
        }
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeoutId);
      // Let caller handle fallback
      throw err;
    }
  }

  /* --------------------------------------------------------------------------
     Deterministic In-Browser Financial Calculation Engine (Parity with Backend)
     -------------------------------------------------------------------------- */
  function clientAnalyzeLoan(payload) {
    const p = payload.loan_amount_required;
    const r = payload.expected_interest_rate;
    const n = payload.loan_tenure_months;
    const income = payload.monthly_income;
    const existingEmi = payload.existing_monthly_emi || 0;
    const expenses = payload.monthly_expenses || 0;
    const creditScore = payload.credit_score;

    // 1. Proposed EMI
    const emiCalc = FinCalc.calculateEMI(p, r, n);
    const proposedEmi = emiCalc.emi;
    const totalEmiBurden = existingEmi + proposedEmi;
    const currentDti = +((existingEmi / income) * 100).toFixed(1);
    const postLoanDti = +((totalEmiBurden / income) * 100).toFixed(1);

    const totalObligations = totalEmiBurden + expenses;
    const netSurplus = Math.round(income - totalObligations);

    // Utilization
    let utilPct = 0;
    if (payload.total_credit_limit > 0) {
      utilPct = +Math.min(100, Math.max(0, (payload.credit_used / payload.total_credit_limit) * 100)).toFixed(1);
    }

    // 2. Score Components (1000 Pts Max)
    // A: Credit Score (max 350 pts)
    const normCredit = Math.max(0, Math.min(1, (creditScore - 300) / 600));
    const creditPts = Math.round(normCredit * 350 * 10) / 10;
    const creditRating = creditScore >= 750 ? "Excellent" : (creditScore >= 700 ? "Good" : (creditScore >= 620 ? "Moderate" : "Low"));

    // B: DTI (max 250 pts)
    let dtiPts = 20;
    let dtiRating = "Severe";
    if (postLoanDti <= 30) { dtiPts = 250; dtiRating = "Very Healthy"; }
    else if (postLoanDti <= 40) { dtiPts = 210; dtiRating = "Healthy"; }
    else if (postLoanDti <= 50) { dtiPts = 150; dtiRating = "Moderate"; }
    else if (postLoanDti <= 65) { dtiPts = 75; dtiRating = "Stretched"; }

    // C: Stability (max 150 pts)
    const exp = payload.employment_experience_years || 2.0;
    const baseStab = payload.employment_type === "Salaried" ? 95 : (payload.employment_type === "Other" ? 60 : 80);
    const expPts = Math.min(40, exp * 8);
    const incBonus = income >= 60000 ? 15 : (income >= 35000 ? 10 : 5);
    const stabilityPts = Math.min(150, Math.round(baseStab + expPts + incBonus));
    const stabilityRating = stabilityPts >= 120 ? "Strong" : (stabilityPts >= 90 ? "Moderate" : "Developing");

    // D: Credit Utilization (max 150 pts)
    let utilPts = 15;
    let utilRating = "Critical";
    if (utilPct <= 20) { utilPts = 150; utilRating = "Optimal"; }
    else if (utilPct <= 30) { utilPts = 130; utilRating = "Healthy"; }
    else if (utilPct <= 50) { utilPts = 85; utilRating = "Fair"; }
    else if (utilPct <= 75) { utilPts = 45; utilRating = "High"; }

    // E: Buffer (max 100 pts)
    const surplusRatio = income > 0 ? (netSurplus / income) : 0;
    let bufferPts = 0;
    let bufferRating = "Deficit";
    if (surplusRatio >= 0.35) { bufferPts = 100; bufferRating = "Generous"; }
    else if (surplusRatio >= 0.20) { bufferPts = 75; bufferRating = "Adequate"; }
    else if (surplusRatio >= 0.05) { bufferPts = 40; bufferRating = "Tight"; }
    else if (surplusRatio >= 0.0) { bufferPts = 15; bufferRating = "Very Tight"; }

    const totalScore = Math.max(100, Math.min(1000, Math.round(creditPts + dtiPts + stabilityPts + utilPts + bufferPts)));

    let category = "Potentially Difficult";
    if (totalScore >= 710 && postLoanDti <= 48 && creditScore >= 680 && netSurplus > 0) {
      category = "Likely Eligible";
    } else if (totalScore >= 540 && postLoanDti <= 65 && creditScore >= 600 && netSurplus >= -5000) {
      category = "May Require Review";
    }

    const reasons = [];
    if (creditScore >= 750) {
      reasons.append ? reasons.append() : reasons.push(`Your credit score of ${creditScore} is within a generally favorable range for prime interest rates.`);
    } else if (creditScore >= 680) {
      reasons.push(`Your credit score of ${creditScore} satisfies standard eligibility criteria for most commercial lenders.`);
    } else {
      reasons.push(`Your credit score of ${creditScore} is below primary lending benchmarks (700+), which may restrict lender options.`);
    }

    if (postLoanDti <= 35) {
      reasons.push(`Your post-loan debt-to-income ratio (${postLoanDti}%) represents a very manageable share of your income.`);
    } else if (postLoanDti <= 50) {
      reasons.push(`Your post-loan DTI of ${postLoanDti}% is acceptable under standard bank guidelines (<=50% FOIR).`);
    } else {
      reasons.push(`Your post-loan DTI of ${postLoanDti}% exceeds 50%, indicating significant monthly debt burden.`);
    }

    if (existingEmi > 0) {
      const pctExisting = ((existingEmi / income) * 100).toFixed(1);
      reasons.push(`Existing EMI commitments (₹${existingEmi.toLocaleString('en-IN')}) claim ${pctExisting}% of your income.`);
    }

    if (utilPct <= 30) {
      reasons.push(`Your credit utilization of ${utilPct}% remains within the recommended 30% ceiling.`);
    } else {
      reasons.push(`Your credit utilization of ${utilPct}% is elevated above the 30% standard, which impacts credit scoring.`);
    }

    const strengths = [];
    if (creditScore >= 700) strengths.push(`Credit score of ${creditScore} provides strong underwriting eligibility.`);
    if (postLoanDti <= 40) strengths.push(`Prudent post-loan DTI (${postLoanDti}%) preserves disposable income buffer.`);
    if (utilPct <= 30) strengths.push(`Controlled credit line utilization at ${utilPct}%.`);
    if (!strengths.length) strengths.push(`Verified income stream of ₹${income.toLocaleString('en-IN')}/mo supports baseline servicing.`);

    const concerns = [];
    if (postLoanDti > 45) concerns.push(`Total debt burden claims ${postLoanDti}% of monthly earnings.`);
    if (utilPct > 35) concerns.push(`Revolving card balance is elevated at ${utilPct}%.`);
    if (netSurplus < 8000) concerns.push(`Monthly surplus of ₹${netSurplus.toLocaleString('en-IN')} leaves minimal room for emergency cash outlays.`);
    if (!concerns.length) concerns.push(`Ensure long-term tenure commitment aligns with future savings milestones.`);

    const recommendations = [
      postLoanDti > 45 ? "Consider increasing loan tenure to lower the proposed monthly EMI below 40% DTI." : "Maintain timely EMI debits to safeguard bureau standing.",
      utilPct > 30 ? "Pay down credit card outstanding balance before filing official bank applications." : "Keep credit card utilization below 30% across billing cycles.",
      "Inquire with lenders regarding floating vs fixed rate pre-payment and foreclosure charges."
    ];

    const questions = [
      "What is the effective Annual Percentage Rate (APR) including processing fees and stamp duty?",
      "Are there zero-penalty part-prepayment options available after 6 or 12 months?",
      "Does having an existing salary account with your bank qualify me for preferential interest rate discounts?"
    ];

    return {
      session_id: `SES-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      status: "success",
      eligibility_category: category,
      estimated_eligibility_score: totalScore,
      score_breakdown: {
        total_score: totalScore,
        max_score: 1000,
        credit_score_component: {
          name: "Credit Bureau Profile",
          points_awarded: creditPts,
          max_points: 350,
          rating: creditRating,
          explanation: `Bureau score of ${creditScore} in ${creditRating} tier.`
        },
        dti_component: {
          name: "Debt-to-Income Capacity",
          points_awarded: dtiPts,
          max_points: 250,
          rating: dtiRating,
          explanation: `Post-loan DTI of ${postLoanDti}% (${dtiRating}).`
        },
        income_stability_component: {
          name: "Employment & Income Stability",
          points_awarded: stabilityPts,
          max_points: 150,
          rating: stabilityRating,
          explanation: `${payload.employment_type} profile with ${exp} yrs experience.`
        },
        credit_utilization_component: {
          name: "Credit Line Discipline",
          points_awarded: utilPts,
          max_points: 150,
          rating: utilRating,
          explanation: `Credit card utilization at ${utilPct}%.`
        },
        expense_buffer_component: {
          name: "Disposable Cash Buffer",
          points_awarded: bufferPts,
          max_points: 100,
          rating: bufferRating,
          explanation: `Monthly surplus of ₹${netSurplus.toLocaleString('en-IN')}.`
        }
      },
      metrics: {
        current_dti_pct: currentDti,
        proposed_emi: proposedEmi,
        total_emi_burden: totalEmiBurden,
        post_loan_dti_pct: postLoanDti,
        total_monthly_obligations: totalObligations,
        net_disposable_surplus: netSurplus,
        credit_utilization_pct: utilPct,
        loan_to_income_ratio: +((p / (income * 12)).toFixed(2)),
        total_interest_payable: emiCalc.interest,
        total_repayment_amount: emiCalc.total
      },
      deterministic_reasons: reasons,
      ai_analysis: {
        summary: `Applicant shows monthly earnings of ₹${income.toLocaleString('en-IN')} with an Estimated Financial Eligibility Score of ${totalScore}/1000 (${category}). Proposed EMI stands at ₹${proposedEmi.toLocaleString('en-IN')}.`,
        eligibility_explanation: `Evaluated using reducing-balance amortization and standard Indian banking FOIR criteria (post-loan debt ratio: ${postLoanDti}%).`,
        strengths: strengths,
        concerns: concerns,
        recommendations: recommendations,
        risk_considerations: [
          "Floating interest rate loans may see EMI adjustments if the RBI adjusts benchmark repo rates.",
          "Filing multiple hard loan inquiries in quick succession can temporarily lower your bureau score."
        ],
        questions_for_lender: questions,
        is_ai_generated: false,
        model_used: "Deterministic Rule-Engine Engine",
        notice: isGitHubPages ? "Running in Web Demo Mode (Deterministic Rule Engine active)." : "AI analysis temporarily unavailable. Showing rule-based analysis."
      },
      disclaimer: DISCLAIMER_TEXT,
      sheets_synced: false
    };
  }

  function clientAnalyzeCredit(payload) {
    const score = payload.credit_score;
    const limit = payload.total_credit_limit || 0;
    const used = payload.used_credit || 0;
    const util = limit > 0 ? +Math.min(100, Math.max(0, (used / limit) * 100)).toFixed(1) : 0;
    const income = payload.monthly_income || 50000;
    const emi = payload.existing_monthly_emi || 0;
    const debtRatio = +((emi / income) * 100).toFixed(1);

    const bands = [
      { range_label: "800–900", band_name: "Excellent", min_score: 800, max_score: 900, is_user_band: score >= 800 },
      { range_label: "740–799", band_name: "Very Good", min_score: 740, max_score: 799, is_user_band: score >= 740 && score < 800 },
      { range_label: "670–739", band_name: "Good", min_score: 670, max_score: 739, is_user_band: score >= 670 && score < 740 },
      { range_label: "580–669", band_name: "Fair", min_score: 580, max_score: 669, is_user_band: score >= 580 && score < 670 },
      { range_label: "300–579", band_name: "Needs Attention", min_score: 300, max_score: 579, is_user_band: score < 580 }
    ];

    const userBand = bands.find(b => b.is_user_band) || bands[2];

    return {
      credit_score: score,
      credit_utilization_pct: util,
      utilization_rating: util <= 30 ? "Optimal" : (util <= 50 ? "Moderate" : "High Risk"),
      debt_burden_ratio_pct: debtRatio,
      reference_band: userBand,
      all_reference_ranges: bands,
      credit_health_factors: [
        { factor: "Payment History Tier", status: score >= 740 ? "Strong" : (score >= 670 ? "Fair" : "Action Needed"), detail: `Score ${score} in '${userBand.band_name}' tier (${userBand.range_label}).` },
        { factor: "Credit Line Utilization", status: util <= 30 ? "Strong" : (util <= 50 ? "Fair" : "High Risk"), detail: `${util}% utilized of ₹${limit.toLocaleString('en-IN')} limit.` },
        { factor: "Existing Debt Burden", status: debtRatio <= 30 ? "Strong" : "Review", detail: `EMIs absorb ${debtRatio}% of monthly net income.` }
      ],
      actionable_recommendations: [
        util > 30 ? `Pay down ₹${Math.max(0, used - (limit * 0.3)).toLocaleString('en-IN')} to bring utilization below 30%.` : "Maintain utilization below 30% for steady score growth.",
        score < 750 ? "Set up auto-debit for total credit card balance due to ensure zero late payments." : "Your credit standing qualifies you for prime lending interest rates.",
        "Refrain from applying for multiple fresh credit lines within short 90-day intervals."
      ],
      disclaimer: DISCLAIMER_TEXT
    };
  }

  function clientGetFinancialTips(topic) {
    const tipsDB = {
      "Credit Score": {
        overview: "Credit score reflects your creditworthiness based on past repayment history, credit mix, and inquiry frequency.",
        pro_tip: "Check your free annual CIBIL/Experian report twice a year to dispute reporting errors or duplicate active loan tags.",
        tips: [
          { title: "Keep Utilization Under 30%", content: "Spending more than 30% of your credit limit flags liquidity dependency to bureau scoring algorithms.", impact_level: "High", action_item: "Request a credit limit increase without increasing discretionary spending." },
          { title: "Never Miss a Due Date", content: "Payment history constitutes ~35% of your credit score. A single 30-day default can depress your score by 40-70 points.", impact_level: "Fundamental", action_item: "Enable auto-debit for 'Total Amount Due' rather than 'Minimum Amount Due'." },
          { title: "Retain Oldest Cards", content: "Credit history age strengthens bureau standing. Closing your oldest zero-annual-fee card shortens average account tenure.", impact_level: "Medium", action_item: "Keep oldest cards open with small recurring utility debits." }
        ]
      },
      "Loans": {
        overview: "Borrowing responsibly requires understanding total borrowing cost, amortizing interest curves, and tenure tradeoffs.",
        pro_tip: "Compare the Annual Percentage Rate (APR) including processing fees and insurance, rather than the headline interest rate alone.",
        tips: [
          { title: "Review Prepayment Clauses", content: "Per RBI guidelines, floating-rate personal and home loans to individuals cannot carry prepayment penalties.", impact_level: "High", action_item: "Confirm zero-prepayment penalty terms before signing loan documentation." },
          { title: "Select Shortest Manageable Tenure", content: "A longer tenure lowers the monthly installment but substantially inflates total interest paid to the lender.", impact_level: "Medium", action_item: "Simulate 36 vs 60 month tenures to find the optimal interest-saving balance." },
          { title: "Avoid Borrowing for Speculation", content: "Never take personal or gold loans to invest in speculative equities or cryptocurrencies.", impact_level: "Fundamental", action_item: "Restrict borrowing strictly to capital assets or planned emergency consolidations." }
        ]
      },
      "EMI Management": {
        overview: "Effective EMI management ensures cash-flow predictability and eliminates default penalties.",
        pro_tip: "Paying just one extra EMI per calendar year on a long-term loan can reduce tenure by several years.",
        tips: [
          { title: "Align Deduction with Salary Dates", content: "Scheduling EMIs 3–5 days after your monthly salary credit avoids NACH bounce charges (₹400–₹500/bounce).", impact_level: "High", action_item: "Contact your lending bank to adjust your mandate deduction date." },
          { title: "Maintain 40% FOIR Boundary", content: "Keep total fixed debt obligations under 40% of net income to maintain a financial safety margin.", impact_level: "Fundamental", action_item: "Pause new retail or gadget EMIs if existing payments cross 40% of income." },
          { title: "Prepay Principal with Annual Bonuses", content: "Direct festive bonuses or tax refunds into principal prepayment tranches to reduce ongoing interest compounding.", impact_level: "High", action_item: "Commit 30% of annual bonuses directly toward debt reduction." }
        ]
      },
      "Budgeting": {
        overview: "Structured budgeting gives you control over cash allocation rather than wondering where your monthly earnings disappeared.",
        pro_tip: "Audit your UPI transaction history every Sunday evening; 5 minutes of weekly tracking prevents end-of-month budget shocks.",
        tips: [
          { title: "Apply the 50/30/20 Rule", content: "Dedicate 50% of income to essential needs, 30% to discretionary lifestyle desires, and 20% directly to savings.", impact_level: "Fundamental", action_item: "Categorize last month's bank statement into Needs vs Wants." },
          { title: "Automate Savings First", content: "Saving what remains after spending typically yields zero savings. Automating savings on salary day enforces discipline.", impact_level: "High", action_item: "Set up a recurring deposit or index fund SIP on the 2nd day of every month." },
          { title: "Prune Dormant Subscriptions", content: "Multiple small digital subscriptions often sum to ₹3,000–₹5,000 monthly with negligible real engagement.", impact_level: "Medium", action_item: "Audit and cancel unused streaming or gym memberships." }
        ]
      },
      "Debt Management": {
        overview: "Strategic debt elimination stops compound interest from eroding your household wealth.",
        pro_tip: "Deploy the Debt Avalanche method: focus surplus cash on the highest-interest obligation first (credit cards at 36-42% APR).",
        tips: [
          { title: "Target High-Interest Credit Cards", content: "Revolving card debt carries aggressive 36%–42% annual interest that severely compounds over time.", impact_level: "Fundamental", action_item: "Pay off credit card balances before making extra payments on low-cost home loans." },
          { title: "Avoid Unnecessary Card EMI Conversions", content: "Banks market card EMI conversions heavily, but processing fees and 14%–20% interest rates make them costly.", impact_level: "High", action_item: "Avoid financing non-essential lifestyle purchases via credit card EMIs." },
          { title: "Consider Low-Cost Debt Consolidation", content: "Consolidating 3 expensive unsecured loans into one lower-rate personal loan simplifies tracking and saves interest.", impact_level: "Medium", action_item: "Evaluate if a single 11% personal loan can clear multiple 18%+ debts." }
        ]
      },
      "Savings": {
        overview: "Savings serve as your personal balance sheet defense against job volatility and unforeseen emergencies.",
        pro_tip: "Keep your emergency buffer in a separate bank account without debit card access enabled on digital wallets.",
        tips: [
          { title: "Build a 6-Month Emergency Runway", content: "Accumulate 6 months of living expenses (rent + food + utilities + EMIs) in safe, liquid savings instruments.", impact_level: "Fundamental", action_item: "Calculate your mandatory monthly survival figure and begin saving toward it." },
          { title: "Step Up Savings by 10% Annually", content: "Whenever you receive a salary increment, increase your monthly investment contributions before expanding your lifestyle.", impact_level: "High", action_item: "Enable annual step-up instructions on your automated investments." },
          { title: "Separate Emergency Funds from Daily Accounts", content: "Keeping emergency reserves in daily UPI-linked accounts creates behavioral temptation to spend them.", impact_level: "Medium", action_item: "Move reserves to a dedicated high-interest savings or sweep FD account." }
        ]
      },
      "Financial Planning": {
        overview: "Comprehensive financial planning integrates insurance protection, long-term wealth compounding, and goal planning.",
        pro_tip: "Purchase pure term insurance early in your career to lock in low annual premium rates for 30+ years.",
        tips: [
          { title: "Secure Pure Term Insurance First", content: "If you have dependents or active loans, purchase pure term insurance cover equal to 10–15 times your annual salary.", impact_level: "Fundamental", action_item: "Avoid complex investment-cum-insurance plans; buy pure term cover." },
          { title: "Maintain Independent Health Cover", content: "A single medical emergency can wipe out years of disciplined savings. Do not depend solely on employer corporate cover.", impact_level: "Fundamental", action_item: "Procure a personal base health policy with a high-deductible super top-up." },
          { title: "Map Money to Specific Time Horizons", content: "Funds needed within 3 years belong in debt instruments or FDs; long-term goals belong in equity index funds.", impact_level: "High", action_item: "Write down your key financial milestones alongside target completion dates." }
        ]
      }
    };

    const data = tipsDB[topic] || tipsDB["Financial Planning"];
    return {
      topic: topic,
      overview: data.overview,
      pro_tip: data.pro_tip,
      tips: data.tips,
      is_ai_generated: false,
      notice: isGitHubPages ? "Educational Guidance (Web Demo Mode)" : "AI analysis temporarily unavailable. Showing rule-based analysis.",
      disclaimer: DISCLAIMER_TEXT
    };
  }

  return {
    async checkHealth() {
      try {
        return await request("/health");
      } catch (err) {
        return {
          status: "healthy",
          service: "AI Loan Eligibility Checker",
          version: "1.0.0",
          environment: "client-demo",
          integrations: {
            claude_ai: { configured: false, mode: "Rule-Engine Fallback" },
            google_sheets: { configured: false, mode: "Local Only" }
          }
        };
      }
    },

    async analyzeLoan(payload) {
      try {
        return await request("/loan/analyze", {
          method: "POST",
          body: JSON.stringify(payload)
        });
      } catch (err) {
        // Fall back to client calculation engine
        return clientAnalyzeLoan(payload);
      }
    },

    async analyzeCredit(payload) {
      try {
        return await request("/credit/analyze", {
          method: "POST",
          body: JSON.stringify(payload)
        });
      } catch (err) {
        return clientAnalyzeCredit(payload);
      }
    },

    async calculateEMI(payload) {
      try {
        return await request("/emi/calculate", {
          method: "POST",
          body: JSON.stringify(payload)
        });
      } catch (err) {
        const tenureMonths = payload.tenure_type === "years" ? payload.tenure_value * 12 : payload.tenure_value;
        const calc = FinCalc.calculateEMI(payload.loan_amount, payload.interest_rate, tenureMonths);
        return {
          principal_amount: payload.loan_amount,
          annual_interest_rate: payload.interest_rate,
          tenure_months: tenureMonths,
          monthly_emi: calc.emi,
          total_interest_payable: calc.interest,
          total_repayment: calc.total,
          principal_ratio_pct: +((payload.loan_amount / calc.total) * 100).toFixed(1),
          interest_ratio_pct: +((calc.interest / calc.total) * 100).toFixed(1),
          amortization_schedule: []
        };
      }
    },

    async getFinancialTips(topic, context = "") {
      try {
        return await request("/ai/financial-tips", {
          method: "POST",
          body: JSON.stringify({ topic, user_context: context })
        });
      } catch (err) {
        return clientGetFinancialTips(topic);
      }
    },

    async submitFeedback(payload) {
      try {
        return await request("/feedback", {
          method: "POST",
          body: JSON.stringify(payload)
        });
      } catch (err) {
        return { status: "received", message: "Thank you for your feedback!" };
      }
    }
  };
})();

window.API = API;
