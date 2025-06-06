
import { useState, useEffect } from 'react';
import { VolumeWidget } from '../components/dashboard/VolumeWidget';
import { PickupsWidget } from '../components/dashboard/PickupsWidget';
import { RoutesWidget } from '../components/dashboard/RoutesWidget';
import { DashboardSummaryWidget } from '../components/dashboard/DashboardSummaryWidget';
import { Barn, CustomerSummary, RouteRecord, DashboardSummary } from '../types/dashboard';

// Mock API functions with enhanced data representing your 41-dairy operation
const fetchBarns = async (): Promise<Barn[]> => {
  // Sample of your real dairies - representing the 41 total
  return [
    {
      id: 1,
      name: "Milky Way (633)-Barn 1",
      producerId: "633",
      location: { lat: 33.4484, lng: -112.0740 },
      tanks: [
        {
          id: 1,
          name: "Tank 1",
          currentVolume: 4200, // Below 5000L threshold
          predictedVolume: 140000, // 140K liters
          capacity: 140000,
          superLoadsAvailable: 2.27,
          lastHit: "2025-06-05T09:58:00Z",
          fillRate: 12000, // 12K L/hr
          washAlertStatus: 'critical',
          washAlertTime: "2025-06-03T10:00:00Z" // >48h ago
        },
        {
          id: 2,
          name: "Tank 2", 
          currentVolume: 3800, // Below threshold
          predictedVolume: 140000,
          capacity: 140000,
          superLoadsAvailable: 1.83,
          lastHit: "2025-06-05T08:15:00Z",
          fillRate: 8500,
          washAlertStatus: 'warning',
          washAlertTime: "2025-06-05T06:00:00Z" // <24h ago
        }
      ]
    },
    {
      id: 2,
      name: "T&K Dairy-Barn 2",
      producerId: "401",
      location: { lat: 33.5484, lng: -112.1740 },
      tanks: [
        {
          id: 3,
          name: "Tank 1",
          currentVolume: 89200,
          predictedVolume: 110000, // 110K liters
          capacity: 110000,
          superLoadsAvailable: 1.95,
          lastHit: "2025-06-05T06:30:00Z",
          fillRate: 15000, // 15K L/hr
          washAlertStatus: 'ok'
        },
        {
          id: 4,
          name: "Tank 2",
          currentVolume: 102400,
          predictedVolume: 170000, // 170K liters
          capacity: 170000,
          superLoadsAvailable: 1.12,
          lastHit: "2025-06-05T05:45:00Z",
          fillRate: 18000, // 18K L/hr
          washAlertStatus: 'ok'
        }
      ]
    },
    {
      id: 3,
      name: "Dickman Dairy-Main",
      producerId: "205",
      location: { lat: 33.6484, lng: -112.2740 },
      tanks: [
        {
          id: 5,
          name: "Tank 1",
          currentVolume: 4950, // Just below threshold
          predictedVolume: 150000,
          capacity: 150000,
          superLoadsAvailable: 0.84,
          lastHit: "2025-06-05T07:42:00Z",
          fillRate: 20000, // 20K L/hr
          washAlertStatus: 'warning',
          washAlertTime: "2025-06-05T12:00:00Z" // Recent
        }
      ]
    }
  ];
};

const fetchDashboardSummary = async (): Promise<DashboardSummary> => {
  return {
    totalDairies: 41,
    tanksNeedingWash: 3, // Based on ≤5000L threshold
    criticalAlerts: 1,
    averageCapacityUtilization: 73.2,
    activeRoutes: 12,
    totalMonthlyVolume: 71087296, // Your June 2025 total
    totalMonthlyPickups: 969 // Your actual pickup count
  };
};

const fetchPickups = async (month: string): Promise<CustomerSummary[]> => {
  // Your actual June 2025 handler breakdown
  return [
    { customer: "Fairlife", totalWeight: 24160296, invoiceCount: 329, marketShare: 34.0 },
    { customer: "Schreiber", totalWeight: 15709244, invoiceCount: 214, marketShare: 22.1 },
    { customer: "UDA", totalWeight: 14285456, invoiceCount: 195, marketShare: 20.1 },
    { customer: "Horizon", totalWeight: 10652592, invoiceCount: 145, marketShare: 15.0 },
    { customer: "Clover", totalWeight: 6279708, invoiceCount: 86, marketShare: 8.8 }
  ];
};

const fetchTodaysRoutes = async (): Promise<RouteRecord[]> => {
  return [
    {
      startTime: "2025-06-05T03:00:00Z",
      routeNumber: 79,
      dairy: "Dickman Dairy",
      tank: 1,
      ltNumber: "YY51760",
      invoiceNumber: "10175325",
      status: "closed",
      eta: "closed",
      trackingUrl: "https://track.example.com/YY51760",
      driverName: "Jeffery Palacio",
      vehicleId: "VEH-001"
    },
    {
      startTime: "2025-06-05T12:00:00Z",
      routeNumber: 74,
      dairy: "Milky Way (633)",
      tank: 2,
      ltNumber: "LMH32001",
      invoiceNumber: "10175359",
      status: "active",
      eta: "7:28",
      trackingUrl: "https://track.example.com/LMH32001",
      driverName: "Maria Rodriguez",
      vehicleId: "VEH-015",
      currentLocation: {
        lat: 33.4584,
        lng: -112.0840,
        speed: 65,
        timestamp: "2025-06-05T14:32:00Z"
      }
    },
    {
      startTime: "2025-06-05T20:00:00Z",
      routeNumber: 75,
      dairy: "T&K Dairy",
      tank: 1,
      ltNumber: "NIM69133",
      invoiceNumber: "10175394",
      status: "scheduled",
      eta: "9:15",
      trackingUrl: "https://track.example.com/NIM69133",
      driverName: "Unknown Driver",
      vehicleId: "VEH-022"
    }
  ];
};

const Dashboard = () => {
  const [barns, setBarns] = useState<Barn[]>([]);
  const [pickups, setPickups] = useState<CustomerSummary[]>([]);
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [barnsData, pickupsData, routesData, summaryData] = await Promise.all([
          fetchBarns(),
          fetchPickups('2025-06'),
          fetchTodaysRoutes(),
          fetchDashboardSummary()
        ]);
        
        setBarns(barnsData);
        setPickups(pickupsData);
        setRoutes(routesData);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();

    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
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
            Dairy Operations Dashboard
          </h1>
          <p className="text-slate-600 text-lg font-medium">Real-time monitoring for 41 dairy locations</p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Dashboard Summary - Top Full Width */}
          {summary && (
            <div className="lg:col-span-12">
              <DashboardSummaryWidget summary={summary} />
            </div>
          )}

          {/* Volume Widget - Left */}
          <div className="lg:col-span-6">
            <VolumeWidget barns={barns} />
          </div>

          {/* Pickups Widget - Right */}
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
