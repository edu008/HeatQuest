import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/lib/supabase';
import { Loader2 } from 'lucide-react';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    console.log('🔄 AuthCallback: Processing OAuth redirect...');
    console.log('🔗 URL:', window.location.href);
    
    // Supabase verarbeitet automatisch den OAuth-Callback
    // Wir müssen nur warten bis die Session geladen ist
    const handleCallback = async () => {
      try {
        // Warte länger damit Supabase den Hash verarbeiten kann
        console.log('⏳ Waiting for Supabase to process callback...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const { data: { session }, error } = await supabase.auth.getSession();
        
        console.log('📦 Session after callback:', session ? 'Found' : 'None');
        
        if (session) {
          console.log('✅ Session found!');
          console.log('👤 User:', session.user.email);
          console.log('🔑 Provider:', session.user.app_metadata.provider);
        }
        
        if (error) {
          console.error('❌ Callback error:', error);
          navigate('/?error=' + encodeURIComponent(error.message));
          return;
        }
        
        if (session) {
          console.log('✅ Redirecting to map...');
          // Warte nochmal kurz damit AuthContext die Session laden kann
          await new Promise(resolve => setTimeout(resolve, 500));
          navigate('/map');
        } else {
          console.log('⚠️ No session found, redirecting to login...');
          navigate('/?error=no_session');
        }
      } catch (error) {
        console.error('❌ Callback processing error:', error);
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

