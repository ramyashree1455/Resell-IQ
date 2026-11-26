import React from "react";

export default function ConditionReportViewer({ report, onStartNew, onCheckFairPrice }) {
  const data = report
    ? {
        title: report.title || "Custom Device",
        category: report.category || "electronics",
        price: Number(report.askingPrice) || 0,
        score: report.score !== undefined ? report.score : 80,
        grade: report.grade || "B",
        confidence: report.confidence || 0.9,
        needs_manual_review: report.needs_manual_review || false,
        defects: report.defects || [],
        contradictions: report.contradictions || [],
        componentHealth: report.componentHealth || [],
        isLive: true,
      }
    : null;

  return (
    <div style={{ width: "100%" }}>
      {/* Inspirante Header */}
      <div className="page-header">
        <h1 className="page-title">Verified Condition Certificate</h1>
        <p className="page-subtitle">
          AI-verified grading report, hardware diagnostic audit, and tamper-resistant resale credentials.
        </p>
      </div>

      {/* Inspirante 4 Stat Cards */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Audit Standard</div>
            <div className="stat-card-number" style={{ fontSize: "19px" }}>Multi-Point CV</div>
          </div>
          <div className="stat-card-icon icon-blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Verification Status</div>
            <div className="stat-card-number" style={{ fontSize: "19px" }}>
              {data ? (data.grade === "REJECTED" ? "Rejected" : "Verified") : "Ready"}
            </div>
          </div>
          <div className="stat-card-icon icon-green">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Hardware Score</div>
            <div className="stat-card-number" style={{ fontSize: "19px" }}>
              {data ? `${data.score}/100` : "Awaiting Audit"}
            </div>
          </div>
          <div className="stat-card-icon icon-orange">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
              <rect x="9" y="9" width="6" height="6"></rect>
              <line x1="9" y1="1" x2="9" y2="4"></line>
              <line x1="15" y1="1" x2="15" y2="4"></line>
              <line x1="9" y1="20" x2="9" y2="23"></line>
              <line x1="15" y1="20" x2="15" y2="23"></line>
              <line x1="20" y1="9" x2="23" y2="9"></line>
              <line x1="20" y1="14" x2="23" y2="14"></line>
              <line x1="1" y1="9" x2="4" y2="9"></line>
              <line x1="1" y1="14" x2="4" y2="14"></line>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Pricing Standard</div>
            <div className="stat-card-number" style={{ fontSize: "19px" }}>INR (₹)</div>
          </div>
          <div className="stat-card-icon icon-purple">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
        </div>
      </div>

      {/* If no inspection has been performed yet */}
      {!data ? (
        <div className="card" style={{ textAlign: "center", padding: "56px 24px" }}>
          <div className="empty-state-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <h2 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "8px", color: "var(--text-main)" }}>
            No Device Inspected Yet
          </h2>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", maxWidth: "520px", margin: "0 auto 24px auto", lineHeight: "1.6" }}>
            The Verified Condition Certificate is generated live from real photo inspection and seller diagnostic responses.
            Please start a new inspection to audit your device and produce an official certificate.
          </p>
          {onStartNew && (
            <button className="btn btn-primary" onClick={onStartNew} style={{ padding: "10px 24px", fontSize: "14px" }}>
              Start Seller Inspection →
            </button>
          )}
        </div>
      ) : data.grade === "REJECTED" ? (
        /* REJECTED NON-DEVICE STATE */
        <div className="card" style={{ border: "2px solid var(--danger)", textAlign: "center", padding: "36px 20px" }}>
          <div style={{ fontSize: "52px", marginBottom: "12px" }}>⛔</div>
          <h2 style={{ color: "var(--danger)", fontSize: "22px", marginBottom: "10px", fontWeight: "700" }}>
            CERTIFICATION REJECTED: Non-Device Visuals Detected
          </h2>
          <p style={{ fontSize: "14px", lineHeight: "1.6", maxWidth: "620px", margin: "0 auto 24px auto", color: "var(--text-muted)" }}>
            ReSellIQ AI inspected the uploaded photo evidence for <strong>{data.title}</strong> and detected non-device visuals (such as wildlife, artwork, landscape, or documents).
            Condition certification and fair price guarantees are exclusively issued for authentic physical electronic devices.
          </p>
          {onStartNew && (
            <button className="btn btn-primary" onClick={onStartNew}>
              Retake Inspection with Valid Device Photos →
            </button>
          )}
        </div>
      ) : (
        /* VALID CERTIFICATE */
        <div className="card">
          <div className="inspirante-success-banner">
            <span className="success-banner-check">✓</span>
            <span>Device inspected and verified condition certificate generated successfully.</span>
          </div>

          <div className="cert-header">
            <div>
              <span className="brand-badge" style={{ marginBottom: "8px", display: "inline-block" }}>
                ReSellIQ Verified Product Certificate
              </span>
              <h1 style={{ fontSize: "24px", fontWeight: "700", color: "var(--text-main)" }}>{data.title}</h1>
              <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                Inspection ID: #RSIQ-{Math.floor(1000 + (data.price % 9000))} • Verified by ReSellIQ Computer Vision & Diagnostic Audit
              </p>
            </div>
            <div className={`cert-grade-badge grade-${data.grade}`}>
              {data.grade}
            </div>
          </div>

          {/* Metrics Row */}
          <div className="metrics-row">
            <div className="metric-box">
              <div className="metric-label">Quality Score</div>
              <div className="metric-value" style={{ color: "var(--primary)" }}>{data.score} / 100</div>
            </div>
            <div className="metric-box">
              <div className="metric-label">Audit Confidence</div>
              <div className="metric-value">{(data.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className="metric-box">
              <div className="metric-label">Market Asking Price</div>
              <div className="metric-value" style={{ color: "var(--success)" }}>
                ₹{Number(data.price).toLocaleString("en-IN")}
              </div>
            </div>
          </div>

          {/* Contradictions Alert if flagged */}
          {data.contradictions && data.contradictions.length > 0 && (
            <div className="alert alert-warning" style={{ marginBottom: "20px" }}>
              <div>
                <strong>Discrepancies Flagged:</strong>
                <ul style={{ margin: "6px 0 0 18px", fontSize: "13px" }}>
                  {data.contradictions.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Component Diagnostics */}
          <div style={{ marginBottom: "24px" }}>
            <h3 style={{ fontSize: "15px", fontWeight: "700", marginBottom: "12px", color: "var(--text-main)" }}>
              Component Health & Diagnostics
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              {data.componentHealth.map((f, i) => (
                <div
                  key={i}
                  style={{
                    backgroundColor: "var(--bg-subtle)",
                    border: "1px solid var(--border)",
                    padding: "12px",
                    borderRadius: "var(--radius)",
                  }}
                >
                  <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>
                    {f.name}
                  </div>
                  <div style={{ fontSize: "13px", fontWeight: "600", color: f.status.includes("Defect") ? "var(--danger)" : "var(--success)" }}>
                    {f.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Physical Defects */}
          <div style={{ marginBottom: "24px" }}>
            <h3 style={{ fontSize: "15px", fontWeight: "700", marginBottom: "12px", color: "var(--text-main)" }}>
              Physical Evidence & Defect Detection
            </h3>
            {data.defects.length === 0 ? (
              <div className="alert alert-success">
                ✓ No visible defects detected.
              </div>
            ) : (
              <div>
                {data.defects.map((d, i) => (
                  <div
                    key={i}
                    style={{
                      backgroundColor: "var(--warning-light)",
                      color: "var(--warning-text)",
                      border: "1px solid #fde68a",
                      padding: "10px 14px",
                      borderRadius: "var(--radius)",
                      marginBottom: "8px",
                      fontSize: "13px",
                    }}
                  >
                    🔍 <strong>{d.type?.toUpperCase()} ({d.severity}):</strong> {d.description}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions & Print */}
          <div style={{ borderTop: "1px solid var(--border)", paddingTop: "16px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Digitally certified & backed by multi-point photo audit trail.
            </span>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {onStartNew && (
                <button className="btn btn-secondary" onClick={onStartNew}>New Inspection</button>
              )}
              {onCheckFairPrice && data.price > 0 && (
                <button
                  className="btn btn-secondary"
                  onClick={() =>
                    onCheckFairPrice({
                      model: data.title,
                      grade: ["A", "B", "C", "D"].includes(data.grade) ? data.grade : "B",
                      askingPrice: String(data.price),
                    })
                  }
                >
                  Check Fair Price (₹) →
                </button>
              )}
              <button className="btn btn-primary" onClick={() => window.print()}>Print Certificate 🖨️</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
