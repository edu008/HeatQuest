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
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: 'linear-gradient(135deg, #FF6D42 0%, #FF8A5C 50%, #0DA5DD 100%)'
      }}
    >
      <div className="w-full max-w-md">
        <div 
          className="rounded-3xl p-8 shadow-2xl"
          style={{ backgroundColor: 'white' }}
        >
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div 
              className="w-24 h-24 rounded-full flex items-center justify-center shadow-lg"
              style={{ backgroundColor: '#FF6D42' }}
            >
              <Flame className="w-12 h-12 text-white" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-center mb-2">
            <span style={{ color: '#FF6D42' }}>Heat</span>
            <span style={{ color: '#718096' }}>Quest</span>
          </h1>
          <p className="text-center mb-8" style={{ color: '#718096' }}>
            Turning Hot Spots into Cool Spots 🌍
          </p>

          {/* Login/Signup Tabs */}
          <div 
            className="flex mb-6 rounded-xl p-1"
            style={{ backgroundColor: '#F7FAFC' }}
          >
            <button
              onClick={() => setIsLogin(true)}
              className="flex-1 py-2 rounded-lg font-medium transition-all"
              style={{
                backgroundColor: isLogin ? 'white' : 'transparent',
                color: isLogin ? '#1A202C' : '#718096',
                boxShadow: isLogin ? '0 1px 2px rgba(0,0,0,0.05)' : 'none'
              }}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className="flex-1 py-2 rounded-lg font-medium transition-all"
              style={{
                backgroundColor: !isLogin ? 'white' : 'transparent',
                color: !isLogin ? '#1A202C' : '#718096',
                boxShadow: !isLogin ? '0 1px 2px rgba(0,0,0,0.05)' : 'none'
              }}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 mb-6">
            <div className="relative">
              <Mail 
                className="absolute left-4 top-1/2 w-5 h-5" 
                style={{ 
                  transform: 'translateY(-50%)',
                  color: '#718096'
                }} 
              />
              <input
                type="email"
                placeholder="Email"
                className="w-full pl-12 pr-4 py-3 border-none rounded-xl focus:outline-none"
                style={{ 
                  backgroundColor: '#F7FAFC',
                  boxShadow: 'inset 0 0 0 1px transparent',
                  transition: 'box-shadow 0.2s'
                }}
                onFocus={(e) => e.target.style.boxShadow = 'inset 0 0 0 2px #FF6D42'}
                onBlur={(e) => e.target.style.boxShadow = 'inset 0 0 0 1px transparent'}
              />
            </div>
            <div className="relative">
              <Lock 
                className="absolute left-4 top-1/2 w-5 h-5" 
                style={{ 
                  transform: 'translateY(-50%)',
                  color: '#718096'
                }} 
              />
              <input
                type="password"
                placeholder="Password"
                className="w-full pl-12 pr-4 py-3 border-none rounded-xl focus:outline-none"
                style={{ 
                  backgroundColor: '#F7FAFC',
                  boxShadow: 'inset 0 0 0 1px transparent',
                  transition: 'box-shadow 0.2s'
                }}
                onFocus={(e) => e.target.style.boxShadow = 'inset 0 0 0 2px #FF6D42'}
                onBlur={(e) => e.target.style.boxShadow = 'inset 0 0 0 1px transparent'}
              />
            </div>
            <button
              type="submit"
              className="w-full py-3 text-white rounded-xl font-medium transition-all shadow-lg hover:opacity-90"
              style={{ backgroundColor: '#FF6D42' }}
            >
              Sign In 🔥
            </button>
          </form>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full" style={{ borderTop: '1px solid #E2E8F0' }}></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-white" style={{ color: '#718096' }}>
                OR CONTINUE WITH
              </span>
            </div>
          </div>

          {/* Social Login */}
          <div className="space-y-3 mb-8">
            <button 
              className="w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 hover:opacity-80"
              style={{ backgroundColor: '#F7FAFC' }}
            >
              <Github className="w-5 h-5" />
              Sign in with GitHub
            </button>
            <button 
              className="w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 hover:opacity-80"
              style={{ backgroundColor: '#F7FAFC' }}
            >
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
          <div className="space-y-2 text-sm" style={{ color: '#718096' }}>
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
