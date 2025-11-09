import React, { Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { GameProvider } from "./contexts/GameContext";
import { AuthProvider } from "./contexts/AuthContext";

const Login = lazy(() => import("./pages/Login"));
const MapView = lazy(() => import("./pages/MapView"));
const Analyze = lazy(() => import("./pages/Analyze"));
const MissionDetail = lazy(() => import("./pages/MissionDetail"));
const Profile = lazy(() => import("./pages/Profile"));
const Leaderboard = lazy(() => import("./pages/Leaderboard"));
const AuthCallback = lazy(() => import("./pages/AuthCallback"));
const NotFound = lazy(() => import("./pages/NotFound"));

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <GameProvider>
        <BrowserRouter>
          <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading…</div>}>
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/auth/callback" element={<AuthCallback />} />
              <Route path="/map" element={<MapView />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/mission/:id" element={<MissionDetail />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </GameProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
