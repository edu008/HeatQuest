import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

console.log("🔎 Step 3: AuthProvider wird initialisiert");

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div style={{ position: 'fixed', top: 16, left: 16, zIndex: 99999, background: 'rgba(0,150,255,0.95)', color: '#fff', padding: 12, borderRadius: 8, boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
          ✅ Step 3: AuthProvider aktiv
        </div>
      </AuthProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

console.log("✅ Step 3: AuthProvider mounted");

