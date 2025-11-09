import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { Loader2 } from 'lucide-react';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          navigate('/?error=' + encodeURIComponent(error.message));
          return;
        }
        
        if (session) {
          await new Promise(resolve => setTimeout(resolve, 500));
          navigate('/map');
        } else {
          navigate('/?error=no_session');
        }
      } catch (error) {
        navigate('/?error=callback_failed');
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-heat-intense via-primary to-secondary">
      <div className="text-center space-y-4">
        <Loader2 className="w-12 h-12 animate-spin mx-auto text-white" />
        <h2 className="text-2xl font-bold text-white">Signing you in...</h2>
        <p className="text-white/80">Please wait while we complete your login</p>
      </div>
    </div>
  );
};

export default AuthCallback;

