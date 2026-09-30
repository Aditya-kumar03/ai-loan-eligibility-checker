/**
 * AI Loan Eligibility Checker - Main Application Coordinator & Router
 */

const App = (() => {
  let currentView = "home";

  function init() {
    setupNavigation();
    setupMobileMenu();
    setupToasts();

    // Initialize sub-controllers
    if (window.LoanController) LoanController.init();
    if (window.CreditController) CreditController.init();
    if (window.EMIController) EMIController.init();
    if (window.TipsController) TipsController.init();

    // Check backend health
    checkBackendHealth();

    // Listen to hash changes for deep linking
    window.addEventListener("hashchange", handleHashChange);
    if (window.location.hash) {
      handleHashChange();
    } else {
      switchView("home");
    }
  }

  function setupNavigation() {
    document.querySelectorAll("[data-nav]").forEach(el => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        const targetView = el.dataset.nav;
        navigateTo(targetView);
      });
    });
  }

  function setupMobileMenu() {
    const hamburger = document.getElementById("hamburger-btn");
    const drawer = document.getElementById("mobile-drawer");

    if (hamburger && drawer) {
      hamburger.addEventListener("click", () => {
        drawer.classList.toggle("open");
      });

      drawer.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
          drawer.classList.remove("open");
        });
      });
    }
  }

  function handleHashChange() {
    const hash = window.location.hash.replace("#", "").trim();
    if (["home", "loan", "credit", "emi", "tips", "about", "privacy"].includes(hash)) {
      switchView(hash);
    }
  }

  function navigateTo(viewName) {
    window.location.hash = viewName;
    switchView(viewName);
  }

  function switchView(viewName) {
    currentView = viewName;

    // Hide all views
    document.querySelectorAll(".page-view").forEach(view => {
      view.classList.remove("active");
    });

    // Show target view
    const targetEl = document.getElementById(`view-${viewName}`);
    if (targetEl) {
      targetEl.classList.add("active");
    }

    // Update nav links
    document.querySelectorAll(".nav-link").forEach(link => {
      if (link.dataset.nav === viewName) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function checkBackendHealth() {
    try {
      const data = await API.checkHealth();
      const statusPill = document.getElementById("system-status-indicator");
      if (statusPill) {
        const aiMode = data.integrations?.claude_ai?.mode || "Rule-Engine";
        statusPill.textContent = `Backend Connected • ${aiMode}`;
      }
    } catch (err) {
      const statusPill = document.getElementById("system-status-indicator");
      if (statusPill) {
        statusPill.textContent = "Offline Mode (Local Math)";
        statusPill.style.color = "var(--warning)";
      }
    }
  }

  /* Toast Notification System */
  function setupToasts() {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }
  }

  function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "ℹ️";
    if (type === "success") icon = "✓";
    if (type === "warning") icon = "⚠️";
    if (type === "danger") icon = "✕";

    toast.innerHTML = `<span>${icon}</span><span>${escapeHTML(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  /* Global Loading Overlay */
  function showLoading(message = "Processing financial data...") {
    let overlay = document.getElementById("global-loading-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "global-loading-overlay";
      overlay.className = "loading-overlay";
      overlay.innerHTML = `
        <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;"></span>
        <div class="loading-text" id="global-loading-text">${escapeHTML(message)}</div>
      `;
      document.body.appendChild(overlay);
    } else {
      const textEl = document.getElementById("global-loading-text");
      if (textEl) textEl.textContent = message;
    }
    overlay.classList.add("active");
  }

  function hideLoading() {
    const overlay = document.getElementById("global-loading-overlay");
    if (overlay) overlay.classList.remove("active");
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
    navigateTo,
    showToast,
    showLoading,
    hideLoading
  };
})();

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});

window.App = App;
