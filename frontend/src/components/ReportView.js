import React from "react";

const RISK_ICONS = {
  critical: "🔴",
  high: "🟠",
  medium: "🟡",
  low: "🟢",
};

function ReportView({ report, onDownloadPDF, pdfAvailable, processingTime }) {
  if (!report) return null;

  const riskLevel = (report.overall_risk_level || "medium").toLowerCase();
  const riskIcon = RISK_ICONS[riskLevel] || "⚪";

  return (
    <div className="report-panel">
      <div className="panel-header">
        <h2>📋 AI Inspection Report</h2>
        {pdfAvailable && (
          <button className="btn btn-accent" onClick={onDownloadPDF}>
            📄 Download PDF
          </button>
        )}
      </div>

      <div className="report-body">
        <div className={`risk-banner risk-${riskLevel}`}>
          <span style={{ fontSize: "1.8rem" }}>{riskIcon}</span>
          <div>
            <div style={{ fontSize: "0.78rem", color: "#64748b" }}>
              Overall Risk Assessment
            </div>
            <div className="risk-label">{riskLevel} RISK</div>
          </div>
        </div>

        <div className="report-meta-bar">
          <div className="meta-item">
            <span className="meta-label">🧠 Model Used</span>
            <span className="meta-value">MobileNetV2 CNN classifier; findings summarized by Gemini 2.0 Flash LLM</span>
          </div>
          {processingTime != null && (
            <div className="meta-item">
              <span className="meta-label">⚡ Processing Time</span>
              <span className="meta-value">{processingTime}s</span>
            </div>
          )}
        </div>

        <div className="severity-legend">
          <span className="legend-title">Severity Legend:</span>
          <span className="severity-badge severity-low">Low</span> Cosmetic
          <span className="severity-badge severity-medium" style={{ marginLeft: 12 }}>Medium</span> Monitor
          <span className="severity-badge severity-high" style={{ marginLeft: 12 }}>High</span> Urgent
          <span className="severity-badge severity-critical" style={{ marginLeft: 12 }}>Critical</span> Immediate action
        </div>

        <div className="report-section">
          <h3>📝 Executive Summary</h3>
          <div className="summary-text">{report.summary}</div>
        </div>

        {report.findings && report.findings.length > 0 && (
          <div className="report-section">
            <h3>🔎 Detailed Findings</h3>
            <div style={{ overflowX: "auto" }}>
              <table className="findings-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Confidence</th>
                    <th>Explanation</th>
                    <th>Recommended Action</th>
                  </tr>
                </thead>
                <tbody>
                  {report.findings.map((f, idx) => (
                    <tr key={idx}>
                      <td>{f.id || idx + 1}</td>
                      <td style={{ textTransform: "capitalize", fontWeight: 600 }}>
                        {f.damage_type}
                      </td>
                      <td>
                        <span
                          className={`severity-badge severity-${(
                            f.severity || ""
                          ).toLowerCase()}`}
                        >
                          {f.severity}
                        </span>
                      </td>
                      <td>{Math.round((f.confidence || 0) * 100)}%</td>
                      <td>{f.explanation}</td>
                      <td>{f.recommended_action}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {report.checklist && report.checklist.length > 0 && (
          <div className="report-section">
            <h3>✅ Inspection Checklist</h3>
            {report.checklist.map((item, idx) => (
              <div key={idx} className="checklist-item">
                <div className="checklist-box" />
                <span>{item.item}</span>
              </div>
            ))}
          </div>
        )}

        {report.safety_notes && report.safety_notes.length > 0 && (
          <div className="report-section">
            <h3>⚠️ Safety Recommendations</h3>
            {report.safety_notes.map((note, idx) => (
              <div key={idx} className="safety-note">
                <span className="safety-icon">⚠️</span>
                <span>{note}</span>
              </div>
            ))}
          </div>
        )}

        <div className="ai-disclaimer">
          <span className="ai-disclaimer-icon">🤖</span>
          <div>
            <strong>Responsible AI Notice:</strong>{" "}
            {report.responsible_ai_note ||
              "This report is AI-generated to assist human inspectors. All findings should be validated by a qualified professional. AI assists — it does not replace — expert judgment."}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportView;
