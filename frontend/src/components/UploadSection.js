import React, { useRef, useState, useCallback } from "react";

function UploadSection({ imagePreview, onImageSelect, onInspect, hasImage }) {
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onImageSelect(file);
  };

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file && file.type.startsWith("image/")) {
        onImageSelect(file);
      }
    },
    [onImageSelect]
  );

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleLoadDemo = useCallback(async () => {
    setLoadingDemo(true);
    try {
      const res = await fetch("/sample_crack.jpg");
      const blob = await res.blob();
      const file = new File([blob], "sample_crack.jpg", { type: "image/jpeg" });
      onImageSelect(file);
    } catch (err) {
      console.error("Failed to load demo image:", err);
    } finally {
      setLoadingDemo(false);
    }
  }, [onImageSelect]);

  return (
    <div className="upload-section">
      <div className="upload-hero">
        <h1>Infrastructure Damage Detection</h1>
        <p>
          Upload a site or drone photo. Our AI will detect damage, assess
          severity, and generate a professional inspection report — in seconds.
        </p>
        <p className="domain-tagline">
          Optimized for bridge decks, walls, pavements &amp; industrial sites.
        </p>
      </div>

      {!imagePreview ? (
        <>
          <div
            className={`dropzone ${dragOver ? "drag-over" : ""}`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="dropzone-icon">📸</div>
            <h3>Drop an inspection image here</h3>
            <p>or click to browse — supports JPG, PNG, WEBP (max 10 MB)</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
          </div>
          <button
            className="btn btn-demo"
            onClick={handleLoadDemo}
            disabled={loadingDemo}
          >
            {loadingDemo ? "Loading\u2026" : "\ud83e\uddea Try with sample crack image"}
          </button>
        </>
      ) : (
        <div className="image-preview-container">
          <img src={imagePreview} alt="Preview" className="image-preview" />
          <div className="preview-actions">
            <button
              className="btn btn-secondary"
              onClick={() => fileInputRef.current?.click()}
            >
              🔄 Change Image
            </button>
            <button
              className="btn btn-primary btn-large"
              onClick={onInspect}
              disabled={!hasImage}
            >
              🚀 Run AI Inspection
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
        </div>
      )}

      <div className="micro-flow">
        <div className="micro-flow-title">How it works</div>
        <div className="micro-flow-steps">
          <div className="micro-step">
            <span className="micro-num">1</span>
            <span>Image analyzed with vision model</span>
          </div>
          <div className="micro-arrow">→</div>
          <div className="micro-step">
            <span className="micro-num">2</span>
            <span>Damage severity assessed</span>
          </div>
          <div className="micro-arrow">→</div>
          <div className="micro-step">
            <span className="micro-num">3</span>
            <span>Inspection report generated</span>
          </div>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h4>Damage Detection</h4>
          <p>Cracks, corrosion, leaks & misalignment</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🧠</div>
          <h4>AI Analysis</h4>
          <p>LLM-powered severity & recommendations</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📄</div>
          <h4>Instant Report</h4>
          <p>Professional PDF generated in seconds</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🛡️</div>
          <h4>Responsible AI</h4>
          <p>AI assists — never replaces — inspectors</p>
        </div>
      </div>
    </div>
  );
}

export default UploadSection;
