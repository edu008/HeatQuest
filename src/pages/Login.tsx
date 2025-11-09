import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { Flame, User } from "lucide-react";

const Login = () => {
  const [username, setUsername] = useState("");
  const { login, user } = useGame();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate("/map", { replace: true });
    }
  }, [user, navigate]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim()) {
      login(username.trim());
      navigate("/map");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-heat-intense via-primary to-secondary">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-card/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 space-y-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="flex justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-heat to-cool-intense rounded-full blur-xl opacity-50 animate-pulse" />
              <div className="relative bg-gradient-to-br from-heat to-primary rounded-full p-6">
                <Flame className="w-12 h-12 text-white" />
              </div>
            </div>
          </motion.div>

          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-muted-foreground">
              Turning Hot Spots into Cool Spots 🌍
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="relative">
              <User className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Dein Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
              />
            </div>

            <Button
              type="submit"
              className="w-full h-12 rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat"
            >
              Los geht's! 🔥
            </Button>
          </form>

          <div className="text-center text-sm text-muted-foreground space-y-2">
            <p>🗺️ Entdecke Hitze-Hotspots</p>
            <p>🔥 Analysiere mit KI</p>
            <p>✅ Starte Klima-Missionen</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
