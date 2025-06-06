
import { Link } from 'react-router-dom';
import { BarChart3, Truck, Droplets, LogIn, ArrowRight, Users, Shield, Zap, Building2 } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <div className="text-center max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="mb-8 md:mb-16 animate-fade-in">
            <div className="flex justify-center mb-6 md:mb-8">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full p-6 md:p-8 shadow-2xl backdrop-blur-sm border border-blue-400/20 hover:scale-110 transition-transform duration-500">
                <Droplets className="w-12 h-12 md:w-20 md:h-20 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl md:text-7xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent mb-4 md:mb-8 tracking-tight leading-tight">
              Milk Ops
            </h1>
            <p className="text-lg md:text-2xl text-slate-300 mb-2 md:mb-4 font-light">
              The Future of Dairy Operations
            </p>
            <p className="text-base md:text-xl text-slate-400 mb-8 md:mb-12 max-w-3xl mx-auto leading-relaxed px-4">
              Real-time monitoring, predictive analytics, and seamless route management for modern dairy operations
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 md:gap-16 items-start">
            {/* Features Section */}
            <div className="space-y-6 md:space-y-8 animate-fade-in animation-delay-500 px-4">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">Built for Excellence</h2>
              
              <div className="space-y-4 md:space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-4 md:p-6 border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-3 md:mb-4">
                    <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg p-2 md:p-3 mr-3 md:mr-4 group-hover:scale-110 transition-transform">
                      <BarChart3 className="w-6 h-6 md:w-8 md:h-8 text-white" />
                    </div>
                    <h3 className="text-lg md:text-xl font-semibold text-white">Smart Analytics</h3>
                  </div>
                  <p className="text-sm md:text-base text-slate-300">Real-time volume tracking with AI-powered predictions for optimal capacity management</p>
                </div>
                
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-4 md:p-6 border border-slate-700/50 hover:border-green-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-3 md:mb-4">
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg p-2 md:p-3 mr-3 md:mr-4 group-hover:scale-110 transition-transform">
                      <Truck className="w-6 h-6 md:w-8 md:h-8 text-white" />
                    </div>
                    <h3 className="text-lg md:text-xl font-semibold text-white">Route Optimization</h3>
                  </div>
                  <p className="text-sm md:text-base text-slate-300">Intelligent routing system that maximizes efficiency and minimizes costs</p>
                </div>
                
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-4 md:p-6 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-3 md:mb-4">
                    <div className="bg-gradient-to-r from-purple-500 to-violet-500 rounded-lg p-2 md:p-3 mr-3 md:mr-4 group-hover:scale-110 transition-transform">
                      <Zap className="w-6 h-6 md:w-8 md:h-8 text-white" />
                    </div>
                    <h3 className="text-lg md:text-xl font-semibold text-white">Lightning Fast</h3>
                  </div>
                  <p className="text-sm md:text-base text-slate-300">Real-time updates and instant notifications to keep operations running smoothly</p>
                </div>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-8 pt-6 md:pt-8 border-t border-slate-700/50">
                <div className="flex items-center text-slate-400">
                  <Users className="w-4 h-4 md:w-5 md:h-5 mr-2" />
                  <span className="text-xs md:text-sm">Trusted by 500+ dairies</span>
                </div>
                <div className="flex items-center text-slate-400">
                  <Shield className="w-4 h-4 md:w-5 md:h-5 mr-2" />
                  <span className="text-xs md:text-sm">Enterprise-grade security</span>
                </div>
              </div>
            </div>

            {/* Login Section */}
            <div className="animate-fade-in animation-delay-1000 px-4">
              <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-6 md:p-8 border border-slate-700/50 shadow-2xl hover:shadow-blue-500/10 transition-all duration-500">
                <div className="flex items-center justify-center mb-6 md:mb-8">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl p-2 md:p-3 mr-3 md:mr-4">
                    <LogIn className="w-6 h-6 md:w-8 md:h-8 text-white" />
                  </div>
                  <h2 className="text-2xl md:text-3xl font-bold text-white">Welcome Back</h2>
                </div>
                
                {/* Dual Login Options */}
                <div className="space-y-4 md:space-y-6 mb-6 md:mb-8">
                  <Link 
                    to="/dashboard"
                    className="w-full inline-flex items-center justify-center px-6 md:px-8 py-3 md:py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 group"
                  >
                    <Building2 className="mr-2 md:mr-3 w-5 h-5 md:w-6 md:h-6" />
                    <div className="text-left">
                      <div className="text-sm md:text-base font-semibold">Admin Dashboard</div>
                      <div className="text-xs md:text-sm opacity-90">Full system access</div>
                    </div>
                    <ArrowRight className="ml-auto w-4 h-4 md:w-5 md:h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                  
                  <Link 
                    to="/dairy-dashboard"
                    className="w-full inline-flex items-center justify-center px-6 md:px-8 py-3 md:py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-2xl hover:shadow-green-500/25 transition-all duration-300 hover:scale-105 group"
                  >
                    <Droplets className="mr-2 md:mr-3 w-5 h-5 md:w-6 md:h-6" />
                    <div className="text-left">
                      <div className="text-sm md:text-base font-semibold">Dairy Access</div>
                      <div className="text-xs md:text-sm opacity-90">Your farm data only</div>
                    </div>
                    <ArrowRight className="ml-auto w-4 h-4 md:w-5 md:h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>

                <div className="text-center border-t border-slate-700/50 pt-4 md:pt-6">
                  <a href="#" className="text-slate-400 hover:text-blue-400 text-xs md:text-sm transition-colors">
                    Need help accessing your account?
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
