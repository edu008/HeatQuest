import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

console.log("🔎 Step 4: BrowserRouter + Routes wird geladen (OHNE Auth)");

const queryClient = new QueryClient();

const TestPage = () => (
  <div style={{ padding: 20, fontFamily: 'system-ui' }}>
    <h1>🎉 Router funktioniert!</h1>
    <p>QueryClient + BrowserRouter sind aktiv</p>
  </div>
);

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <div style={{ position: 'fixed', top: 12, left: 12, zIndex: 99999, background: 'rgba(255,255,0,0.95)', color: '#000', padding: 10, borderRadius: 8 }}>
        Frame OK: QueryClient+Router gerendert
      </div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<TestPage />} />
          <Route path="*" element={<TestPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </ErrorBoundary>
);

console.log("✅ Step 4: Router mounted");


