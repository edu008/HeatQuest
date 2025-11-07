import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { GameProvider } from "./contexts/GameContext";
import Login from "./pages/Login";
import MapView from "./pages/MapView";
import Analyze from "./pages/Analyze";
import MissionDetail from "./pages/MissionDetail";
import Profile from "./pages/Profile";
import Leaderboard from "./pages/Leaderboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <GameProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/mission/:id" element={<MissionDetail />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </GameProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
