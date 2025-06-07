
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Droplets, LogIn } from 'lucide-react';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ username, password });
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    try {
      await login({ username: 'demo', password: 'demo' });
      navigate('/dashboard');
    } catch (err) {
      setError('Demo login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-green-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-72 h-72 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-green-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-teal-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="text-center max-w-md mx-auto">
          {/* Hero Section */}
          <div className="mb-8 animate-fade-in">
            <div className="flex justify-center mb-6">
              <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-full p-6 shadow-2xl backdrop-blur-sm border border-emerald-400/20 hover:scale-110 transition-transform duration-500">
                <Droplets className="w-16 h-16 text-white" />
              </div>
            </div>
            
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-emerald-100 to-green-200 bg-clip-text text-transparent mb-2 tracking-tight leading-tight">
              Milk Ops
            </h1>
            <div className="flex items-center justify-center mb-4">
              <div className="h-px bg-gradient-to-r from-transparent via-emerald-400/40 to-transparent w-16 mr-3"></div>
              <p className="text-sm font-light text-emerald-200/80 tracking-wider uppercase">
                by AgroTrans
              </p>
              <div className="h-px bg-gradient-to-r from-transparent via-emerald-400/40 to-transparent w-16 ml-3"></div>
            </div>
            <p className="text-xl text-slate-300 mb-2 font-light">
              Dairy Dashboard Login
            </p>
            <p className="text-base text-slate-400 mb-8 leading-relaxed">
              Sign in to access your dairy operations dashboard
            </p>
          </div>

          {/* Login Card */}
          <div className="animate-fade-in animation-delay-500">
            <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-2xl hover:shadow-emerald-500/10 transition-all duration-500">
              <div className="flex items-center justify-center mb-8">
                <div className="bg-gradient-to-r from-emerald-500 to-green-500 rounded-xl p-3 mr-4">
                  <LogIn className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white">Welcome Back</h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-slate-300 font-medium">
                    Username
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full h-12 rounded-lg bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-emerald-500 focus:ring-emerald-500"
                    placeholder="Enter your username"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-slate-300 font-medium">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-12 rounded-lg bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-400 focus:border-emerald-500 focus:ring-emerald-500"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                {error && (
                  <div className="bg-red-900/50 border border-red-700/50 rounded-lg p-3 backdrop-blur-sm">
                    <p className="text-red-300 text-sm">{error}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full h-12 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-medium rounded-lg transition-all duration-300 shadow-2xl hover:shadow-emerald-500/25 hover:scale-105"
                >
                  {isLoading ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>

              <div className="mt-6 pt-6 border-t border-slate-700/50">
                <div className="text-center mb-4">
                  <p className="text-sm text-slate-400">Try the demo</p>
                </div>
                <Button
                  onClick={handleDemoLogin}
                  disabled={isLoading}
                  className="w-full h-12 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium rounded-lg transition-all duration-300 shadow-2xl hover:shadow-green-500/25 hover:scale-105"
                >
                  {isLoading ? 'Loading demo...' : 'Demo Login'}
                </Button>
              </div>

              <div className="text-center mt-6 pt-4 border-t border-slate-700/50">
                <a href="#" className="text-slate-400 hover:text-emerald-400 text-sm transition-colors">
                  Need help accessing your account?
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
