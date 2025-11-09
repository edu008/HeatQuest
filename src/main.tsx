import React from "react";
import { createRoot } from "react-dom/client";
// import App from "./App.tsx";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

console.log("🔎 main.tsx loaded");

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <div style={{ position: 'fixed', top: 16, left: 16, zIndex: 99999, background: 'rgba(255,255,0,0.95)', color: '#000', padding: 12, borderRadius: 8, boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
      Step 1: main.tsx mounted
    </div>
  </ErrorBoundary>
);

console.log("✅ Step 1: main.tsx mounted");

