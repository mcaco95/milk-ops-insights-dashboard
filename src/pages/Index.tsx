
import { Link } from 'react-router-dom';
import { BarChart3, Truck, Droplets, LogIn, ArrowRight, Users, Shield, Zap } from 'lucide-react';
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

      <div className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="text-center max-w-6xl mx-auto p-8">
          {/* Hero Section */}
          <div className="mb-16 animate-fade-in">
            <div className="flex justify-center mb-8">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full p-8 shadow-2xl backdrop-blur-sm border border-blue-400/20 hover:scale-110 transition-transform duration-500">
                <Droplets className="w-20 h-20 text-white" />
              </div>
            </div>
            
            <h1 className="text-7xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent mb-8 tracking-tight leading-tight">
              Milk Ops
            </h1>
            <p className="text-2xl text-slate-300 mb-4 font-light">
              The Future of Dairy Operations
            </p>
            <p className="text-xl text-slate-400 mb-12 max-w-3xl mx-auto leading-relaxed">
              Real-time monitoring, predictive analytics, and seamless route management for modern dairy operations
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 text-lg rounded-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 group">
                Get Started
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800/50 px-8 py-4 text-lg rounded-xl backdrop-blur-sm transition-all duration-300 hover:scale-105">
                Learn More
              </Button>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-16 items-start">
            {/* Features Section */}
            <div className="space-y-8 animate-fade-in animation-delay-500">
              <h2 className="text-3xl font-bold text-white mb-8">Built for Excellence</h2>
              
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-4">
                    <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg p-3 mr-4 group-hover:scale-110 transition-transform">
                      <BarChart3 className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-white">Smart Analytics</h3>
                  </div>
                  <p className="text-slate-300">Real-time volume tracking with AI-powered predictions for optimal capacity management</p>
                </div>
                
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700/50 hover:border-green-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-4">
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg p-3 mr-4 group-hover:scale-110 transition-transform">
                      <Truck className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-white">Route Optimization</h3>
                  </div>
                  <p className="text-slate-300">Intelligent routing system that maximizes efficiency and minimizes costs</p>
                </div>
                
                <div className="bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 hover:scale-105 group">
                  <div className="flex items-center mb-4">
                    <div className="bg-gradient-to-r from-purple-500 to-violet-500 rounded-lg p-3 mr-4 group-hover:scale-110 transition-transform">
                      <Zap className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-white">Lightning Fast</h3>
                  </div>
                  <p className="text-slate-300">Real-time updates and instant notifications to keep operations running smoothly</p>
                </div>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center justify-center space-x-8 pt-8 border-t border-slate-700/50">
                <div className="flex items-center text-slate-400">
                  <Users className="w-5 h-5 mr-2" />
                  <span className="text-sm">Trusted by 500+ dairies</span>
                </div>
                <div className="flex items-center text-slate-400">
                  <Shield className="w-5 h-5 mr-2" />
                  <span className="text-sm">Enterprise-grade security</span>
                </div>
              </div>
            </div>

            {/* Login Section */}
            <div className="animate-fade-in animation-delay-1000">
              <div className="bg-slate-800/40 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-2xl hover:shadow-blue-500/10 transition-all duration-500">
                <div className="flex items-center justify-center mb-8">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl p-3 mr-4">
                    <LogIn className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-3xl font-bold text-white">Welcome Back</h2>
                </div>
                
                <form className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-slate-300 font-medium">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      className="bg-slate-900/50 border-slate-600 text-white placeholder:text-slate-400 rounded-xl h-12 backdrop-blur-sm focus:border-blue-500 focus:ring-blue-500/20 transition-all"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-slate-300 font-medium">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your password"
                      className="bg-slate-900/50 border-slate-600 text-white placeholder:text-slate-400 rounded-xl h-12 backdrop-blur-sm focus:border-blue-500 focus:ring-blue-500/20 transition-all"
                    />
                  </div>
                  
                  <Link 
                    to="/dashboard"
                    className="w-full inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 group mt-8"
                  >
                    Sign In to Dashboard
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </form>

                <div className="mt-6 text-center">
                  <a href="#" className="text-slate-400 hover:text-blue-400 text-sm transition-colors">
                    Forgot your password?
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
