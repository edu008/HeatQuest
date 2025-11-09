import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { useAuth } from "@/contexts/AuthContext";
import { Flame, Mail, Lock, User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Login = () => {
  // Schneller Login (ohne Registrierung)
  const [username, setUsername] = useState("");
  
  // Echter Login mit Supabase
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [registerUsername, setRegisterUsername] = useState("");
  const [loading, setLoading] = useState(false);
  
  const { login } = useGame();
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();

  // Schneller Demo-Login
  const handleQuickLogin = () => {
    if (username.trim()) {
      login(username.trim());
      navigate("/map");
    }
  };

  // Echter Login mit Supabase
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signIn(email, password);
      navigate("/map");
    } catch (error) {
      console.error("Login failed:", error);
    } finally {
      setLoading(false);
    }
  };

  // Registrierung mit Supabase
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signUp(email, password, registerUsername);
      navigate("/map");
    } catch (error) {
      console.error("Registration failed:", error);
    } finally {
      setLoading(false);
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
          {/* Logo/Icon */}
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

          {/* Title */}
          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-muted-foreground">
              Turning Hot Spots into Cool Spots 🌍
            </p>
          </div>

          {/* Tabs: Quick Login vs Auth */}
          <Tabs defaultValue="quick" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="quick">Schnellstart</TabsTrigger>
              <TabsTrigger value="auth">Account</TabsTrigger>
            </TabsList>

            {/* Quick Login Tab */}
            <TabsContent value="quick" className="space-y-4">
              <div className="space-y-4">
                <div className="relative">
                  <User className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Dein Spielername"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleQuickLogin()}
                    className="h-12 pl-10 text-lg rounded-2xl border-2 focus:border-primary"
                  />
                </div>

                <Button
                  onClick={handleQuickLogin}
                  disabled={!username.trim()}
                  className="w-full h-12 text-lg rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat shadow-lg hover:shadow-xl transition-all"
                >
                  Schnellstart 🚀
                </Button>

                <p className="text-xs text-center text-muted-foreground">
                  Kein Account nötig • Daten nur lokal gespeichert
                </p>
              </div>
            </TabsContent>

            {/* Auth Tab (Login & Register) */}
            <TabsContent value="auth" className="space-y-4">
              <Tabs defaultValue="login" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="login">Login</TabsTrigger>
                  <TabsTrigger value="register">Registrieren</TabsTrigger>
                </TabsList>

                {/* Login Form */}
                <TabsContent value="login">
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="relative">
                      <Mail className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                      <Input
                        type="email"
                        placeholder="E-Mail"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
                      />
                    </div>

                    <div className="relative">
                      <Lock className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                      <Input
                        type="password"
                        placeholder="Passwort"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full h-12 rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat"
                    >
                      {loading ? "Lädt..." : "Einloggen 🔥"}
                    </Button>
                  </form>
                </TabsContent>

                {/* Register Form */}
                <TabsContent value="register">
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="relative">
                      <User className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                      <Input
                        type="text"
                        placeholder="Benutzername"
                        value={registerUsername}
                        onChange={(e) => setRegisterUsername(e.target.value)}
                        required
                        className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
                      />
                    </div>

                    <div className="relative">
                      <Mail className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                      <Input
                        type="email"
                        placeholder="E-Mail"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
                      />
                    </div>

                    <div className="relative">
                      <Lock className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
                      <Input
                        type="password"
                        placeholder="Passwort (min. 6 Zeichen)"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={6}
                        className="h-12 pl-10 rounded-2xl border-2 focus:border-primary"
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full h-12 rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat"
                    >
                      {loading ? "Lädt..." : "Account erstellen 🎉"}
                    </Button>
                  </form>
                </TabsContent>
              </Tabs>
            </TabsContent>
          </Tabs>

          {/* Info */}
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
