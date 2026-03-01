import React, { useRef, useEffect, useState } from "react";

const DAMAGE_COLORS = {
  crack: "#ef4444",
  corrosion: "#f59e0b",
  leak: "#3b82f6",
  misalignment: "#a855f7",
};

const DAMAGE_ICONS = {
  crack: "🔨",
  corrosion: "🧪",
  leak: "💧",
  misalignment: "📐",
};

function DetectionResults({ imageUrl, detections, imageSize }) {
  const imageRef = useRef(null);
  const [imgDims, setImgDims] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDims = () => {
      if (imageRef.current) {
        setImgDims({
          width: imageRef.current.clientWidth,
          height: imageRef.current.clientHeight,
        });
      }
    };
    const img = imageRef.current;
    if (img) {
      img.addEventListener("load", updateDims);
      window.addEventListener("resize", updateDims);
    }
    return () => {
      if (img) img.removeEventListener("load", updateDims);
      window.removeEventListener("resize", updateDims);
    };
  }, [imageUrl]);

  const scaleX = imgDims.width / (imageSize?.[0] || 1);
  const scaleY = imgDims.height / (imageSize?.[1] || 1);

  return (
    <div className="detection-panel">
      <div className="panel-header">
        <h2>
          🔍 Damage Detection Results
          <span className="detection-count">
            {detections.length} issue{detections.length !== 1 ? "s" : ""} found
          </span>
        </h2>
      </div>

      <div className="detection-body">
        <div className="detection-image-wrapper">
          <img
            ref={imageRef}
            src={imageUrl}
            alt="Inspected"
            className="detection-image"
            onLoad={() => {
              if (imageRef.current) {
                setImgDims({
                  width: imageRef.current.clientWidth,
                  height: imageRef.current.clientHeight,
                });
              }
            }}
          />
          {imgDims.width > 0 && (
            <div className="bbox-overlay">
              {detections.map((d, idx) => {
                const color = DAMAGE_COLORS[d.type] || "#888";
                const bbox = d.bbox;
                return (
                  <div
                    key={idx}
                    className="bbox"
                    style={{
                      left: `${bbox.x * scaleX}px`,
                      top: `${bbox.y * scaleY}px`,
                      width: `${bbox.width * scaleX}px`,
                      height: `${bbox.height * scaleY}px`,
                      borderColor: color,
                    }}
                  >
                    <span
                      className="bbox-label"
                      style={{ backgroundColor: color }}
                    >
                      {d.type} {Math.round(d.confidence * 100)}%
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="detection-list">
          {detections.map((d, idx) => {
            const color = DAMAGE_COLORS[d.type] || "#888";
            const icon = DAMAGE_ICONS[d.type] || "⚠️";
            return (
              <div key={idx} className="detection-item">
                <div
                  className="detection-type-icon"
                  style={{ background: `${color}15`, color }}
                >
                  {icon}
                </div>
                <div className="detection-info">
                  <h4 style={{ color }}>{d.type}</h4>
                  <p>{d.description}</p>
                  <span className={`severity-badge severity-${d.severity}`}>
                    {d.severity}
                  </span>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${d.confidence * 100}%`,
                        background: color,
                      }}
                    />
                  </div>
                  <p style={{ fontSize: "0.72rem", marginTop: 2 }}>
                    Confidence: {Math.round(d.confidence * 100)}%
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default DetectionResults;
