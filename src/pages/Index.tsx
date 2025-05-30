
import { Link } from 'react-router-dom';
import { BarChart3, Truck, Droplets } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center max-w-2xl mx-auto p-8">
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
        
        <div className="grid md:grid-cols-3 gap-6 mb-12">
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
        
        <Link 
          to="/dashboard"
          className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Open Dashboard
        </Link>
      </div>
    </div>
  );
};

export default Index;
