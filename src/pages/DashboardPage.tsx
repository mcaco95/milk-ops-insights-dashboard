
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { DashboardResponse } from '../types/api';
import { formatNumber, formatPercentage } from '../utils/formatters';

const DashboardPage = () => {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchData = async () => {
    if (!user?.dairy_id) return;
    
    try {
      const dashboardData = await apiService.getDashboard(user.dairy_id);
      setData(dashboardData);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [user?.dairy_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-700 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 font-medium">{error}</p>
          <button
            onClick={fetchData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Tanks',
      value: data?.total_tanks || 0,
      subtitle: `${data?.tanks_full || 0} tanks full`,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Active Routes',
      value: data?.active_routes || 0,
      subtitle: 'Currently active',
      color: 'from-green-500 to-emerald-500',
    },
    {
      title: 'Monthly Volume',
      value: formatNumber(data?.monthly_volume || 0),
      subtitle: 'Gallons this month',
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Capacity Usage',
      value: formatPercentage(data?.capacity_utilization || 0),
      subtitle: 'Tank utilization',
      color: 'from-orange-500 to-red-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2">
            Welcome back, {user?.dairy_name}
          </h1>
          <p className="text-slate-600 text-lg">
            Here's your operation overview
          </p>
        </div>

        {/* 4-Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {cards.map((card, index) => (
            <div
              key={card.title}
              className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6 hover:shadow-xl transition-all duration-300"
            >
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${card.color} mb-4`}>
                <div className="w-6 h-6 bg-white/30 rounded"></div>
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide">
                  {card.title}
                </h3>
                <p className="text-3xl font-bold text-slate-900">
                  {card.value}
                </p>
                <p className="text-sm text-slate-500">
                  {card.subtitle}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Critical Alerts Section */}
        {data && data.critical_alerts > 0 && (
          <div className="mt-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-red-800 mb-2">
                Critical Alerts
              </h2>
              <p className="text-red-600">
                You have {data.critical_alerts} critical alert{data.critical_alerts !== 1 ? 's' : ''} requiring attention.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
