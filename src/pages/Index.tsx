import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, Mail, Lock, Github } from 'lucide-react';

const Index = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/map');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary via-primary/80 to-secondary flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-24 h-24 bg-primary rounded-full flex items-center justify-center shadow-lg">
              <Flame className="w-12 h-12 text-white" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-center mb-2">
            <span className="text-primary">Heat</span>
            <span className="text-muted-foreground">Quest</span>
          </h1>
          <p className="text-center text-muted-foreground mb-8">
            Turning Hot Spots into Cool Spots 🌍
          </p>

          {/* Login/Signup Tabs */}
          <div className="flex mb-6 bg-muted rounded-xl p-1">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                isLogin
                  ? 'bg-white shadow-sm text-foreground'
                  : 'text-muted-foreground'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                !isLogin
                  ? 'bg-white shadow-sm text-foreground'
                  : 'text-muted-foreground'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 mb-6">
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                placeholder="Email"
                className="w-full pl-12 pr-4 py-3 bg-muted border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                placeholder="Password"
                className="w-full pl-12 pr-4 py-3 bg-muted border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              type="submit"
              className="w-full py-3 bg-primary hover:bg-primary/90 text-white rounded-xl font-medium transition-colors shadow-lg"
            >
              Sign In 🔥
            </button>
          </form>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-white text-muted-foreground">
                OR CONTINUE WITH
              </span>
            </div>
          </div>

          {/* Social Login */}
          <div className="space-y-3 mb-8">
            <button className="w-full py-3 bg-muted hover:bg-muted/80 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
              <Github className="w-5 h-5" />
              Sign in with GitHub
            </button>
            <button className="w-full py-3 bg-muted hover:bg-muted/80 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
              <svg className="w-5 h-5" viewBox="0 0 24 24">
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
              Sign in with Google
            </button>
          </div>

          {/* Features */}
          <div className="space-y-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span>🗺️</span>
              <span>Discover Heat Hotspots</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🔥</span>
              <span>Analyze with AI</span>
            </div>
            <div className="flex items-center gap-2">
              <span>✅</span>
              <span>Start Climate Missions</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
