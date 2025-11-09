import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { GameProvider } from "./contexts/GameContext";
import { AuthProvider, useAuth } from "./contexts/AuthContextMock";

import Login from "./pages/Login";
const MapView = React.lazy(() => import("./pages/MapView"));
const Analyze = React.lazy(() => import("./pages/Analyze"));
const MissionDetail = React.lazy(() => import("./pages/MissionDetail"));
const Profile = React.lazy(() => import("./pages/Profile"));
const Leaderboard = React.lazy(() => import("./pages/Leaderboard"));
const AuthCallback = React.lazy(() => import("./pages/AuthCallback"));
const NotFound = React.lazy(() => import("./pages/NotFound"));

import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }
  
  return user ? children : <Navigate to="/" replace />;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <GameProvider>
        <BrowserRouter>
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/auth/callback" element={<AuthCallback />} />
              <Route path="/map" element={<ProtectedRoute><MapView /></ProtectedRoute>} />
              <Route path="/analyze" element={<ProtectedRoute><Analyze /></ProtectedRoute>} />
              <Route path="/mission/:id" element={<ProtectedRoute><MissionDetail /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </React.Suspense>
        </BrowserRouter>
      </GameProvider>
    </AuthProvider>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

console.log("✅ Komplette App mit Mock Auth aktiviert");


