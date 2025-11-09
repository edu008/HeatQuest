import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { useAuth } from "@/contexts/AuthContext";
import { Flame, Mail, Lock, User, Github } from "lucide-react";
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
  const { signIn, signUp, signInWithOAuth } = useAuth();
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

  // OAuth Login (GitHub, Google)
  const handleOAuthLogin = async (provider: 'github' | 'google') => {
    setLoading(true);
    try {
      await signInWithOAuth(provider);
      // Weiterleitung erfolgt automatisch durch Supabase
    } catch (error) {
      console.error(`${provider} login failed:`, error);
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
              {/* OAuth Buttons */}
              <div className="space-y-3">
                <Button
                  onClick={() => handleOAuthLogin('github')}
                  disabled={loading}
                  variant="outline"
                  className="w-full h-12 rounded-2xl border-2 hover:bg-accent transition-all"
                >
                  <Github className="mr-2 h-5 w-5" />
                  Mit GitHub anmelden
                </Button>

                <Button
                  onClick={() => handleOAuthLogin('google')}
                  disabled={loading}
                  variant="outline"
                  className="w-full h-12 rounded-2xl border-2 hover:bg-accent transition-all"
                >
                  <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Mit Google anmelden
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">
                      Oder mit E-Mail
                    </span>
                  </div>
                </div>
              </div>

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
