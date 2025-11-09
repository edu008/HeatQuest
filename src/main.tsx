import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { GameProvider, useGame } from "./contexts/GameContext";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";
console.log("[BOOT] main.tsx loaded");

// Pages
import Login from "./pages/Login";
import MapView from "./pages/MapView";
import Analyze from "./pages/Analyze";
import MissionDetail from "./pages/MissionDetail";
import Profile from "./pages/Profile";
import Leaderboard from "./pages/Leaderboard";

// Protected Route
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useGame();
  return user ? <>{children}</> : <Navigate to="/" replace />;
};

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <GameProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/map" element={<ProtectedRoute><MapView /></ProtectedRoute>} />
            <Route path="/analyze" element={<ProtectedRoute><Analyze /></ProtectedRoute>} />
            <Route path="/mission/:id" element={<ProtectedRoute><MissionDetail /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </GameProvider>
    </ErrorBoundary>
  </StrictMode>
);
