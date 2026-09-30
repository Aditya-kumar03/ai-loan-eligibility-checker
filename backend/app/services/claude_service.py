import json
import logging
from typing import Optional, List, Dict, Any
from backend.app.config.settings import settings
from backend.app.models.loan import LoanApplicationRequest, FinancialMetrics, AIAnalysisResult
from backend.app.models.tips import FinancialTipsRequest, FinancialTipsResponse, TipItem
from backend.app.utils.logger import logger

AI_SYSTEM_PROMPT = (
    "You are an educational financial analysis assistant for an Indian BFSI decision-support platform. "
    "You provide objective explanations based strictly on the financial numbers supplied. "
    "Rules you must strictly follow:\n"
    "1. You DO NOT guarantee loan approval or issue official credit decisions.\n"
    "2. You DO NOT pretend to represent any specific bank, NBFC, or credit bureau (CIBIL/Experian).\n"
    "3. You DO NOT invent financial data or claim access to confidential banking records.\n"
    "4. You must format your final response ONLY as a valid JSON object matching the requested schema.\n"
    "5. Use Indian financial context (INR, FOIR, DTI, CIBIL benchmarks, pre-payment clauses)."
)

FALLBACK_NOTICE = "AI analysis temporarily unavailable. Showing rule-based analysis."

def generate_deterministic_loan_ai_fallback(
    req: LoanApplicationRequest,
    metrics: FinancialMetrics,
    category: str,
    score: int
) -> AIAnalysisResult:
    """
    Robust rule-based financial analysis generated when Claude API is unavailable or offline.
    Never invents data; strictly references the user's provided numbers.
    """
    strengths = []
    concerns = []
    recommendations = []
    risks = []
    questions = []

    # Strengths
    if req.credit_score >= 750:
        strengths.append(f"Strong bureau credit score ({req.credit_score}) places you in an advantageous tier for prime interest rate quotes.")
    elif req.credit_score >= 700:
        strengths.append(f"Healthy credit score of {req.credit_score} satisfies underwriting thresholds for conventional lenders.")

    if metrics.post_loan_dti_pct <= 40.0:
        strengths.append(f"Prudent post-loan DTI ({metrics.post_loan_dti_pct}%) keeps total debt well within safe living margin.")

    if metrics.credit_utilization_pct <= 30.0:
        strengths.append(f"Disciplined credit card utilization at {metrics.credit_utilization_pct}%, indicating low dependency on revolving credit.")

    if req.employment_experience_years and req.employment_experience_years >= 2.0:
        strengths.append(f"Stable employment profile with {req.employment_experience_years:.1f} years in {req.employment_type} sector.")

    if not strengths:
        strengths.append(f"Clear income flow of ₹{req.monthly_income:,.0f} per month provides an operational baseline for debt servicing.")

    # Concerns
    if metrics.post_loan_dti_pct > 50.0:
        concerns.append(f"Post-loan monthly obligations will absorb {metrics.post_loan_dti_pct}% of your net income, exceeding standard 50% FOIR.")

    if req.existing_monthly_emi > 0 and (req.existing_monthly_emi / req.monthly_income) > 0.25:
        concerns.append(f"Existing EMIs already consume ₹{req.existing_monthly_emi:,.0f} monthly before taking on the proposed loan.")

    if metrics.credit_utilization_pct > 40.0:
        concerns.append(f"Credit utilization at {metrics.credit_utilization_pct}% is elevated above the 30% guideline.")

    if req.credit_score < 680:
        concerns.append(f"A credit score of {req.credit_score} may trigger stricter underwriting scrutiny, collateral demands, or rate surcharges.")

    if metrics.net_disposable_surplus <= 5000:
        concerns.append(f"Slim monthly buffer of ₹{max(0.0, metrics.net_disposable_surplus):,.0f} leaves little room for unexpected financial emergencies.")

    if not concerns:
        concerns.append("Ensure long-term tenure commitment doesn't impede retirement or liquid savings allocations.")

    # Recommendations
    if metrics.post_loan_dti_pct > 45.0:
        recommendations.append("Consider opting for a longer tenure or a smaller principal amount to bring proposed EMI under 40% of income.")
    if metrics.credit_utilization_pct > 30.0:
        recommendations.append("Pay down existing credit card balances before submitting official bank applications.")
    if req.existing_monthly_emi > 0:
        recommendations.append("Explore prepaying or consolidating higher-interest short-term loans to reduce monthly EMI burden.")
    recommendations.append("Verify your formal bureau credit report for inaccuracies or disputed entries prior to lender inquiries.")

    # Risks
    risks.append("Multiple hard credit inquiries across various lenders within a short timeframe can temporarily depress your credit score.")
    risks.append("Floating interest rate products may experience EMI increases during RBI monetary tightening cycles.")

    # Questions for Lender
    questions.append("What is the annual percentage rate (APR), inclusive of all mandatory processing fees and insurance charges?")
    questions.append("Are there any pre-payment or foreclosure penalties on partial repayments after 6 or 12 months?")
    questions.append("What concessions or interest rate discounts are available for borrowers with my credit score tier?")

    summary = (
        f"Borrower profile reflects a monthly net income of ₹{req.monthly_income:,.0f} with an estimated financial "
        f"eligibility score of {score}/1000 ({category}). The requested loan of ₹{req.loan_amount_required:,.0f} "
        f"results in a proposed monthly EMI of ₹{metrics.proposed_emi:,.0f}."
    )

    explanation = (
        f"Under rule-based financial evaluation, your post-loan debt service ratio stands at {metrics.post_loan_dti_pct}%. "
        f"Lenders in India generally mandate a Fixed Obligation to Income Ratio (FOIR) between 45% and 55%. "
        f"With your credit score at {req.credit_score}, your profile is evaluated as {category}."
    )

    return AIAnalysisResult(
        summary=summary,
        eligibility_explanation=explanation,
        strengths=strengths,
        concerns=concerns,
        recommendations=recommendations,
        risk_considerations=risks,
        questions_for_lender=questions,
        is_ai_generated=False,
        model_used="Deterministic Rule-Based Underwriting Engine",
        notice=FALLBACK_NOTICE
    )

async def analyze_loan_with_claude(
    req: LoanApplicationRequest,
    metrics: FinancialMetrics,
    category: str,
    score: int
) -> AIAnalysisResult:
    """
    Sends structured financial context to Anthropic Claude API.
    Gracefully falls back to deterministic rule engine if API is not configured or unavailable.
    """
    if not settings.is_claude_configured:
        logger.info("Claude API key not configured. Using deterministic rule-based analysis.")
        return generate_deterministic_loan_ai_fallback(req, metrics, category, score)

    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

        user_content = {
            "applicant": {
                "age": req.age,
                "employment_type": req.employment_type,
                "employment_experience_years": req.employment_experience_years,
                "monthly_income_inr": req.monthly_income,
                "existing_monthly_emi_inr": req.existing_monthly_emi,
                "monthly_expenses_inr": req.monthly_expenses,
                "credit_score": req.credit_score,
                "credit_utilization_pct": metrics.credit_utilization_pct,
                "active_loans": req.number_of_existing_loans,
                "credit_cards": req.number_of_credit_cards
            },
            "loan_request": {
                "preferred_type": req.preferred_loan_type,
                "amount_inr": req.loan_amount_required,
                "tenure_months": req.loan_tenure_months,
                "interest_rate_pct": req.expected_interest_rate
            },
            "deterministic_metrics": {
                "proposed_monthly_emi_inr": metrics.proposed_emi,
                "total_emi_burden_inr": metrics.total_emi_burden,
                "post_loan_dti_pct": metrics.post_loan_dti_pct,
                "net_disposable_surplus_inr": metrics.net_disposable_surplus,
                "loan_to_income_ratio": metrics.loan_to_income_ratio,
                "internal_eligibility_score": f"{score}/1000",
                "internal_category": category
            }
        }

        instructions = (
            "Analyze the above applicant data and return ONLY a JSON object with this exact structure:\n"
            "{\n"
            '  "summary": "1-2 sentences summarizing borrower profile and proposed debt.",\n'
            '  "eligibility_explanation": "Objective explanation of why this profile falls into the estimated category without guaranteeing any approval.",\n'
            '  "strengths": ["3 to 4 specific positive financial factors based on provided numbers"],\n'
            '  "concerns": ["2 to 4 specific potential risk or stretch factors"],\n'
            '  "recommendations": ["3 to 4 actionable, practical steps for financial optimization"],\n'
            '  "risk_considerations": ["2 practical risk points like interest fluctuations, emergency buffer impact"],\n'
            '  "questions_for_lender": ["3 to 4 smart questions to ask loan officers (processing fees, pre-payment, etc.)"]\n'
            "}"
        )

        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1500,
            system=AI_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Financial Profile Data:\n```json\n{json.dumps(user_content, indent=2)}\n```\n\n{instructions}"
                }
            ]
        )

        response_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_text += block.text

        # Parse JSON from response
        # Find JSON boundaries if wrapped in markdown
        cleaned = response_text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        data = json.loads(cleaned)

        return AIAnalysisResult(
            summary=data.get("summary", ""),
            eligibility_explanation=data.get("eligibility_explanation", ""),
            strengths=data.get("strengths", []),
            concerns=data.get("concerns", []),
            recommendations=data.get("recommendations", []),
            risk_considerations=data.get("risk_considerations", []),
            questions_for_lender=data.get("questions_for_lender", []),
            is_ai_generated=True,
            model_used=f"Anthropic {settings.CLAUDE_MODEL}",
            notice=None
        )

    except Exception as e:
        logger.warning(f"Claude API invocation encountered an issue: {str(e)}. Falling back to deterministic analysis.")
        return generate_deterministic_loan_ai_fallback(req, metrics, category, score)

CURATED_TIPS_DATABASE: Dict[str, Dict[str, Any]] = {
    "Credit Score": {
        "overview": "Your credit score is a numerical snapshot of your creditworthiness based on past repayment history, credit mix, and bureau inquiries.",
        "tips": [
            {
                "title": "Keep Credit Utilization Under 30%",
                "content": "Even if your bank gives you a ₹1,00,000 credit limit, spending over ₹30,000 in a billing cycle signals credit dependency to bureau algorithms.",
                "impact_level": "High",
                "action_item": "Set automated mid-cycle balance payments or request an increase in your credit limit without increasing spending."
            },
            {
                "title": "Never Miss a Payment Due Date",
                "content": "Payment history accounts for approximately 35% of your credit score. A single 30-day delinquency can drop your score by 40-70 points.",
                "impact_level": "Fundamental",
                "action_item": "Enable auto-debit for at least the 'Total Amount Due' rather than the misleading 'Minimum Amount Due'."
            },
            {
                "title": "Preserve Old Credit Card Accounts",
                "content": "Credit history length contributes positively to your standing. Closing your oldest zero-fee card truncates your average account age.",
                "impact_level": "Medium",
                "action_item": "Keep old zero-annual-fee cards active with one recurring small subscription paid off immediately."
            }
        ],
        "pro_tip": "Check your free annual CIBIL/Experian report once every six months to dispute reporting errors or duplicate active loan tags."
    },
    "Loans": {
        "overview": "Borrowing responsibly requires understanding total borrowing cost, amortizing interest curves, and tenure tradeoffs.",
        "tips": [
            {
                "title": "Compare APR, Not Just Headline Interest",
                "content": "A 10.5% loan with a 2% processing fee and mandatory insurance can be substantially more expensive than an 11% loan with zero fees.",
                "impact_level": "High",
                "action_item": "Request a Key Fact Statement (KFS) detailing the comprehensive Annual Percentage Rate (APR) from every prospective lender."
            },
            {
                "title": "Evaluate Prepayment & Foreclosure Terms",
                "content": "Per RBI guidelines, floating-rate personal/home loans to individuals cannot carry foreclosure penalties, but fixed-rate loans often do.",
                "impact_level": "High",
                "action_item": "Verify the exact prepayment clause so you can make lump-sum principal payments whenever annual bonuses arrive."
            },
            {
                "title": "Opt for the Shortest Comfortable Tenure",
                "content": "Extending a ₹10 Lakh loan from 3 years to 7 years lowers the monthly EMI but can more than double your total interest paid.",
                "impact_level": "Medium",
                "action_item": "Use our EMI calculator to compare total interest outgo across 36 vs 60 month tenures before signing."
            }
        ],
        "pro_tip": "Never borrow money to invest in speculative instruments like stocks or crypto; your loan interest is guaranteed, but returns are not."
    },
    "EMI Management": {
        "overview": "Managing multiple EMIs demands cash-flow predictability and disciplined debt structuring.",
        "tips": [
            {
                "title": "Align EMI Dates with Salary Credits",
                "content": "Scheduling EMIs 3–5 days after your regular salary credit date avoids embarrassing bounce charges and ECS return penalties (₹400-₹500/bounce).",
                "impact_level": "High",
                "action_item": "Contact your lending bank's customer support to adjust mandate deduction dates to the 5th or 7th of the month."
            },
            {
                "title": "Target One Extra EMI Payment Annually",
                "content": "Paying just one extra EMI per calendar year on a 20-year home loan can shave off nearly 3 to 4 years from your total loan tenure.",
                "impact_level": "High",
                "action_item": "Direct a portion of festive bonuses or tax refunds into an annual principal-only pre-payment tranche."
            },
            {
                "title": "Respect the 40% FOIR Ceiling",
                "content": "Fixed Obligation to Income Ratio (FOIR) should ideally remain under 40% so that unexpected lifestyle inflation doesn't cause defaults.",
                "impact_level": "Fundamental",
                "action_item": "If existing EMIs cross 45% of income, institute an immediate freeze on new retail or gadget loans."
            }
        ],
        "pro_tip": "If cash flow is temporarily tight, contact your lender proactively for tenure restructuring rather than letting an EMI dishonor."
    },
    "Budgeting": {
        "overview": "Structured budgeting gives you control over cash allocation rather than wondering where your monthly earnings disappeared.",
        "tips": [
            {
                "title": "Apply the 50/30/20 Framework",
                "content": "Allocate 50% of net income to fixed needs (rent, groceries, utilities, EMIs), 30% to discretionary lifestyle wants, and at least 20% to savings.",
                "impact_level": "Fundamental",
                "action_item": "Audit last month's UPI transactions and categorize them into Needs vs. Wants."
            },
            {
                "title": "Treat Savings as an Upfront Expense",
                "content": "Saving what remains after spending usually results in zero savings. Saving first and spending what remains ensures wealth compounding.",
                "impact_level": "High",
                "action_item": "Set up a recurring deposit or index fund SIP automated on the 2nd day of every month."
            },
            {
                "title": "Audit Recurring Micro-Subscriptions",
                "content": "Multiple small OTT streaming, gym, and app subscriptions often add up to ₹3,000–₹5,000 a month with minimal actual usage.",
                "impact_level": "Medium",
                "action_item": "Cancel inactive subscriptions and use quarterly on-demand reactivation instead."
            }
        ],
        "pro_tip": "Review your bank statement every Sunday evening; 5 minutes of weekly tracking prevents end-of-month budget shocks."
    },
    "Debt Management": {
        "overview": "Strategic debt elimination prevents interest compounding against you and clears borrowing bandwidth.",
        "tips": [
            {
                "title": "Deploy Debt Avalanche for Highest Interest",
                "content": "List all active debts by interest rate. Pay minimums on all, and direct every spare rupee to the loan with the highest interest (typically credit cards at 36-42% APR).",
                "impact_level": "High",
                "action_item": "Rank your debts by APR and focus surplus cash strictly on the top item."
            },
            {
                "title": "Avoid Converting Card Spends to Costly EMIs",
                "content": "Banks market credit card EMI conversions as low cost, but processing fees, GST on interest, and 14-20% rates make them expensive debt traps.",
                "impact_level": "High",
                "action_item": "If you cannot pay for a discretionary item in full within 30 days, delay the purchase."
            },
            {
                "title": "Consider Low-Cost Debt Consolidation",
                "content": "Replacing multiple fragmented 18-36% unsecured liabilities with a single 11-13% personal loan simplifies tracking and slashes total interest.",
                "impact_level": "Medium",
                "action_item": "Calculate whether a personal loan can close out 3 high-interest revolving card balances."
            }
        ],
        "pro_tip": "Never borrow from unverified mobile lending apps that demand contact-list permissions; stick strictly to RBI-registered banks and NBFCs."
    },
    "Savings": {
        "overview": "Savings form your personal balance sheet defense against job volatility, medical emergencies, and market downturns.",
        "tips": [
            {
                "title": "Build a 6-Month Emergency Runway",
                "content": "Accumulate 6 months of mandatory living expenses (rent + food + utilities + active EMIs) in high-liquidity, capital-safe accounts.",
                "impact_level": "Fundamental",
                "action_item": "Calculate your exact monthly survival number and open a dedicated high-interest savings account or sweep FD for this fund."
            },
            {
                "title": "Keep Emergency Funds Separate from Daily Spend",
                "content": "Keeping emergency cash in your daily UPI-linked spending account creates behavioral temptation to spend it.",
                "impact_level": "Medium",
                "action_item": "Hold the emergency buffer in a secondary bank account without debit card access enabled on digital wallets."
            },
            {
                "title": "Step Up Your Savings by 10% Each Year",
                "content": "Whenever you receive an annual salary increment or bonus, increase your monthly savings rate by at least 10% before upgrading your lifestyle.",
                "impact_level": "High",
                "action_item": "Configure an annual step-up instruction on your recurring deposits or mutual fund SIPs."
            }
        ],
        "pro_tip": "Emergency funds are not for earning maximum alpha; their primary purpose is liquidity and peace of mind when life is unpredictable."
    },
    "Financial Planning": {
        "overview": "Holistic financial planning integrates insurance protection, long-term wealth building, and goal-based asset allocation.",
        "tips": [
            {
                "title": "Secure Pure Term Insurance First",
                "content": "If you have dependents or active loans, secure a pure term insurance policy with coverage equal to at least 10–15 times your annual income.",
                "impact_level": "Fundamental",
                "action_item": "Avoid complex endowment or ULIP insurance-cum-investment plans; buy pure term cover at younger ages to lock in cheap premiums."
            },
            {
                "title": "Maintain Comprehensive Health Insurance",
                "content": "A single major hospitalization can wipe out years of disciplined savings. Do not rely solely on corporate employer health cover.",
                "impact_level": "Fundamental",
                "action_item": "Purchase an independent personal base policy (e.g. ₹5–₹10 Lakh) paired with a high-deductible super top-up policy (e.g. ₹20–₹50 Lakh)."
            },
            {
                "title": "Map Investments to Specific Time Horizons",
                "content": "Goals under 3 years belong in debt instruments or FDs. Goals 5+ years away belong in equity index funds for inflation-beating growth.",
                "impact_level": "High",
                "action_item": "Write down your key financial milestones (down payment, child education, retirement) alongside target dates."
            }
        ],
        "pro_tip": "Never sign insurance or investment documents under pressure; insist on a 15-day free look period to read the fine print."
    }
}

async def generate_financial_tips(req: FinancialTipsRequest) -> FinancialTipsResponse:
    """
    Generates actionable financial guidance using Claude if configured,
    or curated high-grade fallback database when offline.
    """
    topic_data = CURATED_TIPS_DATABASE.get(req.topic, CURATED_TIPS_DATABASE["Financial Planning"])
    default_tips = [TipItem(**item) for item in topic_data["tips"]]
    default_overview = topic_data["overview"]
    default_pro_tip = topic_data["pro_tip"]

    if not settings.is_claude_configured:
        return FinancialTipsResponse(
            topic=req.topic,
            overview=default_overview,
            tips=default_tips,
            pro_tip=default_pro_tip,
            is_ai_generated=False,
            notice=FALLBACK_NOTICE,
            disclaimer=(
                "These tips provide educational financial principles for Indian users. "
                "They do not constitute personalized financial advisory, tax advice, or loan approval guarantees."
            )
        )

    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

        prompt = (
            f"Generate educational, practical financial tips for an Indian borrower on the topic: '{req.topic}'.\n"
            f"User Context: {req.user_context or 'General Indian retail borrower / professional'}.\n\n"
            "Return ONLY a JSON object matching this structure:\n"
            "{\n"
            '  "overview": "2 sentences explaining why this topic matters for borrowing and financial health.",\n'
            '  "tips": [\n'
            '    {\n'
            '      "title": "Short actionable title",\n'
            '      "content": "Clear, practical advice in Indian context (INR, RBI norms, CIBIL, FOIR).",\n'
            '      "impact_level": "High" | "Medium" | "Fundamental",\n'
            '      "action_item": "Specific 1-sentence step the user can take today."\n'
            '    }\n'
            "  ],\n"
            '  "pro_tip": "One concise, powerful insider tip for Indian consumers."\n'
            "}"
        )

        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1000,
            system=AI_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_text += block.text

        cleaned = response_text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        data = json.loads(cleaned)

        raw_tips = data.get("tips", [])
        parsed_tips = [TipItem(**t) for t in raw_tips] if raw_tips else default_tips

        return FinancialTipsResponse(
            topic=req.topic,
            overview=data.get("overview", default_overview),
            tips=parsed_tips,
            pro_tip=data.get("pro_tip", default_pro_tip),
            is_ai_generated=True,
            notice=None,
            disclaimer=(
                "These tips provide educational financial principles for Indian users. "
                "They do not constitute personalized financial advisory, tax advice, or loan approval guarantees."
            )
        )

    except Exception as e:
        logger.warning(f"Claude tips generation failed: {str(e)}. Using curated tips.")
        return FinancialTipsResponse(
            topic=req.topic,
            overview=default_overview,
            tips=default_tips,
            pro_tip=default_pro_tip,
            is_ai_generated=False,
            notice=FALLBACK_NOTICE,
            disclaimer=(
                "These tips provide educational financial principles for Indian users. "
                "They do not constitute personalized financial advisory, tax advice, or loan approval guarantees."
            )
        )
