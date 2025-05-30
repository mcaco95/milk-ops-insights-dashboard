
import { Link } from 'react-router-dom';
import { BarChart3, Truck, Droplets, LogIn } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center max-w-4xl mx-auto p-8">
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-full p-6 shadow-lg">
            <Droplets className="w-16 h-16 text-blue-600" />
          </div>
        </div>
        
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Milk Ops
        </h1>
        <p className="text-xl text-gray-600 mb-12">
          Professional dairy operations management platform for real-time monitoring and analytics
        </p>
        
        <div className="grid md:grid-cols-2 gap-12 items-start">
          {/* Features Section */}
          <div>
            <div className="grid gap-6 mb-8">
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Volume Tracking</h3>
                <p className="text-sm text-gray-600">Monitor tank levels and predict capacity needs</p>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <Truck className="w-8 h-8 text-green-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Route Management</h3>
                <p className="text-sm text-gray-600">Track pickups and deliveries in real-time</p>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Analytics</h3>
                <p className="text-sm text-gray-600">Comprehensive reporting and insights</p>
              </div>
            </div>
          </div>

          {/* Login Section */}
          <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-200">
            <div className="flex items-center justify-center mb-6">
              <LogIn className="w-8 h-8 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Login</h2>
            </div>
            
            <form className="space-y-6">
              <div>
                <Label htmlFor="email" className="text-left block mb-2">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  className="w-full"
                />
              </div>
              
              <div>
                <Label htmlFor="password" className="text-left block mb-2">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  className="w-full"
                />
              </div>
              
              <Link 
                to="/dashboard"
                className="w-full inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Sign In
              </Link>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
