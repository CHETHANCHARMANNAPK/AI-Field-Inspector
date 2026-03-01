import React from "react";

function Header() {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="header-logo">🔍</div>
        <div>
          <div className="header-title">AI Field Inspector</div>
          <div className="header-subtitle">
            Vision + LLM for Infrastructure Damage Detection
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
