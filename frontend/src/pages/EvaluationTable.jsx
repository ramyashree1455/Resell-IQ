import React, { useState } from "react";

export default function EvaluationTable({ evaluations = [], onInspectItem, onStartNew }) {
  const [filter, setFilter] = useState("all");

  const totalCount = evaluations.length;
  const gradeACount = evaluations.filter((e) => e.grade === "A").length;
  const gradeBCount = evaluations.filter((e) => e.grade === "B").length;
  const reviewCount = evaluations.filter(
    (e) => e.status?.includes("Review") || e.status?.includes("Flagged") || e.status?.includes("Rejected")
  ).length;

  const filteredItems = evaluations.filter((item) => {
    if (filter === "gradeA") return item.grade === "A";
    if (filter === "gradeB") return item.grade === "B";
    if (filter === "review") return item.status?.includes("Review") || item.status?.includes("Flagged") || item.status?.includes("Rejected");
    return true;
  });

  return (
    <div style={{ width: "100%" }}>
      {/* Inspirante Header */}
      <div className="page-header">
        <h1 className="page-title">
          Audited Devices
        </h1>
        <p className="page-subtitle">
          View all audited devices and track their certification progress.
        </p>
      </div>

      {/* Inspirante 4 Stat Cards */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Total Audited</div>
            <div className="stat-card-number">{totalCount}</div>
          </div>
          <div className="stat-card-icon icon-blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Grade A Certified</div>
            <div className="stat-card-number">{gradeACount}</div>
          </div>
          <div className="stat-card-icon icon-green">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Under Review</div>
            <div className="stat-card-number">{reviewCount}</div>
          </div>
          <div className="stat-card-icon icon-orange">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Grade B / Active</div>
            <div className="stat-card-number">{gradeBCount}</div>
          </div>
          <div className="stat-card-icon icon-purple">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="card" style={{ marginTop: "24px" }}>
        {/* Inspirante Filter Section */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2 style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-main)", marginBottom: "2px" }}>
              Device Overview
            </h2>
          </div>

          <div className="filter-pills">
            <button
              className={`filter-pill ${filter === "all" ? "active" : ""}`}
              onClick={() => setFilter("all")}
            >
              All Devices {totalCount}
            </button>
            <button
              className={`filter-pill ${filter === "gradeA" ? "active" : ""}`}
              onClick={() => setFilter("gradeA")}
            >
              Grade A {gradeACount}
            </button>
            <button
              className={`filter-pill ${filter === "gradeB" ? "active" : ""}`}
              onClick={() => setFilter("gradeB")}
            >
              Grade B {gradeBCount}
            </button>
            <button
              className={`filter-pill ${filter === "review" ? "active" : ""}`}
              onClick={() => setFilter("review")}
            >
              Under Review {reviewCount}
            </button>
          </div>
        </div>

        {totalCount === 0 ? (
          <div style={{ textAlign: "center", padding: "48px 20px" }}>
            <div className="empty-state-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: "700", color: "var(--text-main)", marginBottom: "8px" }}>
              No Evaluations Recorded Yet
            </h3>
            <p style={{ fontSize: "14px", color: "var(--text-muted)", maxWidth: "480px", margin: "0 auto 20px auto", lineHeight: "1.5" }}>
              When you complete a device inspection, the certified grade, condition score, and defect summary will be automatically recorded here.
            </p>
            {onStartNew && (
              <button className="btn btn-primary" onClick={onStartNew} style={{ padding: "9px 22px", fontSize: "13px" }}>
                Start First Inspection →
              </button>
            )}
          </div>
        ) : filteredItems.length === 0 ? (
          <div style={{ textAlign: "center", padding: "36px 20px", color: "var(--text-muted)", fontSize: "14px" }}>
            No devices match the selected filter.
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Listing ID</th>
                  <th>Product Model</th>
                  <th>Category</th>
                  <th>Asking Price</th>
                  <th>Condition Grade</th>
                  <th>Score</th>
                  <th>Defects</th>
                  <th>Review Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: "600", color: "var(--text-muted)" }}>{item.id}</td>
                    <td style={{ fontWeight: "600" }}>{item.title}</td>
                    <td>
                      <span style={{ textTransform: "capitalize", fontSize: "12px" }}>
                        {item.category}
                      </span>
                    </td>
                    <td style={{ fontWeight: "600", color: "var(--success)" }}>
                      ₹{Number(item.askingPrice).toLocaleString("en-IN")}
                    </td>
                    <td>
                      <span
                        className={`cert-grade-badge-sm grade-${item.grade}`}
                      >
                        Grade {item.grade}
                      </span>
                    </td>
                    <td>{item.score}/100</td>
                    <td>
                      {item.defectsCount === 0 ? (
                        <span style={{ color: "var(--success)", fontWeight: "600" }}>0 defects</span>
                      ) : (
                        <span style={{ color: "var(--warning)", fontWeight: "600" }}>
                          {item.defectsCount} defect(s)
                        </span>
                      )}
                    </td>
                    <td>
                      <span
                        style={{
                          fontSize: "12px",
                          color: item.status?.includes("Rejected")
                            ? "var(--danger)"
                            : item.status?.includes("Flagged") || item.status?.includes("Review")
                            ? "var(--warning)"
                            : "var(--success)",
                          fontWeight: "600",
                        }}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: "4px 10px", fontSize: "12px" }}
                        onClick={() => onInspectItem(item)}
                      >
                        View Certificate →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
