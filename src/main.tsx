import React, { Component, Suspense } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

class ErrorBoundary extends Component<{ children: React.ReactNode }, { error: any | null }> {
  constructor(props: any) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { error };
  }
  componentDidCatch(error: any, info: any) {
    console.error("Root ErrorBoundary caught:", error, info);
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 16 }}>
          <h1>App crashed</h1>
          <pre style={{ whiteSpace: "pre-wrap" }}>{String(this.state.error)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

console.log("🔸 Booting React app...");
createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <Suspense fallback={<div style={{ padding: 16 }}>Loading App…</div>}>
      <App />
    </Suspense>
  </ErrorBoundary>
);
