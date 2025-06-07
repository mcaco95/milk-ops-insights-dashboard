
import { useState, useEffect } from 'react';
import { DairyLayout } from '../../components/dairy/DairyLayout';
import { AlertTriangle, CheckCircle, Clock, Droplets } from 'lucide-react';
import { Barn, Tank } from '../../types/dashboard';

const fetchTankData = async () => {
  // Mock data - in real app would fetch from API
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
  return barn;
};

const TankCard = ({ tank }: { tank: Tank }) => {
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'critical':
        return {
          icon: AlertTriangle,
          text: 'Needs Wash Now',
          color: 'text-red-600',
          bgColor: 'bg-red-50 border-red-200'
        };
      case 'warning':
        return {
          icon: Clock,
          text: 'Wash Soon',
          color: 'text-orange-600',
          bgColor: 'bg-orange-50 border-orange-200'
        };
      default:
        return {
          icon: CheckCircle,
          text: 'All Good',
          color: 'text-green-600',
          bgColor: 'bg-green-50 border-green-200'
        };
    }
  };

  const status = getStatusInfo(tank.washAlertStatus);
  const StatusIcon = status.icon;
  const fillPercentage = (tank.currentVolume / tank.capacity) * 100;

  return (
    <div className={`p-4 rounded-lg border-2 ${status.bgColor} mb-4`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-slate-800">{tank.name}</h3>
        <div className={`flex items-center ${status.color}`}>
          <StatusIcon size={20} className="mr-2" />
          <span className="font-medium">{status.text}</span>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-slate-600">Current Volume:</span>
          <span className="text-lg font-semibold text-slate-800">
            {tank.currentVolume.toLocaleString()}L
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-600">Capacity:</span>
          <span className="text-slate-700">
            {tank.capacity.toLocaleString()}L
          </span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-600">Fill Level:</span>
            <span className="text-slate-700">{Math.round(fillPercentage)}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-3">
            <div 
              className="bg-blue-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${fillPercentage}%` }}
            />
          </div>
        </div>

        {tank.washAlertStatus !== 'ok' && tank.washAlertTime && (
          <div className="pt-2 border-t border-slate-200">
            <span className="text-sm text-slate-600">
              Last washed: {new Date(tank.washAlertTime).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

const TanksPage = () => {
  const [barn, setBarn] = useState<Barn | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchTankData();
        setBarn(data);
      } catch (error) {
        console.error('Failed to load tank data:', error);
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
            <p className="text-slate-600">Loading tanks...</p>
          </div>
        </div>
      </DairyLayout>
    );
  }

  return (
    <DairyLayout>
      <div className="p-4 pb-20 md:pb-4">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">Your Tanks</h1>
          <p className="text-slate-600">Monitor your milk storage tanks</p>
        </div>

        {barn && (
          <div className="space-y-4">
            {barn.tanks.map((tank) => (
              <TankCard key={tank.id} tank={tank} />
            ))}
          </div>
        )}
      </div>
    </DairyLayout>
  );
};

export default TanksPage;
