import { useState, useEffect } from 'react';
import { VolumeWidget } from '../components/dashboard/VolumeWidget';
import { PickupsWidget } from '../components/dashboard/PickupsWidget';
import { RoutesWidget } from '../components/dashboard/RoutesWidget';
import { DairyOverviewWidget } from '../components/dashboard/DairyOverviewWidget';
import { SimpleTankStatus } from '../components/dashboard/SimpleTankStatus';
import { AppSidebar } from '../components/AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Barn, CustomerSummary, RouteRecord, Tank } from '../types/dashboard';

// Mock function to get dairy-specific data
const fetchDairyData = async (dairyId: string) => {
  // In real implementation, this would filter by dairy ID
  // For now, showing Milky Way (633) as example
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

  const routes: RouteRecord[] = [
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
    }
  ];

  const pickups: CustomerSummary[] = [
    { customer: "Fairlife", totalWeight: 2890000, invoiceCount: 42, marketShare: 35.2 },
    { customer: "Schreiber", totalWeight: 1850000, invoiceCount: 28, marketShare: 22.5 },
    { customer: "UDA", totalWeight: 1720000, invoiceCount: 25, marketShare: 20.9 },
    { customer: "Horizon", totalWeight: 1240000, invoiceCount: 18, marketShare: 15.1 },
    { customer: "Clover", totalWeight: 512000, invoiceCount: 7, marketShare: 6.3 }
  ];

  return { barn, routes, pickups };
};

const DairyDashboard = () => {
  const [barn, setBarn] = useState<Barn | null>(null);
  const [pickups, setPickups] = useState<CustomerSummary[]>([]);
  const [routes, setRoutes] = useState<RouteRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // In real implementation, get dairy ID from authentication
  const dairyId = "633"; // Milky Way dairy ID

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchDairyData(dairyId);
        setBarn(data.barn);
        setPickups(data.pickups);
        setRoutes(data.routes);
      } catch (error) {
        console.error('Failed to load dairy data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [dairyId]);

  if (loading) {
    return (
      <SidebarProvider>
        <div className="min-h-screen flex w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
          <AppSidebar />
          <SidebarInset className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-6 shadow-lg"></div>
              <p className="text-slate-700 font-medium text-lg">Loading your dairy data...</p>
            </div>
          </SidebarInset>
        </div>
      </SidebarProvider>
    );
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <AppSidebar />
        <SidebarInset>
          <div className="container mx-auto p-4 md:p-6">
            {/* Header with sidebar toggle */}
            <div className="flex items-center justify-between mb-6 md:mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-800 to-blue-800 bg-clip-text text-transparent mb-2 md:mb-3 tracking-tight">
                  {barn?.name || 'Dairy Dashboard'}
                </h1>
                <p className="text-slate-600 text-base md:text-lg font-medium">
                  Farm monitoring dashboard
                </p>
              </div>
              <SidebarTrigger />
            </div>

            {/* Dashboard Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
              {/* Dairy Overview - Top Full Width */}
              {barn && (
                <div className="lg:col-span-12">
                  <DairyOverviewWidget barn={barn} />
                </div>
              )}

              {/* Simple Tank Status - Left */}
              {barn && (
                <div className="lg:col-span-12 bg-white rounded-2xl shadow-xl p-4 md:p-6">
                  <SimpleTankStatus tanks={barn.tanks} />
                </div>
              )}

              {/* Routes Widget - Bottom Full Width */}
              <div className="lg:col-span-12">
                <RoutesWidget routes={routes} />
              </div>
            </div>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default DairyDashboard;
