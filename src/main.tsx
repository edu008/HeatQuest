import React, { Suspense } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// Lazy load AuthProvider to avoid hard crashes on import
const LazyAuthProvider = React.lazy(() => import("./contexts/AuthContext").then(m => ({ default: m.AuthProvider })));
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

console.log("🔎 Step 3 (lazy): AuthProvider wird geladen");

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <div style={{ position: 'fixed', top: 16, left: 16, zIndex: 99999, background: 'rgba(0,255,0,0.95)', color: '#000', padding: 12, borderRadius: 8, boxShadow: '0 4px 20px rgba(0,0,0,0.2)', marginBottom: 8 }}>
        ✅ Step 2: QueryClient aktiv
      </div>
      <Suspense fallback={<div style={{ position: 'fixed', top: 56, left: 16, zIndex: 99999, background: 'rgba(255,165,0,0.95)', color: '#000', padding: 12, borderRadius: 8, boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>⏳ Step 3: Lade AuthProvider…</div>}>
        <LazyAuthProvider>
          <div style={{ position: 'fixed', top: 56, left: 16, zIndex: 99999, background: 'rgba(0,150,255,0.95)', color: '#fff', padding: 12, borderRadius: 8, boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
            ✅ Step 3: AuthProvider aktiv
          </div>
        </LazyAuthProvider>
      </Suspense>
    </QueryClientProvider>
  </ErrorBoundary>
);


