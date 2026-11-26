/**
 * ReSellIQ Lens Popup Controller
 * Connects to the local ReSellIQ FastAPI price intelligence backend (http://127.0.0.1:8000).
 */

const API_BASE = "http://127.0.0.1:8000";

// DOM Elements
const statusPill = document.getElementById("backend-status");
const statusText = document.getElementById("status-text");
const modelInput = document.getElementById("model-input");
const gradeSelect = document.getElementById("grade-select");
const priceInput = document.getElementById("price-input");
const evaluateBtn = document.getElementById("evaluate-btn");
const spinner = document.getElementById("loading-spinner");
const rescanBtn = document.getElementById("rescan-btn");
const detectedText = document.getElementById("detected-text");

const errorBox = document.getElementById("error-box");
const errorMessage = document.getElementById("error-message");
const resultsCard = document.getElementById("results-card");

const verdictBadge = document.getElementById("verdict-badge");
const meterPointer = document.getElementById("meter-pointer");
const statMedian = document.getElementById("stat-median");
const statRange = document.getElementById("stat-range");
const statDiff = document.getElementById("stat-diff");
const explanationText = document.getElementById("explanation-text");

let detectedMrp = 0;

// Initialize on popup load
document.addEventListener("DOMContentLoaded", async () => {
  await checkBackendStatus();
  await scanActiveTab();

  evaluateBtn.addEventListener("click", () => handleEvaluation());
  rescanBtn.addEventListener("click", () => scanActiveTab());

  // Bind quick preset chips
  document.querySelectorAll(".chip-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const model = btn.getAttribute("data-model");
      const price = btn.getAttribute("data-price");
      detectedMrp = 0;
      if (model) modelInput.value = model;
      if (price) priceInput.value = price;
      handleEvaluation();
    });
  });

  modelInput.addEventListener("input", () => {
    detectedMrp = 0;
  });

  // Allow pressing Enter in price input or model input to evaluate
  modelInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleEvaluation();
  });
  priceInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleEvaluation();
  });
});

/** Check if backend FastAPI server is running */
async function checkBackendStatus() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${API_BASE}/`, { method: "GET", signal: controller.signal });
    clearTimeout(timeoutId);

    if (res.ok) {
      statusPill.className = "status-pill status-online";
      statusText.textContent = "Online";
      return true;
    }
  } catch (_) {}

  statusPill.className = "status-pill status-offline";
  statusText.textContent = "Offline";
  return false;
}

/** Helper: parse any user input price string (removes commas, currency signs, spaces) */
function parsePrice(raw) {
  if (!raw) return 0;
  const cleaned = String(raw).replace(/[^0-9.]/g, "");
  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

/** Helper: apply extracted product info to the UI */
function applyExtractedProduct(data) {
  if (!data) return;
  if (data.title) {
    modelInput.value = data.title;
    detectedText.textContent = `Detected: "${data.title.substring(0, 28)}..."`;
  }
  if (data.price && data.price > 0) {
    priceInput.value = Math.round(data.price);
  }
  detectedMrp = data.mrp && data.mrp > 0 ? Math.round(data.mrp) : 0;
}

/** Extract product data from the current active tab (WITHOUT locking evaluate button) */
async function scanActiveTab() {
  detectedText.textContent = "Scanning active tab...";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) {
      detectedText.textContent = "Ready for price analysis.";
      return;
    }

    // Try communicating with content script
    chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_PRODUCT" }, async (response) => {
      if (chrome.runtime.lastError || !response) {
        // Inject script dynamically if missing
        try {
          if (chrome.scripting && chrome.scripting.executeScript) {
            await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: ["content.js"],
            });
            chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_PRODUCT" }, (res2) => {
              if (res2 && res2.title) {
                applyExtractedProduct(res2);
              } else {
                detectedText.textContent = "Page active. Click Evaluate Fair Price.";
              }
            });
            return;
          }
        } catch (_) {}
        detectedText.textContent = "Ready for price analysis.";
        return;
      }

      applyExtractedProduct(response);
    });
  } catch (err) {
    detectedText.textContent = "Ready for price analysis.";
  }
}

/** Submit price evaluation to backend */
async function handleEvaluation() {
  const modelKey = modelInput.value.trim();
  const grade = gradeSelect.value.trim();
  const askingPrice = parsePrice(priceInput.value);

  hideError();

  if (!modelKey) {
    showError("Please enter a product model.");
    return;
  }
  if (askingPrice <= 0) {
    showError("Please enter a valid asking price (e.g. 1299 or 38999).");
    return;
  }

  setLoading(true);

  try {
    const mrpParam = detectedMrp > 0 ? `&mrp=${detectedMrp}` : "";
    const url = `${API_BASE}/price/estimate?model_key=${encodeURIComponent(modelKey)}&grade=${encodeURIComponent(grade)}&asking_price=${askingPrice}&currency=INR${mrpParam}`;
    const response = await fetch(url);

    if (!response.ok) {
      let errMsg = `Server returned status ${response.status}`;
      try {
        const errData = await response.json();
        if (typeof errData.detail === "string") {
          errMsg = errData.detail;
        } else if (Array.isArray(errData.detail)) {
          errMsg = errData.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
        }
      } catch (_) {}
      throw new Error(errMsg);
    }

    const data = await response.json();
    displayResults(data);
  } catch (err) {
    showError(`Evaluation failed: ${err.message}. Ensure backend is running at http://127.0.0.1:8000.`);
  } finally {
    setLoading(false);
  }
}

/** Render API evaluation results onto the UI */
function displayResults(data) {
  resultsCard.classList.remove("hidden");

  // 1. Verdict Badge
  const verdict = data.verdict || "Fair";
  verdictBadge.textContent = verdict;
  verdictBadge.className = "verdict-badge";
  if (verdict === "Great deal") {
    verdictBadge.classList.add("badge-great");
  } else if (verdict === "Overpriced") {
    verdictBadge.classList.add("badge-over");
  } else {
    verdictBadge.classList.add("badge-fair");
  }

  // 2. Position Meter Pointer accurately based on verdict & percentage
  let pointerPos = 50;
  const pct = Number(data.percentage_vs_median) || 0;

  if (verdict === "Great deal") {
    // 10% to 30% range (Green zone)
    const ratio = Math.min(1.0, Math.abs(pct) / 40);
    pointerPos = Math.max(10, Math.round(30 - ratio * 18));
  } else if (verdict === "Overpriced") {
    // 70% to 92% range (Red zone)
    const ratio = Math.min(1.0, Math.abs(pct) / 40);
    pointerPos = Math.min(92, Math.round(70 + ratio * 20));
  } else {
    // 40% to 60% range (Blue zone)
    const offset = Math.max(-12, Math.min(12, pct * 0.8));
    pointerPos = Math.round(50 + offset);
  }
  meterPointer.style.left = `${pointerPos}%`;

  // 3. Stats in INR (₹)
  statMedian.textContent = `₹${Math.round(data.market_median).toLocaleString("en-IN")}`;
  statRange.textContent = `₹${Math.round(data.fair_range_min).toLocaleString("en-IN")} - ₹${Math.round(data.fair_range_max).toLocaleString("en-IN")}`;

  const diffSign = data.diff_from_median >= 0 ? "+" : "";
  statDiff.textContent = `${diffSign}₹${Math.round(data.diff_from_median).toLocaleString("en-IN")} (${data.percentage_vs_median}%)`;

  // 4. Explanation
  explanationText.textContent = data.explanation;

  // 5. Grade Benchmarks Table in INR (₹)
  if (data.grade_benchmarks && data.grade_benchmarks.length > 0) {
    for (const b of data.grade_benchmarks) {
      const el = document.getElementById(`bench-price-${b.grade}`);
      if (el) {
        el.textContent = `₹${Math.round(b.median_price).toLocaleString("en-IN")}`;
      }
    }
  }
}

function setLoading(isLoading) {
  if (isLoading) {
    spinner.classList.remove("hidden");
    evaluateBtn.disabled = true;
    // Safety auto-unlock after 3 seconds in case of network freeze
    setTimeout(() => {
      evaluateBtn.disabled = false;
      spinner.classList.add("hidden");
    }, 3000);
  } else {
    spinner.classList.add("hidden");
    evaluateBtn.disabled = false;
  }
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.classList.add("hidden");
}
