import { useState, useEffect } from 'react';
import { DairyLayout } from '../components/dairy/DairyLayout';
import { Link } from 'react-router-dom';
import { Droplets, Truck, FileText, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Barn } from '../types/dashboard';

// Mock function to get dairy-specific data
const fetchDairyData = async () => {
  // Mock data - simplified for overview
  const barn: Barn = {
    id: 1,
    name: "Milky Way Dairy",
    producerId: "633",
    location: { lat: 33.4484, lng: -112.0740 },
    tanks: [
      {
        id: 1,
        name: "Barn 1 - Tank A",
        currentVolume: 4200,
        predictedVolume: 140000,
        capacity: 140000,
        superLoadsAvailable: 2.27,
        lastHit: "2025-06-05T09:58:00Z",
        fillRate: 12000,
        washAlertStatus: 'critical',
        washAlertTime: "2025-06-03T10:00:00Z"
      },
      {
        id: 2,
        name: "Barn 1 - Tank B",
        currentVolume: 3800,
        predictedVolume: 140000,
        capacity: 140000,
        superLoadsAvailable: 1.83,
        lastHit: "2025-06-05T08:15:00Z",
        fillRate: 8500,
        washAlertStatus: 'warning',
        washAlertTime: "2025-06-05T06:00:00Z"
      },
      {
        id: 3,
        name: "Barn 2 - Tank A",
        currentVolume: 87200,
        predictedVolume: 170000,
        capacity: 170000,
        superLoadsAvailable: 1.95,
        lastHit: "2025-06-05T06:30:00Z",
        fillRate: 15000,
        washAlertStatus: 'ok'
      },
      {
        id: 4,
        name: "Barn 2 - Tank B",
        currentVolume: 102400,
        predictedVolume: 170000,
        capacity: 170000,
        superLoadsAvailable: 1.12,
        lastHit: "2025-06-05T05:45:00Z",
        fillRate: 18000,
        washAlertStatus: 'ok'
      },
      {
        id: 5,
        name: "Barn 3 - Tank A",
        currentVolume: 65800,
        predictedVolume: 110000,
        capacity: 110000,
        superLoadsAvailable: 0.84,
        lastHit: "2025-06-05T07:42:00Z",
        fillRate: 20000,
        washAlertStatus: 'ok'
      },
      {
        id: 6,
        name: "Barn 3 - Tank B",
        currentVolume: 95400,
        predictedVolume: 110000,
        capacity: 110000,
        superLoadsAvailable: 0.92,
        lastHit: "2025-06-05T04:20:00Z",
        fillRate: 16000,
        washAlertStatus: 'ok'
      }
    ]
  };

  return { barn };
};

const DairyDashboard = () => {
  const [barn, setBarn] = useState<Barn | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchDairyData();
        setBarn(data.barn);
      } catch (error) {
        console.error('Failed to load dairy data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <DairyLayout>
        <div className="flex items-center justify-center min-h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading your dairy data...</p>
          </div>
        </div>
      </DairyLayout>
    );
  }

  const tanksNeedingWash = barn?.tanks.filter(tank => tank.washAlertStatus !== 'ok').length || 0;
  const totalVolume = barn?.tanks.reduce((sum, tank) => sum + tank.currentVolume, 0) || 0;
  const totalCapacity = barn?.tanks.reduce((sum, tank) => sum + tank.capacity, 0) || 0;
  const capacityUtilization = Math.round((totalVolume / totalCapacity) * 100);

  return (
    <DairyLayout dairyName={barn?.name}>
      <div className="p-4 pb-20 md:pb-4">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">
            Welcome to {barn?.name || 'Your Dairy'}
          </h1>
          <p className="text-slate-600">Here's what's happening with your dairy today</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">{barn?.tanks.length || 0}</p>
                <p className="text-sm text-slate-600">Total Tanks</p>
              </div>
              <Droplets size={24} className="text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-orange-600">{tanksNeedingWash}</p>
                <p className="text-sm text-slate-600">Need Wash</p>
              </div>
              <AlertTriangle size={24} className="text-orange-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">{capacityUtilization}%</p>
                <p className="text-sm text-slate-600">Capacity</p>
              </div>
              <CheckCircle size={24} className="text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-purple-600">{Math.round(totalVolume/1000)}K</p>
                <p className="text-sm text-slate-600">Liters</p>
              </div>
              <Droplets size={24} className="text-purple-600" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">Quick Actions</h2>
          
          <div className="grid gap-4 md:grid-cols-3">
            <Link to="/dairy/tanks">
              <Button className="w-full h-24 flex flex-col space-y-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200 border-2">
                <Droplets size={24} />
                <span className="font-medium">Check Tanks</span>
                <span className="text-sm opacity-75">Monitor tank status & volumes</span>
              </Button>
            </Link>

            <Link to="/dairy/routes">
              <Button className="w-full h-24 flex flex-col space-y-2 bg-green-50 hover:bg-green-100 text-green-700 border-green-200 border-2">
                <Truck size={24} />
                <span className="font-medium">Track Pickups</span>
                <span className="text-sm opacity-75">See active milk collections</span>
              </Button>
            </Link>

            <Link to="/dairy/reports">
              <Button className="w-full h-24 flex flex-col space-y-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200 border-2">
                <FileText size={24} />
                <span className="font-medium">View Reports</span>
                <span className="text-sm opacity-75">Production summaries</span>
              </Button>
            </Link>
          </div>
        </div>

        {/* Urgent Alerts */}
        {tanksNeedingWash > 0 && (
          <div className="mt-8 bg-orange-50 border-2 border-orange-200 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <AlertTriangle size={20} className="text-orange-600 mr-2" />
              <h3 className="font-semibold text-orange-800">Action Needed</h3>
            </div>
            <p className="text-orange-700 mb-3">
              {tanksNeedingWash} tank{tanksNeedingWash > 1 ? 's' : ''} need{tanksNeedingWash === 1 ? 's' : ''} washing
            </p>
            <Link to="/dairy/tanks">
              <Button size="sm" className="bg-orange-600 hover:bg-orange-700 text-white">
                View Tank Details
              </Button>
            </Link>
          </div>
        )}
      </div>
    </DairyLayout>
  );
};

export default DairyDashboard;
