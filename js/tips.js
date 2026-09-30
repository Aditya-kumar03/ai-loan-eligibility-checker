/**
 * AI Loan Eligibility Checker - AI Financial Tips Controller
 */

const TipsController = (() => {
  let selectedTopic = "Credit Score";

  function init() {
    const pills = document.querySelectorAll(".topic-pill");
    const generateBtn = document.getElementById("btn-generate-tips");

    pills.forEach(pill => {
      pill.addEventListener("click", () => {
        pills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        selectedTopic = pill.dataset.topic;
        fetchTips();
      });
    });

    if (generateBtn) {
      generateBtn.addEventListener("click", () => fetchTips());
    }

    // Initial load
    fetchTips();
  }

  async function fetchTips() {
    const context = document.getElementById("tips-context-input")?.value?.trim() || "";
    const container = document.getElementById("tips-cards-container");
    const overviewEl = document.getElementById("tips-overview-text");
    const proTipEl = document.getElementById("tips-pro-tip-text");
    const noticeEl = document.getElementById("tips-ai-notice");

    if (!container) return;

    try {
      container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-secondary);"><span class="spinner"></span> Preparing financial guidance...</div>`;

      const res = await API.getFinancialTips(selectedTopic, context);

      if (overviewEl) overviewEl.textContent = res.overview;
      if (proTipEl) proTipEl.textContent = res.pro_tip;

      if (noticeEl) {
        if (res.notice) {
          noticeEl.style.display = "block";
          noticeEl.textContent = res.notice;
        } else {
          noticeEl.style.display = "none";
        }
      }

      container.innerHTML = "";
      res.tips.forEach(tip => {
        const card = document.createElement("div");
        card.className = "tip-card";

        const impactClass = (tip.impact_level || "Medium").toLowerCase();

        card.innerHTML = `
          <div class="tip-impact-badge ${impactClass}">${escapeHTML(tip.impact_level || 'General')} Impact</div>
          <div class="tip-title">${escapeHTML(tip.title)}</div>
          <div class="tip-content">${escapeHTML(tip.content)}</div>
          <div class="tip-action-box"><strong>Action:</strong> ${escapeHTML(tip.action_item)}</div>
        `;
        container.appendChild(card);
      });

    } catch (err) {
      container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--danger);">${escapeHTML(err.message)}</div>`;
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
    init,
    fetchTips
  };
})();

window.TipsController = TipsController;
