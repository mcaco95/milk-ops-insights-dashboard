import { useState, useEffect } from 'react';
import { VolumeWidget } from '../components/dashboard/VolumeWidget';
import { PickupsWidget } from '../components/dashboard/PickupsWidget';
import { RoutesWidget } from '../components/dashboard/RoutesWidget';
import { Barn, CustomerSummary, RouteRecord } from '../types/dashboard';

// Mock API functions with enhanced data
const fetchBarns = async (): Promise<Barn[]> => {
  return [
    {
      id: 1,
      name: "Barn A",
      tanks: [
        {
          id: 1,
          name: "Tank 1",
          currentVolume: 17340,
          predictedVolume: 100000,
          superLoadsAvailable: 2.27,
          lastHit: "2025-05-30T09:58:00Z",
          eta: "9:15"
        },
        {
          id: 2,
          name: "Tank 2", 
          currentVolume: 45280,
          predictedVolume: 100000,
          superLoadsAvailable: 1.83,
          lastHit: "2025-05-30T08:15:00Z",
          eta: "7:28"
        },
        {
          id: 3,
          name: "Tank 3",
          currentVolume: 78920,
          predictedVolume: 100000,
          superLoadsAvailable: 0.84,
          lastHit: "2025-05-30T07:42:00Z"
        }
      ]
    },
    {
      id: 2,
      name: "Barn B",
      tanks: [
        {
          id: 4,
          name: "Tank 4",
          currentVolume: 32580,
          predictedVolume: 85000,
          superLoadsAvailable: 1.95,
          lastHit: "2025-05-30T06:30:00Z"
        },
        {
          id: 5,
          name: "Tank 5",
          currentVolume: 61420,
          predictedVolume: 85000,
          superLoadsAvailable: 1.12,
          lastHit: "2025-05-30T05:45:00Z"
        }
      ]
    }
  ];
};

const fetchPickups = async (month: string): Promise<CustomerSummary[]> => {
  return [
    { customer: "UDA", totalWeight: 4967480, invoiceCount: 15 },
    { customer: "Fairlife", totalWeight: 3245670, invoiceCount: 12 },
    { customer: "Organic Valley", totalWeight: 2156340, invoiceCount: 8 },
    { customer: "Horizon", totalWeight: 1845920, invoiceCount: 7 },
    { customer: "Clover", totalWeight: 1234560, invoiceCount: 5 }
  ];
};

const fetchTodaysRoutes = async (): Promise<RouteRecord[]> => {
  return [
    {
      startTime: "2025-05-30T03:00:00Z",
      routeNumber: 79,
      dairy: "Dickman",
      tank: 3,
      ltNumber: "YY51760",
      invoiceNumber: "10175325",
      status: "closed",
      eta: "closed",
      trackingUrl: "https://track.example.com/YY51760"
    },
    {
      startTime: "2025-05-30T12:00:00Z",
      routeNumber: 74,
      dairy: "Dickman",
      tank: 2,
      ltNumber: "LMH32001",
      invoiceNumber: "10175359",
      status: "active",
      eta: "7:28",
      trackingUrl: "https://track.example.com/LMH32001"
    },
    {
      startTime: "2025-05-30T20:00:00Z",
      routeNumber: 75,
      dairy: "Dickman",
      tank: 1,
      ltNumber: "NIM69133",
      invoiceNumber: "10175394",
      status: "active",
      eta: "9:15",
      trackingUrl: "https://track.example.com/NIM69133"
    }
  ];
};

const Dashboard = () => {
  const [barns, setBarns] = useState<Barn[]>([]);
  const [pickups, setPickups] = useState<CustomerSummary[]>([]);
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [barnsData, pickupsData, routesData] = await Promise.all([
          fetchBarns(),
          fetchPickups('2025-05'),
          fetchTodaysRoutes()
        ]);
        
        setBarns(barnsData);
        setPickups(pickupsData);
        setRoutes(routesData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-6 shadow-lg"></div>
          <p className="text-slate-700 font-medium text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-3 tracking-tight">
            Milk Ops Dashboard
          </h1>
          <p className="text-slate-600 text-lg font-medium">Real-time operations monitoring and analytics</p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Volume Widget - Top Left */}
          <div className="lg:col-span-6">
            <VolumeWidget barns={barns} />
          </div>

          {/* Pickups Widget - Top Right */}
          <div className="lg:col-span-6">
            <PickupsWidget pickups={pickups} />
          </div>

          {/* Routes Widget - Bottom Full Width */}
          <div className="lg:col-span-12">
            <RoutesWidget routes={routes} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
