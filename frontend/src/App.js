import React, { useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import UploadSection from "./components/UploadSection";
import DetectionResults from "./components/DetectionResults";
import ReportView from "./components/ReportView";
import Footer from "./components/Footer";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [step, setStep] = useState("upload"); // upload | detecting | results
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = useCallback((file) => {
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setResults(null);
    setError(null);
    setStep("upload");
  }, []);

  const handleInspect = useCallback(async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);
    setStep("detecting");

    try {
      const formData = new FormData();
      formData.append("file", imageFile);

      const response = await axios.post(`${API_BASE}/api/inspect`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResults(response.data);
      setStep("results");
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          "Inspection failed. Please check the backend server."
      );
      setStep("upload");
    } finally {
      setLoading(false);
    }
  }, [imageFile]);

  const handleReset = useCallback(() => {
    setStep("upload");
    setImageFile(null);
    setImagePreview(null);
    setResults(null);
    setError(null);
  }, []);

  const handleDownloadPDF = useCallback(() => {
    if (results?.pdf_url) {
      window.open(`${API_BASE}${results.pdf_url}`, "_blank");
    }
  }, [results]);

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
            <button onClick={() => setError(null)} className="error-close">
              ×
            </button>
          </div>
        )}

        {step === "upload" && (
          <UploadSection
            imagePreview={imagePreview}
            onImageSelect={handleImageSelect}
            onInspect={handleInspect}
            hasImage={!!imageFile}
          />
        )}

        {step === "detecting" && (
          <div className="detecting-overlay">
            <div className="spinner" />
            <h2>Running AI Inspection…</h2>
            <p>Detecting damage &amp; generating report</p>
            <div className="pipeline-steps">
              <div className="pipeline-step active">
                <span className="step-num">1</span> Uploading Image
              </div>
              <div className="pipeline-step active">
                <span className="step-num">2</span> Detecting Damage
              </div>
              <div className="pipeline-step">
                <span className="step-num">3</span> AI Analysis
              </div>
              <div className="pipeline-step">
                <span className="step-num">4</span> Generating PDF
              </div>
            </div>
          </div>
        )}

        {step === "results" && results && (
          <div className="results-container">
            {results.classification && (
              <div className={`classification-banner ${results.classification.is_cracked ? "cracked" : "uncracked"}`}>
                <span className="classification-icon">
                  {results.classification.is_cracked ? "⚠️" : "✅"}
                </span>
                <div className="classification-info">
                  <h3>
                    AI Classification:{" "}
                    {results.classification.is_cracked ? "DAMAGE DETECTED" : "NO DAMAGE DETECTED"}
                  </h3>
                  <p>
                    Confidence: {Math.round(results.classification.confidence * 100)}%
                    {results.classification.probabilities && (
                      <span className="prob-detail">
                        {" "}— Cracked: {Math.round((results.classification.probabilities.cracked || 0) * 100)}%
                        {" "}| Uncracked: {Math.round((results.classification.probabilities.uncracked || 0) * 100)}%
                      </span>
                    )}
                  </p>
                </div>
              </div>
            )}

            <DetectionResults
              imageUrl={`${API_BASE}${results.image_url}`}
              detections={results.detections}
              imageSize={results.image_size}
            />
            <ReportView
              report={results.report}
              onDownloadPDF={handleDownloadPDF}
              pdfAvailable={!!results.pdf_url}
              processingTime={results.processing_time_seconds}
            />
            <div className="action-bar">
              <button className="btn btn-secondary" onClick={handleReset}>
                ← New Inspection
              </button>
              {results.pdf_url && (
                <button className="btn btn-primary" onClick={handleDownloadPDF}>
                  📄 Download PDF Report
                </button>
              )}
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
