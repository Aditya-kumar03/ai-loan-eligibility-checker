/**
 * AI Loan Eligibility Checker - Centralized REST API Service
 */

const API = (() => {
  // Determine Base URL: If served from FastAPI on port 8000, use relative '/api'
  // If served from Live Server or static file, use 'http://127.0.0.1:8000/api'
  const isLocalOrigin = window.location.port === "8000";
  const BASE_URL = isLocalOrigin ? "/api" : "http://127.0.0.1:8000/api";

  async function request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const defaultHeaders = {
      "Content-Type": "application/json",
      "Accept": "application/json"
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, config);

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
      if (err.name === "TypeError" && err.message.includes("fetch")) {
        throw new Error("Unable to connect to financial server. Please ensure backend is running at http://127.0.0.1:8000.");
      }
      throw err;
    }
  }

  return {
    async checkHealth() {
      return await request("/health");
    },

    async analyzeLoan(payload) {
      return await request("/loan/analyze", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },

    async analyzeCredit(payload) {
      return await request("/credit/analyze", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },

    async calculateEMI(payload) {
      return await request("/emi/calculate", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },

    async getFinancialTips(topic, context = "") {
      return await request("/ai/financial-tips", {
        method: "POST",
        body: JSON.stringify({ topic, user_context: context })
      });
    },

    async submitFeedback(payload) {
      return await request("/feedback", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    }
  };
})();

window.API = API;
