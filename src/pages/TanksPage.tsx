
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { TanksResponse } from '../types/api';
import { formatNumber, formatDateTime } from '../utils/formatters';

const TanksPage = () => {
  const [data, setData] = useState<TanksResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchData = async () => {
    if (!user?.dairy_id) return;
    
    try {
      const tanksData = await apiService.getTanks(user.dairy_id);
      setData(tanksData);
      setError(null);
    } catch (err) {
      setError('Failed to load tanks data');
      console.error('Tanks fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 2 minutes
    const interval = setInterval(fetchData, 120000);
    return () => clearInterval(interval);
  }, [user?.dairy_id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal':
        return 'from-green-500 to-emerald-500';
      case 'warning':
        return 'from-yellow-500 to-orange-500';
      case 'critical':
        return 'from-red-500 to-pink-500';
      default:
        return 'from-gray-500 to-slate-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'normal':
        return 'Normal';
      case 'warning':
        return 'Warning';
      case 'critical':
        return 'Critical';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-700 font-medium">Loading tank status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2">
            Tank Status
          </h1>
          <p className="text-slate-600 text-lg">
            Real-time monitoring of all your storage tanks
          </p>
        </div>

        {error ? (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        ) : data && data.tanks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.tanks.map((tank) => (
              <div
                key={tank.id}
                className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6 hover:shadow-xl transition-all duration-300"
              >
                {/* Tank Header */}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900">
                    {tank.name}
                  </h3>
                  <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full bg-gradient-to-r ${getStatusColor(tank.status)} text-white`}>
                    {getStatusText(tank.status)}
                  </span>
                </div>

                {/* Visual Tank Cylinder */}
                <div className="mb-6">
                  <div className="relative w-20 h-32 mx-auto bg-slate-200 rounded-lg border-2 border-slate-300 overflow-hidden">
                    {/* Fill Level */}
                    <div
                      className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t ${getStatusColor(tank.status)} transition-all duration-1000 ease-out rounded-b-md`}
                      style={{ height: `${tank.fill_percentage}%` }}
                    />
                    {/* Fill Percentage Label */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-sm font-bold text-slate-700 bg-white/80 px-2 py-1 rounded">
                        {Math.round(tank.fill_percentage)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Tank Details */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Current Volume</span>
                    <span className="font-medium text-slate-900">
                      {formatNumber(tank.current_volume)} gal
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Capacity</span>
                    <span className="font-medium text-slate-900">
                      {formatNumber(tank.capacity)} gal
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Last Pickup</span>
                    <span className="font-medium text-slate-900">
                      {formatDateTime(tank.last_pickup)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Est. Full</span>
                    <span className="font-medium text-slate-900">
                      {formatDateTime(tank.estimated_full)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6 text-center text-slate-500">
            No tanks found for your dairy
          </div>
        )}

        {/* Auto-refresh indicator */}
        <div className="mt-6 text-center">
          <p className="text-sm text-slate-500">
            Auto-refreshes every 2 minutes
          </p>
        </div>
      </div>
    </div>
  );
};

export default TanksPage;
