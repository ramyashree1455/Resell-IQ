import React, { useState, useEffect } from "react";
import Interview from "./pages/Interview";
import ConditionReportViewer from "./pages/ConditionReport";
import PriceLens from "./pages/PriceLens";
import EvaluationTable from "./pages/EvaluationTable";
import "./styles.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("interview");
  const [latestReport, setLatestReport] = useState(null);
  const [priceLensInitial, setPriceLensInitial] = useState(null);
  
  // Real evaluations: persisted in localStorage, starts empty until an inspection is actually completed
  const [evaluations, setEvaluations] = useState(() => {
    try {
      const saved = localStorage.getItem("reselliq_evaluations");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("reselliq_evaluations", JSON.stringify(evaluations));
    } catch (e) {
      console.warn("Failed to persist evaluations:", e);
    }
  }, [evaluations]);

  // Theme management: persisted in localStorage, defaults to light
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("reselliq_theme") || "light";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("reselliq_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleReportGenerated = (reportData) => {
    setLatestReport(reportData);
    // Add real evaluated device to history list
    if (reportData && reportData.title) {
      const newEntry = {
        id: `RSIQ-${Math.floor(1000 + Math.random() * 9000)}`,
        title: reportData.title,
        category: reportData.category || "electronics",
        askingPrice: Number(reportData.askingPrice) || 0,
        grade: reportData.grade || "B",
        score: reportData.score || 80,
        confidence: reportData.confidence || 0.90,
        defectsCount: (reportData.defects || []).length,
        status: reportData.grade === "REJECTED" ? "Rejected (Non-Device)" : reportData.needs_manual_review ? "Flagged for Review" : "Verified & Active",
        date: new Date().toISOString().split("T")[0],
        fullReport: reportData,
      };
      setEvaluations((prev) => [newEntry, ...prev]);
    }
    // Flow: automatically transition to Condition Certificate for this device
    setActiveTab("report");
  };

  return (
    <div className="app-container">
      {/* Inspirante-Style Professional Navbar */}
      <nav className="navbar">
        <div className="nav-brand">
          <span className="brand-title">ReSellIQ</span>
          <span className="brand-badge">Verification Platform</span>
        </div>

        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === "interview" ? "active" : ""}`}
            onClick={() => setActiveTab("interview")}
          >
            Seller Inspection
          </button>
          <button
            className={`nav-tab ${activeTab === "report" ? "active" : ""}`}
            onClick={() => setActiveTab("report")}
          >
            Condition Certificate
          </button>
          <button
            className={`nav-tab ${activeTab === "lens" ? "active" : ""}`}
            onClick={() => setActiveTab("lens")}
          >
            Fair Price Meter (₹)
          </button>
          <button
            className={`nav-tab ${activeTab === "table" ? "active" : ""}`}
            onClick={() => setActiveTab("table")}
          >
            Audit History
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === "light" ? "Dark Mode" : "Light Mode"}
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {activeTab === "interview" && (
          <Interview
            onReportGenerated={handleReportGenerated}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        )}
        {activeTab === "report" && (
          <ConditionReportViewer
            report={latestReport}
            onStartNew={() => setActiveTab("interview")}
            onCheckFairPrice={(payload) => {
              setPriceLensInitial({ ...payload, _ts: Date.now() });
              setActiveTab("lens");
            }}
          />
        )}
        {activeTab === "lens" && <PriceLens initialQuery={priceLensInitial} />}
        {activeTab === "table" && (
          <EvaluationTable
            evaluations={evaluations}
            onInspectItem={(item) => {
              setLatestReport(item.fullReport || {
                title: item.title,
                category: item.category,
                askingPrice: item.askingPrice,
                grade: item.grade,
                score: item.score,
                confidence: item.confidence,
                needs_manual_review: item.status.includes("Review"),
                defects: [],
              });
              setActiveTab("report");
            }}
            onStartNew={() => setActiveTab("interview")}
          />
        )}
      </main>
    </div>
  );
}
