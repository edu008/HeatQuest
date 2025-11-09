import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContextMock";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

console.log("🔎 Step 5: Mit Mock AuthProvider");

const queryClient = new QueryClient();

const TestPage = () => (
  <div style={{ padding: 20, fontFamily: 'system-ui' }}>
    <h1>✅ Mock Auth + Router aktiv!</h1>
    <p>QueryClient + Mock AuthProvider + BrowserRouter sind online</p>
  </div>
);

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<TestPage />} />
            <Route path="*" element={<TestPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

console.log("✅ Step 5: Mock Auth mounted");


